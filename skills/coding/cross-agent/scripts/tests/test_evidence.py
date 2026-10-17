"""Discussion exports preserve attributable text and fail closed on bad sources."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crossagent import evidence
from crossagent.errors import UsageError


SESSION = "11f5c3fa-1520-453c-980a-1a33bc0ec672"


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.source = self.root / "config/projects/encoded-project" / f"{SESSION}.jsonl"
        self.source.parent.mkdir(parents=True)
        self.destination = self.project / ".cross-agent/evidence/discussion.json"
        environment = patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(self.root / "config")})
        environment.start()
        self.addCleanup(environment.stop)

    def message(self, role="user", text="User requirement", **extra):
        return {"type": role, "uuid": f"{role}-uuid", "parentUuid": None,
                "cwd": str(self.project), "sessionId": SESSION,
                "timestamp": "2026-10-16T12:00:00Z", "isSidechain": False,
                "message": {"role": role, "content": text}, **extra}

    def save(self, *records):
        self.source.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    def run_import(self):
        return evidence.import_claude(self.project, SESSION, self.destination)

    def test_export_only_text_with_stable_locators_and_source_hash(self):
        user = self.message(text=[{"type": "tool_result", "content": "SECRET tool result"},
                                  {"type": "text", "text": "Actual user instruction"}])
        assistant = self.message("assistant", [{"type": "thinking", "thinking": "SECRET reasoning"},
                                                {"type": "text", "text": "Candidate, not confirmed"},
                                                {"type": "tool_use", "input": {"secret": "SECRET input"}}])
        sidechain = self.message(text="SECRET child", isSidechain=True, cwd="unrelated")
        self.save({"type": "system", "content": "SECRET system"}, user, assistant, sidechain)
        manifest = self.run_import()
        payload = evidence.read(manifest)
        self.assertEqual(manifest["message_count"], 2)
        self.assertEqual(payload["messages"][0], {"uuid": "user-uuid", "parentUuid": None,
                         "timestamp": "2026-10-16T12:00:00Z", "role": "user",
                         "text": "Actual user instruction", "source_id": f"{SESSION}:user-uuid"})
        self.assertNotIn("SECRET", self.destination.read_text(encoding="utf-8"))
        first = self.destination.read_bytes()
        self.assertEqual(manifest, self.run_import())
        self.assertEqual(first, self.destination.read_bytes())
        self.assertEqual(payload["source_sha256"], evidence._digest(self.source.read_bytes()))

    def test_missing_invalid_or_ambiguous_session(self):
        with self.assertRaisesRegex(UsageError, "missing or ambiguous"):
            self.run_import()
        with self.assertRaisesRegex(UsageError, "UUID"):
            evidence.import_claude(self.project, "../unsafe", self.destination)
        self.save(self.message())
        duplicate = self.source.parent.parent / "another-project" / self.source.name
        duplicate.parent.mkdir()
        duplicate.write_bytes(self.source.read_bytes())
        with self.assertRaisesRegex(UsageError, "missing or ambiguous"):
            self.run_import()
        self.assertFalse(self.destination.exists())

    def test_project_and_session_mismatch_rejected(self):
        self.save(self.message(cwd=str(self.root / "other-project")))
        with self.assertRaisesRegex(UsageError, "different project"):
            self.run_import()
        self.save(self.message(sessionId="another-session"))
        with self.assertRaisesRegex(UsageError, "malformed"):
            self.run_import()
        self.assertFalse(self.destination.exists())

    def test_malformed_or_unattributed_source_is_not_partially_imported(self):
        invalid = ["{invalid", "[]", json.dumps(self.message(uuid=None)),
                   json.dumps(self.message(cwd=None)), json.dumps(self.message(text=["bad block"])),
                   json.dumps(self.message(text=[{"type": "text", "text": 1}]))]
        for raw in invalid:
            with self.subTest(raw=raw):
                self.source.write_text(raw, encoding="utf-8")
                with self.assertRaises(UsageError):
                    self.run_import()
                self.assertFalse(self.destination.exists())
        self.save(self.message(), self.message())
        with self.assertRaises(UsageError):
            self.run_import()

    def test_tampered_export_rejected_but_live_session_can_continue(self):
        self.save(self.message())
        manifest = self.run_import()
        self.save(self.message(), self.message("assistant", "Later discussion"))
        self.assertEqual(len(evidence.read(manifest)["messages"]), 1)
        self.destination.write_bytes(self.destination.read_bytes() + b" ")
        with self.assertRaisesRegex(UsageError, "changed"):
            evidence.read(manifest)

    def test_no_tool_only_export_or_source_overwrite(self):
        self.save(self.message(text=[{"type": "tool_result", "content": "tool"}]))
        with self.assertRaisesRegex(UsageError, "no attributable"):
            self.run_import()
        self.save(self.message())
        original = self.source.read_bytes()
        with self.assertRaisesRegex(UsageError, "overwrite"):
            evidence.import_claude(self.project, SESSION, self.source)
        self.assertEqual(self.source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
