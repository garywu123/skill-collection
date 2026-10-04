"""Stage role selection, pre-launch validation, saved roles, and configured stage Skills."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_cli import Harness, configuration_text, decision, finding, produce, review


def stages_text(stages: dict) -> str:
    return "".join(f"\n[stages.{json.dumps(stage)}]\n" + "".join(
        f"{key} = {json.dumps(value)}\n" for key, value in values.items()) for stage, values in stages.items())


class StageRoleTests(unittest.TestCase):
    def configure(self, h: Harness, stages: dict, **config) -> None:
        config.setdefault("producer", "fake:default-model:low")
        config.setdefault("reviewer", "fake:default-model:low")
        h.config.write_text(configuration_text(**config) + stages_text(stages), encoding="utf-8")

    def general(self, h: Harness, *extra, first="produce", expect=0) -> dict:
        return h.run("start", "--stage", "general", "--artifact", "docs/plan.md", "--first", first,
                     "--request", "Keep the plan correct.", *extra, expect=expect)

    def test_override_then_stage_role_then_default_reach_the_adapter(self):
        h = Harness(self, {"producer": [produce(), produce()], "reviewer": [review(), review()]})
        self.configure(h, {"general": {"producer": "fake:stage-model:high"}})
        status = h.run("status")
        self.assertEqual(status["effective_roles"]["general"]["producer"],
                         {"provider": "fake", "model": "stage-model", "effort": "high", "source": "stage"})
        self.assertEqual(status["effective_roles"]["feature-plan"]["producer"]["source"], "default")
        first = self.general(h)
        self.assertEqual(first["role_sources"], {"producer": "stage", "reviewer": "default"})
        h.next(first["run_id"])
        h.next(first["run_id"])
        h.run("close", "--run", first["run_id"])
        second = self.general(h, "--producer", "fake:override-model:max")
        self.assertEqual(second["role_sources"], {"producer": "override", "reviewer": "default"})
        h.next(second["run_id"])
        h.next(second["run_id"])
        received = [(call["model"], call["effort"]) for call in h.calls("producer")]
        self.assertEqual(received, [("stage-model", "high"), ("override-model", "max")])
        self.assertEqual([(call["model"], call["effort"]) for call in h.calls("reviewer")],
                         [("default-model", "low")] * 2)

    def test_real_adapter_commands_receive_the_effective_stage_spec(self):
        selected = str(Path(sys.executable).resolve())
        h = Harness(self, {})
        self.configure(h, {"feature-plan": {"producer": "claude:stage-claude:high",
                                            "reviewer": "codex:stage-codex:xhigh"}},
                       producer="codex:default-codex:low", reviewer="claude:default-claude:low",
                       cli={"claude": selected, "codex": selected})
        def preview(first, *extra):
            return h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", first,
                         "--request", "Preview.", "--dry-run", *extra)
        producer = preview("produce")["command"]
        self.assertEqual(producer[0], selected)
        self.assertEqual(producer[producer.index("--model") + 1], "stage-claude")
        self.assertEqual(producer[producer.index("--effort") + 1], "high")
        reviewer = preview("review")["command"]
        self.assertEqual(reviewer[reviewer.index("-m") + 1], "stage-codex")
        self.assertIn('model_reasoning_effort="xhigh"', reviewer)
        overridden = preview("produce", "--producer", "codex:override-codex:medium")
        self.assertEqual(overridden["role_sources"]["producer"], "override")
        self.assertEqual(overridden["command"][overridden["command"].index("-m") + 1], "override-codex")
        general = h.run("start", "--stage", "general", "--artifact", "docs/plan.md", "--first", "produce",
                        "--request", "Preview.", "--dry-run")["command"]
        self.assertEqual(general[general.index("-m") + 1], "default-codex")
        self.assertFalse((h.repo / ".cross-agent" / "runs").exists())

    def test_invalid_or_unsupported_selection_stops_before_any_worker(self):
        h = Harness(self, {"producer": [produce()], "reviewer": [review()]})
        missing = str(h.dir / "missing.exe")
        cases = [
            ({"general": {"producer": "codex"}}, {}, "[stages.general] producer"),
            ({"general": {"reviewer": "codex::high"}}, {}, "all three are required"),
            ({"general": {"producer": "unknown:model:high"}}, {}, "Unknown provider"),
            ({"general": {"producer": "codex:model:high"}}, {}, "Missing required [cli] codex"),
            ({"general": {"producer": 3}}, {}, "must be a nonempty string"),
            ({"general": {"tester": "fake:model:high"}}, {}, "with only skill, producer, reviewer"),
            ({"delivery": {"producer": "fake:model:high"}}, {}, "[stages.delivery]"),
            ({"general": {"skill": ""}}, {}, "must be a nonempty string"),
            ({"general": {"skill": str(h.dir / "missing" / "SKILL.md")}}, {}, "does not exist"),
            ({"general": {"producer": "codex:model:high"}}, {"cli": {"codex": missing}}, "Configured codex CLI"),
        ]
        for stages, config, message in cases:
            with self.subTest(stages=stages, config=config):
                self.configure(h, stages, **config)
                self.assertIn(message, self.general(h, expect=2)["error"])
        self.configure(h, {})
        self.assertIn("all three are required", self.general(h, "--producer", "codex", expect=2)["error"])
        self.assertEqual(h.calls("producer") + h.calls("reviewer"), [])
        self.assertFalse((h.repo / ".cross-agent" / "runs").exists())

    def test_legacy_complete_config_without_stage_roles_uses_defaults(self):
        h = Harness(self, {"producer": [produce()], "reviewer": [review()]})
        self.configure(h, {})
        status = h.run("status")
        self.assertEqual(status["stages"], {})
        self.assertTrue(all(role["source"] == "default" for roles in status["effective_roles"].values()
                            for role in roles.values()))
        event = self.general(h)
        self.assertEqual(event["role_sources"], {"producer": "default", "reviewer": "default"})
        self.assertIsNone(h.state(event["run_id"])["skill"])
        h.next(event["run_id"])
        self.assertIn("No lifecycle Skill applies", h.calls("producer")[0]["prompt"])
        self.assertNotIn("Stage Skill supplied by CLI", h.calls("producer")[0]["prompt"])

    def test_saved_roles_and_budgets_survive_config_edits_and_old_state(self):
        h = Harness(self, {"producer": [produce(), produce(outcomes=[("R1-001", "fixed")])],
                           "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])]})
        self.configure(h, {"general": {"producer": "fake:stage-a:high", "reviewer": "fake:stage-r:high"}})
        run_id = self.general(h)["run_id"]
        h.next(run_id)
        self.configure(h, {"general": {"producer": "fake:stage-b:low", "reviewer": "fake:stage-s:low"}},
                       producer="fake:other:low", reviewer="fake:other:low", max_reviews=1)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        # A run saved before stage roles has no role_sources; its saved roles remain authoritative.
        path = h.repo / ".cross-agent" / "runs" / run_id / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        del state["role_sources"]
        path.write_text(json.dumps(state), encoding="utf-8")
        status = h.run("status", "--run", run_id)
        self.assertIsNone(status["role_sources"])
        self.assertEqual(status["max_reviews"], 2)
        h.next(run_id)
        final = h.next(run_id)
        self.assertEqual(final["final_status"], "independently-passed")
        self.assertEqual(final["reviews_done"], 2)
        self.assertEqual([call["model"] for call in h.calls("producer")], ["stage-a"] * 2)
        self.assertEqual([call["model"] for call in h.calls("reviewer")], ["stage-r"] * 2)

    def test_configured_general_skill_is_injected_and_saved_with_the_run(self):
        h = Harness(self, {"producer": [produce()], "reviewer": [review()]})
        skill = h.dir / "skills" / "architecture-design" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: architecture-design\n---\n\n# Architecture\n\nMARKER-B2-SKILL\n", encoding="utf-8")
        plan_skill = h.dir / "skills" / "plan" / "SKILL.md"
        plan_skill.parent.mkdir(parents=True)
        plan_skill.write_text("# Plan Skill\n", encoding="utf-8")
        self.configure(h, {"general": {"skill": str(skill), "producer": "fake:stage-model:high"},
                           "feature-plan": {"skill": str(plan_skill), "reviewer": "fake:plan-review:high"}})
        preview = h.run("start", "--stage", "feature-plan", "--artifact", "docs/plan.md", "--first", "review",
                        "--dry-run")
        self.assertEqual(preview["skill"], str(plan_skill.resolve()))
        self.assertEqual(preview["role_sources"], {"producer": "default", "reviewer": "stage"})
        run_id = self.general(h)["run_id"]
        self.assertEqual(h.state(run_id)["skill"], str(skill.resolve()))
        self.configure(h, {})
        h.next(run_id)
        h.next(run_id)
        digest = hashlib.sha256(skill.read_bytes()).hexdigest()
        self.assertEqual(h.state(run_id)["workers"]["producer"]["loaded_skill"]["sha256"], digest)
        producer, reviewer = h.calls("producer")[0]["prompt"], h.calls("reviewer")[0]["prompt"]
        self.assertIn("Execute this stage within the request.", producer)
        self.assertIn("Review criteria only", reviewer)
        for prompt in (producer, reviewer):
            self.assertIn("MARKER-B2-SKILL", prompt)
            self.assertNotIn("No lifecycle Skill applies", prompt)


if __name__ == "__main__":
    unittest.main()
