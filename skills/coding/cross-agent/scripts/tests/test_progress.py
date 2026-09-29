"""Check observable streaming behavior and telemetry privacy with real subprocesses."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crossagent import providers
from crossagent.progress import Observer


def call(root, progress=None, timeout=5):
    return providers.Call("producer", None, None, "", {}, None, root, [], [], [], timeout, root,
                          progress=progress)


class ProgressTests(unittest.TestCase):
    def test_progress_arrives_before_worker_exits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            events = []

            def receive(event):
                events.append(event)
                (root / "observed").touch()

            # This child only succeeds if the parent consumes its event while it is running.
            script = (
                "import json,time,pathlib; "
                "print(json.dumps({'type':'system','subtype':'init','model':'observed-model'}),flush=True); "
                "deadline=time.monotonic()+3\n"
                "while not pathlib.Path('observed').exists() and time.monotonic()<deadline: time.sleep(.02)\n"
                "raise SystemExit(0 if pathlib.Path('observed').exists() else 1)"
            )
            result = providers._run([sys.executable, "-c", script], call(root, receive))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(events[0]["telemetry"]["model"], "observed-model")

    def test_silent_worker_times_out(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(subprocess.TimeoutExpired):
                providers._run([sys.executable, "-c", "import time; time.sleep(10)"],
                               call(Path(directory), timeout=.2))

    def test_parent_context_and_private_text_are_not_mixed_with_children(self):
        events = []
        worker = call(Path("."), events.append)
        observer = Observer(worker)
        observer.observe({"type": "assistant", "message": {
            "model": "parent", "usage": {"input_tokens": 20, "cache_read_input_tokens": 80},
            "content": [{"type": "thinking", "thinking": "SECRET"},
                        {"type": "tool_use", "name": "Read", "input": {"file": "SECRET"}}]}})
        observer.observe({"type": "assistant", "parent_tool_use_id": "child", "message": {
            "model": "child-model", "usage": {"input_tokens": 9000}, "content": []}})
        self.assertEqual(worker.telemetry["context_tokens"], 100)
        self.assertEqual(worker.telemetry["model"], "parent")
        self.assertNotIn("SECRET", json.dumps(events))
        self.assertIsNone(worker.telemetry["subagents_active"])

    def test_subagent_request_is_not_an_observed_start_and_compaction_invalidates_usage(self):
        worker = call(Path("."))
        observer = Observer(worker)
        event = {"type": "assistant", "message": {"usage": {"input_tokens": 300}, "content": [
            {"type": "tool_use", "name": "Agent", "id": "a"}]}}
        observer.observe(event)
        observer.observe(event)
        self.assertEqual(worker.telemetry["subagents_requested"], 1)
        self.assertIsNone(worker.telemetry["subagents_started"])
        observer.observe({"type": "result", "subagent_stats": {"spawned": 0}})
        self.assertEqual(worker.telemetry["subagents_started"], 0)
        observer.observe({"type": "system", "subtype": "compact_boundary"})
        self.assertIsNone(worker.telemetry["context_tokens"])
        self.assertEqual(worker.telemetry["compactions"], 1)

    def test_codex_runtime_uses_latest_usage_not_total_spend(self):
        worker = call(Path("."))
        observer = Observer(worker)
        observer.observe({"type": "turn_context", "payload": {"model": "model", "effort": "high"}})
        observer.observe({"type": "event_msg", "payload": {"type": "token_count", "info": {
            "last_token_usage": {"input_tokens": 200}, "total_token_usage": {"input_tokens": 9000},
            "model_context_window": 1000}}})
        self.assertEqual(worker.telemetry["context_tokens"], 200)
        self.assertEqual(worker.telemetry["context_limit"], 1000)
        self.assertEqual(worker.telemetry["effort"], "high")

    def test_claude_subagent_starts_and_completions_update_live_counts(self):
        worker = call(Path("."))
        observer = Observer(worker)
        for task_id in ("a", "b", "b"):
            observer.observe({"type": "system", "subtype": "task_started",
                              "task_type": "local_agent", "task_id": task_id})
        self.assertEqual(worker.telemetry["subagents_started"], 2)
        self.assertEqual(worker.telemetry["subagents_active"], 2)
        observer.observe({"type": "system", "subtype": "task_notification", "task_id": "a"})
        self.assertEqual(worker.telemetry["subagents_started"], 2)
        self.assertEqual(worker.telemetry["subagents_active"], 1)


if __name__ == "__main__":
    unittest.main()
