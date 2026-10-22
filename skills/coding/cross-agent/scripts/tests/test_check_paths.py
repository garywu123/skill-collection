"""Path-scoped delivery checks: a check with check_paths reruns only when its paths changed or it failed."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_cli import Harness, configuration_text, decision, finding, produce, review
from crossagent import config
from crossagent.errors import UsageError


def counting(counter: Path, exit_code: int = 0) -> str:
    return f'"{sys.executable}" -c "open(r\'{counter.as_posix()}\', \'a\').write(\'x\'); raise SystemExit({exit_code})"'


def configure(h: Harness, checks: list[str], paths: dict) -> None:
    text = configuration_text(projects={".": dict(allowed_commands=[], delivery_checks=checks, extra_dirs=[])})
    text += "check_paths = { " + ", ".join(f"{json.dumps(k)} = {json.dumps(v)}" for k, v in paths.items()) + " }\n"
    h.config.write_text(text, encoding="utf-8")


def runs(counter: Path) -> int:
    return len(counter.read_text(encoding="utf-8")) if counter.exists() else 0


def two_rounds(test, first: dict, second: dict) -> Harness:
    h = Harness(test, {"producer": [produce(write=first), produce(outcomes=[("R1-001", "fixed")], write=second)],
                       "reviewer": [review(findings=[finding()]), review(earlier=[("R1-001", "resolved")])]})
    return h


def drive(h: Harness) -> str:
    run_id = h.start("produce")["run_id"]
    h.next(run_id)
    h.next(run_id)
    h.decide(run_id, decision("R1-001", "accepted"))
    h.next(run_id)
    h.next(run_id)
    return run_id


class CheckPathsTests(unittest.TestCase):
    def test_scoped_check_skips_unmatched_round_and_runs_on_match(self):
        h = two_rounds(self, {"docs/plan.md": "v1\n"}, {"src/a.py": "x = 1\n"})
        scoped, full = h.dir / "scoped.txt", h.dir / "full.txt"
        configure(h, [counting(scoped), counting(full)], {counting(scoped): ["src/*"]})
        run_id = drive(h)
        self.assertEqual((runs(scoped), runs(full)), (1, 2))
        first_review = h.calls("reviewer")[0]["prompt"]
        self.assertIn("Skipped: no changed path matches its check_paths.", first_review)
        self.assertEqual(h.state(run_id)["final_status"], "independently-passed")

    def test_failed_scoped_check_reruns_without_a_matching_change(self):
        h = two_rounds(self, {"src/a.py": "x = 1\n"}, {"docs/plan.md": "v2\n"})
        failing = h.dir / "failing.txt"
        configure(h, [counting(failing, 1)], {counting(failing, 1): ["src/*"]})
        run_id = drive(h)
        self.assertEqual(runs(failing), 2)
        self.assertEqual(h.state(run_id)["final_status"], "needs-user-decision")

    def test_note_reaches_only_the_next_producer_call(self):
        h = two_rounds(self, {"docs/plan.md": "v1\n"}, {"docs/plan.md": "v2\n"})
        run_id = h.start("produce")["run_id"]
        h.run("note", "--run", run_id, "--text", "Orchestrator ran the focused tests: 12/12 passed.")
        h.next(run_id)
        h.run("note", "--run", run_id, "--text", "Too late.", expect=2)
        h.next(run_id)
        h.decide(run_id, decision("R1-001", "accepted"))
        h.next(run_id)
        prompts = [call["prompt"] for call in h.calls("producer")]
        self.assertIn("Orchestrator ran the focused tests: 12/12 passed.", prompts[0])
        self.assertNotIn("Orchestrator note (evidence", prompts[1])

    def test_check_paths_must_name_configured_checks_with_globs(self):
        base = configuration_text(projects={".": dict(allowed_commands=[], delivery_checks=["dotnet test"], extra_dirs=[])})
        parsed = config._parse_config(base + 'check_paths = { "dotnet test" = ["src/*"] }\n', Path("c.toml"))
        self.assertEqual(config.project_settings(parsed, Path("."))["check_paths"], {"dotnet test": ["src/*"]})
        for bad in ('{ "npm test" = ["src/*"] }', '{ "dotnet test" = [] }', '{ "dotnet test" = "src/*" }'):
            with self.subTest(bad=bad), self.assertRaises(UsageError):
                config._parse_config(base + f"check_paths = {bad}\n", Path("c.toml"))


if __name__ == "__main__":
    unittest.main()
