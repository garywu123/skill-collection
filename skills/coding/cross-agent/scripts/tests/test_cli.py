"""End-to-end tests of the cross-agent CLI with the scripted fake provider.

Run from the repository root:
    python -m unittest discover -s skills/coding/cross-agent/scripts/tests
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "cross_agent.py"


def finding(claim="The requested outcome is missing.", severity="major", category="unmet-outcome", evidence=None):
    return {
        "id": "X-1",
        "category": category,
        "severity": severity,
        "claim": claim,
        "evidence": ["docs/plan.md:1"] if evidence is None else evidence,
        "recommendation": "Fix it.",
    }


def review(findings=(), earlier=(), notes=(), write=None):
    step = {
        "output": {
            "findings": list(findings),
            "earlier_results": [{"finding_id": fid, "result": result} for fid, result in earlier],
            "notes": list(notes),
        }
    }
    if write:
        step["write"] = write
    return step


def produce(outcomes=(), status="done", questions=(), write=None, **extra):
    step = {
        "output": {
            "status": status,
            "summary": "Did the work.",
            "questions": list(questions),
            "blocker": None,
            "outcomes": [{"finding_id": fid, "result": result, "rationale": "Because."} for fid, result in outcomes],
        }
    }
    if write:
        step["write"] = write
    step.update(extra)
    return step


def decision(finding_id, disposition, rationale=None, priority=None):
    return {"finding_id": finding_id, "disposition": disposition, "rationale": rationale, "priority": priority}


def _remove_tree(path: Path) -> None:
    def make_writable(function, target, _info):
        os.chmod(target, stat.S_IWRITE)
        function(target)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=make_writable)
    else:
        shutil.rmtree(path, onerror=make_writable)


def _toml(value) -> str:
    return ("true" if value else "false") if isinstance(value, bool) else json.dumps(value)


class Harness:
    def __init__(self, test: unittest.TestCase, script: dict, **config):
        self.dir = Path(tempfile.mkdtemp(prefix="cross-agent-test-"))
        test.addCleanup(_remove_tree, self.dir)
        self.repo = self.dir / "repo"
        (self.repo / "docs").mkdir(parents=True)
        (self.repo / "AGENTS.md").write_text("# Test Project\n", encoding="utf-8")
        (self.repo / "docs" / "plan.md").write_text("# Plan\n", encoding="utf-8")
        for args in (
            ["init", "-q"],
            ["config", "user.email", "test@example.com"],
            ["config", "user.name", "Test"],
            ["config", "core.autocrlf", "false"],
            ["add", "-A"],
            ["commit", "-q", "-m", "init"],
        ):
            subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)
        self.script = self.dir / "fake.json"
        self.script.write_text(json.dumps(script), encoding="utf-8")
        self.config = self.dir / "config.toml"
        self.config.write_text("".join(f"{key} = {_toml(value)}\n" for key, value in config.items()), encoding="utf-8")
        self.env = {**os.environ, "CROSS_AGENT_CONFIG": str(self.config), "CROSS_AGENT_FAKE_SCRIPT": str(self.script)}

    def run(self, *args, expect=0) -> dict:
        process = subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=self.repo,
            env=self.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if process.returncode != expect:
            raise AssertionError(f"exit {process.returncode}\n{process.stdout}\n{process.stderr}")
        return json.loads(process.stdout)

    def start(self, first="review", *extra) -> dict:
        return self.run(
            "start", "--stage", "general", "--artifact", "docs/plan.md", "--first", first,
            "--request", "Keep the plan correct.", "--producer", "fake", "--reviewer", "fake", *extra,
        )

    def next(self, run_id) -> dict:
        return self.run("next", "--run", run_id)

    def decide(self, run_id, *decisions, expect=0) -> dict:
        path = self.dir / "decisions.json"
        path.write_text(json.dumps({"decisions": list(decisions)}), encoding="utf-8")
        return self.run("decide", "--run", run_id, "--input", str(path), expect=expect)

    def calls(self, role) -> list[dict]:
        log = self.script.with_name(self.script.name + ".log.jsonl")
        entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        return [entry for entry in entries if entry["role"] == role]

    def state(self, run_id) -> dict:
        path = self.repo / ".cross-agent" / "runs" / run_id / "state.json"
        return json.loads(path.read_text(encoding="utf-8"))


class BudgetTests(unittest.TestCase):
    def test_produce_mode_runs_at_most_n_plus_one_producer_steps(self):
        h = Harness(
            self,
            {
                "producer": [produce(write={"docs/plan.md": "v1\n"})]
                + [produce(outcomes=[("R1-001", "fixed")], write={"docs/plan.md": f"v{n}\n"}) for n in (2, 3, 4)],
                "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "open")]), review(earlier=[("R1-001", "open")])],
            },
            max_reviews=3,
        )
        run_id = h.start("produce")["run_id"]
        for _ in range(3):
            self.assertEqual(h.next(run_id)["phase"], "review")
            self.assertEqual(h.next(run_id)["phase"], "awaiting-decision")
            h.decide(run_id, decision("R1-001", "accepted"))
        event = h.next(run_id)
        self.assertEqual(event["phase"], "finalizing")
        self.assertEqual([item["id"] for item in event["remaining_accepted_findings"]], ["R1-001"])
        event = h.next(run_id)
        self.assertEqual(event["final_status"], "completed-by-orchestrator")
        self.assertEqual(len(h.calls("producer")), 4)
        self.assertEqual(len(h.calls("reviewer")), 3)
        self.assertTrue(all(call["session_id"] for call in h.calls("producer")[1:]), "later calls resume the session")

    def test_review_mode_runs_at_most_n_producer_steps(self):
        h = Harness(
            self,
            {
                "producer": [produce(outcomes=[("R1-001", "fixed")], write={"docs/plan.md": f"v{n}\n"}) for n in (1, 2, 3)],
                "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "open")]), review(earlier=[("R1-001", "open")])],
            },
            max_reviews=3,
        )
        run_id = h.start("review")["run_id"]
        for _ in range(3):
            self.assertEqual(h.next(run_id)["phase"], "awaiting-decision")
            h.decide(run_id, decision("R1-001", "accepted"))
            h.next(run_id)
        self.assertEqual(h.state(run_id)["phase"], "finalizing")
        self.assertEqual(len(h.calls("producer")), 3)

    def test_a_clean_first_review_ends_the_run(self):
        h = Harness(self, {"reviewer": [review()]})
        run_id = h.start()["run_id"]
        event = h.next(run_id)
        self.assertEqual((event["phase"], event["final_status"]), ("done", "independently-passed"))
        self.assertEqual(h.calls("producer"), [])


class AdjudicationTests(unittest.TestCase):
    def test_only_the_accepted_defect_reaches_the_producer_and_polish_reaches_the_backlog(self):
        h = Harness(
            self,
            {
                "reviewer": [
                    review(findings=[finding("Outcome X is missing."), finding("Rename the heading.", severity="minor", category="contradiction")]),
                    review(earlier=[("R1-001", "resolved")]),
                ],
                "producer": [produce(outcomes=[("R1-001", "fixed")], write={"docs/plan.md": "# Plan\nOutcome X\n"})],
            },
        )
        run_id = h.start()["run_id"]
        event = h.next(run_id)
        self.assertEqual([item["id"] for item in event["pending_findings"]], ["R1-001", "R1-002"])
        h.decide(
            run_id,
            decision("R1-001", "accepted", "Add outcome X, as the user asked."),
            decision("R1-002", "note-only", "Wording only; the outcome is met.", "low"),
        )
        self.assertEqual(h.next(run_id)["phase"], "review")
        producer_prompt = h.calls("producer")[0]["prompt"]
        self.assertIn("R1-001", producer_prompt)
        self.assertIn("Add outcome X, as the user asked.", producer_prompt)
        self.assertNotIn("R1-002", producer_prompt)
        event = h.next(run_id)
        self.assertEqual(event["final_status"], "independently-passed")
        self.assertIn('"R1-002"', h.calls("reviewer")[1]["prompt"], "closed findings are shown so they are not raised again")
        closed = h.run("close", "--run", run_id)
        self.assertEqual(closed["backlog_items"], ["RB-0001"])
        backlog_text = (h.repo / "docs" / "review-backlog.md").read_text(encoding="utf-8")
        self.assertIn("## RB-0001: Rename the heading.", backlog_text)
        self.assertIn("- Status: `open`", backlog_text)
        self.assertFalse((h.repo / ".cross-agent" / "runs" / run_id).exists())

    def test_a_minor_finding_cannot_be_accepted(self):
        h = Harness(self, {"reviewer": [review(findings=[finding(severity="minor")])]})
        run_id = h.start()["run_id"]
        h.next(run_id)
        error = h.decide(run_id, decision("R1-001", "accepted"), expect=2)
        self.assertIn("only blocker and major", error["error"])
        self.assertEqual(h.state(run_id)["phase"], "awaiting-decision")

    def test_every_pending_finding_needs_a_decision(self):
        h = Harness(self, {"reviewer": [review(findings=[finding(), finding("Second.")])]})
        run_id = h.start()["run_id"]
        h.next(run_id)
        error = h.decide(run_id, decision("R1-001", "accepted"), expect=2)
        self.assertIn("R1-002", error["error"])

    def test_rejected_findings_skip_the_backlog_when_configured(self):
        h = Harness(self, {"reviewer": [review(findings=[finding("Add a cache for future scale.")])]}, backlog_rejected=False)
        run_id = h.start()["run_id"]
        h.next(run_id)
        self.assertEqual(h.decide(run_id, decision("R1-001", "rejected", "Speculative.", "none"))["final_status"], "independently-passed")
        self.assertEqual(h.run("close", "--run", run_id)["backlog_items"], [])
        self.assertFalse((h.repo / "docs" / "review-backlog.md").exists())

    def test_findings_without_evidence_become_notes(self):
        h = Harness(self, {"reviewer": [review(findings=[finding(evidence=["  "])])]})
        run_id = h.start()["run_id"]
        event = h.next(run_id)
        self.assertEqual(event["final_status"], "independently-passed")
        self.assertIn("Demoted, no evidence", event["report"]["notes"][0])


class FinalizationTests(unittest.TestCase):
    def test_an_unfixed_finding_left_for_the_user_reaches_the_backlog(self):
        h = Harness(
            self,
            {
                "reviewer": [review(findings=[finding("Show a velocity overlay.")])],
                "producer": [produce(outcomes=[("R1-001", "not-fixed")])],
            },
            max_reviews=1,
        )
        run_id = h.start()["run_id"]
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        self.assertEqual(h.next(run_id)["phase"], "finalizing")
        h.decide(run_id, decision("R1-001", "needs-user-decision", "Adds UI behavior.", "high"))
        self.assertEqual(h.next(run_id)["final_status"], "needs-user-decision")
        closed = h.run("close", "--run", run_id)
        self.assertEqual(closed["backlog_items"], ["RB-0001"])
        text = (h.repo / "docs" / "review-backlog.md").read_text(encoding="utf-8")
        self.assertIn("- Type: `needs-user-decision`", text)
        self.assertIn("- Priority: `high`", text)


class WorkerTests(unittest.TestCase):
    def test_a_reviewer_write_fails_the_run_and_keeps_its_state(self):
        h = Harness(self, {"reviewer": [review(write={"docs/plan.md": "tampered\n"})]})
        run_id = h.start()["run_id"]
        event = h.next(run_id)
        self.assertEqual(event["phase"], "failed")
        self.assertIn("Reviewer changed files", event["error"]["message"])
        self.assertTrue(Path(event["state_path"]).is_file())

    def test_an_unavailable_session_is_replaced_from_the_run_state(self):
        h = Harness(
            self,
            {
                "producer": [
                    produce(write={"docs/plan.md": "v1\n"}),
                    produce(outcomes=[("R1-001", "fixed")], write={"docs/plan.md": "v2\n"}, fail_on_resume="session not found"),
                ],
                "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])],
            },
        )
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        self.assertEqual(h.next(run_id)["phase"], "review")
        calls = h.calls("producer")
        self.assertEqual([call["session_id"] is None for call in calls], [True, False, True])
        self.assertIn("Run summary so far", calls[2]["prompt"])
        state = h.state(run_id)
        self.assertEqual(state["workers"]["producer"]["generation"], 2)
        self.assertEqual((state["reviews_done"], [f["id"] for f in state["findings"]]), (1, ["R1-001"]))
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")

    def test_a_large_context_rotates_to_a_fresh_session(self):
        h = Harness(
            self,
            {
                "producer": [produce(write={"docs/plan.md": "v1\n"}, context_tokens=500), produce(outcomes=[("R1-001", "fixed")])],
                "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])],
            },
            rotate_at_tokens=100,
        )
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        second = h.calls("producer")[1]
        self.assertIsNone(second["session_id"])
        self.assertIn("Run summary so far", second["prompt"])

    def test_a_producer_question_waits_for_the_user_and_resumes_the_same_session(self):
        h = Harness(
            self,
            {
                "producer": [produce(status="needs-user-decision", questions=["Option A or B?"]), produce(write={"docs/plan.md": "B\n"})],
                "reviewer": [review()],
            },
        )
        run_id = h.start("produce")["run_id"]
        event = h.next(run_id)
        self.assertEqual((event["phase"], event["questions"]), ("awaiting-answer", ["Option A or B?"]))
        self.assertEqual(h.next(run_id)["phase"], "awaiting-answer", "next re-prints a pending event")
        h.run("answer", "--run", run_id, "--text", "Option B")
        self.assertEqual(h.next(run_id)["phase"], "review")
        second = h.calls("producer")[1]
        self.assertIsNotNone(second["session_id"])
        self.assertIn("Answer: Option B", second["prompt"])
        self.assertEqual(h.state(run_id)["producer_steps"], 1)


class RunLifecycleTests(unittest.TestCase):
    def test_dry_run_starts_and_saves_nothing(self):
        h = Harness(self, {"reviewer": [review()]})
        event = h.start("review", "--dry-run")
        self.assertTrue(event["dry_run"])
        self.assertIn("read-only Reviewer", event["prompt"])
        self.assertFalse((h.repo / ".cross-agent").exists())
        self.assertEqual(h.calls("reviewer"), [])

    def test_one_open_run_per_artifact_and_state_stays_out_of_git(self):
        h = Harness(self, {"reviewer": [review(findings=[finding()])]})
        run_id = h.start()["run_id"]
        error = h.run(
            "start", "--stage", "general", "--artifact", "docs/plan.md", "--first", "review",
            "--request", "Again.", "--producer", "fake", "--reviewer", "fake", expect=2,
        )
        self.assertIn(run_id, error["error"])
        status = subprocess.run(["git", "status", "--porcelain"], cwd=h.repo, capture_output=True, text=True).stdout
        self.assertEqual(status.strip(), "")
        listed = h.run("status")
        self.assertEqual([run["run_id"] for run in listed["open_runs"]], [run_id])
        self.assertIn("backlog_rejected", listed["settings"])

    def test_closing_an_unfinished_run_needs_abandon(self):
        h = Harness(self, {"reviewer": [review(findings=[finding()])]})
        run_id = h.start()["run_id"]
        h.next(run_id)
        self.assertIn("--abandon", h.run("close", "--run", run_id, expect=2)["error"])
        closed = h.run("close", "--run", run_id, "--abandon")
        self.assertEqual((closed["final_status"], closed["backlog_items"]), ("abandoned", []))


if __name__ == "__main__":
    unittest.main()
