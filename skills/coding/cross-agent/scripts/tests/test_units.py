"""Unit tests for role specs, stage Skill discovery, and schema validation."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crossagent import config, providers, schemas  # noqa: E402
from crossagent.errors import UsageError  # noqa: E402


class SpecTests(unittest.TestCase):
    def test_provider_only_keeps_the_provider_default_model(self):
        self.assertEqual(config.parse_spec("codex"), config.RoleSpec("codex"))
        self.assertEqual(config.parse_spec("claude:opus:high"), config.RoleSpec("claude", "opus", "high"))
        self.assertEqual(config.parse_spec("codex::low"), config.RoleSpec("codex", None, "low"))

    def test_unknown_provider_is_refused(self):
        with self.assertRaises(UsageError):
            config.parse_spec("gemini")


class DiscoveryTests(unittest.TestCase):
    def test_stage_skills_are_found_next_to_cross_agent(self):
        skill = config.find_stage_skill(copy.deepcopy(config.DEFAULTS), "feature-plan")
        self.assertEqual(skill.name, "SKILL.md")
        self.assertTrue(skill.parent.name.endswith("feature-plan"))
        self.assertIsNone(config.find_stage_skill(copy.deepcopy(config.DEFAULTS), "general"))


class CodexCommandTests(unittest.TestCase):
    def _command(self, role, session_id=None, model=None, effort=None):
        call = providers.Call(
            role=role, model=model, effort=effort, prompt="", schema={}, session_id=session_id, cwd=Path("."),
            read_dirs=[], write_dirs=[], allowed_commands=[], timeout=1, work_dir=Path("."),
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


class ClaudeCommandTests(unittest.TestCase):
    def test_windows_producer_allows_configured_commands_in_powershell(self):
        call = providers.Call(
            role="producer", model="opus", effort="high", prompt="", schema={}, session_id=None, cwd=Path("."),
            read_dirs=[], write_dirs=[], allowed_commands=["python -m unittest"], timeout=1, work_dir=Path("."),
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
