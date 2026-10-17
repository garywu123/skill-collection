"""Direct discussion ownership, authorization, evidence, and independent handoff."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crossagent import engine, exploration, providers, store
from crossagent.errors import UsageError
from test_cli import Harness, produce, review, finding


class ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness(self, {}, producer="claude:claude-opus-5-5:high",
                         reviewer="claude:claude-opus-5-5:high",
                         cli={"claude": str(Path(sys.executable).resolve())})
        self.skill = self.h.dir / "skills" / "product-brief" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text("# Product Brief\nExplore before authorized writing.\n", encoding="utf-8")
        self.provider_root = self.h.dir / "claude"
        self.h.env["CLAUDE_CONFIG_DIR"] = str(self.provider_root)
        env = patch.dict(os.environ, {**self.h.env, "CLAUDE_CONFIG_DIR": str(self.provider_root)})
        env.start()
        self.addCleanup(env.stop)
        self.calls = []

    def start(self, **overrides):
        args = dict(stage="general", artifact=None, first="explore", request="Discuss the existing app.",
                    producer=None, reviewer=None, dry_run=False, skill=str(self.skill))
        args.update(overrides)
        return engine.start(self.h.repo, **args)["run_id"]

    def source(self, run):
        state = self.h.state(run)
        session = state["exploration"]["session_id"]
        path = self.provider_root / "projects" / "fixture" / f"{session}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        records = [{"type": role, "sessionId": session, "cwd": str(self.h.repo),
                    "uuid": str(uuid.uuid4()), "timestamp": "2026-10-16T12:00:00Z",
                    "message": {"role": role, "content": text}}
                   for role, text in (("user", "Use local storage; cloud sync is undecided."),
                                      ("assistant", "Candidate: a single file HTML prototype."))]
        path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")
        return path

    def discuss(self, run):
        source = None
        child = Mock(pid=987654, wait=Mock(return_value=0))
        def launch(*args, **kwargs):
            nonlocal source
            source = self.source(run)
            return child
        with patch.object(exploration.subprocess, "Popen", side_effect=launch) as process:
            result = exploration.expert(self.h.repo, run)
        self.assertEqual(result["phase"], "explore")
        return source, process.call_args.args[0]

    def promote(self, run, **extra):
        return exploration.promote(self.h.repo, run, artifact="docs/plan.md",
                                   request="User authorized writing the discussed brief.", **extra)

    def model(self, call):
        self.calls.append(call)
        if call.role == "producer":
            (self.h.repo / "docs" / "plan.md").write_text("# Brief\nLocal storage.\n", encoding="utf-8")
            data = produce()["output"]
        else:
            data = review()["output"]
        return providers.CallResult(data=data, session_id=call.session_id or str(uuid.uuid4()))

    def test_explore_is_read_only_next_does_not_invoke_and_resume_keeps_session(self):
        before = (self.h.repo / "docs" / "plan.md").read_bytes()
        run = self.start()
        self.assertIsNone(self.h.state(run)["artifact"])
        with patch.object(providers.Claude, "run") as invoke:
            self.assertEqual(engine.next_step(self.h.repo, run)["phase"], "explore")
            invoke.assert_not_called()
        _, first = self.discuss(run)
        _, resumed = self.discuss(run)
        for command in (first, resumed):
            self.assertEqual(command[command.index("--tools") + 1], "Read,Grep,Glob")
            self.assertEqual(command[command.index("--permission-mode") + 1], "plan")
            self.assertIn("--strict-mcp-config", command)
            self.assertNotIn("--dangerously-skip-permissions", command)
            self.assertEqual(command[-2], "--")
            self.assertIn("Discuss the existing app.", command[-1])
            self.assertIn("# Product Brief", command[-1])
            self.assertEqual(command[command.index("--add-dir") + 1], str(self.skill.parent))
        session = self.h.state(run)["exploration"]["session_id"]
        self.assertEqual(first[first.index("--session-id") + 1], session)
        self.assertEqual(resumed[resumed.index("--resume") + 1], session)
        self.assertEqual((self.h.repo / "docs" / "plan.md").read_bytes(), before)

    def test_explicit_expert_selection_still_requires_the_lifecycle_owner(self):
        with self.assertRaisesRegex(UsageError, "owning Skill"):
            self.start(stage="feature-plan")
        plan_skill = self.h.dir / "skills" / "30.feature-plan" / "SKILL.md"
        plan_skill.parent.mkdir(parents=True)
        plan_skill.write_text("# Feature Plan\n", encoding="utf-8")
        run = self.start(stage="feature-plan", skill=str(plan_skill))
        self.assertEqual(self.h.state(run)["skill"], str(plan_skill.resolve()))

    def test_failed_launch_without_transcript_can_retry_and_abandon_with_evidence_gap(self):
        for failure in (OSError("launch failed"), None):
            with self.subTest(failure=failure):
                run = self.start()
                child = Mock(pid=987654, wait=Mock(return_value=2))
                with patch.object(exploration.subprocess, "Popen", side_effect=failure, return_value=child):
                    if failure:
                        with self.assertRaisesRegex(UsageError, "Cannot launch"):
                            exploration.expert(self.h.repo, run)
                    else:
                        self.assertEqual(exploration.expert(self.h.repo, run)["exit_code"], 2)
                state = self.h.state(run)
                self.assertEqual(state["phase"], "explore")
                self.assertFalse((store.run_path(self.h.repo, run) / "interactive.lock").exists())
                args, _ = exploration.command(state)
                self.assertEqual(args[args.index("--session-id") + 1], state["exploration"]["session_id"])
                self.assertNotIn("--resume", args)
                with patch.object(providers.Claude, "cleanup") as cleanup:
                    closed = engine.close(self.h.repo, run, True)
                    cleanup.assert_not_called()
                self.assertEqual(closed["final_status"], "abandoned")
                self.assertIn(state["exploration"]["session_id"], closed["protected_sessions"])
                handoff = json.loads((Path(closed["retained_evidence"]) / "handoff.json").read_text(encoding="utf-8"))
                self.assertIsNone(handoff["evidence"])
                self.assertIn("missing or ambiguous", handoff["evidence_gap"]["reason"])
                self.assertEqual(handoff["evidence_gap"], closed["report"]["discussion_evidence_gap"])
                self.assertFalse(store.run_path(self.h.repo, run).exists())

    def test_failed_launch_retry_creates_transcript_then_resumes_the_same_session(self):
        run = self.start()
        with patch.object(exploration.subprocess, "Popen", side_effect=OSError("launch failed")):
            with self.assertRaises(UsageError):
                exploration.expert(self.h.repo, run)
        _, first = self.discuss(run)
        _, resumed = self.discuss(run)
        session = self.h.state(run)["exploration"]["session_id"]
        self.assertEqual(first[first.index("--session-id") + 1], session)
        self.assertEqual(resumed[resumed.index("--resume") + 1], session)

    def test_abandon_unpromoted_import_failure_retains_source_and_reports_gap(self):
        run = self.start()
        source, _ = self.discuss(run)
        source.write_text("malformed transcript", encoding="utf-8")
        with patch.object(providers.Claude, "cleanup") as cleanup:
            closed = engine.close(self.h.repo, run, True)
            cleanup.assert_not_called()
        self.assertEqual(source.read_text(encoding="utf-8"), "malformed transcript")
        self.assertIn("malformed or unreadable", closed["report"]["discussion_evidence_gap"]["reason"])

    def test_same_expert_produces_and_fresh_independent_reviewer_gets_evidence(self):
        run = self.start()
        self.discuss(run)
        original = self.h.state(run)
        self.promote(run)
        with patch.object(providers.Claude, "run", side_effect=self.model):
            self.assertEqual(engine.next_step(self.h.repo, run)["phase"], "review")
            result = engine.next_step(self.h.repo, run)
        self.assertEqual(result["final_status"], "independently-passed")
        producer, reviewer = self.calls
        self.assertEqual(producer.session_id, original["exploration"]["session_id"])
        self.assertIsNone(reviewer.session_id)
        self.assertEqual(reviewer.allowed_commands, [])
        for call in self.calls:
            self.assertIn("Original discussion evidence", call.prompt)
            self.assertIn("original message IDs", call.prompt)
        self.assertEqual(self.h.state(run)["trees"]["baseline"], original["trees"]["baseline"])

    def test_intervening_changes_require_reconciliation_and_keep_original_baseline(self):
        run = self.start()
        self.discuss(run)
        baseline = self.h.state(run)["trees"]["baseline"]
        (self.h.repo / "docs" / "plan.md").write_text("Changed by user during discussion.\n", encoding="utf-8")
        with self.assertRaisesRegex(UsageError, "reconcile"):
            self.promote(run)
        self.assertEqual(self.h.state(run)["phase"], "explore")
        self.promote(run, reconcile="User confirms their concurrent draft belongs in the final review.")
        state = self.h.state(run)
        self.assertEqual(state["trees"]["baseline"], baseline)
        self.assertIn("docs/plan.md", state["exploration_transition"]["changed_files"])

    def test_tampered_import_fails_before_any_provider_call(self):
        run = self.start()
        self.discuss(run)
        self.promote(run)
        manifest = self.h.state(run)["discussion_evidence"]
        Path(manifest["file"]).write_text("tampered", encoding="utf-8")
        with patch.object(providers.Claude, "run") as invoke:
            result = engine.next_step(self.h.repo, run)
            invoke.assert_not_called()
        self.assertEqual(result["phase"], "failed")
        self.assertIn("changed since import", result["error"]["message"])

    def test_missing_or_wrong_project_transcript_cannot_promote(self):
        run = self.start()
        with self.assertRaisesRegex(UsageError, "missing or ambiguous"):
            self.promote(run)
        source = self.source(run)
        records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
        for record in records:
            record["cwd"] = str(self.h.dir / "different-project")
        source.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")
        with self.assertRaisesRegex(UsageError, "different project"):
            self.promote(run)
        self.assertEqual(self.h.state(run)["phase"], "explore")

    def test_close_retains_user_session_and_verified_evidence_before_cleanup(self):
        run = self.start()
        source, _ = self.discuss(run)
        self.promote(run)
        with patch.object(providers.Claude, "run", side_effect=self.model):
            engine.next_step(self.h.repo, run)
            engine.next_step(self.h.repo, run)
        state = self.h.state(run)
        protected = state["exploration"]["session_id"]
        reviewer = state["workers"]["reviewer"]["session_id"]
        with patch.object(providers.Claude, "cleanup", return_value=[]) as cleanup:
            closed = engine.close(self.h.repo, run, False)
        cleanup.assert_called_once_with(reviewer)
        self.assertIn(protected, closed["protected_sessions"])
        self.assertTrue(source.is_file())
        folder = Path(closed["retained_evidence"])
        self.assertTrue((folder / "discussion.json").is_file())
        handoff = json.loads((folder / "handoff.json").read_text(encoding="utf-8"))
        self.assertEqual(handoff["evidence"]["session_id"], protected)
        exploration.forget_history(self.h.repo, run)
        self.assertFalse(folder.exists())
        self.assertTrue(source.is_file())

    def test_tampered_evidence_blocks_close_and_session_cleanup(self):
        run = self.start()
        self.discuss(run)
        self.promote(run)
        Path(self.h.state(run)["discussion_evidence"]["file"]).write_text("tampered", encoding="utf-8")
        with patch.object(providers.Claude, "cleanup") as cleanup:
            with self.assertRaisesRegex(UsageError, "changed since import"):
                engine.close(self.h.repo, run, True)
            cleanup.assert_not_called()
        self.assertTrue((store.run_path(self.h.repo, run) / "state.json").is_file())

    def test_explicit_skip_records_missing_review_and_failed_checks_never_pass(self):
        for exit_code, expected in ((0, "completed-without-review"), (1, "needs-user-decision")):
            with self.subTest(exit_code=exit_code):
                run = self.start()
                self.discuss(run)
                with self.assertRaisesRegex(UsageError, "reason"):
                    self.promote(run, skip_review=True)
                self.promote(run, skip_review=True, reason="User says this round does not need independent review.")
                check = {"exit_code": exit_code, "command": "project-check", "after": "P0"}
                with patch.object(providers.Claude, "run", side_effect=self.model), patch.object(
                        engine, "_run_checks", return_value=[check]):
                    result = engine.next_step(self.h.repo, run)
                self.assertEqual(result["final_status"], expected)
                self.assertEqual(self.h.state(run)["reviews_done"], 0)
                with patch.object(providers.Claude, "cleanup", return_value=[]):
                    engine.close(self.h.repo, run, False)

    def test_waiver_before_first_review_does_not_bypass_existing_findings(self):
        run = self.start()
        self.discuss(run)
        self.promote(run)
        with patch.object(providers.Claude, "run", side_effect=self.model):
            engine.next_step(self.h.repo, run)
        with self.assertRaisesRegex(UsageError, "explicit reason"):
            exploration.waive_review(self.h.repo, run, " ")
        def review_with_finding(call):
            return providers.CallResult(data=review(findings=[finding()])["output"], session_id=str(uuid.uuid4()))
        with patch.object(providers.Claude, "run", side_effect=review_with_finding):
            self.assertEqual(engine.next_step(self.h.repo, run)["phase"], "awaiting-decision")
        with self.assertRaisesRegex(UsageError, "never bypass findings"):
            exploration.waive_review(self.h.repo, run, "Skip now")

    def test_exclusive_terminal_control_and_interruption_release(self):
        run = self.start()
        def during_interaction(*args, **kwargs):
            self.assertEqual(self.h.state(run)["phase"], "interacting")
            with self.assertRaises(UsageError):
                self.promote(run)
            with self.assertRaises(UsageError):
                exploration.expert(self.h.repo, run)
            with self.assertRaises(UsageError):
                engine.close(self.h.repo, run, True)
            with patch.object(providers.Claude, "run") as invoke:
                engine.next_step(self.h.repo, run)
                invoke.assert_not_called()
            return 0
        child = Mock(pid=987654, wait=Mock(side_effect=during_interaction))
        with patch.object(exploration.subprocess, "Popen", return_value=child):
            exploration.expert(self.h.repo, run)
        self.assertEqual(self.h.state(run)["phase"], "explore")
        state = store.load(self.h.repo, run)
        state["phase"] = "interacting"
        store.save(state)
        state["exploration"]["pid"] = 987654
        store.save(state)
        lock = store.run_path(self.h.repo, run) / "interactive.lock"
        lock.write_text("interrupted launcher", encoding="utf-8")
        with patch.object(exploration, "_process_alive", return_value=True):
            with self.assertRaisesRegex(UsageError, "still alive"):
                exploration.expert(self.h.repo, run, release=True)
        with patch.object(exploration, "_process_alive", side_effect=OSError("access denied")):
            with self.assertRaisesRegex(UsageError, "Cannot verify"):
                exploration.expert(self.h.repo, run, release=True)
        self.assertEqual(self.h.state(run)["phase"], "interacting")
        with patch.object(exploration, "_process_alive", return_value=False):
            self.assertEqual(exploration.expert(self.h.repo, run, release=True)["phase"], "explore")
        self.assertFalse(lock.exists())
        with self.assertRaises(UsageError):
            exploration.expert(self.h.repo, run, release=True)
        closed = engine.close(self.h.repo, run, True)
        self.assertIn("missing or ambiguous", closed["report"]["discussion_evidence_gap"]["reason"])

    @unittest.skipUnless(os.name == "nt", "Windows native process query")
    def test_windows_release_queries_live_and_exited_real_child_without_signalling(self):
        run = self.start()
        with subprocess.Popen([sys.executable, "-c", "import sys; sys.stdin.buffer.read(1)"],
                              stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as child:
            state = store.load(self.h.repo, run)
            state["phase"] = "interacting"
            state["exploration"]["pid"] = child.pid
            store.save(state)
            lock = store.run_path(self.h.repo, run) / "interactive.lock"
            lock.write_text("interrupted launcher", encoding="utf-8")
            try:
                with patch.object(exploration.os, "kill", side_effect=AssertionError("must not signal")):
                    with self.assertRaisesRegex(UsageError, "still alive"):
                        exploration.expert(self.h.repo, run, release=True)
                    self.assertIsNone(child.poll())
                    self.assertTrue(lock.exists())
                    child.stdin.close()
                    self.assertEqual(child.wait(timeout=10), 0)
                    self.assertEqual(exploration.expert(self.h.repo, run, release=True)["phase"], "explore")
                    self.assertFalse(lock.exists())
            finally:
                if not child.stdin.closed:
                    child.stdin.close()
                child.wait(timeout=10)

    def test_interrupted_live_child_keeps_control_until_release(self):
        run = self.start()
        child = Mock(pid=987654, wait=Mock(side_effect=[KeyboardInterrupt(), subprocess.TimeoutExpired("claude", 1)]))
        with patch.object(exploration.subprocess, "Popen", return_value=child):
            with self.assertRaisesRegex(UsageError, "still running"):
                exploration.expert(self.h.repo, run)
        self.assertEqual(self.h.state(run)["phase"], "interacting")
        self.assertTrue((store.run_path(self.h.repo, run) / "interactive.lock").exists())

    def test_cli_explore_without_artifact_and_explicit_promotion_route(self):
        preview = self.h.run("start", "--stage", "general", "--first", "explore", "--skill", str(self.skill),
                             "--request", "Discuss the product first.", "--dry-run")
        self.assertTrue(preview["dry_run"])
        run = self.h.run("start", "--stage", "general", "--first", "explore", "--skill", str(self.skill),
                         "--request", "Discuss the product first.")["run_id"]
        self.assertEqual(self.h.next(run)["phase"], "explore")
        self.source(run)
        result = self.h.run("promote", "--run", run, "--artifact", "docs/plan.md", "--request",
                            "User authorized the brief.", "--skip-review", "--reason", "User opted out this round.")
        self.assertEqual(result["phase"], "produce")
        self.assertEqual(self.h.state(run)["review_policy"], {"skip": True, "reason": "User opted out this round."})


if __name__ == "__main__":
    unittest.main()
