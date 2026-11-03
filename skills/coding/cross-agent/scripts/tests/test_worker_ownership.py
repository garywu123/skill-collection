"""External work-tree changes during review, worker process-tree ownership, and orphan detection."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_cli import Harness, review
from crossagent import proctree, providers

EDITOR_FILE = ".vscode/settings.json"


def external_harness(test, *reviews, **config):
    script = {"reviewer_cannot_write": True,
              "reviewer": [review(write={EDITOR_FILE: '{"dotnet.defaultSolution": "a.sln"}\n'}), *reviews]}
    return Harness(test, script, **config)


class ExternalChangeTests(unittest.TestCase):
    def test_change_during_write_denied_review_is_reported_and_budget_unspent(self):
        h = external_harness(self, review())
        run_id = h.start()["run_id"]
        event = h.next(run_id)
        self.assertEqual(event["phase"], "failed")
        self.assertEqual(event["error"]["kind"], "work-tree-changed")
        self.assertEqual(event["error"]["changed_files"], [EDITOR_FILE])
        self.assertIn("work tree changed during review 1", event["error"]["message"])
        self.assertNotIn("Reviewer changed files", event["error"]["message"])
        self.assertEqual(event["reviews_done"], 0)
        self.assertIn("adopt-external", event["next_action"])
        self.assertEqual(h.state(run_id)["findings"], [])

    def test_retry_requires_revert_then_reviews_again(self):
        h = external_harness(self, review())
        run_id = h.start()["run_id"]
        h.next(run_id)
        self.assertIn("still differs", h.run("retry-review", "--run", run_id, expect=2)["error"])
        (h.repo / EDITOR_FILE).unlink()
        self.assertEqual(h.run("retry-review", "--run", run_id)["phase"], "review")
        done = h.next(run_id)
        self.assertEqual(done["final_status"], "independently-passed")
        self.assertEqual(done["reviews_done"], 1)
        self.assertNotIn(EDITOR_FILE, h.calls("reviewer")[-1]["prompt"])

    def test_adopted_change_joins_the_reviewed_diff_with_its_reason(self):
        h = external_harness(self, review())
        run_id = h.start()["run_id"]
        h.next(run_id)
        adopted = h.run("adopt-external", "--run", run_id, "--reason", "VS Code C# extension; keep the setting.")
        self.assertEqual(adopted["adoption"]["files"], [EDITOR_FILE])
        self.assertEqual(adopted["phase"], "failed")
        h.run("retry-review", "--run", run_id)
        done = h.next(run_id)
        self.assertEqual(done["final_status"], "independently-passed")
        prompt = h.calls("reviewer")[-1]["prompt"]
        self.assertIn("adopted these changes made outside the Producer", prompt)
        self.assertIn("VS Code C# extension; keep the setting.", prompt)
        self.assertIn("+++ b/" + EDITOR_FILE, prompt)
        self.assertEqual(done["report"]["external_adoptions"][0]["reason"], "VS Code C# extension; keep the setting.")

    def test_adoption_covers_only_the_tree_it_recorded(self):
        h = external_harness(self)
        run_id = h.start()["run_id"]
        h.next(run_id)
        h.run("adopt-external", "--run", run_id, "--reason", "Keep it.")
        (h.repo / "docs" / "plan.md").write_text("# Plan\nedited later\n", encoding="utf-8")
        self.assertIn("still differs", h.run("retry-review", "--run", run_id, expect=2)["error"])

    def test_adopt_refuses_without_an_external_change_to_keep(self):
        h = external_harness(self)
        run_id = h.start()["run_id"]
        self.assertIn("Only a review failed", h.run("adopt-external", "--run", run_id, "--reason", "x", expect=2)["error"])
        h.next(run_id)
        (h.repo / EDITOR_FILE).unlink()
        self.assertIn("nothing to adopt", h.run("adopt-external", "--run", run_id, "--reason", "x", expect=2)["error"])

    def test_a_reviewer_that_can_write_still_fails_closed(self):
        h = Harness(self, {"reviewer": [review(write={EDITOR_FILE: "{}"})]})
        run_id = h.start()["run_id"]
        event = h.next(run_id)
        self.assertIn("Reviewer changed files", event["error"]["message"])
        self.assertNotIn("kind", event["error"])
        self.assertIn("Only a failed Reviewer", h.run("retry-review", "--run", run_id, expect=2)["error"])
        self.assertIn("Only a review failed", h.run("adopt-external", "--run", run_id, "--reason", "x", expect=2)["error"])

    def test_real_providers_report_write_denial_from_their_reviewer_restrictions(self):
        self.assertTrue(providers.get("claude").reviewer_cannot_write())
        self.assertTrue(providers.get("codex").reviewer_cannot_write())
        with patch.object(providers, "CLAUDE_REVIEWER_TOOLS", ("Read", "Grep", "Glob", "Edit")):
            self.assertFalse(providers.get("claude").reviewer_cannot_write())
        with patch.object(providers, "CODEX_REVIEWER_SANDBOX", "workspace-write"):
            self.assertFalse(providers.get("codex").reviewer_cannot_write())


STAND_IN = r"""
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from crossagent import providers
root = Path(sys.argv[2])
worker = (
    "import subprocess,sys,time,pathlib; "
    "g=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
    "pathlib.Path('grandchild.pid').write_text(str(g.pid)); time.sleep(60)"
)
call = providers.Call("producer", None, None, "", {}, None, root, [], [], [], 120, root)
providers._run([sys.executable, "-c", worker], call)
"""


class ProcessTreeTests(unittest.TestCase):
    def test_worker_tree_dies_when_the_cli_process_is_killed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cli = subprocess.Popen([sys.executable, "-c", STAND_IN, str(Path(__file__).resolve().parents[1]), str(root)])
            pid_file = root / "grandchild.pid"
            deadline = time.monotonic() + 20
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue(pid_file.exists(), "worker did not start")
            time.sleep(0.2)
            grandchild = int(pid_file.read_text())
            self.assertTrue(proctree.alive(grandchild))
            # Windows: TerminateProcess closes the job handle. POSIX: SIGTERM runs the group kill.
            cli.kill() if os.name == "nt" else cli.send_signal(signal.SIGTERM)
            cli.wait(timeout=10)
            deadline = time.monotonic() + 10
            while proctree.alive(grandchild) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertFalse(proctree.alive(grandchild), "the worker's descendant outlived the CLI")

    def test_finished_worker_leaves_no_descendants(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = ("import subprocess,sys,pathlib; "
                      "g=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],"
                      "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); "
                      "pathlib.Path('grandchild.pid').write_text(str(g.pid))")
            events = []
            call = providers.Call("producer", None, None, "", {}, None, root, [], [], [], 30, root,
                                  progress=events.append)
            providers._run([sys.executable, "-c", worker], call)
            grandchild = int((root / "grandchild.pid").read_text())
            deadline = time.monotonic() + 5
            while proctree.alive(grandchild) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertFalse(proctree.alive(grandchild))
            self.assertEqual(events[0]["event"], "worker-process")

    def test_a_reused_pid_is_not_the_recorded_worker(self):
        started = proctree.process_started(os.getpid())
        self.assertTrue(proctree.alive(os.getpid(), started))
        if started is not None:
            self.assertFalse(proctree.alive(os.getpid(), "different-start"))


class OrphanTests(unittest.TestCase):
    def _record(self, h, run_id, pid, started):
        path = h.repo / ".cross-agent" / "runs" / run_id / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["workers"]["producer"]["process"] = {"pid": pid, "started": started, "at": "2026-11-03T00:00:00Z"}
        path.write_text(json.dumps(state), encoding="utf-8")

    def test_live_orphan_blocks_next_and_is_reported_by_status(self):
        sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(lambda: (sleeper.kill(), sleeper.wait()))
        h = Harness(self, {"producer": []})
        run_id = h.start("produce")["run_id"]
        self._record(h, run_id, sleeper.pid, proctree.process_started(sleeper.pid))
        refused = h.run("next", "--run", run_id, expect=2)["error"]
        self.assertIn(f"PID {sleeper.pid}", refused)
        self.assertIn("still running", refused)
        self.assertEqual(h.calls("producer"), [])
        status = h.run("status", "--run", run_id)
        self.assertEqual(status["orphan_worker"]["pid"], sleeper.pid)
        self.assertEqual(status["phase"], "produce")

    def test_exited_worker_record_does_not_block_and_is_cleared(self):
        exited = subprocess.Popen([sys.executable, "-c", "pass"])
        exited.wait()
        h = Harness(self, {"producer": [{"output": {
            "status": "done", "summary": "Did it.", "questions": [], "blocker": None, "outcomes": [],
            "segment_outcomes": [], "remaining_work": []}}], "reviewer": [review()]})
        run_id = h.start("produce")["run_id"]
        self._record(h, run_id, exited.pid, "stale")
        self.assertIsNone(h.run("status", "--run", run_id)["orphan_worker"])
        self.assertEqual(h.next(run_id)["phase"], "review")
        self.assertNotIn("process", h.state(run_id)["workers"]["producer"])


if __name__ == "__main__":
    unittest.main()
