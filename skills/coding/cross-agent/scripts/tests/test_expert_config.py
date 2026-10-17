"""Explicit expert routing preserves stage/default compatibility and fails closed."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crossagent import config
from crossagent.errors import UsageError
from test_cli import configuration_text


def tables(name, settings):
    return "".join(f"\n[{name}.{json.dumps(key)}]\n" + "".join(
        f"{field} = {json.dumps(value)}\n" for field, value in values.items())
        for key, values in settings.items())


class ExpertConfigTests(unittest.TestCase):
    def parse(self, experts=None, stages=None, **kwargs):
        text = configuration_text(**kwargs)
        if experts is not None:
            text += tables("experts", experts)
        if stages is not None:
            text += tables("stages", stages)
        return config._parse_config(text, Path("config.toml"))

    def test_each_role_resolves_override_expert_stage_default_independently(self):
        settings = self.parse(
            experts={"product-brief": {"producer": "fake:expert:high"}},
            stages={"general": {"producer": "fake:stage:low", "reviewer": "fake:stage-review:medium"}},
        )
        roles, sources = config.resolve_roles(settings, "general", expert="product-brief")
        self.assertEqual((roles["producer"].model, roles["reviewer"].model), ("expert", "stage-review"))
        self.assertEqual(sources, {"producer": "expert", "reviewer": "stage"})
        roles, sources = config.resolve_roles(settings, "general", {"producer": "fake:override:max"}, "product-brief")
        self.assertEqual(roles["producer"].model, "override")
        self.assertEqual(sources["producer"], "override")
        roles, sources = config.resolve_roles(settings, "feature-plan", expert="unknown-expert")
        self.assertEqual(sources, {"producer": "default", "reviewer": "default"})

    def test_existing_config_without_experts_keeps_stage_routing(self):
        settings = self.parse(stages={"feature-plan": {"producer": "fake:stage:high"}})
        self.assertEqual(settings["experts"], {})
        self.assertEqual(config.resolve_roles(settings, "feature-plan")[1],
                         {"producer": "stage", "reviewer": "default"})
        self.assertEqual(config.find_skill(settings, "feature-plan"), config.find_stage_skill(settings, "feature-plan"))
        self.assertIsNone(config.find_skill(settings, "general"))

    def test_invalid_expert_tables_specs_and_missing_cli_fail_on_config_load(self):
        cases = [
            ({"product-brief": {"producer": "codex"}}, "all three are required"),
            ({"product-brief": {"reviewer": "codex::high"}}, "all three are required"),
            ({"product-brief": {"producer": "unknown:model:high"}}, "Unknown provider"),
            ({"product-brief": {"producer": "codex:model:high"}}, "Missing required [cli] codex"),
            ({"product-brief": {"producer": 7}}, "nonempty string"),
            ({"product-brief": {"skill": " "}}, "nonempty string"),
            ({"product-brief": {"tester": "fake:model:high"}}, "with only skill, producer, reviewer"),
            ({"Product Brief": {}}, "kebab-case"),
            ({"../product-brief": {}}, "kebab-case"),
        ]
        for experts, message in cases:
            with self.subTest(experts=experts), self.assertRaisesRegex(UsageError, message.replace("[", r"\[").replace("]", r"\]")):
                self.parse(experts=experts)
        for suffix in ('\nexperts = []\n', '\n[experts]\nproduct-brief = "invalid"\n'):
            with self.subTest(suffix=suffix), self.assertRaises(UsageError):
                # Put top-level experts before any existing table.
                config._parse_config(suffix + configuration_text(), Path("config.toml"))

    def test_expert_tables_survive_initialization_serialization(self):
        settings = self.parse(experts={"product-brief": {"producer": "fake:expert:high", "skill": "product-brief"}})
        self.assertEqual(config._parse_config(config._render_config(settings), Path("roundtrip.toml")), settings)


class ExpertSkillDiscoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cross-agent-experts-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.patch = patch.object(config, "skills_root", return_value=self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.settings = {"stages": {}, "experts": {}}

    def skill(self, folder):
        path = self.root / folder / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Expert\n", encoding="utf-8")
        return path.resolve()

    def test_logical_names_find_deployed_and_ordinal_authoring_sources(self):
        brief = self.skill("10.product-brief")
        architecture = self.skill("architecture-design")
        self.assertEqual(config.find_skill(self.settings, "general", "product-brief"), brief)
        self.assertEqual(config.find_skill(self.settings, "general", "architecture-design"), architecture)
        self.assertEqual(config.expert_name(str(brief)), "product-brief")

    def test_explicit_path_wins_while_logical_name_uses_expert_path_override(self):
        brief = self.skill("10.product-brief")
        alternate = self.skill("custom-brief")
        self.settings["experts"] = {"product-brief": {"skill": str(alternate)}}
        self.assertEqual(config.find_skill(self.settings, "general", "product-brief"), alternate)
        self.assertEqual(config.find_skill(self.settings, "general", str(brief)), brief)
        parsed = ExpertConfigTests().parse(experts={"product-brief": {"producer": "fake:expert:high"}})
        self.assertEqual(config.resolve_roles(parsed, "general", expert=str(brief))[0]["producer"].model, "expert")

    def test_missing_and_ambiguous_sources_do_not_fall_back_to_stage(self):
        self.skill("30.feature-plan")
        self.settings["stages"] = {"general": {"skill": "feature-plan"}}
        for selector in ("product-brief", str(self.root / "missing" / "SKILL.md")):
            with self.subTest(selector=selector), self.assertRaises(UsageError):
                config.find_skill(self.settings, "general", selector)
        self.settings["experts"] = {"product-brief": {"skill": str(self.root / "missing" / "SKILL.md")}}
        with self.assertRaises(UsageError):
            config.find_skill(self.settings, "general", "product-brief")
        self.skill("product-brief")
        self.skill("10.product-brief")
        with self.assertRaisesRegex(UsageError, "Multiple Skills"):
            config.find_skill({"stages": {}}, "general", "product-brief")

    def test_only_numeric_ordinal_prefixes_match_and_source_must_be_skill_file(self):
        self.skill("unrelated.product-brief")
        with self.assertRaises(UsageError):
            config.find_skill(self.settings, "general", "product-brief")
        other = self.root / "README.md"
        other.write_text("Not a Skill", encoding="utf-8")
        for selector in (str(other), str(self.root)):
            with self.subTest(selector=selector), self.assertRaises(UsageError):
                config.find_skill(self.settings, "general", selector)
        for selector in ("", " "):
            with self.subTest(selector=selector), self.assertRaises(UsageError):
                config.find_skill(self.settings, "general", selector)


if __name__ == "__main__":
    unittest.main()
