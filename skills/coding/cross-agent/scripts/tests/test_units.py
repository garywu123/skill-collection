"""Unit tests for role specs, stage Skill discovery, and schema validation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crossagent import config, providers, schemas  # noqa: E402
from crossagent.errors import UsageError  # noqa: E402


class SpecTests(unittest.TestCase):
    def test_explicit_roles_and_missing_fields(self):
        self.assertEqual(config.parse_spec("claude:opus:high"), config.RoleSpec("claude", "opus", "high"))
        self.assertEqual(config.parse_spec("codex:gpt-6.1-sol:xhigh"), config.RoleSpec("codex", "gpt-6.1-sol", "xhigh"))
        for value in ("codex", "codex::low", "claude:opus", "claude:opus:", "claude: :high"):
            with self.subTest(value=value), self.assertRaises(UsageError):
                config.parse_spec(value)

    def test_unknown_provider_is_refused(self):
        with self.assertRaises(UsageError):
            config.parse_spec("gemini:model:high")


class DiscoveryTests(unittest.TestCase):
    def test_stage_skills_are_found_next_to_cross_agent(self):
        skill = config.find_stage_skill({"stages": {}}, "feature-plan")
        self.assertEqual(skill.name, "SKILL.md")
        self.assertTrue(skill.parent.name.endswith("feature-plan"))
        self.assertIsNone(config.find_stage_skill({"stages": {}}, "general"))


class CodexCommandTests(unittest.TestCase):
    def _command(self, role, session_id=None, model="requested-model", effort="high"):
        call = providers.Call(
            role=role, model=model, effort=effort, prompt="", schema={}, session_id=session_id, cwd=Path("."),
            read_dirs=[], write_dirs=[], allowed_commands=[], timeout=1, work_dir=Path("."), executable=sys.executable,
        )
        return providers.Codex().command(call, Path("schema.json"), Path("last.json"))

    def test_model_and_effort_reach_codex_on_start_and_resume(self):
        for session_id in (None, "saved-session"):
            command = self._command("producer", session_id, model="requested-model", effort="high")
            self.assertEqual(command[command.index("-m") + 1], "requested-model")
            self.assertIn('model_reasoning_effort="high"', command)

    def test_workers_never_escalate_and_keep_their_sandbox_on_resume(self):
        for role, mode in (("reviewer", "read-only"), ("producer", "workspace-write")):
            for session_id in (None, "01a0dd98-2c86-75c1-b758-38c7fbcf9afd"):
                command = self._command(role, session_id)
                self.assertIn('approval_policy="never"', command)
                self.assertIn(f'sandbox_mode="{mode}"', command)
                self.assertEqual("multi_agent" in command, role == "reviewer")


class CodexResultTests(unittest.TestCase):
    def test_recovered_errors_require_success_and_do_not_hide_terminal_failures(self):
        data = {"findings": [], "earlier_results": [], "notes": []}
        recovered = {"type": "error", "message": "Reconnecting... 3/5 (request timed out)"}
        completed = {"type": "turn.completed", "usage": {}}
        failed = {"type": "turn.failed", "error": {"message": "terminal failure"}}
        cases = [
            ("success", [completed], 0, json.dumps(data), None),
            ("recovered", [recovered, completed], 0, json.dumps(data), None),
            ("multiple retries", [recovered, recovered, completed], 0, json.dumps(data), None),
            ("unrecovered", [recovered], 0, json.dumps(data), "request timed out"),
            ("terminal", [failed], 0, json.dumps(data), "terminal failure"),
            ("terminal then completed", [failed, completed], 0, json.dumps(data), "terminal failure"),
            ("error after completed", [completed, recovered], 0, json.dumps(data), "request timed out"),
            ("nonzero exit", [recovered, completed], 1, json.dumps(data), "exited with code 1"),
            ("invalid output", [recovered, completed], 0, "incomplete JSON", "no structured output"),
            ("missing output", [recovered, completed], 0, None, "no structured output"),
        ]
        for name, events, returncode, output, error in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                call = providers.Call(
                    role="reviewer", model="requested-model", effort="high", prompt="", schema=schemas.REVIEW,
                    session_id=None, cwd=root, read_dirs=[], write_dirs=[],
                    allowed_commands=[], timeout=1, work_dir=root, executable=sys.executable,
                )

                def fake_run(command, call):
                    if output is not None:
                        (root / "reviewer.last-message.json").write_text(output, encoding="utf-8")
                    return subprocess.CompletedProcess(
                        command, returncode, "\n".join(json.dumps(event) for event in events), "",
                    )

                with patch.object(providers, "_run", side_effect=fake_run), patch.object(
                    providers, "_codex_context_tokens", return_value=None,
                ):
                    result = providers.Codex().run(call)
                if error is None:
                    self.assertIsNone(result.error)
                    self.assertEqual(result.data, data)
                    self.assertEqual(schemas.validate(result.data, call.schema), [])
                else:
                    self.assertIn(error, result.error or "")
                    self.assertIsNone(result.data)


class CliSelectionTests(unittest.TestCase):
    def test_missing_path_or_saved_role_never_falls_back_to_cli_defaults(self):
        for provider in ("claude", "codex"):
            for session_id in (None, "saved-session"):
                for model, effort, executable in ((None, "high", sys.executable),
                                                   ("test-model", None, sys.executable),
                                                   ("test-model", "high", None)):
                    with self.subTest(provider=provider, session_id=session_id, model=model, effort=effort, executable=executable):
                        call = providers.Call(role="reviewer", model=model, effort=effort, prompt="", schema={},
                            session_id=session_id, cwd=Path("."), read_dirs=[], write_dirs=[], allowed_commands=[],
                            timeout=1, work_dir=Path("."), executable=executable)
                        with patch.object(providers.shutil, "which", return_value=sys.executable) as discover:
                            with self.assertRaises(UsageError):
                                providers.preview_command(provider, call)
                            discover.assert_not_called()

    def test_configured_path_reaches_start_and_resume_for_both_providers(self):
        selected = str(Path(sys.executable).resolve())
        for provider in ("claude", "codex"):
            for session_id in (None, "saved-session"):
                with self.subTest(provider=provider, session_id=session_id):
                    call = providers.Call(
                        role="reviewer", model="requested-model", effort="high", prompt="", schema={},
                        session_id=session_id, cwd=Path("."), read_dirs=[], write_dirs=[],
                        allowed_commands=[], timeout=1, work_dir=Path("."), executable=selected,
                    )
                    with patch.object(providers.shutil, "which", return_value=selected) as discover:
                        providers.get(provider).check(selected)
                        command = providers.preview_command(provider, call)
                        self.assertEqual(command[0], selected)
                        discover.assert_called_with(selected)
                    with patch.object(providers.shutil, "which", return_value=None):
                        with self.assertRaises(UsageError):
                            providers.get(provider).check(selected)
                        with self.assertRaises(UsageError):
                            providers.preview_command(provider, call)


class ClaudeCommandTests(unittest.TestCase):
    def test_configured_effort_overrides_inherited_effort_environment(self):
        call = providers.Call(role="producer", model="claude-opus-5-5", effort="medium", prompt="", schema={},
            session_id=None, cwd=Path("."), read_dirs=[], write_dirs=[], allowed_commands=[], timeout=1,
            work_dir=Path("."), executable=sys.executable)
        final = json.dumps({"type": "result", "structured_output": {}, "is_error": False})
        with patch.dict(os.environ, {"CLAUDE_CODE_EFFORT_LEVEL": "max"}), patch.object(providers, "_run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, final, "")
            self.assertIsNone(providers.Claude().run(call).error)
            command, _, environment = run.call_args.args
            self.assertEqual(command[command.index("--effort") + 1], "medium")
            self.assertEqual(environment["CLAUDE_CODE_EFFORT_LEVEL"], "medium")

    def test_windows_producer_allows_configured_commands_in_powershell(self):
        call = providers.Call(
            role="producer", model="opus", effort="high", prompt="", schema={}, session_id=None, cwd=Path("."),
            read_dirs=[], write_dirs=[], allowed_commands=["python -m unittest"], timeout=1, work_dir=Path("."), executable=sys.executable,
        )
        command = providers.Claude().command(call, "00000000-0000-0000-0000-000000000000", True)
        self.assertEqual(command[command.index("--model") + 1], "opus")
        self.assertEqual(command[command.index("--effort") + 1], "high")
        allowed = command[command.index("--allowedTools") + 1]
        self.assertIn("Bash(python -m unittest:*)", allowed)
        if sys.platform == "win32":
            self.assertIn("PowerShell(python -m unittest:*)", allowed)


class SchemaTests(unittest.TestCase):
    def test_a_valid_producer_result_passes(self):
        data = {"status": "done", "summary": "", "questions": [], "blocker": None, "outcomes": []}
        self.assertEqual(schemas.validate(data, schemas.PRODUCER), [])

    def test_missing_extra_and_invalid_values_are_reported(self):
        data = {"status": "finished", "summary": "", "questions": [], "outcomes": [], "extra": 1}
        errors = schemas.validate(data, schemas.PRODUCER)
        self.assertTrue(any("missing 'blocker'" in error for error in errors))
        self.assertTrue(any("unexpected 'extra'" in error for error in errors))
        self.assertTrue(any("'finished' is not one of" in error for error in errors))

    def test_decision_priority_may_be_null(self):
        data = {"decisions": [{"finding_id": "R1-001", "disposition": "accepted", "rationale": None, "priority": None}]}
        self.assertEqual(schemas.validate(data, schemas.DECIDE), [])


if __name__ == "__main__":
    unittest.main()
