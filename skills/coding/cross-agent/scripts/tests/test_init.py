"""Initialization creates configuration only and preserves existing user settings."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "cross_agent.py"


class InitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cross-agent-init-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        self.config = self.directory / "settings" / "config.toml"
        self.input = self.directory / "input.json"
        self.proposal = {
            "allowed_commands": ["python -m unittest"],
            "delivery_checks": ['python -c "open(\'check-ran\', \'w\').close()"'],
            "extra_dirs": [],
        }
        self.input.write_text(json.dumps(self.proposal), encoding="utf-8")
        self.env = {**os.environ, "CROSS_AGENT_CONFIG": str(self.config)}

    def run_cli(self, *args, expect=0, cwd=None):
        result = subprocess.run(
            [sys.executable, str(CLI), *args], cwd=cwd or self.root,
            env=self.env, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def initialize(self, expect=0):
        return self.run_cli("init", "--input", str(self.input), expect=expect)

    def test_create_and_status_without_workers_checks_or_run_state(self):
        result = self.initialize()
        self.assertEqual(result["action"], "created")
        self.assertEqual(result["project"], self.proposal)
        self.assertEqual(result["proposed_differences"], {})
        self.assertFalse(result["workers_started"])
        self.assertFalse(result["checks_executed"])
        self.assertFalse((self.root / "check-ran").exists())
        self.assertFalse((self.root / ".cross-agent").exists())
        status = self.run_cli("status")
        self.assertTrue(status["project_configured"])
        self.assertEqual(status["project"], self.proposal)
        self.assertEqual(status["open_runs"], [])

    def test_append_preserves_bom_comments_defaults_other_projects_and_repeat(self):
        self.config.parent.mkdir()
        original = b'\xef\xbb\xbf# Keep this comment\r\nmax_reviews = 7\r\n[defaults]\r\nproducer = "codex"\r\n[projects."other-project"]\r\nallowed_commands = ["original"]'
        self.config.write_bytes(original)
        result = self.initialize()
        self.assertEqual(result["action"], "project-added")
        self.assertEqual(result["settings"]["max_reviews"], 7)
        self.assertEqual(result["defaults"]["producer"], "codex")
        updated = self.config.read_bytes()
        self.assertTrue(updated.startswith(original))
        parsed = tomllib.loads(updated.decode("utf-8-sig"))
        self.assertEqual(parsed["projects"]["other-project"]["allowed_commands"], ["original"])
        self.proposal["delivery_checks"] = ["a different test"]
        self.input.write_text(json.dumps(self.proposal), encoding="utf-8")
        repeated = self.initialize()
        self.assertEqual(repeated["action"], "unchanged")
        self.assertEqual(repeated["proposed_differences"], {"delivery_checks": ["a different test"]})
        self.assertEqual(self.config.read_bytes(), updated)

    def test_existing_project_path_alias_is_preserved(self):
        self.config.parent.mkdir()
        alias = self.root.as_posix() + "/../project"
        original = f'[projects.{json.dumps(alias)}]\ndelivery_checks = ["existing test"]\n'
        self.config.write_text(original, encoding="utf-8")
        result = self.initialize()
        self.assertEqual(result["action"], "unchanged")
        self.assertEqual(result["project"]["delivery_checks"], ["existing test"])
        self.assertEqual(self.config.read_text(encoding="utf-8"), original)

    def test_empty_input_reports_checks_unconfigured(self):
        self.input.write_text("{}", encoding="utf-8")
        result = self.initialize()
        self.assertFalse(result["checks_configured"])
        self.assertEqual(result["project"], dict.fromkeys(self.proposal, []))

    def test_invalid_input_and_config_never_change_files(self):
        for value in ([], {"unknown": []}, {"delivery_checks": "not a list"}):
            with self.subTest(value=value):
                self.input.write_text(json.dumps(value), encoding="utf-8")
                self.assertIn("error", self.initialize(expect=2))
                self.assertFalse(self.config.exists())
        self.input.write_text("{", encoding="utf-8")
        self.initialize(expect=2)
        self.assertFalse(self.config.exists())
        self.input.write_text("{}", encoding="utf-8")
        self.config.parent.mkdir()
        for original in (b"not = [valid", b"unknown = true\n", b"\xff"):
            self.config.write_bytes(original)
            self.assertIn("error", self.initialize(expect=2))
            self.assertEqual(self.config.read_bytes(), original)

    def test_non_git_project_is_reported_without_initializing_git(self):
        outside = self.directory / "outside"
        outside.mkdir()
        result = self.run_cli("init", "--input", str(self.input), expect=2, cwd=outside)
        self.assertIn("Git work tree", result["error"])
        self.assertFalse((outside / ".git").exists())
        self.assertFalse(self.config.exists())


if __name__ == "__main__":
    unittest.main()
