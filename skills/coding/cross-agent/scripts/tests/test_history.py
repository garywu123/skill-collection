"""Retained CSV history, call boundaries, and provider token accounting."""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_cli import Harness, decision, finding, produce, review
from crossagent import engine, history, providers
from crossagent.errors import UsageError
from crossagent.progress import Observer, codex_usage


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def call(root=Path("."), session_id=None, baseline=None):
    return providers.Call("producer", None, None, "", {}, session_id, root, [], [], [], 5, root,
                          token_baseline=baseline)


class HistoryTests(unittest.TestCase):
    def test_checkpoint_revision_and_closed_runs_export_one_row_per_call(self):
        item = 'F08 中文, "inventory"'
        usage = {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120,
                 "usage_source": "fake", "usage_scope": "parent-call", "usage_status": "reported"}
        h = Harness(self, {"producer": [produce(status="checkpoint", telemetry={"token_usage": usage}),
                                        produce(), produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")]), review()]})
        run_id = h.start("produce", "--item", item)["run_id"]
        for _ in range(3):
            h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        h.next(run_id)
        closed = h.run("close", "--run", run_id)
        self.assertFalse((h.repo / ".cross-agent/runs" / run_id).exists())
        rows = read_csv(closed["history_file"])
        self.assertEqual([row["round"] for row in rows], ["P0", "P0", "R1", "P1", "R2"])
        self.assertEqual([row["call_status"] for row in rows],
                         ["checkpoint", "done", "review-returned", "done", "review-returned"])
        self.assertEqual(rows[0]["generation"], "1")
        self.assertEqual(rows[1]["generation"], "2")
        self.assertEqual(rows[1]["session_id"], rows[3]["session_id"])
        self.assertEqual(rows[0]["total_tokens"], "120")
        self.assertEqual(rows[1]["total_tokens"], "")
        self.assertTrue(all(row["item"] == item and row["run_status"] == "independently-passed" for row in rows))
        self.assertTrue(all(row["started_at_utc"].endswith("+00:00") and row["ended_at_utc"] and
                            float(row["elapsed_seconds"]) >= 0 for row in rows))
        second = h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", "review",
                       "--item", item, "--producer", "fake", "--reviewer", "fake:configured-model:high")["run_id"]
        self.assertNotEqual(second, run_id)
        h.next(second)
        h.run("close", "--run", second)
        exported = h.run("history")
        self.assertEqual((exported["calls"], exported["runs"], exported["unknown_usage_calls"]), (6, 2, 5))
        exported_rows = read_csv(exported["history_file"])
        self.assertEqual(exported_rows[:5], rows)
        self.assertEqual((exported_rows[-1]["item"], exported_rows[-1]["stage"],
                          exported_rows[-1]["configured_model"], exported_rows[-1]["configured_effort"],
                          exported_rows[-1]["observed_model"]), (item, "feature-plan", "configured-model", "high", ""))
        self.assertEqual(h.run("history"), exported)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=h.repo, capture_output=True, text=True, check=True)
        self.assertNotIn(".cross-agent", status.stdout)

    def test_automatic_retry_records_failure_without_reusing_its_tokens(self):
        h = Harness(self, {"producer": [{"fail": "timed out after 1800 s", "telemetry": {
            "token_usage": {"input_tokens": 40, "usage_status": "partial"}}}, produce()]})
        run_id = h.start("produce")["run_id"]
        event = h.next(run_id)
        rows = read_csv(event["history_file"])
        self.assertEqual([row["call_status"] for row in rows], ["execution-failed", "done"])
        self.assertEqual([row["usage_status"] for row in rows], ["partial", "unknown"])
        self.assertEqual(rows[0]["session_id"], rows[1]["session_id"])
        self.assertEqual(rows[1]["input_tokens"], "")
        self.assertEqual(rows[0]["item"], "docs/plan.md")

    def test_schema_failure_and_abandon_are_retained(self):
        h = Harness(self, {"producer": [{"output": {"status": "done"}}]})
        run_id = h.start("produce")["run_id"]
        event = h.next(run_id)
        rows = read_csv(event["history_file"])
        self.assertEqual((rows[0]["call_status"], rows[0]["run_status"]), ("invalid-output", "failed"))
        h.run("close", "--run", run_id, "--abandon")
        self.assertEqual(read_csv(event["history_file"])[0]["run_status"], "failed")
        self.assertEqual(h.run("history")["calls"], 1)

    def test_legacy_run_and_dry_run_do_not_invent_old_records(self):
        h = Harness(self, {"reviewer": [review()]})
        h.start("produce", "--dry-run", "--item", "preview")
        self.assertFalse((h.repo / ".cross-agent/history").exists())
        run_id = h.start()["run_id"]
        state = h.state(run_id)
        state.pop("item")
        (h.repo / ".cross-agent/runs" / run_id / "state.json").write_text(json.dumps(state), encoding="utf-8")
        event = h.next(run_id)
        row = read_csv(event["history_file"])[0]
        self.assertEqual((row["call"], row["item"]), ("1", "docs/plan.md"))

    def test_running_row_and_locked_file_keep_previous_complete_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = {"project_root": str(root), "run_id": "test-run", "phase": "produce", "worker_calls": [
                {"run_id": "test-run", "item": "=1+1", "call": 1, "started_at_utc": "2026-10-02T00:00:00+00:00",
                 "call_status": "running", "usage_status": "unknown"}]}
            history.save(state)
            path = history.run_file(root, "test-run")
            before = path.read_bytes()
            row = read_csv(path)[0]
            self.assertEqual((row["item"], row["ended_at_utc"], row["total_tokens"]), ("'=1+1", "", ""))
            with patch.object(history.os, "replace", side_effect=PermissionError("Excel lock")):
                with self.assertRaisesRegex(Exception, "Cannot write history CSV"):
                    history.save(state)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(len(list(path.parent.iterdir())), 1)
            self.assertEqual(history.export(root)["calls"], 1)

    def test_csv_failure_after_worker_completion_stops_repeat_execution_and_can_reexport(self):
        h = Harness(self, {"producer": [produce()]})
        run_id = h.start("produce")["run_id"]
        write = history._write
        def locked_at_finish(path, rows):
            if rows[-1]["call_status"] != "running":
                raise UsageError("Cannot write history CSV: Excel lock")
            write(path, rows)
        with patch.dict(providers.os.environ, h.env), patch.object(history, "_write", side_effect=locked_at_finish):
            with self.assertRaises(UsageError):
                engine.next_step(h.repo, run_id)
        self.assertEqual(h.state(run_id)["phase"], "failed")
        self.assertEqual(h.next(run_id)["phase"], "failed")
        self.assertEqual(len(h.calls("producer")), 1)
        exported = h.run("history")
        self.assertEqual(read_csv(exported["history_file"])[0]["call_status"], "done")


class TokenAccountingTests(unittest.TestCase):
    def test_codex_resumed_session_totals_become_call_delta(self):
        baseline = {"input_tokens": 1000, "cached_input_tokens": 800, "output_tokens": 100,
                    "reasoning_output_tokens": 20}
        worker = call(session_id="saved-session", baseline=baseline)
        observer = Observer(worker)
        observer.observe({"type": "turn.completed", "usage": {
            "input_tokens": 1300, "cached_input_tokens": 1000, "output_tokens": 150,
            "reasoning_output_tokens": 30}})
        usage = worker.telemetry["token_usage"]
        self.assertEqual((usage["input_tokens"], usage["cached_input_tokens"], usage["output_tokens"],
                          usage["reasoning_output_tokens"], usage["total_tokens"]), (300, 200, 50, 10, 350))
        self.assertEqual(usage["usage_scope"], "parent-call")
        self.assertEqual(worker.telemetry["session_token_usage"]["input_tokens"], 1300)

    def test_codex_unknown_or_reset_baseline_never_becomes_false_zero(self):
        for baseline in (None, {"input_tokens": 1000, "output_tokens": 100}):
            worker = call(session_id="saved-session", baseline=baseline)
            codex_usage(worker, {"input_tokens": 300, "output_tokens": 50}, "test", "reported")
            self.assertIsNone(worker.telemetry["token_usage"]["total_tokens"])
            self.assertEqual(worker.telemetry["token_usage"]["usage_status"], "unknown")
        worker = call()
        codex_usage(worker, {"input_tokens": 0, "output_tokens": 0}, "test", "reported")
        self.assertEqual(worker.telemetry["token_usage"]["total_tokens"], 0)

    def test_claude_deduplicates_partial_inputs_and_uses_final_output(self):
        worker = call(session_id="saved-session")
        observer = Observer(worker)
        event = {"type": "assistant", "message": {"id": "msg1", "usage": {
            "input_tokens": 10, "cache_read_input_tokens": 80, "cache_creation_input_tokens": 5,
            "output_tokens": 1}, "content": []}}
        observer.observe(event)
        observer.observe(event)
        observer.observe({**event, "parent_tool_use_id": "child"})
        usage = worker.telemetry["token_usage"]
        self.assertEqual(usage["input_tokens"], 95)
        self.assertIsNone(usage["output_tokens"])
        self.assertEqual(usage["usage_status"], "partial")
        observer.observe({"type": "result", "usage": {"input_tokens": 30, "cache_read_input_tokens": 100,
                         "cache_creation_input_tokens": 10, "output_tokens": 20}, "modelUsage": {
                         "model": {"inputTokens": 99999}}})
        usage = worker.telemetry["token_usage"]
        self.assertEqual((usage["input_tokens"], usage["total_tokens"]), (140, 160))
        self.assertEqual(usage["usage_status"], "reported")
        observer.observe({"type": "result", "subtype": "error_during_execution", "is_error": True,
                          "usage": {"input_tokens": 0, "output_tokens": 0}})
        self.assertEqual(worker.telemetry["token_usage"]["total_tokens"], 160)

    def test_codex_provider_uses_saved_baseline_when_rollout_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = call(root, "saved-session", {"input_tokens": 500, "output_tokens": 50})
            def run(command, call):
                (root / "producer.last-message.json").write_text('{"status":"done"}', encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, json.dumps({"type": "turn.completed", "usage": {
                    "input_tokens": 900, "output_tokens": 90}}), "")
            with patch.object(providers, "_run", side_effect=run), patch.object(
                providers, "_codex_token_totals", return_value=None), patch.object(
                providers, "_codex_context_tokens", return_value=None):
                self.assertIsNone(providers.Codex().run(worker).error)
            self.assertEqual(worker.telemetry["token_usage"]["total_tokens"], 440)


if __name__ == "__main__":
    unittest.main()
