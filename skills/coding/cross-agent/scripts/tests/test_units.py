"""Unit tests for role specs, stage Skill discovery, and schema validation."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crossagent import config, schemas  # noqa: E402
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
