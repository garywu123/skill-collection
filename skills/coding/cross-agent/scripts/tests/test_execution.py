"""Execution handoffs, bounded recovery, and deterministic Skill supply."""
from __future__ import annotations

import copy
import json
import subprocess
from unittest.mock import patch
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_cli import CLI, Harness, decision, finding, produce, review
from crossagent import engine, providers, schemas, store


class ExecutionTests(unittest.TestCase):
    def test_timeout_recovers_same_producer_and_feedback_returns_to_it(self):
        h = Harness(self, {
            "producer": [{"fail": "timed out after 1800 s", "write": {"result.txt": "partial"}},
                         produce(), produce(outcomes=[("R1-001", "fixed")])],
            "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])],
        })
        run_id = h.start("produce")["run_id"]
        initial = h.state(run_id)
        recovered = h.next(run_id)
        self.assertEqual(recovered["phase"], "review")
        self.assertEqual(recovered["producer_auto_retries"], 1)
        self.assertEqual((recovered["reviews_done"], recovered["producer_steps"]), (0, 1))
        calls = h.calls("producer")
        self.assertIsNone(calls[0]["session_id"])
        self.assertEqual(calls[1]["session_id"], recovered["workers"]["producer"]["session_id"])
        self.assertIn("Inspect existing edits", calls[1]["prompt"])
        self.assertEqual(h.state(run_id)["trees"]["baseline"], initial["trees"]["baseline"])
        self.assertEqual((h.repo / "result.txt").read_text(), "partial")
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        self.assertEqual(h.calls("producer")[-1]["session_id"], calls[1]["session_id"])
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")

    def test_streamed_context_survives_timeout_and_rotates_recovery(self):
        h = Harness(self, {"producer": [{"fail": "timed out after 1800 s", "telemetry": {"context_tokens": 500}},
                                        produce()]}, rotate_at_tokens=100)
        run_id = h.start("produce")["run_id"]
        result = h.next(run_id)
        self.assertEqual(result["workers"]["producer"]["generation"], 2)
        self.assertIsNone(h.calls("producer")[1]["session_id"])
        self.assertIn("Run summary so far", h.calls("producer")[1]["prompt"])
        self.assertIn("Inspect existing edits", h.calls("producer")[1]["prompt"])
        self.assertIsNone(result["workers"]["producer"]["context_tokens"], "old usage does not contaminate fresh session")
        self.assertEqual(len(result["workers"]["producer"]["sessions"]), 2)

    def test_auto_recovery_is_bounded_across_repeated_next_calls(self):
        h = Harness(self, {"producer": [{"fail": "timed out after 1800 s"}] * 3})
        run_id = h.start("produce")["run_id"]
        event = h.next(run_id)
        self.assertEqual(event["phase"], "failed")
        self.assertFalse(event["automatic_recovery_available"])
        for _ in range(2):
            self.assertEqual(h.next(run_id)["phase"], "failed")
        self.assertEqual(len(h.calls("producer")), 2)
        self.assertEqual(event["producer_steps"], 0)

    def test_legacy_timeout_run_recovers_without_reinitializing(self):
        h = Harness(self, {"producer": [produce()]}, rotate_at_tokens=100)
        run_id = h.start("produce")["run_id"]
        state = h.state(run_id)
        before = copy.deepcopy(state)
        state["phase"] = "failed"
        state["final_status"] = "failed"
        state["error"] = {"message": "The producer (claude) timed out after 1800 s", "raw_excerpt": ""}
        state["workers"]["producer"].update(session_id="fake-legacy-session", generation=1,
                                             sessions=["fake-legacy-session"], context_tokens=None,
                                             telemetry={"context_tokens": 500})
        (h.repo / ".cross-agent" / "runs" / run_id / "state.json").write_text(json.dumps(state))
        event = h.next(run_id)
        self.assertEqual(event["phase"], "review")
        self.assertEqual(event["producer_auto_retries"], 1)
        self.assertEqual(h.state(run_id)["trees"]["baseline"], before["trees"]["baseline"])
        self.assertIn("fake-legacy-session", event["workers"]["producer"]["sessions"])
        self.assertIsNone(h.calls("producer")[0]["session_id"])

    def test_explicit_retry_preserves_pending_findings_answer_and_budgets(self):
        h = Harness(self, {"producer": [produce(), {"fail": "model unavailable"},
                                        produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [review(findings=[finding()])]}, max_reviews=1)
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        self.assertEqual(h.next(run_id)["phase"], "failed")
        before = h.state(run_id)
        retried = h.run("retry-producer", "--run", run_id)
        self.assertEqual(retried["phase"], "produce")
        after = h.state(run_id)
        for key in ("trees", "workers", "findings", "settings", "reviews_done", "producer_steps", "answer"):
            self.assertEqual(after[key], before[key], key)
        self.assertEqual(h.next(run_id)["phase"], "finalizing")
        self.assertEqual(h.calls("producer")[-1]["session_id"], before["workers"]["producer"]["session_id"])
        self.assertIn("R1-001", h.calls("producer")[-1]["prompt"])

    def test_schema_and_missing_output_failures_never_retry(self):
        for step in ({"output": {"status": "done"}}, {"fail": "returned no structured output"}):
            with self.subTest(step=step):
                h = Harness(self, {"producer": [step, produce()]})
                run_id = h.start("produce")["run_id"]
                self.assertEqual(h.next(run_id)["phase"], "failed")
                h.next(run_id)
                self.assertEqual(len(h.calls("producer")), 1)
                self.assertIn("Only a failed Producer", h.run("retry-producer", "--run", run_id, expect=2)["error"])

    def test_reviewer_write_guard_applies_even_when_execution_failed(self):
        h = Harness(self, {"reviewer": [{"fail": "timed out after 1800 s", "write": {"docs/plan.md": "tampered"}}]})
        run_id = h.start()["run_id"]
        self.assertIn("Reviewer changed files", h.next(run_id)["error"]["message"])
        self.assertIn("Only a failed Reviewer", h.run("retry-review", "--run", run_id, expect=2)["error"])

    def test_checkpoint_continues_in_fresh_session_before_whole_feature_review(self):
        partial = produce(status="checkpoint", write={"result.txt": "segment one"})
        partial["output"]["summary"] = "S1 accepted: focused checks passed; contract stable; next S2 persistence."
        h = Harness(self, {"producer": [partial, produce(write={"result.txt": "all segments"})],
                           "reviewer": [review()]})
        run_id = h.start("produce")["run_id"]
        baseline = h.state(run_id)["trees"]["baseline"]
        checkpoint = h.next(run_id)
        self.assertEqual((checkpoint["phase"], checkpoint["reviews_done"], checkpoint["producer_steps"]), ("produce", 0, 0))
        self.assertEqual(h.calls("reviewer"), [])
        self.assertEqual(h.next(run_id)["phase"], "review")
        call = h.calls("producer")[1]
        self.assertIsNone(call["session_id"])
        self.assertIn("S1 accepted", call["prompt"])
        self.assertIn("Original request", call["prompt"])
        self.assertEqual(h.state(run_id)["trees"]["baseline"], baseline)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertIn("all segments", h.calls("reviewer")[0]["prompt"])

    def test_section_commits_keep_original_baseline_budget_and_review_scope(self):
        # Fake providers only; Git commits happen in the Harness's disposable temporary repository.
        segment = produce(status="checkpoint", write={"src/one.txt": "segment one"})
        segment["output"]["summary"] = "S1 accepted: focused check passed; next S2."
        fix = produce(status="checkpoint", write={"src/two.txt": "segment two fixed"})
        fix["output"]["summary"] = "R1-001 fix segment checked; next finish the revision."
        h = Harness(self, {"producer": [segment, produce(write={"src/two.txt": "segment two"}), fix,
                                        produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])]})
        (h.repo / "unrelated.txt").write_text("user file\n", encoding="utf-8")
        (h.repo / "staged.txt").write_text("user staged\n", encoding="utf-8")
        git = lambda *args: subprocess.run(["git", *args], cwd=h.repo, check=True, capture_output=True,
                                           text=True).stdout
        git("add", "--", "staged.txt")

        def commit_section(message, *paths):
            git("add", "--", *paths)
            git("commit", "-q", "-m", message, "--", *paths)
            self.assertEqual(git("show", "--name-only", "--format=", "HEAD").split(), list(paths))

        handoff = "Before continuing after a checkpoint, run git log -1 --format=%h to read the committed revision."
        run_id = h.start("produce", "--request", handoff)["run_id"]
        baseline = h.state(run_id)["trees"]["baseline"]
        self.assertEqual(h.next(run_id)["phase"], "produce")
        commit_section("demo S1: checkpoint, not independently reviewed", "src/one.txt")
        self.assertEqual(h.next(run_id)["phase"], "review")
        self.assertEqual(h.next(run_id)["phase"], "awaiting-decision")
        first_review = h.calls("reviewer")[0]["prompt"]
        self.assertIn("segment one", first_review, "committed checkpoint changes stay in the review diff")
        self.assertIn("segment two", first_review)
        h.decide(run_id, decision("R1-001", "accepted"))
        self.assertEqual(h.next(run_id)["phase"], "produce")
        commit_section("demo S2: revision checkpoint, not independently reviewed", "src/two.txt")
        state = h.state(run_id)
        self.assertEqual((state["trees"]["baseline"], state["reviews_done"], state["producer_steps"]),
                         (baseline, 1, 1))
        self.assertEqual([item["id"] for item in state["findings"]], ["R1-001"])
        self.assertEqual(h.next(run_id)["phase"], "review")
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertIn("segment two fixed", h.calls("reviewer")[1]["prompt"])
        self.assertEqual(h.state(run_id)["trees"]["baseline"], baseline)
        self.assertEqual(len(h.state(run_id)["producer_checkpoints"]), 2)
        self.assertEqual(git("status", "--porcelain", "--", "unrelated.txt", "staged.txt").splitlines(),
                         ["A  staged.txt", "?? unrelated.txt"])
        # Instruction supply only: fresh continuation Producers receive the revision handoff, not proof of compliance.
        producers = h.calls("producer")
        for index in (1, 3):
            self.assertIsNone(producers[index]["session_id"])
            self.assertIn(handoff, producers[index]["prompt"])

    def test_failed_section_recovery_commit_keeps_one_automatic_recovery(self):
        # Fake provider; the failed state is simulated in the Harness's disposable repository, as for legacy runs.
        h = Harness(self, {"producer": [produce(write={"src/one.txt": "segment one done"})],
                           "reviewer": [review()]})
        git = lambda *args: subprocess.run(["git", *args], cwd=h.repo, check=True, capture_output=True,
                                           text=True).stdout
        run_id = h.start("produce")["run_id"]
        state = h.state(run_id)
        baseline = state["trees"]["baseline"]
        state.update(phase="failed", final_status="failed",
                     error={"message": "The producer (fake) timed out after 1800 s", "raw_excerpt": ""})
        (h.repo / ".cross-agent" / "runs" / run_id / "state.json").write_text(json.dumps(state))
        (h.repo / "src").mkdir()
        (h.repo / "src" / "one.txt").write_text("segment one partial", encoding="utf-8")
        status = h.run("status", "--run", run_id)
        self.assertTrue(status["automatic_recovery_available"])
        git("add", "--", "src/one.txt")
        git("commit", "-q", "-m", "demo S1: failed, local recovery commit", "--", "src/one.txt")
        recovered = h.next(run_id)
        self.assertEqual((recovered["phase"], recovered["producer_auto_retries"]), ("review", 1))
        self.assertIn("Inspect existing edits", h.calls("producer")[0]["prompt"])
        self.assertEqual(h.state(run_id)["trees"]["baseline"], baseline)
        self.assertEqual(h.next(run_id)["final_status"], "independently-passed")
        self.assertIn("segment one done", h.calls("reviewer")[0]["prompt"])
        self.assertIn("failed, local recovery commit", git("log", "-1", "--format=%s"))

    def test_revision_checkpoints_do_not_replenish_last_revision(self):
        h = Harness(self, {"producer": [produce(), produce(status="checkpoint"),
                                        produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [review(findings=[finding()])]}, max_reviews=1)
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        self.assertEqual(h.next(run_id)["phase"], "produce")
        event = h.next(run_id)
        self.assertEqual((event["phase"], event["reviews_done"], event["producer_steps"]), ("finalizing", 1, 2))
        self.assertEqual(len(h.calls("reviewer")), 1)

    def test_checkpoint_limit_and_invalid_handoffs_stop_without_review(self):
        h = Harness(self, {"producer": [produce(status="checkpoint")] * 9})
        run_id = h.start("produce")["run_id"]
        for _ in range(8):
            self.assertEqual(h.next(run_id)["phase"], "produce")
        self.assertEqual(h.next(run_id)["phase"], "failed")
        self.assertEqual(h.calls("reviewer"), [])
        self.assertIn("Only a failed Producer", h.run("retry-producer", "--run", run_id, expect=2)["error"])
        for patch in ({"summary": " "}, {"questions": ["Unresolved?"]}, {"blocker": "blocked"},
                      {"outcomes": [{"finding_id": "R1-001", "result": "fixed", "rationale": "premature"}]}):
            with self.subTest(patch=patch):
                step = produce(status="checkpoint")
                step["output"].update(patch)
                h2 = Harness(self, {"producer": [step]})
                self.assertEqual(h2.next(h2.start("produce")["run_id"])["phase"], "failed")

    def test_dry_run_shows_the_complete_prompt_for_both_worker_roles(self):
        h = Harness(self, {})
        for first in ("produce", "review"):
            event = h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", first,
                          "--request", "Preview a feature plan.", "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high", "--dry-run")
            self.assertIn("## Execution Planning", event["prompt"])
            self.assertIn("Stage Skill supplied by CLI", event["prompt"])
            self.assertEqual(event["loaded_skill"]["name"], "feature-plan")
        self.assertEqual(h.calls("producer"), [])
        self.assertEqual(h.calls("reviewer"), [])
        self.assertFalse((h.repo / ".cross-agent/runs").exists())

    def test_skill_content_is_supplied_and_load_start_events_are_distinct(self):
        h = Harness(self, {"producer": [produce()], "reviewer": [review()]})
        run_id = h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", "produce",
                       "--request", "Plan one feature.", "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high")["run_id"]
        for role in ("producer", "reviewer"):
            process = subprocess.run([sys.executable, str(CLI), "next", "--run", run_id, "--stream"],
                                     cwd=h.repo, env=h.env, capture_output=True, text=True, check=True)
            events = [json.loads(line) for line in process.stdout.splitlines()]
            loaded = next(event for event in events if event["event"] == "skill-loaded")
            started = next(event for event in events if event["event"] == "skill-started")
            self.assertEqual(loaded["method"], "prompt-injected")
            self.assertEqual(len(loaded["skill"]["sha256"]), 64)
            self.assertEqual(started["mode"], "execute" if role == "producer" else "judge")
            self.assertLess(events.index(loaded), events.index(started))
            prompt = h.calls(role)[0]["prompt"]
            self.assertIn("## Execution Planning", prompt)
            self.assertIn("Stage Skill supplied by CLI", prompt)
            if role == "reviewer":
                self.assertIn("Do not create, modify, or delete any file", prompt)

    def test_compaction_with_unknown_usage_does_not_restore_old_context(self):
        state = {"project_root": ".", "run_id": "test", "stage": "general", "artifact": "result",
                 "roles": {"producer": {"provider": "fake", "model": None, "effort": None}},
                 "workers": {"producer": {"session_id": "saved-session", "sessions": ["saved-session"],
                                            "generation": 1, "context_tokens": 500}},
                 "settings": {"rotate_at_tokens": 1000}}
        call = providers.Call(role="producer", model=None, effort=None, prompt="", schema={},
                              session_id="saved-session", cwd=Path("."), read_dirs=[], write_dirs=[],
                              allowed_commands=[], timeout=1800, work_dir=Path("."))
        def run(_call):
            _call.telemetry.update(context_tokens=None, compactions=1)
            return providers.CallResult(error="timed out", session_id="saved-session")
        with patch.object(engine, "_call", return_value=call), patch.object(engine.store, "save"), patch.object(
            providers.Fake, "run", side_effect=run
        ):
            engine._attempt(state, "producer", providers.Fake(), lambda _: "", {}, False)
        self.assertIsNone(state["workers"]["producer"]["context_tokens"])

    def test_authentication_failure_on_resume_keeps_previous_session(self):
        h = Harness(self, {"producer": [produce(), {"fail": "authentication failed"}],
                           "reviewer": [review(findings=[finding()])]})
        run_id = h.start("produce")["run_id"]
        h.next(run_id)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        before = h.state(run_id)["workers"]["producer"]["session_id"]
        event = h.next(run_id)
        self.assertEqual(event["phase"], "failed")
        self.assertEqual(event["workers"]["producer"]["session_id"], before)
        self.assertEqual(len(h.calls("producer")), 2)
        self.assertFalse(event["automatic_recovery_available"])

    def test_active_output_cannot_extend_the_hard_timeout(self):
        import tempfile
        import time
        with tempfile.TemporaryDirectory() as directory:
            call = providers.Call(role="producer", model=None, effort=None, prompt="", schema={},
                                  session_id=None, cwd=Path(directory), read_dirs=[], write_dirs=[],
                                  allowed_commands=[], timeout=0.25, work_dir=Path(directory))
            started = time.monotonic()
            with self.assertRaises(subprocess.TimeoutExpired):
                providers._run([sys.executable, "-u", "-c",
                                "import time; exec('while True:\\n print(1, flush=True); time.sleep(0.02)')"], call)
            self.assertLess(time.monotonic() - started, 5)

    def test_implicit_policy_is_enabled_for_the_agreed_skills(self):
        coding = Path(__file__).resolve().parents[3]
        for name in ("20.feature-map", "30.feature-plan", "40.feature-delivery", "cross-agent"):
            folder = coding / name
            self.assertIn("disable-model-invocation: false", (folder / "SKILL.md").read_text())
            self.assertNotIn("Invoke explicitly", (folder / "SKILL.md").read_text())
            self.assertEqual((folder / "agents" / "openai.yaml").read_text().strip(),
                             "policy:\n  allow_implicit_invocation: true")


    def test_replan_parks_and_resumes_with_original_delivery_baseline_and_budget(self):
        h = Harness(self, {"producer": [{"fail": "model unavailable"}, produce()], "reviewer": [review()]})
        delivery = h.run("start", "--stage", "feature-delivery", "--artifact", "docs/plan.md",
                         "--first", "produce", "--request", "Deliver existing plan.",
                         "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high")["run_id"]
        h.next(delivery)
        before = h.state(delivery)
        h.run("park", "--run", delivery, "--reason", "User requests reviewed replanning.")
        self.assertEqual(h.run("status")["open_runs"], [])
        self.assertEqual(h.next(delivery)["phase"], "parked")
        self.assertEqual(len(h.calls("producer")), 1)
        (h.repo / "docs/plan.md").write_text("# Revised segmented plan\n")
        plan = h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", "review",
                     "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high")["run_id"]
        self.assertIn("independently passed", h.run("resume-delivery", "--run", delivery, "--plan-run", plan,
                       "--request", "Execute S1 only then checkpoint.", expect=2)["error"])
        self.assertEqual(h.next(plan)["final_status"], "independently-passed")
        event = h.run("resume-delivery", "--run", delivery, "--plan-run", plan,
                      "--request", "Execute S1 only then checkpoint.", "--max-diff-kb", "400")
        self.assertEqual((event["reviews_done"], event["max_reviews"]), (before["reviews_done"], 2))
        after = h.state(delivery)
        for key in ("trees", "findings", "producer_steps"):
            self.assertEqual(after[key], before[key])
        self.assertEqual(after["workers"]["producer"]["sessions"], before["workers"]["producer"]["sessions"])
        self.assertEqual(after["settings"]["timeout_minutes"], 30)
        self.assertEqual(after["settings"]["max_diff_kb"], 400)
        self.assertEqual(after["workers"]["producer"]["fresh_reason"], "reviewed-replan")
        h.run("close", "--run", plan)
        h.next(delivery)
        self.assertIsNone(h.calls("producer")[-1]["session_id"])
        self.assertIn("Execute S1 only", h.calls("producer")[-1]["prompt"])

    def test_replan_cannot_bypass_readonly_or_schema_guards(self):
        for error in ("Reviewer changed files", "Producer result does not match schema"):
            with self.subTest(error=error):
                h = Harness(self, {})
                delivery = h.run("start", "--stage", "feature-delivery", "--artifact", "docs/plan.md",
                                 "--first", "review", "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high")["run_id"]
                state = h.state(delivery)
                state.update(phase="failed", error={"message": error, "execution": False})
                (h.repo / ".cross-agent/runs" / delivery / "state.json").write_text(json.dumps(state))
                h.run("park", "--run", delivery, "--reason", "Replan requested.")
                self.assertIn("cannot bypass", h.run("resume-delivery", "--run", delivery, "--plan-run", "unused",
                              "--request", "Continue.", expect=2)["error"])

    def test_diff_capacity_replan_preserves_budget_and_rejects_other_owner(self):
        h = Harness(self, {"producer": [produce(write={"result.txt": "x" * 2500})], "reviewer": [review()]}, max_diff_kb=1)
        delivery = h.run("start", "--stage", "feature-delivery", "--artifact", "docs/plan.md", "--first", "produce",
                         "--request", "Deliver.", "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high")["run_id"]
        h.next(delivery)
        self.assertIn("exceed max_diff_kb", h.next(delivery)["error"]["message"])
        h.run("park", "--run", delivery, "--reason", "Replan requested.")
        plan = h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", "review",
                     "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high")["run_id"]
        h.next(plan)
        self.assertIn("must explicitly increase", h.run("resume-delivery", "--run", delivery, "--plan-run", plan,
                       "--request", "Continue segmented plan.", "--max-diff-kb", "1", expect=2)["error"])
        event = h.run("resume-delivery", "--run", delivery, "--plan-run", plan,
                      "--request", "Continue segmented plan.", "--max-diff-kb", "10")
        self.assertEqual((event["phase"], event["reviews_done"], event["max_reviews"]), ("produce", 0, 2))
        self.assertIn("already open", h.run(
            "start", "--stage", "general", "--artifact", "docs/plan.md", "--first", "review", "--request", "Other.",
            "--producer", "fake:test-model:high", "--reviewer", "fake:test-model:high", expect=2)["error"])

    def test_windows_state_replace_retries_are_bounded_and_atomic(self):
        h = Harness(self, {})
        run_id = h.start()["run_id"]
        state = h.state(run_id)
        state["request"] = "Updated request."
        locked = PermissionError("Windows denied replacement")
        locked.winerror = 5
        replace = store.os.replace
        attempts = 0
        def temporarily_locked(source, target):
            nonlocal attempts
            attempts += 1
            if attempts <= 2:
                raise locked
            replace(source, target)
        with patch.object(store.os, "replace", side_effect=temporarily_locked), patch.object(store.time, "sleep"):
            store.save(state)
        self.assertEqual(attempts, 3)
        self.assertEqual(h.state(run_id)["request"], "Updated request.")
        state["request"] = "Must not overwrite complete state."
        with patch.object(store.os, "replace", side_effect=locked) as mutation, patch.object(store.time, "sleep"):
            with self.assertRaises(PermissionError):
                store.save(state)
            self.assertEqual(mutation.call_count, 4)
        self.assertEqual(h.state(run_id)["request"], "Updated request.")

if __name__ == "__main__":
    unittest.main()
