"""Initialization creates configuration only and preserves existing user settings."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crossagent import config, engine, providers, versions  # noqa: E402
from test_cli import configuration_text  # noqa: E402

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
        self.cli_paths = dict.fromkeys(("codex", "claude"), str(Path(sys.executable).resolve()))
        self.input.write_text(json.dumps({**self.proposal, "cli": self.cli_paths}), encoding="utf-8")
        self.env = {**os.environ, "CROSS_AGENT_CONFIG": str(self.config)}

    def run_cli(self, *args, expect=0, cwd=None):
        result = subprocess.run(
            [sys.executable, str(CLI), *args], cwd=cwd or self.root,
            env=self.env, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def initialize(self, *args, expect=0):
        return self.run_cli("init", "--input", str(self.input), "--skip-version-check", *args, expect=expect)

    def test_local_config_roles_checkout_move_and_repo_isolation(self):
        self.env.pop("CROSS_AGENT_CONFIG")
        home = self.directory / "home"
        (home / ".cross-agent").mkdir(parents=True)
        (home / ".cross-agent" / "config.toml").write_text('[defaults]\nproducer = "codex:legacy-model:low"\n', encoding="utf-8")
        self.env.update({"HOME": str(home), "USERPROFILE": str(home)})
        result = self.initialize("--producer", "codex:chosen-model:high", "--reviewer", "codex:review-model:low")
        local = self.root / ".cross-agent" / "config.toml"
        self.assertEqual(result["config_path"], str(local.resolve()))
        self.assertFalse(self.config.exists())
        parsed = tomllib.loads(local.read_text(encoding="utf-8"))
        self.assertIn(".", parsed["projects"])
        self.assertEqual(parsed["defaults"], {"producer": "codex:chosen-model:high", "reviewer": "codex:review-model:low"})
        self.assertEqual(self.run_cli("status")["defaults"], parsed["defaults"])
        with patch.dict(os.environ, self.env, clear=True), patch.object(providers.Codex, "check"):
            preview = engine.start(
                self.root, stage="general", artifact="output.md", first="produce",
                request="Write a bounded plan.", producer=None, reviewer=None, dry_run=True,
            )
        self.assertEqual(preview["roles"]["producer"], {"provider": "codex", "model": "chosen-model", "effort": "high"})
        self.assertEqual(preview["roles"]["reviewer"]["effort"], "low")
        self.assertIn('model_reasoning_effort="high"', preview["command"])
        ignored = subprocess.run(["git", "check-ignore", ".cross-agent/config.toml"], cwd=self.root, capture_output=True)
        self.assertEqual(ignored.returncode, 0)
        self.assertFalse((local.parent / "runs").exists())
        other = self.directory / "other"
        other.mkdir()
        subprocess.run(["git", "init", "-q", str(other)], check=True, capture_output=True)
        self.assertIn("does not exist", self.run_cli("status", cwd=other, expect=2)["error"])
        (other / ".cross-agent").mkdir()
        shutil.copyfile(local, other / ".cross-agent" / "config.toml")
        moved = self.run_cli("status", cwd=other)
        self.assertEqual(moved["project"], self.proposal)
        self.assertEqual(moved["defaults"], parsed["defaults"])
        nested = self.root / "nested"
        nested.mkdir()
        self.assertIn("does not exist", self.run_cli("status", cwd=nested, expect=2)["error"])

    def test_shared_pointer_keeps_project_commands_separate_and_selects_configured_cli(self):
        self.env.pop("CROSS_AGENT_CONFIG")
        workspace = self.directory / "workspace"
        shared = workspace / ".cross-agent" / "config.toml"
        shared.parent.mkdir(parents=True)
        other = self.directory / "other"
        other.mkdir()
        selected = str(Path(sys.executable).resolve())
        shared.write_text(configuration_text(producer="codex:chosen-model:high", reviewer="codex:review-model:high",
            cli={"codex": selected}, projects={self.root.as_posix(): self.proposal,
            other.as_posix(): dict(allowed_commands=["other command"], delivery_checks=[], extra_dirs=[])}), encoding="utf-8")
        original = shared.read_bytes()
        for project in (self.root, other):
            local = project / ".cross-agent" / "config.toml"
            local.parent.mkdir()
            reference = Path(os.path.relpath(shared, local.parent)).as_posix()
            local.write_text(f"config_file = {json.dumps(reference)}\n", encoding="utf-8")
        status = self.run_cli("status")
        self.assertEqual(status["config_path"], str(shared))
        self.assertEqual(status["project"], self.proposal)
        self.assertEqual(status["cli_executables"]["codex"], selected)
        other_status = self.run_cli("status", cwd=other)
        self.assertEqual(other_status["config_path"], str(shared))
        self.assertEqual(other_status["project"]["allowed_commands"], ["other command"])
        self.assertEqual(other_status["project"]["delivery_checks"], [])
        repeated = self.initialize()
        self.assertEqual(repeated["action"], "unchanged")
        self.assertEqual(shared.read_bytes(), original)
        with patch.dict(os.environ, self.env, clear=True):
            preview = engine.start(
                self.root, stage="general", artifact="output.md", first="produce",
                request="Write a bounded plan.", producer=None, reviewer=None, dry_run=True,
            )
            state = {
                "project_root": str(self.root), "run_id": "saved-run", "project": status["project"],
                "skill": None, "roles": preview["roles"], "settings": status["settings"],
            }
            call = engine._call(state, "reviewer", "", {}, "saved-session")
            self.assertEqual(call.executable, selected)
            self.assertEqual(providers.preview_command("codex", call)[0], selected)
        self.assertEqual(preview["command"][0], selected)
        self.assertFalse((self.root / ".cross-agent" / "runs").exists())
        self.assertEqual(shared.read_bytes(), original)

    def test_invalid_shared_pointers_and_cli_values_are_refused(self):
        self.config.parent.mkdir()
        shared = self.directory / "shared.toml"
        cases = [
            'config_file = "missing.toml"\n',
            'config_file = "shared.toml"\nmax_reviews = 2\n',
            'config_file = ""\n',
            '[cli]\ncodex = "relative/codex.exe"\n',
            '[cli]\ncodex = 42\n',
            '[cli]\nunknown = "/cli"\n',
        ]
        for original in cases:
            with self.subTest(original=original):
                self.config.write_text(original, encoding="utf-8")
                self.run_cli("status", expect=2)
                self.assertEqual(self.config.read_text(encoding="utf-8"), original)
        shared.write_text('config_file = "settings/config.toml"\n', encoding="utf-8")
        self.config.write_text('config_file = "../shared.toml"\n', encoding="utf-8")
        self.assertIn("cannot be chained", self.run_cli("status", expect=2)["error"])

    def test_repeat_preserves_roles_and_reports_requested_differences(self):
        self.initialize("--producer", "codex:model-a:high")
        original = self.config.read_bytes()
        result = self.initialize("--producer", "codex:model-b:low")
        self.assertEqual(result["defaults"]["producer"], "codex:model-a:high")
        self.assertEqual(result["proposed_role_differences"], {"producer": "codex:model-b:low"})
        self.assertEqual(self.config.read_bytes(), original)

    def test_invalid_role_does_not_create_config(self):
        self.assertIn("error", self.initialize("--reviewer", "unknown:model:high", expect=2))
        self.assertFalse(self.config.exists())

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
        original = b'\xef\xbb\xbf# Keep this comment\r\n' + configuration_text(max_reviews=7,
            producer="codex:chosen-model:high", reviewer="codex:review-model:high", cli=self.cli_paths,
            projects={"other-project": dict(allowed_commands=["original"], delivery_checks=[], extra_dirs=[])}
            ).rstrip().replace("\n", "\r\n").encode("utf-8")
        self.config.write_bytes(original)
        result = self.initialize()
        self.assertEqual(result["action"], "project-added")
        self.assertEqual(result["settings"]["max_reviews"], 7)
        self.assertEqual(result["defaults"]["producer"], "codex:chosen-model:high")
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
        original = configuration_text(projects={alias: dict(allowed_commands=[], delivery_checks=["existing test"], extra_dirs=[])})
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

    def test_initialization_copies_template_values_not_python_defaults(self):
        template_path = CLI.parents[1] / "assets" / "config.example.toml"
        template = tomllib.loads(template_path.read_text(encoding="utf-8-sig"))
        result = self.initialize()
        parsed = tomllib.loads(self.config.read_text(encoding="utf-8"))
        for key in config.RUN_SETTINGS:
            self.assertEqual(parsed[key], template[key])
        self.assertEqual(parsed["defaults"], template["defaults"])
        self.assertEqual(parsed["cli"], self.cli_paths)
        self.assertEqual(result["defaults"], template["defaults"])
        original_read = Path.read_text

        def read_without_template(path, *args, **kwargs):
            if path == template_path:
                raise AssertionError("Existing configuration must not read the initialization template")
            return original_read(path, *args, **kwargs)

        with patch.dict(os.environ, self.env, clear=True), patch.object(Path, "read_text", read_without_template):
            self.assertEqual(config.load_config(self.root)["defaults"], parsed["defaults"])
            self.assertEqual(config.initialize(self.root, str(self.input), check_version=False)["action"], "unchanged")

    def test_missing_required_configuration_never_starts_workers_or_writes_files(self):
        htext = configuration_text(producer="codex:test-model:high", reviewer="claude:opus:medium", cli=self.cli_paths)
        cases = [
            htext.replace('producer = "codex:test-model:high"', 'producer = "codex"'),
            htext.replace('reviewer = "claude:opus:medium"', 'reviewer = "claude:opus:"'),
            htext.replace(f'codex = {json.dumps(self.cli_paths["codex"])}\n', ""),
            htext.replace("delivery_checks = []\n", ""),
        ]
        cases += ["\n".join(line for line in htext.split("\n") if not line.startswith(key + " = "))
                  for key in ("max_reviews", "timeout_minutes", "rotate_at_tokens", "backlog_rejected", "max_diff_kb")]
        self.config.parent.mkdir()
        for text in cases:
            with self.subTest(text=text):
                self.config.write_text(text, encoding="utf-8")
                self.run_cli("status", expect=2)
                self.run_cli("start", "--stage", "general", "--artifact", "output.md", "--first", "produce",
                             "--request", "Do not run with missing configuration.", expect=2)
                self.assertEqual(self.config.read_text(encoding="utf-8"), text)
                self.assertFalse((self.root / ".cross-agent" / "runs").exists())

    def test_project_section_is_required_and_configuration_is_not_backfilled(self):
        self.config.parent.mkdir()
        self.config.write_text(configuration_text(projects={}), encoding="utf-8")
        self.assertIn("Missing project configuration", self.run_cli("status", expect=2)["error"])

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


class CodexVersionTests(unittest.TestCase):
    def test_stable_versions_are_compared_numerically(self):
        for installed, latest, status in (
            ("1.9.0", "1.10.0", "update-available"),
            ("1.10.0", "1.10.0", "current"),
            ("2.0.0", "1.10.0", "ahead"),
            ("1.10.0-alpha.1", "1.10.0", "unknown"),
        ):
            with self.subTest(installed=installed), patch.object(versions.shutil, "which", return_value="codex"), \
                    patch.object(versions.subprocess, "run") as run, patch.object(versions, "urlopen") as fetch:
                run.return_value = subprocess.CompletedProcess([], 0, stdout=f"codex-cli {installed}\n")
                fetch.return_value.__enter__.return_value.read.return_value = json.dumps({"version": latest}).encode()
                result = versions.check_codex_version("codex")
                self.assertEqual(result["status"], status)
                self.assertEqual(result["installed"], installed)
                self.assertEqual(result["latest"], latest)
                self.assertEqual(run.call_args.args[0], ["codex", "--version"])
                self.assertEqual(fetch.call_args.args[0], versions.CODEX_LATEST_URL)

    def test_version_check_uses_the_configured_cli(self):
        selected = str(Path(sys.executable).resolve())
        with patch.object(versions.shutil, "which", return_value=selected) as discover, \
                patch.object(versions.subprocess, "run") as run, patch.object(versions, "urlopen") as fetch:
            run.return_value = subprocess.CompletedProcess([], 0, stdout="codex-cli 1.0.0")
            fetch.return_value.__enter__.return_value.read.return_value = b'{"version":"1.0.0"}'
            self.assertEqual(versions.check_codex_version(selected)["status"], "current")
            discover.assert_called_once_with(selected)
            self.assertEqual(run.call_args.args[0], [selected, "--version"])

    def test_missing_failed_offline_and_malformed_are_never_current(self):
        with patch.object(versions.shutil, "which", return_value=None), patch.object(versions, "urlopen") as fetch:
            self.assertEqual(versions.check_codex_version()["status"], "not-installed")
            fetch.assert_not_called()
        for failure in (OSError("offline"), b"not json", b'{"version": null}'):
            with self.subTest(failure=failure), patch.object(versions.shutil, "which", return_value="codex"), \
                    patch.object(versions.subprocess, "run") as run, patch.object(versions, "urlopen") as fetch:
                run.return_value = subprocess.CompletedProcess([], 0, stdout="codex-cli 1.0.0\n")
                if isinstance(failure, Exception):
                    fetch.side_effect = failure
                else:
                    fetch.return_value.__enter__.return_value.read.return_value = failure
                self.assertEqual(versions.check_codex_version("codex")["status"], "unknown")
        with patch.object(versions.shutil, "which", return_value="codex"), \
                patch.object(versions.subprocess, "run", side_effect=subprocess.TimeoutExpired("codex", 5)):
            self.assertEqual(versions.check_codex_version("codex")["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
