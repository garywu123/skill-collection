from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "flow_state.py"
TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "flow-state.template.yaml"


class FlowStateIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        (self.root / "doc").mkdir()

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def run_flow(
        self, *args: str, succeeds: bool = True,
        inject_decision_authority: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = list(args)
        if command and command[0] == "decide" and inject_decision_authority:
            if "--decided-by" not in command:
                command.extend(("--decided-by", "Integration test human"))
            if "--decision-date" not in command:
                command.extend(("--decision-date", "2026-08-01"))
            if "--decision-evidence" not in command:
                command.extend(("--decision-evidence", "integration-test-user-message"))
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *command],
            text=True,
            capture_output=True,
            check=False,
            # Windows raises WinError 6 when an invalid parent stdin is inherited.
            stdin=subprocess.DEVNULL,
        )
        if succeeds and result.returncode != 0:
            self.fail(f"command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}")
        if not succeeds and result.returncode == 0:
            self.fail(f"command unexpectedly succeeded: {args}\nstdout={result.stdout}")
        return result

    def state(self) -> dict:
        return yaml.safe_load((self.root / ".specify" / "flow-state.yaml").read_text("utf-8"))

    def write(self, relative: str, content: str) -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def pre_review(self, result: str = "Pass", suffix: str = "") -> str:
        blocker = "AC-001 conflict" if result == "Blocked" else "None"
        return (
            "# Pre-implementation Review: F001\n\n"
            "**Work item**: F001\n"
            "**Work kind**: feature\n"
            f"**Review result**: {result}\n"
            "**Reviewed revision**: plan-v1\n"
            "**Reviewed by**: Reviewer\n"
            "**Reviewed on**: 2026-08-01\n"
            "**Scope**: Vertical feature readiness only\n\n"
            "## Inputs\n\n"
            "| Artifact | Path or ID | Revision or anchor |\n"
            "|---|---|---|\n"
            "| Work-item spec | specs/001/spec.md | spec-v1 |\n"
            "| Plan | specs/001/plan.md | plan-v1 |\n"
            "| Tasks | specs/001/tasks.md | tasks-v1 |\n"
            "| Requirements checklist | specs/001/requirements.md | checklist-v1 |\n\n"
            "## Alignment Checks\n\n"
            "| Check | Result | Evidence | Notes |\n"
            "|---|---|---|---|\n"
            "| Scope | Pass | F001 | Aligned |\n\n"
            "## Coverage Batches\n\n"
            "| Batch | Stable IDs / paths | Result | Evidence |\n"
            "|---|---|---|---|\n"
            "| B-001 | F001, PR-001 | Pass | review-notes.md |\n\n"
            f"## Blocking Findings\n\n- {blocker}\n\n"
            "## Advisory Findings\n\n- None\n\n"
            "## Skipped Checks\n\n- None\n\n"
            f"## Outcome Rationale\n\nConcrete review rationale.\n{suffix}"
        )

    def verification_review(
        self, *, work_id: str = "F001", work_kind: str = "feature",
        candidate_state: str | None = None, blocker: str = "None",
        directory: str | None = None,
    ) -> str:
        if candidate_state is None:
            candidate_state = (
                "Ready for Acceptance" if work_kind == "feature" else "Ready for Review"
            )
        if directory is None:
            directory = "specs/001" if work_id == "F001" else f"specs/{work_id.lower()}"
        return (
            f"# {work_id} Verification Evidence\n\n"
            f"**Work item**: {work_id}\n"
            f"**Work kind**: {work_kind}\n"
            "**Reviewed revision**: commit-abc\n"
            "**Reviewed on**: 2026-08-01\n"
            f"**Candidate state**: {candidate_state}\n\n"
            "## Inputs\n\n"
            "| Artifact | Path/ID | Revision or anchor |\n"
            "|---|---|---|\n"
            f"| Work-item spec | {directory}/spec.md | spec-v1 |\n\n"
            "## Proof Evidence\n\n"
            "| Scenario ID | Command/activity | Result | Evidence path/run ID |\n"
            "|---|---|---|---|\n"
            "| SC-001 | targeted tests | Pass | test-output.txt |\n\n"
            "## Tasks, Checks, and Deferrals\n\n"
            "| Item | Result | Evidence or deferred-work destination |\n"
            "|---|---|---|\n"
            "| T-001 | Complete | commit-abc |\n\n"
            "## Constraint and Scope Drift\n\n"
            "| Constraint/scope ID | Result | Evidence | Required owner/action |\n"
            "|---|---|---|---|\n"
            "| AC-001 | Aligned | review-note | None |\n\n"
            "## Coverage Batches\n\n"
            "| Batch | Stable IDs / paths | Result | Evidence |\n"
            "|---|---|---|---|\n"
            f"| B-001 | {work_id}, SC-001, T-001 | Pass | verification-notes.md |\n\n"
            f"## Blocking Findings\n\n- {blocker}\n\n"
            "## Skipped Checks\n\n- None\n\n"
            "## Readiness Conclusion\n\n"
            f"Evidence supports {candidate_state}.\n"
        )

    def acceptance_review(self) -> str:
        return (
            "# Feature Acceptance: F001\n\n"
            "**Work item**: F001\n"
            "**Review status**: ready\n"
            "**Reviewed by**: Independent acceptance reviewer\n"
            "**Reviewed on**: 2026-08-01\n"
            "**Independence**: non-implementer\n"
            "**Human decision**: {{PENDING_OR_DECISION}}\n"
            "**Decided by**: {{PENDING_OR_ACTOR}}\n"
            "**Decision date**: {{PENDING_OR_DATE}}\n"
            "**Decision evidence**: {{PENDING_OR_REFERENCE}}\n"
            "**Spec**: specs/001/spec.md\n"
            "**Implementation revision**: commit-abc\n\n"
            "## Scenario Evidence\n\n"
            "| Scenario | Result | Evidence | Notes |\n"
            "|---|---|---|---|\n"
            "| SC-001 | Pass | test-output.txt | Verified |\n"
            "| SC-002 | Pass | test-output.txt | Verified |\n\n"
            "## Applicable Quality Gates\n\n"
            "| Gate | Applicability | Result | Evidence / reason |\n"
            "|---|---|---|---|\n"
            "| Tests | required | Pass | test-output.txt |\n"
            "| Coverage policy | not_applicable | not_applicable | No project coverage threshold |\n"
            "| CI | required | Pass | ci-run-42 |\n"
            "| Code review | applicable | Pass | review-42 |\n"
            "| Security review | not_applicable | not_applicable | No security signal in fixed diff |\n\n"
            "## Blockers\n\n- None\n\n"
            "## Follow-ups\n\n"
            "| Type | ID | Description | Blocking |\n"
            "|---|---|---|---|\n"
            "| None | N/A | None | No |\n\n"
            "## Human Decision Notes\n\nPending human decision.\n"
        )

    def release_readiness(self) -> str:
        return (
            "# Release Readiness: REL-2026.08\n\n"
            "**Release ID**: REL-2026.08\n"
            "**Review status**: ready\n"
            "**Reviewed by**: Independent release reviewer\n"
            "**Reviewed on**: 2026-08-01\n"
            "**Independence**: non-implementer\n"
            "**Human readiness decision**: {{PENDING_OR_DECISION}}\n"
            "**Authorization evidence**: {{PENDING_OR_REFERENCE}}\n"
            "**Authorized by**: {{PENDING_OR_ACTOR}}\n"
            "**Authorized on**: {{PENDING_OR_DATE}}\n"
            "**Scope**: F001\n"
            "**Artifact revision**: build-sha-abc\n\n"
            "## Included Acceptance Decisions\n\n"
            "| Feature | Human decision | Acceptance artifact |\n"
            "|---|---|---|\n"
            "| F001 | Accepted | specs/001/acceptance.md |\n\n"
            "## Release Gates\n\n"
            "| Gate | Applicability | Result | Evidence / reason |\n"
            "|---|---|---|---|\n"
            "| Build provenance | required | Pass | build-42 |\n"
            "| CI | required | Pass | ci-42 |\n"
            "| Code review | required | Pass | review-42 |\n"
            "| Dependency review | not_applicable | not_applicable | Lockfile unchanged |\n"
            "| Security review | not_applicable | not_applicable | No security signal |\n"
            "| Migration | not_applicable | not_applicable | No schema or data change |\n"
            "| Compatibility | required | Pass | compatibility-42 |\n"
            "| Rollback | required | Pass | rollback-42 |\n"
            "| Observability / operations | required | Pass | ops-42 |\n"
            "| User / operator documentation | required | Pass | docs-42 |\n\n"
            "## Blockers\n\n- None\n\n"
            "## Deferred Items\n\n"
            "| Type | ID | Disposition | Owner |\n"
            "|---|---|---|---|\n"
            "| None | N/A | None | N/A |\n\n"
            "## Release Execution Result\n\n"
            "**Execution**: {{PENDING_OR_RESULT}}\n"
            "**Execution evidence**: {{PENDING_OR_EVIDENCE}}\n"
            "**Execution evidence SHA-256**: {{PENDING_OR_EVIDENCE_SHA256}}\n"
            "**Confirmed by**: {{PENDING_OR_ACTOR}}\n"
            "**Confirmed on**: {{PENDING_OR_DATE}}\n\n"
            "Pending execution result.\n"
        )

    def release_receipt(self, result: str = "succeeded") -> str:
        return (
            "schema_version: 1\n"
            "release_id: REL-2026.08\n"
            f"result: {result}\n"
            "producer: ci-release-job\n"
            "run_id: release-run-9001\n"
            "completed_at: '2026-08-01T15:04:05Z'\n"
            f"artifact_sha256: {'a' * 64 if result == 'succeeded' else 'null'}\n"
        )

    def write_accepted_feature(self) -> None:
        artifact_path = "specs/001/acceptance.md"
        self.write(
            artifact_path,
            "# Feature Acceptance: F001\n\n"
            "**Work item**: F001\n"
            "**Human decision**: Accepted\n"
            "**Decided by**: Integration test human\n"
            "**Decision date**: 2026-08-01\n"
            "**Decision evidence**: integration-test-user-message\n",
        )
        artifact_digest = hashlib.sha256(
            (self.root / artifact_path).read_bytes()
        ).hexdigest()
        receipt = {
            "schema_version": 1,
            "receipt_type": "feature_acceptance_decision",
            "pointer_revision": 1,
            "work_kind": "feature",
            "work_id": "F001",
            "stage": "acceptance",
            "decision": "accepted",
            "decided_by": "Integration test human",
            "decided_on": "2026-08-01",
            "evidence": "integration-test-user-message",
            "artifacts": [
                {
                    "role": "acceptance",
                    "path": artifact_path,
                    "reviewed_sha256": artifact_digest,
                    "result_sha256": artifact_digest,
                }
            ],
        }
        rendered = yaml.safe_dump(
            receipt, sort_keys=False, allow_unicode=True, width=1000
        )
        receipt_digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
        receipt_path = (
            self.root / ".specify" / "decisions"
            / f"000001-feature-f001-acceptance-{receipt_digest}.yaml"
        )
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_bytes(rendered.encode("utf-8"))

    def prepare_work_item(
        self, *, expected_revision: int, kind: str = "feature",
        work_id: str = "F001", directory: str = "specs/001",
    ) -> int:
        self.run_flow(
            "start", "--expect-revision", str(expected_revision), "--kind", kind,
            "--work-id", work_id, "--stage", "specify",
        )
        self.write(
            f"{directory}/spec.md",
            f"# Spec {work_id}\n\n## Acceptance Scenarios\n\n"
            "- SC-001: primary behavior\n"
            "- SC-002: boundary behavior\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", str(expected_revision + 1),
            "--stage", "specify", "--artifact", f"spec={directory}/spec.md",
        )
        self.run_flow(
            "decide", "--expect-revision", str(expected_revision + 2),
            "--decision", "approved",
        )
        self.run_flow(
            "start", "--expect-revision", str(expected_revision + 3), "--kind", kind,
            "--work-id", work_id, "--stage", "plan",
        )
        self.write(f"{directory}/plan.md", f"# Plan {work_id}\n")
        self.write(f"{directory}/tasks.md", f"# Tasks {work_id}\n")
        self.write(f"{directory}/requirements.md", f"# Requirements Checklist {work_id}\n")
        self.run_flow(
            "record-output", "--expect-revision", str(expected_revision + 4),
            "--stage", "plan",
            "--artifact", f"plan={directory}/plan.md",
            "--artifact", f"tasks={directory}/tasks.md",
            "--artifact", f"requirements_checklist={directory}/requirements.md",
        )
        self.run_flow(
            "decide", "--expect-revision", str(expected_revision + 5),
            "--decision", "approved",
        )
        self.run_flow(
            "start", "--expect-revision", str(expected_revision + 6), "--kind", kind,
            "--work-id", work_id, "--stage", "pre_implement",
        )
        return expected_revision + 7

    def prepare_implementation(
        self, *, expected_revision: int = 0, kind: str = "feature",
        work_id: str = "F001", directory: str = "specs/001",
    ) -> int:
        pre_revision = self.prepare_work_item(
            expected_revision=expected_revision,
            kind=kind,
            work_id=work_id,
            directory=directory,
        )
        review = self.pre_review().replace("F001", work_id).replace(
            "specs/001/", f"{directory}/"
        )
        review = review.replace("**Work kind**: feature", f"**Work kind**: {kind}")
        self.write(f"{directory}/pre-implementation-review.md", review)
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision),
            "--stage", "pre_implement", "--artifact",
            f"pre_implementation={directory}/pre-implementation-review.md",
        )
        self.run_flow(
            "decide", "--expect-revision", str(pre_revision + 1),
            "--decision", "approved",
        )
        self.run_flow(
            "start", "--expect-revision", str(pre_revision + 2), "--kind", kind,
            "--work-id", work_id, "--stage", "implementation",
        )
        return pre_revision + 3

    def prepare_post_implementation_candidate(self) -> int:
        implementation_revision = self.prepare_implementation()
        self.write("specs/001/verification.md", self.verification_review())
        self.run_flow(
            "record-output", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement", "--status", "ready_for_acceptance",
            "--artifact", "verification=specs/001/verification.md",
        )
        return implementation_revision + 1

    def test_human_gates_profile_and_feature_acceptance(self) -> None:
        self.run_flow("init", "--project-id", "WMS", "--profile", "full")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "WMS", "--stage", "discovery",
        )
        self.write(
            "doc/discovery.md",
            "# Discovery\n\n**Artifact bundle**: single\n\nF001 PR-001\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md", "--next", "approve discovery",
        )
        candidate = self.state()
        self.assertEqual(candidate["canonical_status"]["discovery"], "ready_for_review")
        self.assertTrue(candidate["next"]["allowed"][0]["requires_human"])
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        self.assertEqual(self.state()["canonical_status"]["discovery"], "approved")

        missing_roadmap = self.run_flow(
            "confirm-profile", "--expect-revision", "3", "--profile", "full", succeeds=False,
        )
        self.assertIn("approved roadmap", missing_roadmap.stderr)

        self.run_flow(
            "start", "--expect-revision", "3", "--kind", "project",
            "--work-id", "WMS", "--stage", "roadmap",
        )
        self.write(
            "doc/roadmap.md",
            "# Roadmap\n\n**Artifact bundle**: single\n"
            "**Profile sizing**: full\n"
            "**Sizing evidence**: PR-100 and F001..F012 roadmap anchors\n\n"
            "**Feature count**: 12\n"
            "**Deployable count**: 2\n"
            "**Datastore count**: 2\n"
            "**Owning team count**: 2\n"
            "**Regulatory/audit/contractual constraint**: yes\n\n"
            "F001 owns PR-001\n"
            "F002 F003 F004 F005 F006 F007 F008 F009 F010 F011 F012\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "roadmap",
            "--artifact", "roadmap=doc/roadmap.md",
        )
        self.run_flow("decide", "--expect-revision", "5", "--decision", "approved")
        mismatched_sizing = self.run_flow(
            "confirm-profile", "--expect-revision", "6", "--profile", "lite",
            succeeds=False,
        )
        self.assertIn("Profile sizing", mismatched_sizing.stderr)
        self.run_flow("confirm-profile", "--expect-revision", "6", "--profile", "full")
        self.assertEqual(self.state()["project"]["profile_status"], "confirmed")

        pre_revision = self.prepare_work_item(expected_revision=7)
        self.write("specs/001/pre-implementation-review.md", self.pre_review())
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
        )
        self.run_flow(
            "decide", "--expect-revision", str(pre_revision + 1), "--decision", "approved"
        )
        self.run_flow(
            "start", "--expect-revision", str(pre_revision + 2), "--kind", "feature",
            "--work-id", "F001", "--stage", "implementation",
        )
        self.write("specs/001/verification.md", self.verification_review())
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision + 3), "--stage", "post_implement",
            "--status", "ready_for_acceptance", "--artifact",
            "verification=specs/001/verification.md", "--context-id", "F001",
        )
        generic_bypass = self.run_flow(
            "decide", "--expect-revision", str(pre_revision + 4),
            "--decision", "approved", succeeds=False,
        )
        self.assertIn("generic decide only", generic_bypass.stderr)

        missing_scenario = self.acceptance_review().replace(
            "| SC-002 | Pass | test-output.txt | Verified |\n", ""
        )
        self.write("specs/001/acceptance.md", missing_scenario)
        incomplete_acceptance = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision + 4),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("exactly cover", incomplete_acceptance.stderr)
        self.write("specs/001/acceptance.md", self.acceptance_review())
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision + 4), "--stage", "acceptance",
            "--status", "ready_for_acceptance", "--artifact",
            "acceptance=specs/001/acceptance.md",
        )
        self.write("specs/001/acceptance.md", "# Acceptance\n")
        malformed = self.run_flow(
            "record-feature-decision", "--expect-revision", str(pre_revision + 5),
            "--decision", "accepted", "--artifact", "specs/001/acceptance.md",
            "--decided-by", "Product owner", "--decision-date", "2026-08-01",
            "--decision-evidence", "user-message-42",
            succeeds=False,
        )
        self.assertIn("hash is stale", malformed.stderr)
        self.write("specs/001/acceptance.md", self.acceptance_review())
        self.run_flow(
            "record-feature-decision", "--expect-revision", str(pre_revision + 5),
            "--decision", "accepted", "--artifact", "specs/001/acceptance.md",
            "--decided-by", "Product owner", "--decision-date", "2026-08-01",
            "--decision-evidence", "user-message-42",
        )
        accepted = self.state()
        self.assertEqual(accepted["active_work"]["status"], "accepted")
        self.assertEqual(
            next(item for item in accepted["active_artifacts"] if item["role"] == "acceptance")["status"],
            "accepted",
        )
        self.assertIn(
            "**Human decision**: Accepted",
            (self.root / "specs/001/acceptance.md").read_text("utf-8"),
        )
        self.assertIn(
            "SC-001",
            (self.root / "specs/001/acceptance.md").read_text("utf-8"),
        )
        feature_receipts = [
            yaml.safe_load(path.read_text("utf-8"))
            for path in (self.root / ".specify" / "decisions").glob("*.yaml")
            if yaml.safe_load(path.read_text("utf-8")).get("receipt_type")
            == "feature_acceptance_decision"
        ]
        self.assertEqual(len(feature_receipts), 1)
        self.assertEqual(feature_receipts[0]["decision"], "accepted")
        self.assertEqual(
            feature_receipts[0]["artifacts"][0]["result_sha256"],
            hashlib.sha256(
                (self.root / "specs/001/acceptance.md").read_bytes()
            ).hexdigest(),
        )

        resolved = self.run_flow("resolve", "--id", "F001")
        self.assertIn("doc/roadmap.md", resolved.stdout)
        self.run_flow("validate", "--check-paths")

    def test_profile_sizing_requires_concrete_anchor_evidence(self) -> None:
        self.run_flow("init", "--project-id", "sizing-anchor", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "sizing-anchor", "--stage", "roadmap",
        )
        self.write(
            "doc/roadmap.md",
            "# Roadmap\n\n"
            "**Artifact bundle**: single\n"
            "**Profile sizing**: lite\n"
            "**Feature count**: 1\n"
            "**Deployable count**: 1\n"
            "**Datastore count**: 0\n"
            "**Owning team count**: 1\n"
            "**Regulatory/audit/contractual constraint**: no\n"
            "**Sizing evidence**: [Stable source anchor(s) only]\n\n"
            "F001\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "roadmap",
            "--artifact", "roadmap=doc/roadmap.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        placeholder = self.run_flow(
            "confirm-profile", "--expect-revision", "3", "--profile", "lite",
            succeeds=False,
        )
        self.assertIn("Sizing evidence", placeholder.stderr)
        self.assertEqual(self.state()["revision"], 3)

    def test_release_requires_authorization_then_confirmed_execution(self) -> None:
        self.run_flow("init", "--project-id", "release-demo", "--profile", "lite")
        self.write_accepted_feature()
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "release",
            "--work-id", "REL-2026.08", "--stage", "release_readiness",
        )
        self.write(
            "doc/releases/REL-2026.08-readiness.md", self.release_readiness()
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/REL-2026.08-readiness.md",
        )
        bypass = self.run_flow(
            "decide", "--expect-revision", "2", "--decision", "approved", succeeds=False,
        )
        self.assertIn("specialized delivery", bypass.stderr)
        premature = self.run_flow(
            "record-release-result", "--expect-revision", "2", "--result", "succeeded",
            "--artifact", "doc/releases/REL-2026.08-readiness.md",
            "--execution-evidence", "release-run-9001", "--confirmed-by", "Release manager",
            "--confirmed-on", "2026-08-01", succeeds=False,
        )
        self.assertIn("previously authorized", premature.stderr)
        self.run_flow(
            "authorize-release", "--expect-revision", "2", "--artifact",
            "doc/releases/REL-2026.08-readiness.md",
            "--authorized-by", "Release manager", "--authorized-on", "2026-08-01",
            "--authorization-evidence", "user-message-84",
        )
        self.assertEqual(self.state()["active_work"]["status"], "release_authorized")
        arbitrary = self.run_flow(
            "record-release-result", "--expect-revision", "3", "--result", "succeeded",
            "--artifact", "doc/releases/REL-2026.08-readiness.md",
            "--execution-evidence", "release-run-9001", "--confirmed-by", "Release manager",
            "--confirmed-on", "2026-08-01", succeeds=False,
        )
        self.assertIn("receipt", arbitrary.stderr)
        self.write(
            "doc/releases/wrong-result.yaml",
            self.release_receipt().replace("REL-2026.08", "REL-WRONG"),
        )
        wrong_receipt = self.run_flow(
            "record-release-result", "--expect-revision", "3", "--result", "succeeded",
            "--artifact", "doc/releases/REL-2026.08-readiness.md",
            "--execution-evidence", "doc/releases/wrong-result.yaml",
            "--confirmed-by", "Release manager", "--confirmed-on", "2026-08-01",
            succeeds=False,
        )
        self.assertIn("release_id", wrong_receipt.stderr)
        self.write("doc/releases/REL-2026.08-result.yaml", self.release_receipt())
        self.run_flow(
            "record-release-result", "--expect-revision", "3", "--result", "succeeded",
            "--artifact", "doc/releases/REL-2026.08-readiness.md",
            "--execution-evidence", "doc/releases/REL-2026.08-result.yaml",
            "--confirmed-by", "Release manager",
            "--confirmed-on", "2026-08-01",
        )
        self.assertEqual(self.state()["active_work"]["status"], "released")
        release_receipt_path = self.root / "doc" / "releases" / "REL-2026.08-result.yaml"
        release_receipt_digest = hashlib.sha256(release_receipt_path.read_bytes()).hexdigest()
        self.assertIn(
            f"**Execution evidence SHA-256**: {release_receipt_digest}",
            (self.root / "doc" / "releases" / "REL-2026.08-readiness.md").read_text("utf-8"),
        )
        specialized_types = {
            receipt["receipt_type"]
            for path in (self.root / ".specify" / "decisions").glob("*.yaml")
            if (receipt := yaml.safe_load(path.read_text("utf-8"))).get("receipt_type")
        }
        self.assertEqual(
            specialized_types,
            {"feature_acceptance_decision", "release_authorization", "release_result"},
        )
        immutable = self.run_flow(
            "start", "--expect-revision", "4", "--kind", "release",
            "--work-id", "REL-2026.08", "--stage", "release_readiness", succeeds=False,
        )
        self.assertIn("immutable", immutable.stderr)
        resolved = self.run_flow("resolve", "--id", "REL-2026.08")
        self.assertIn("REL-2026.08-readiness.md", resolved.stdout)
        self.run_flow("validate", "--check-paths")

        self.run_flow(
            "start", "--expect-revision", "4", "--kind", "maintenance",
            "--work-id", "MAINT-1", "--stage", "specify",
        )
        original_receipt = release_receipt_path.read_text("utf-8")
        release_receipt_path.write_text(original_receipt + "# silent edit\n", encoding="utf-8")
        stale_history = self.run_flow("rebuild-index", succeeds=False)
        self.assertIn("release-result decision receipt evidence hash is stale", stale_history.stderr)
        self.assertEqual(self.state()["revision"], 5)

    def test_release_requires_bound_feature_acceptance_receipt(self) -> None:
        self.run_flow("init", "--project-id", "release-binding", "--profile", "lite")
        self.write(
            "specs/001/acceptance.md",
            "# Feature Acceptance: F001\n\n"
            "**Work item**: F001\n"
            "**Human decision**: Accepted\n"
            "**Decided by**: Integration test human\n"
            "**Decision date**: 2026-08-01\n"
            "**Decision evidence**: integration-test-user-message\n",
        )
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "release",
            "--work-id", "REL-2026.08", "--stage", "release_readiness",
        )
        self.write("doc/releases/readiness.md", self.release_readiness())
        missing_receipt = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("durable accepted feature decision", missing_receipt.stderr)

        self.write_accepted_feature()
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md",
        )
        acceptance_path = self.root / "specs" / "001" / "acceptance.md"
        acceptance_path.write_text(
            acceptance_path.read_text("utf-8") + "\nUnreviewed edit.\n", encoding="utf-8"
        )
        stale_acceptance = self.run_flow(
            "authorize-release", "--expect-revision", "2", "--artifact",
            "doc/releases/readiness.md", "--authorized-by", "Release manager",
            "--authorized-on", "2026-08-01", "--authorization-evidence",
            "user-message-85", succeeds=False,
        )
        self.assertIn("accepted feature decision artifact hash is stale", stale_acceptance.stderr)
        self.assertEqual(self.state()["revision"], 2)

    def test_asset_template_matches_initialized_schema(self) -> None:
        self.run_flow("init", "--project-id", "PROJECT_ID", "--profile", "full")
        expected = yaml.safe_load(TEMPLATE.read_text("utf-8"))
        self.assertEqual(self.state(), expected)

    def test_full_guide_pointer_example_matches_live_schema(self) -> None:
        guide = SCRIPT.parents[2] / "spec-driven-flow.md"
        text = guide.read_text("utf-8")
        section = text.split("### 3.2 Pointer 样例", 1)[1]
        sample = section.split("```yaml", 1)[1].split("```", 1)[0]
        self.write(".specify/flow-state.yaml", sample.strip() + "\n")
        self.run_flow("validate")

    def test_stale_revision_and_path_escape_fail_without_transition(self) -> None:
        self.run_flow("init", "--project-id", "safe", "--profile", "lite")
        stale = self.run_flow(
            "start", "--expect-revision", "9", "--kind", "project",
            "--work-id", "safe", "--stage", "discovery", succeeds=False,
        )
        self.assertIn("stale revision", stale.stderr)
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "safe", "--stage", "discovery",
        )
        switched = self.run_flow(
            "start", "--expect-revision", "1", "--kind", "feature",
            "--work-id", "F001", "--stage", "specify", succeeds=False,
        )
        self.assertIn("block or complete", switched.stderr)
        escaped = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=../outside.md", succeeds=False,
        )
        self.assertIn("escapes the project root", escaped.stderr)
        self.assertEqual(self.state()["revision"], 1)

    def test_block_artifact_and_index_tampering_are_durable_and_safe(self) -> None:
        self.run_flow("init", "--project-id", "safe", "--profile", "lite")
        pre_revision = self.prepare_work_item(expected_revision=0)
        self.write("specs/001/pre-implementation-review.md", self.pre_review("Blocked"))
        self.run_flow(
            "block", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
            "--blocker", "AC-001 conflict",
        )
        blocked = self.state()
        self.assertEqual(blocked["active_work"]["status"], "blocked")
        self.assertEqual(
            next(
                item for item in blocked["active_artifacts"]
                if item["role"] == "pre_implementation"
            )["status"],
            "blocked",
        )
        self.run_flow("validate", "--check-paths")

        index_file = self.root / ".specify" / "artifact-index.yaml"
        index = yaml.safe_load(index_file.read_text("utf-8"))
        index["artifacts"][0]["path"] = "../../outside.md"
        index_file.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
        unsafe = self.run_flow("resolve", "--id", "F001", succeeds=False)
        self.assertIn("index digest mismatch", unsafe.stderr)
        invalid = self.run_flow("validate", "--check-paths", succeeds=False)
        self.assertIn("index digest mismatch", invalid.stderr)

    def test_implementation_requires_approved_unchanged_pre_review(self) -> None:
        self.run_flow("init", "--project-id", "guarded", "--profile", "lite")
        pre_revision = self.prepare_work_item(expected_revision=0)
        self.write("specs/001/pre-implementation-review.md", self.pre_review())
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
        )
        premature = self.run_flow(
            "start", "--expect-revision", str(pre_revision + 1), "--kind", "feature",
            "--work-id", "F001", "--stage", "implementation", succeeds=False,
        )
        self.assertIn("pending human gate", premature.stderr)
        self.run_flow(
            "decide", "--expect-revision", str(pre_revision + 1), "--decision", "approved"
        )
        self.write(
            "specs/001/pre-implementation-review.md", self.pre_review("Pass", "\nchanged\n")
        )
        changed = self.run_flow(
            "start", "--expect-revision", str(pre_revision + 2), "--kind", "feature",
            "--work-id", "F001", "--stage", "implementation", succeeds=False,
        )
        self.assertIn("hash is stale", changed.stderr)
        self.write("specs/001/pre-implementation-review.md", self.pre_review())
        self.run_flow(
            "start", "--expect-revision", str(pre_revision + 2), "--kind", "feature",
            "--work-id", "F001", "--stage", "implementation",
        )
        self.assertEqual(self.state()["active_work"]["stage"], "implementation")

    def test_canonical_amendment_requires_reviewed_proposal_then_promotion(self) -> None:
        self.run_flow("init", "--project-id", "amend", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "amend", "--stage", "discovery",
        )
        self.write(
            "doc/discovery.md", "# Discovery\n\n**Artifact bundle**: single\n\nOriginal truth\n"
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        self.run_flow(
            "start", "--expect-revision", "3", "--kind", "change_request",
            "--work-id", "CR-0001", "--stage", "change_request",
        )
        self.write("doc/product-amendments/CR-0001.md", "# Product Amendment CR-0001\n")
        self.write(
            "doc/discovery.md", "# Discovery\n\n**Artifact bundle**: single\n\nProposed truth\n"
        )
        direct = self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "change_request",
            "--artifact", "product_amendment=doc/product-amendments/CR-0001.md",
            "--artifact", "discovery=doc/discovery.md", succeeds=False,
        )
        self.assertIn("reviewed change-request", direct.stderr)
        self.write(
            "doc/discovery.md", "# Discovery\n\n**Artifact bundle**: single\n\nOriginal truth\n"
        )
        self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "change_request",
            "--artifact", "product_amendment=doc/product-amendments/CR-0001.md",
        )
        self.write(
            "doc/discovery.md",
            "# Discovery\n\n**Artifact bundle**: single\n\nApproved amended truth\n",
        )
        self.write("doc/product-amendments/injected.md", "# Injected CR\n")
        bypass = self.run_flow(
            "record-output", "--expect-revision", "5", "--stage", "change_request",
            "--artifact", "product_amendment=doc/product-amendments/CR-0001.md",
            "--artifact", "change_request=doc/product-amendments/injected.md",
            "--artifact", "discovery=doc/discovery.md", succeeds=False,
        )
        self.assertIn("cannot add or omit amendment roles", bypass.stderr)
        self.run_flow(
            "record-output", "--expect-revision", "5", "--stage", "change_request",
            "--artifact", "product_amendment=doc/product-amendments/CR-0001.md",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.run_flow("decide", "--expect-revision", "6", "--decision", "approved")
        amended = self.state()
        self.assertEqual(amended["canonical_status"]["discovery"], "approved")
        self.assertEqual(
            next(
                item
                for item in amended["active_artifacts"]
                if item["role"] == "product_amendment"
            )["status"],
            "approved",
        )

    def test_candidate_contract_rejects_wrong_target_and_empty_body(self) -> None:
        self.run_flow("init", "--project-id", "candidate", "--profile", "lite")
        pre_revision = self.prepare_work_item(expected_revision=0)
        self.write(
            "specs/001/pre-implementation-review.md",
            self.pre_review().replace("**Work item**: F001", "**Work item**: F999"),
        )
        wrong_target = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
            succeeds=False,
        )
        self.assertIn("must match active work", wrong_target.stderr)
        self.write(
            "specs/001/pre-implementation-review.md",
            "# Pre-implementation Review: F001\n\n"
            "**Work item**: F001\n**Work kind**: feature\n**Review result**: Pass\n"
            "**Reviewed revision**: plan-v1\n**Reviewed by**: Reviewer\n"
            "**Reviewed on**: 2026-08-01\n",
        )
        empty_body = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
            succeeds=False,
        )
        self.assertIn("missing required section", empty_body.stderr)
        self.assertEqual(self.state()["revision"], pre_revision)

    def test_non_feature_implementation_uses_review_not_feature_acceptance(self) -> None:
        self.run_flow("init", "--project-id", "bugfix", "--profile", "lite")
        pre_revision = self.prepare_work_item(
            expected_revision=0, kind="bug", work_id="BUG-7", directory="specs/bug-7"
        )
        self.write(
            "specs/bug-7/pre-implementation-review.md",
            self.pre_review().replace("F001", "BUG-7")
            .replace("specs/001/", "specs/bug-7/")
            .replace("**Work kind**: feature", "**Work kind**: bug"),
        )
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/bug-7/pre-implementation-review.md",
        )
        self.run_flow(
            "decide", "--expect-revision", str(pre_revision + 1), "--decision", "approved"
        )
        self.run_flow(
            "start", "--expect-revision", str(pre_revision + 2), "--kind", "bug",
            "--work-id", "BUG-7", "--stage", "implementation",
        )
        self.write(
            "specs/bug-7/verification.md",
            self.verification_review(work_id="BUG-7", work_kind="bug"),
        )
        self.run_flow(
            "record-output", "--expect-revision", str(pre_revision + 3), "--stage", "post_implement",
            "--status", "ready_for_review", "--artifact",
            "verification=specs/bug-7/verification.md",
        )
        feature_decision = self.run_flow(
            "record-feature-decision", "--expect-revision", str(pre_revision + 4),
            "--decision", "accepted", "--artifact", "specs/bug-7/verification.md",
            "--decided-by", "Owner", "--decision-date", "2026-08-01",
            "--decision-evidence", "review-7", succeeds=False,
        )
        self.assertIn("active acceptance candidate", feature_decision.stderr)
        self.run_flow(
            "decide", "--expect-revision", str(pre_revision + 4), "--decision", "approved"
        )
        self.assertEqual(self.state()["active_work"]["status"], "approved")

    def test_approved_canonical_drift_cannot_be_reindexed_or_resolved(self) -> None:
        self.run_flow("init", "--project-id", "canonical", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "canonical", "--stage", "discovery",
        )
        self.write(
            "doc/discovery.md",
            "# Discovery\n\n**Artifact bundle**: single\n\nPR-001 original\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        self.write(
            "doc/discovery.md",
            "# Discovery\n\n**Artifact bundle**: single\n\nPR-001 unreviewed rewrite\n",
        )
        rebuilt = self.run_flow("rebuild-index", succeeds=False)
        self.assertIn("canonical artifact hash is stale", rebuilt.stderr)
        resolved = self.run_flow("resolve", "--id", "PR-001", succeeds=False)
        self.assertIn("canonical artifact hash is stale", resolved.stderr)
        started = self.run_flow(
            "start", "--expect-revision", "3", "--kind", "project",
            "--work-id", "canonical", "--stage", "prd", succeeds=False,
        )
        self.assertIn("canonical artifact hash is stale", started.stderr)
        self.assertEqual(self.state()["revision"], 3)

    def test_mutators_reject_malformed_or_oversized_pointer_without_crashing(self) -> None:
        self.run_flow("init", "--project-id", "strict", "--profile", "lite")
        state_file = self.root / ".specify" / "flow-state.yaml"
        state = self.state()
        state["unknown_blob"] = "x"
        state_file.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        unknown = self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "strict", "--stage", "discovery", succeeds=False,
        )
        self.assertIn("pointer keys", unknown.stderr)

        state = self.state()
        state.pop("unknown_blob")
        state["human_gate"]["artifact_roles"] = [{}]
        state_file.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        malformed = self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "strict", "--stage", "discovery", succeeds=False,
        )
        self.assertIn("valid role strings", malformed.stderr)
        self.assertNotIn("Traceback", malformed.stderr)

        state = self.state()
        state["human_gate"]["artifact_roles"] = []
        state["evidence"] = [
            {"path": f"doc/e-{number}.md", "sha256": "a" * 64}
            for number in range(25)
        ]
        state_file.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        oversized = self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "strict", "--stage", "discovery", succeeds=False,
        )
        self.assertIn("at most 24", oversized.stderr)

    def test_validate_rejects_recommended_command_outside_allowed(self) -> None:
        self.run_flow("init", "--project-id", "safe", "--profile", "lite")
        state_file = self.root / ".specify" / "flow-state.yaml"
        state = self.state()
        state["next"] = {
            "allowed": [{"command": "one", "requires_human": True}],
            "recommended": "two",
            "auto_invoke": False,
        }
        state_file.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        invalid = self.run_flow("validate", succeeds=False)
        self.assertIn("next.recommended", invalid.stderr)

    def test_resolve_caps_large_match_sets(self) -> None:
        self.run_flow("init", "--project-id", "bounded", "--profile", "lite")
        for number in range(3):
            body = f"# Match {number}\n\nF001\n"
            if number == 0:
                body += "\n## Dependencies\n\nF001\n\n## Coverage\n\nF001\n"
            self.write(f"doc/match-{number}.md", body)
        self.run_flow("rebuild-index")
        result = self.run_flow("resolve", "--id", "F001", "--limit", "2")
        resolved = yaml.safe_load(result.stdout)
        self.assertEqual(resolved["match_count"], 3)
        self.assertTrue(resolved["truncated"])
        self.assertEqual(len(resolved["matches"]), 2)
        self.assertEqual(resolved["matches"][0]["occurrence_count"], 3)
        self.assertEqual(resolved["matches"][0]["artifact_unique_id_count"], 1)
        self.assertNotIn("id_count", resolved["matches"][0])
        self.assertEqual(len(resolved["matches"][0]["occurrences"]), 3)
        self.assertFalse(resolved["matches"][0]["occurrences_truncated"])

    def test_generic_decide_requires_authority_and_writes_indexed_receipt(self) -> None:
        self.run_flow("init", "--project-id", "receipt-demo", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "feature",
            "--work-id", "F001", "--stage", "specify",
        )
        self.write("specs/001/spec.md", "# F001 Spec\n\nReviewed candidate.\n")
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "specify",
            "--artifact", "spec=specs/001/spec.md",
        )
        candidate = self.state()
        reviewed_hash = candidate["human_gate"]["artifact_hashes"]["spec"]
        index_file = self.root / ".specify" / "artifact-index.yaml"
        index_before = yaml.safe_load(index_file.read_text("utf-8"))
        files_before = {
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*") if path.is_file()
        }

        missing_authority = self.run_flow(
            "decide", "--expect-revision", "2", "--decision", "approved",
            succeeds=False, inject_decision_authority=False,
        )
        self.assertIn("--decided-by", missing_authority.stderr)
        self.assertIn("--decision-date", missing_authority.stderr)
        self.assertIn("--decision-evidence", missing_authority.stderr)
        self.assertEqual(self.state()["revision"], 2)
        self.assertEqual(yaml.safe_load(index_file.read_text("utf-8")), index_before)
        self.assertEqual(
            files_before,
            {path.relative_to(self.root).as_posix() for path in self.root.rglob("*") if path.is_file()},
        )

        self.run_flow(
            "decide", "--expect-revision", "2", "--decision", "approved",
            "--decided-by", "Product owner", "--decision-date", "2026-08-01",
            "--decision-evidence", "user-message-1001",
        )
        approved = self.state()
        self.assertEqual(approved["active_work"]["status"], "approved")
        index_after = yaml.safe_load(index_file.read_text("utf-8"))
        before_paths = {item["path"] for item in index_before["artifacts"]}
        new_entries = [
            item for item in index_after["artifacts"] if item["path"] not in before_paths
        ]
        self.assertEqual(len(new_entries), 1, "decide must create one durable decision receipt")
        receipt_entry = new_entries[0]
        receipt_path = self.root / receipt_entry["path"]
        receipt_text = receipt_path.read_text("utf-8")
        for expected in (
            "F001", "specify", "approved", "Product owner", "2026-08-01",
            "user-message-1001", "spec", reviewed_hash,
        ):
            self.assertIn(expected, receipt_text)
        self.assertEqual(
            receipt_entry["sha256"], hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        )
        resolved = self.run_flow("resolve", "--id", "F001")
        self.assertIn(receipt_entry["path"], resolved.stdout)

        self.run_flow(
            "start", "--expect-revision", "3", "--kind", "maintenance",
            "--work-id", "MAINT-1", "--stage", "specify",
        )
        self.write("specs/maint-1/spec.md", "# MAINT-1 Spec\n\nNo behavior change.\n")
        receipt_path.write_text(receipt_text + "\n# silent edit\n", encoding="utf-8")
        revision_before_tamper_check = self.state()["revision"]
        renamed_hash_guard = self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "specify",
            "--artifact", "spec=specs/maint-1/spec.md", succeeds=False,
        )
        self.assertIn(
            "decision receipt filename does not match content hash", renamed_hash_guard.stderr
        )
        self.assertEqual(self.state()["revision"], revision_before_tamper_check)

    def test_canonical_approved_bundle_is_checked_before_record_and_decide(self) -> None:
        self.run_flow("init", "--project-id", "bundle-demo", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "bundle-demo", "--stage", "prd",
        )
        self.write("doc/requirements/domain.md", "# Domain Requirements\n\nPR-001\n")
        bundle_member = self.root / "doc" / "requirements" / "domain.md"
        valid_digest = hashlib.sha256(bundle_member.read_bytes()).hexdigest()
        self.write("doc/requirements.md", "# Requirements Index\n\nPR-001\n")
        missing_declaration = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "prd",
            "--artifact", "requirements=doc/requirements.md", succeeds=False,
        )
        self.assertIn("declare single or split", missing_declaration.stderr)
        self.assertEqual(self.state()["revision"], 1)
        root_template = (
            "# Requirements Index\n\n"
            "**Artifact bundle**: split\n\n"
            "## Domain Registry\n\n"
            "| Domain key | Detail path | Purpose |\n"
            "|---|---|---|\n"
            "| core | `doc/requirements/domain.md` | Domain requirements |\n\n"
            "## Approved Bundle\n\n"
            "| Path | SHA-256 |\n"
            "|---|---|\n"
            "| `doc/requirements/domain.md` | `{digest}` |\n"
        )
        self.write("doc/requirements/benign.md", "# Benign\n")
        benign_digest = hashlib.sha256(
            (self.root / "doc" / "requirements" / "benign.md").read_bytes()
        ).hexdigest()
        registry_mismatch = root_template.format(digest=valid_digest).replace(
            f"| `doc/requirements/domain.md` | `{valid_digest}` |",
            f"| `doc/requirements/benign.md` | `{benign_digest}` |",
        )
        self.write("doc/requirements.md", registry_mismatch)
        mismatched_registry = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "prd",
            "--artifact", "requirements=doc/requirements.md", succeeds=False,
        )
        self.assertIn("registry paths missing", mismatched_registry.stderr.lower())
        self.assertEqual(self.state()["revision"], 1)

        self.write("doc/requirements.md", root_template.format(digest="0" * 64))
        stale_at_record = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "prd",
            "--artifact", "requirements=doc/requirements.md", succeeds=False,
        )
        self.assertIn("bundle", stale_at_record.stderr.lower())
        self.assertIn("stale", stale_at_record.stderr.lower())
        self.assertEqual(self.state()["revision"], 1)

        self.write("doc/requirements.md", root_template.format(digest=valid_digest))
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "prd",
            "--artifact", "requirements=doc/requirements.md",
        )
        self.write("doc/requirements/domain.md", "# Domain Requirements\n\nPR-001 changed\n")
        stale_rebuild = self.run_flow("rebuild-index", succeeds=False)
        self.assertIn("bundle", stale_rebuild.stderr.lower())
        stale_validation = self.run_flow("validate", "--check-paths", succeeds=False)
        self.assertIn("bundle", stale_validation.stderr.lower())
        self.assertEqual(self.state()["revision"], 2)
        stale_at_decide = self.run_flow(
            "decide", "--expect-revision", "2", "--decision", "approved",
            succeeds=False,
        )
        self.assertIn("bundle", stale_at_decide.stderr.lower())
        self.assertIn("stale", stale_at_decide.stderr.lower())
        unchanged = self.state()
        self.assertEqual(unchanged["revision"], 2)
        self.assertEqual(unchanged["canonical_status"]["requirements"], "ready_for_review")

    def test_core_work_artifact_roles_are_owned_by_their_lifecycle_stages(self) -> None:
        self.run_flow("init", "--project-id", "role-owner", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "feature",
            "--work-id", "F001", "--stage", "specify",
        )
        wrong_at_specify = {
            "plan": "specs/001/plan.md",
            "tasks": "specs/001/tasks.md",
            "requirements_checklist": "specs/001/requirements.md",
            "wireframes": "specs/001/wireframes.md",
            "verification": "specs/001/verification.md",
        }
        for role, path in wrong_at_specify.items():
            with self.subTest(role=role, stage="specify"):
                self.write(path, f"# {role}\n")
                rejected = self.run_flow(
                    "record-output", "--expect-revision", "1", "--stage", "specify",
                    "--artifact", f"{role}={path}", succeeds=False,
                )
                self.assertIn(role, rejected.stderr)
                self.assertIn("stage", rejected.stderr)
                self.assertEqual(self.state()["revision"], 1)

        self.write("specs/001/spec.md", "# F001 Spec\n")
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "specify",
            "--artifact", "spec=specs/001/spec.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        self.run_flow(
            "start", "--expect-revision", "3", "--kind", "feature",
            "--work-id", "F001", "--stage", "plan",
        )
        wrong_spec = self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "plan",
            "--artifact", "spec=specs/001/spec.md", succeeds=False,
        )
        self.assertIn("spec", wrong_spec.stderr)
        self.assertIn("stage", wrong_spec.stderr)
        self.assertEqual(self.state()["revision"], 4)

    def test_pre_review_blocker_semantics_and_exact_gate_roles(self) -> None:
        self.run_flow("init", "--project-id", "pre-review", "--profile", "lite")
        pre_revision = self.prepare_work_item(expected_revision=0)
        passing_with_blocker = self.pre_review().replace(
            "## Blocking Findings\n\n- None",
            "## Blocking Findings\n\n- AC-001 conflicts with the approved plan",
        )
        self.write("specs/001/pre-implementation-review.md", passing_with_blocker)
        contradictory_pass = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision),
            "--stage", "pre_implement", "--artifact",
            "pre_implementation=specs/001/pre-implementation-review.md", succeeds=False,
        )
        self.assertIn("blocking", contradictory_pass.stderr.lower())
        self.assertEqual(self.state()["revision"], pre_revision)

        failed_alignment = self.pre_review().replace(
            "| Scope | Pass | F001 | Aligned |",
            "| Scope | Fail | F001 | Misaligned |",
        )
        self.write("specs/001/pre-implementation-review.md", failed_alignment)
        false_pass = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision),
            "--stage", "pre_implement", "--artifact",
            "pre_implementation=specs/001/pre-implementation-review.md", succeeds=False,
        )
        self.assertIn("non-ready result", false_pass.stderr.lower())

        skipped_alignment = self.pre_review().replace(
            "## Skipped Checks\n\n- None", "## Skipped Checks\n\n- UI alignment not checked"
        )
        self.write("specs/001/pre-implementation-review.md", skipped_alignment)
        skipped_pass = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision),
            "--stage", "pre_implement", "--artifact",
            "pre_implementation=specs/001/pre-implementation-review.md", succeeds=False,
        )
        self.assertIn("skipped checks", skipped_pass.stderr.lower())

        blocked_without_finding = self.pre_review("Blocked").replace(
            "## Blocking Findings\n\n- AC-001 conflict",
            "## Blocking Findings\n\n- None",
        )
        self.write("specs/001/pre-implementation-review.md", blocked_without_finding)
        contradictory_block = self.run_flow(
            "block", "--expect-revision", str(pre_revision), "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
            "--blocker", "AC-001 conflict", succeeds=False,
        )
        self.assertIn("concrete", contradictory_block.stderr.lower())
        self.assertEqual(self.state()["revision"], pre_revision)

        self.write("specs/001/pre-implementation-review.md", self.pre_review())
        self.write("specs/001/extra.md", "# Extra\n")
        extra_role = self.run_flow(
            "record-output", "--expect-revision", str(pre_revision),
            "--stage", "pre_implement",
            "--artifact", "pre_implementation=specs/001/pre-implementation-review.md",
            "--artifact", "extra=specs/001/extra.md", succeeds=False,
        )
        self.assertIn("exactly", extra_role.stderr.lower())
        self.assertEqual(self.state()["revision"], pre_revision)

    def test_acceptance_rejects_blockers_duplicate_sections_and_extra_roles(self) -> None:
        self.run_flow("init", "--project-id", "acceptance-guard", "--profile", "lite")
        acceptance_revision = self.prepare_post_implementation_candidate()
        implementer_review = self.acceptance_review().replace(
            "**Independence**: non-implementer", "**Independence**: implementer"
        )
        self.write("specs/001/acceptance.md", implementer_review)
        not_independent = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("independence", not_independent.stderr.lower())

        self.write(
            "specs/alternate/spec.md",
            "# Alternate Spec\n\n- SC-001\n- SC-002\n",
        )
        alternate_spec = self.acceptance_review().replace(
            "**Spec**: specs/001/spec.md", "**Spec**: specs/alternate/spec.md"
        )
        self.write("specs/001/acceptance.md", alternate_spec)
        wrong_spec = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("approved registered spec", wrong_spec.stderr.lower())

        with_blocker = self.acceptance_review().replace(
            "## Blockers\n\n- None", "## Blockers\n\n- SC-001 fails in production"
        )
        self.write("specs/001/acceptance.md", with_blocker)
        blocked = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("blocker", blocked.stderr.lower())

        duplicate_blockers = self.acceptance_review() + (
            "\n## Blockers\n\n- SC-001 hidden duplicate blocker\n"
        )
        self.write("specs/001/acceptance.md", duplicate_blockers)
        duplicate = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("duplicate", duplicate.stderr.lower())

        missing_scenario_evidence = self.acceptance_review().replace(
            "| SC-001 | Pass | test-output.txt | Verified |",
            "| SC-001 | Pass |  | Verified |",
        )
        self.write("specs/001/acceptance.md", missing_scenario_evidence)
        no_scenario_evidence = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("scenario evidence", no_scenario_evidence.stderr.lower())

        missing_gate = self.acceptance_review().replace(
            "| Security review | not_applicable | not_applicable | No security signal in fixed diff |\n",
            "",
        )
        self.write("specs/001/acceptance.md", missing_gate)
        incomplete_gates = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("security review gate row", incomplete_gates.stderr.lower())

        optional_tests = self.acceptance_review().replace(
            "| Tests | required | Pass | test-output.txt |",
            "| Tests | applicable | Pass | test-output.txt |",
        )
        self.write("specs/001/acceptance.md", optional_tests)
        tests_not_required = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("must be required", tests_not_required.stderr.lower())

        conditional_without_condition = self.acceptance_review().replace(
            "**Review status**: ready", "**Review status**: conditional"
        )
        self.write("specs/001/acceptance.md", conditional_without_condition)
        missing_condition = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("follow-up condition", missing_condition.stderr.lower())

        not_ready_without_blocker = self.acceptance_review().replace(
            "**Review status**: ready", "**Review status**: not_ready"
        )
        self.write("specs/001/acceptance.md", not_ready_without_blocker)
        contradictory_not_ready = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md", succeeds=False,
        )
        self.assertIn("requires a concrete blocker", contradictory_not_ready.stderr.lower())

        self.write("specs/001/acceptance.md", self.acceptance_review())
        self.write("specs/001/extra.md", "# Extra Acceptance Output\n")
        extra = self.run_flow(
            "record-output", "--expect-revision", str(acceptance_revision),
            "--stage", "acceptance", "--status", "ready_for_acceptance",
            "--artifact", "acceptance=specs/001/acceptance.md",
            "--artifact", "extra=specs/001/extra.md", succeeds=False,
        )
        self.assertIn("exactly", extra.stderr.lower())
        self.assertEqual(self.state()["revision"], acceptance_revision)

    def test_release_readiness_rejects_blockers_and_extra_roles(self) -> None:
        self.run_flow("init", "--project-id", "release-guard", "--profile", "lite")
        self.write_accepted_feature()
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "release",
            "--work-id", "REL-2026.08", "--stage", "release_readiness",
        )
        self.write("doc/releases/readiness.md", self.release_readiness())
        generic_gate_bypass = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--artifact", "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("status ready_for_release", generic_gate_bypass.stderr)
        self.assertEqual(self.state()["revision"], 1)

        implementer_review = self.release_readiness().replace(
            "**Independence**: non-implementer", "**Independence**: implementer"
        )
        self.write("doc/releases/readiness.md", implementer_review)
        not_independent = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("independence", not_independent.stderr.lower())

        with_blocker = self.release_readiness().replace(
            "## Blockers\n\n- None", "## Blockers\n\n- Rollback evidence is missing"
        )
        self.write("doc/releases/readiness.md", with_blocker)
        blocked = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("blocker", blocked.stderr.lower())

        missing_gate = self.release_readiness().replace(
            "| Code review | required | Pass | review-42 |\n", ""
        )
        self.write("doc/releases/readiness.md", missing_gate)
        incomplete_gates = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("code review gate row", incomplete_gates.stderr.lower())

        optional_build = self.release_readiness().replace(
            "| Build provenance | required | Pass | build-42 |",
            "| Build provenance | applicable | Pass | build-42 |",
        )
        self.write("doc/releases/readiness.md", optional_build)
        build_not_required = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("must be required", build_not_required.stderr.lower())

        self.write(
            "specs/999/acceptance.md",
            "# Feature Acceptance: F999\n\n"
            "**Work item**: F999\n"
            "**Human decision**: Accepted\n",
        )
        wrong_scope = self.release_readiness().replace(
            "| F001 | Accepted | specs/001/acceptance.md |",
            "| F999 | Accepted | specs/999/acceptance.md |",
        )
        self.write("doc/releases/readiness.md", wrong_scope)
        invented_acceptance = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("durable accepted feature decision", invented_acceptance.stderr.lower())

        self.write("doc/releases/readiness.md", self.release_readiness())
        self.write("doc/releases/extra.md", "# Extra Release Output\n")
        extra = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release",
            "--artifact", "release_readiness=doc/releases/readiness.md",
            "--artifact", "extra=doc/releases/extra.md", succeeds=False,
        )
        self.assertIn("exactly", extra.stderr.lower())
        self.assertEqual(self.state()["revision"], 1)

        not_ready = self.release_readiness().replace(
            "**Review status**: ready", "**Review status**: not_ready"
        ).replace(
            "## Blockers\n\n- None", "## Blockers\n\n- Rollback rehearsal failed"
        )
        self.write("doc/releases/readiness.md", not_ready)
        wrong_transition = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "release_readiness",
            "--status", "ready_for_release", "--artifact",
            "release_readiness=doc/releases/readiness.md", succeeds=False,
        )
        self.assertIn("must use block", wrong_transition.stderr.lower())
        self.run_flow(
            "block", "--expect-revision", "1", "--stage", "release_readiness",
            "--artifact", "release_readiness=doc/releases/readiness.md",
            "--blocker", "Rollback rehearsal failed",
        )
        self.assertEqual(self.state()["active_work"]["status"], "blocked")

    def test_non_feature_post_implementation_requires_verification_role(self) -> None:
        self.run_flow("init", "--project-id", "bug-review", "--profile", "lite")
        implementation_revision = self.prepare_implementation(
            kind="bug", work_id="BUG-7", directory="specs/bug-7"
        )
        self.write("specs/bug-7/notes.md", "# BUG-7 Notes\n\nNo verification report.\n")
        wrong_role = self.run_flow(
            "record-output", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement", "--status", "ready_for_review",
            "--artifact", "notes=specs/bug-7/notes.md", succeeds=False,
        )
        self.assertIn("verification", wrong_role.stderr.lower())
        self.assertEqual(self.state()["revision"], implementation_revision)

        self.write(
            "specs/bug-7/verification.md",
            self.verification_review(work_id="BUG-7", work_kind="bug"),
        )
        self.run_flow(
            "record-output", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement", "--status", "ready_for_review",
            "--artifact", "verification=specs/bug-7/verification.md",
        )
        self.run_flow(
            "decide", "--expect-revision", str(implementation_revision + 1),
            "--decision", "approved",
        )
        self.assertEqual(self.state()["active_work"]["status"], "approved")

    def test_verification_candidate_and_block_contract(self) -> None:
        self.run_flow("init", "--project-id", "verification-guard", "--profile", "lite")
        implementation_revision = self.prepare_implementation()

        complete_candidate = self.verification_review()
        required_fragments = (
            "**Work item**: F001\n",
            "**Work kind**: feature\n",
            "**Reviewed revision**: commit-abc\n",
            "**Reviewed on**: 2026-08-01\n",
            "**Candidate state**: Ready for Acceptance\n",
            "## Inputs\n",
            "## Proof Evidence\n",
            "## Tasks, Checks, and Deferrals\n",
            "## Constraint and Scope Drift\n",
            "## Coverage Batches\n",
            "## Blocking Findings\n",
            "## Skipped Checks\n",
            "## Readiness Conclusion\n",
        )
        for fragment in required_fragments:
            with self.subTest(missing=fragment.strip()):
                self.write(
                    "specs/001/verification.md",
                    complete_candidate.replace(fragment, "", 1),
                )
                incomplete = self.run_flow(
                    "record-output", "--expect-revision", str(implementation_revision),
                    "--stage", "post_implement", "--status", "ready_for_acceptance",
                    "--artifact", "verification=specs/001/verification.md",
                    succeeds=False,
                )
                expected_error = "unresolved" if fragment.startswith("**") else "missing"
                self.assertIn(expected_error, incomplete.stderr.lower())
                self.assertEqual(self.state()["revision"], implementation_revision)

        self.write(
            "specs/001/verification.md",
            self.verification_review(blocker="AC-001 still fails"),
        )
        contradictory_ready = self.run_flow(
            "record-output", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement", "--status", "ready_for_acceptance",
            "--artifact", "verification=specs/001/verification.md", succeeds=False,
        )
        self.assertIn("blocking", contradictory_ready.stderr.lower())
        self.assertEqual(self.state()["revision"], implementation_revision)

        failed_proof = self.verification_review().replace(
            "| SC-001 | targeted tests | Pass | test-output.txt |",
            "| SC-001 | targeted tests | Fail | test-output.txt |",
        )
        self.write("specs/001/verification.md", failed_proof)
        false_ready = self.run_flow(
            "record-output", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement", "--status", "ready_for_acceptance",
            "--artifact", "verification=specs/001/verification.md", succeeds=False,
        )
        self.assertIn("non-ready result", false_ready.stderr.lower())

        skipped_proof = self.verification_review().replace(
            "## Skipped Checks\n\n- None", "## Skipped Checks\n\n- Regression suite not run"
        )
        self.write("specs/001/verification.md", skipped_proof)
        skipped_ready = self.run_flow(
            "record-output", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement", "--status", "ready_for_acceptance",
            "--artifact", "verification=specs/001/verification.md", succeeds=False,
        )
        self.assertIn("skipped checks", skipped_ready.stderr.lower())

        self.write(
            "specs/001/verification.md",
            self.verification_review(candidate_state="Blocked"),
        )
        blocker_without_finding = self.run_flow(
            "block", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement",
            "--artifact", "verification=specs/001/verification.md",
            "--blocker", "AC-001 still fails", succeeds=False,
        )
        self.assertIn("concrete", blocker_without_finding.stderr.lower())
        self.assertEqual(self.state()["revision"], implementation_revision)

        self.write(
            "specs/001/verification.md",
            self.verification_review(
                candidate_state="Blocked", blocker="AC-001 still fails"
            ),
        )
        self.run_flow(
            "block", "--expect-revision", str(implementation_revision),
            "--stage", "post_implement",
            "--artifact", "verification=specs/001/verification.md",
            "--blocker", "AC-001 still fails",
        )
        blocked = self.state()
        self.assertEqual(blocked["active_work"]["status"], "blocked")
        verification = next(
            item for item in blocked["active_artifacts"]
            if item["role"] == "verification"
        )
        self.assertEqual(verification["status"], "blocked")

    def test_spike_result_requires_approved_architecture_and_exact_role(self) -> None:
        self.run_flow("init", "--project-id", "spike-guard", "--profile", "lite")
        missing_architecture = self.run_flow(
            "start", "--expect-revision", "0", "--kind", "spike",
            "--work-id", "SPK-1", "--stage", "spike_result", succeeds=False,
        )
        self.assertIn("approved architecture", missing_architecture.stderr.lower())
        self.assertEqual(self.state()["revision"], 0)

        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "spike-guard", "--stage", "architecture",
        )
        self.write(
            "doc/architecture.md",
            "# Architecture\n\n**Artifact bundle**: single\n\n"
            "## Spikes\n\n"
            "| ID | Question | Time box | Blocks | Output |\n"
            "|---|---|---|---|---|\n"
            "| SPK-1 | Can option A satisfy AC-001? | 1 day | F001 | Disposable |\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "architecture",
            "--artifact", "architecture=doc/architecture.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        undefined_spike = self.run_flow(
            "start", "--expect-revision", "3", "--kind", "spike",
            "--work-id", "SPK-999", "--stage", "spike_result", succeeds=False,
        )
        self.assertIn("define SPK-999 exactly once", undefined_spike.stderr)
        self.assertEqual(self.state()["revision"], 3)
        self.run_flow(
            "start", "--expect-revision", "3", "--kind", "spike",
            "--work-id", "SPK-1", "--stage", "spike_result",
        )

        self.write("specs/spk-1/notes.md", "# SPK-1 Notes\n\nExperiment complete.\n")
        wrong_role = self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "spike_result",
            "--artifact", "notes=specs/spk-1/notes.md", succeeds=False,
        )
        self.assertIn("spike_result", wrong_role.stderr)
        self.assertIn("exactly", wrong_role.stderr.lower())
        self.assertEqual(self.state()["revision"], 4)

        self.write(
            "specs/spk-1/spike-result.md",
            "# SPK-1 Spike Result\n\n"
            "**Work item**: SPK-1\n"
            "**Question**: Can option A satisfy AC-001?\n"
            "**Source architecture**: doc/architecture.md#spk-1\n"
            "**Time box**: 1 day\n"
            "**Investigated revision**: commit-abc\n"
            "**Investigated by**: Investigator\n"
            "**Investigated on**: 2026-08-02\n"
            "**Outcome**: answered\n\n"
            "## Evidence\n\n"
            "| Activity or command | Result | Evidence path or immutable reference |\n"
            "|---|---|---|\n"
            "| Prototype | Pass | reports/spk-1.txt |\n\n"
            "## Findings\n\nOption A remained within the measured bound.\n\n"
            "## Answer\n\nYes, for the approved boundary.\n\n"
            "## Follow-up Routing\n\nA separate CR is required before changing AC-001.\n",
        )
        spike_result_path = self.root / "specs" / "spk-1" / "spike-result.md"
        valid_spike_result = spike_result_path.read_text("utf-8")
        spike_result_path.write_text(
            valid_spike_result.replace(
                "doc/architecture.md#spk-1", "doc/missing-architecture.md#spk-1"
            ),
            encoding="utf-8",
        )
        bad_source = self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "spike_result",
            "--artifact", "spike_result=specs/spk-1/spike-result.md", succeeds=False,
        )
        self.assertIn("spike source architecture", bad_source.stderr)
        self.assertEqual(self.state()["revision"], 4)
        spike_result_path.write_text(valid_spike_result, encoding="utf-8")
        self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "spike_result",
            "--artifact", "spike_result=specs/spk-1/spike-result.md",
        )
        self.run_flow("decide", "--expect-revision", "5", "--decision", "approved")
        approved = self.state()
        self.assertEqual(approved["active_work"]["kind"], "spike")
        self.assertEqual(approved["active_work"]["stage"], "spike_result")
        self.assertEqual(approved["active_work"]["status"], "approved")
        spike_result = next(
            item for item in approved["active_artifacts"]
            if item["role"] == "spike_result"
        )
        self.assertEqual(spike_result["status"], "approved")

    def test_approved_work_cannot_be_demoted_by_block(self) -> None:
        self.run_flow("init", "--project-id", "block-guard", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "block-guard", "--stage", "discovery",
        )
        self.write(
            "doc/discovery.md",
            "# Discovery\n\n**Artifact bundle**: single\n\nReviewed truth.\n",
        )
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        rejected = self.run_flow(
            "block", "--expect-revision", "3", "--blocker", "late blocker",
            succeeds=False,
        )
        self.assertIn("in-progress", rejected.stderr.lower())
        unchanged = self.state()
        self.assertEqual(unchanged["revision"], 3)
        self.assertEqual(unchanged["active_work"]["status"], "approved")
        self.assertEqual(unchanged["canonical_status"]["discovery"], "approved")

    def test_pointer_and_index_reject_boolean_and_unknown_schema_values(self) -> None:
        self.run_flow("init", "--project-id", "schema-guard", "--profile", "lite")
        state_file = self.root / ".specify" / "flow-state.yaml"
        original_state = self.state()
        malformed_state = self.state()
        malformed_state["schema_version"] = True
        malformed_state["revision"] = True
        state_file.write_text(yaml.safe_dump(malformed_state, sort_keys=False), encoding="utf-8")
        invalid_pointer = self.run_flow("validate", succeeds=False)
        self.assertIn("schema_version", invalid_pointer.stderr)
        self.assertIn("revision", invalid_pointer.stderr)
        self.assertNotIn("Traceback", invalid_pointer.stderr)

        state_file.write_text(yaml.safe_dump(original_state, sort_keys=False), encoding="utf-8")
        index_file = self.root / ".specify" / "artifact-index.yaml"
        index = yaml.safe_load(index_file.read_text("utf-8"))
        index["unknown"] = "not allowed"
        index_file.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
        index_digest_file = self.root / ".specify" / "artifact-index.sha256"
        index_digest_file.write_text(
            hashlib.sha256(index_file.read_bytes()).hexdigest() + "\n", encoding="utf-8"
        )
        unknown_index = self.run_flow("validate", "--check-paths", succeeds=False)
        self.assertIn("keys", unknown_index.stderr.lower())
        unsafe_resolve = self.run_flow("resolve", "--path", "doc", succeeds=False)
        self.assertIn("structurally unsafe", unsafe_resolve.stderr)

        index.pop("unknown")
        index["schema_version"] = True
        index["artifact_count"] = False
        index_file.write_text(yaml.safe_dump(index, sort_keys=False), encoding="utf-8")
        index_digest_file.write_text(
            hashlib.sha256(index_file.read_bytes()).hexdigest() + "\n", encoding="utf-8"
        )
        boolean_index = self.run_flow("validate", "--check-paths", succeeds=False)
        self.assertIn("schema_version", boolean_index.stderr)
        self.assertIn("artifact_count", boolean_index.stderr)
        self.assertNotIn("Traceback", boolean_index.stderr)

    # ------------------------------------------------------------------
    # Contract tests for the stable CLI entry that every SKILL.md cites.
    # These pin the behaviour the compressed skill bodies now rely on.
    # ------------------------------------------------------------------

    def run_entry(
        self, script: Path, *args: str, cwd: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        """Invoke a script path directly with no inherited PYTHONPATH."""
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        return subprocess.run(
            [sys.executable, "-B", str(script), "--root", str(self.root), *args],
            text=True,
            capture_output=True,
            check=False,
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
        )

    def test_entry_runs_standalone_from_any_cwd_without_pythonpath(self) -> None:
        """Skills call the absolute script path. Nothing may depend on the
        repository root, the caller's working directory, or PYTHONPATH."""
        self.run_flow("init", "--project-id", "standalone", "--profile", "lite")
        neutral = tempfile.TemporaryDirectory()
        self.addCleanup(neutral.cleanup)
        result = self.run_entry(SCRIPT, "status", cwd=neutral.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("standalone", result.stdout)

    def test_deployed_skill_directory_invocation_is_self_contained(self) -> None:
        """Deploy-Skills.ps1 copies each skill folder recursively into a tool
        skills directory. The copied tree must run without the repository."""
        deployed_parent = tempfile.TemporaryDirectory()
        self.addCleanup(deployed_parent.cleanup)
        deployed_skill = Path(deployed_parent.name) / "flow-state"
        shutil.copytree(
            SCRIPT.resolve().parents[1],
            deployed_skill,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        deployed_script = deployed_skill / "scripts" / "flow_state.py"
        self.assertTrue(deployed_script.is_file())
        result = self.run_entry(
            deployed_script, "init", "--project-id", "deployed", "--profile", "lite",
            cwd=deployed_parent.name,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / ".specify" / "flow-state.yaml").is_file())

    def test_stale_revision_reports_current_value_and_writes_nothing(self) -> None:
        """The revision placeholder contract depends on compare-and-swap
        rejecting a guessed revision with an actionable current value."""
        self.run_flow("init", "--project-id", "cas", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "cas", "--stage", "discovery",
        )
        self.write("doc/discovery.md", "# Discovery\n\n**Artifact bundle**: single\n\nPR-001\n")
        before = self.state()
        stale = self.run_flow(
            "record-output", "--expect-revision", "7", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md", succeeds=False,
        )
        self.assertIn("stale revision: expected 7, current 1", stale.stderr)
        self.assertEqual(self.state(), before)
        # A rejected call must not consume the revision it failed against.
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.assertEqual(self.state()["revision"], 2)

    def test_check_only_validates_without_writing_state(self) -> None:
        """--check-only pre-flights a transition so a skill avoids the
        write/fail/rewrite loop. It must never consume a revision."""
        self.run_flow("init", "--project-id", "preflight", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "preflight", "--stage", "discovery",
        )
        self.write("doc/discovery.md", "# Discovery\n\n**Artifact bundle**: single\n\nPR-001\n")
        before = self.state()

        accepted = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md", "--check-only",
        )
        self.assertIn("check-only", accepted.stdout)
        self.assertIn("discovery", accepted.stdout)
        # Must not look like a completed write that returned a new revision.
        self.assertNotEqual(accepted.stdout.strip(), "2")
        self.assertEqual(self.state(), before)

        self.write("doc/undeclared.md", "# Discovery\n\nPR-001\n")
        rejected = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/undeclared.md", "--check-only", succeeds=False,
        )
        self.assertIn("declare single or split", rejected.stderr)
        self.assertEqual(self.state(), before)

        # The real write still succeeds at the revision the check used.
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.assertEqual(self.state()["revision"], 2)
        self.assertEqual(self.state()["human_gate"]["status"], "pending")

    def test_sync_bundle_writes_current_member_hashes(self) -> None:
        """A skill must never transcribe a SHA-256 by hand: sync-bundle owns
        the Approved Bundle table end to end and preserves section prose."""
        self.run_flow("init", "--project-id", "bundle-sync", "--profile", "lite")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "bundle-sync", "--stage", "prd",
        )
        self.write("doc/requirements/core.md", "# Core Requirements\n\nPR-001\n")
        self.write(
            "doc/requirements.md",
            "# Requirements Index\n\n"
            "**Artifact bundle**: split\n\n"
            "## Domain Registry\n\n"
            "| Domain key | Detail path | Purpose |\n"
            "|---|---|---|\n"
            "| core | `doc/requirements/core.md` | Core requirements |\n\n"
            "## Approved Bundle\n\n"
            "This table is the complete set of external files owned by this root.\n\n"
            "| Path | SHA-256 |\n"
            "|---|---|\n"
            f"| `doc/requirements/core.md` | `{'0' * 64}` |\n",
        )
        stale = self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "prd",
            "--artifact", "requirements=doc/requirements.md", succeeds=False,
        )
        self.assertIn("stale", stale.stderr.lower())

        self.run_flow(
            "sync-bundle", "--artifact", "doc/requirements.md",
            "--member", "doc/requirements/core.md", "--role", "requirements",
        )
        synced = (self.root / "doc" / "requirements.md").read_text("utf-8")
        expected = hashlib.sha256(
            (self.root / "doc" / "requirements" / "core.md").read_bytes()
        ).hexdigest()
        self.assertIn(expected, synced)
        self.assertNotIn("0" * 64, synced)
        self.assertIn("This table is the complete set", synced)
        self.assertIn("## Domain Registry", synced)
        # sync-bundle is a file operation only; it never moves the pointer.
        self.assertEqual(self.state()["revision"], 1)

        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "prd",
            "--artifact", "requirements=doc/requirements.md",
        )

        # A changed member re-syncs without the caller handling digests.
        self.write("doc/requirements/core.md", "# Core Requirements\n\nPR-001 revised\n")
        self.run_flow(
            "sync-bundle", "--artifact", "doc/requirements.md",
            "--member", "doc/requirements/core.md", "--role", "requirements",
        )
        resynced = (self.root / "doc" / "requirements.md").read_text("utf-8")
        self.assertIn(
            hashlib.sha256(
                (self.root / "doc" / "requirements" / "core.md").read_bytes()
            ).hexdigest(),
            resynced,
        )

        # Guard rails: single roots have no table, and the root is not a member.
        self.write("doc/discovery.md", "# Discovery\n\n**Artifact bundle**: single\n\nPR-001\n")
        single = self.run_flow(
            "sync-bundle", "--artifact", "doc/discovery.md",
            "--member", "doc/requirements/core.md", succeeds=False,
        )
        self.assertIn("split", single.stderr)
        self_member = self.run_flow(
            "sync-bundle", "--artifact", "doc/requirements.md",
            "--member", "doc/requirements.md", succeeds=False,
        )
        self.assertIn("root", self_member.stderr.lower())

    def test_sync_bundle_restores_the_root_when_the_result_is_invalid(self) -> None:
        """A registry/bundle disagreement must leave the root byte-identical
        rather than half-written."""
        self.run_flow("init", "--project-id", "bundle-guard", "--profile", "lite")
        self.write("doc/requirements/core.md", "# Core Requirements\n\nPR-001\n")
        self.write("doc/requirements/extra.md", "# Extra Requirements\n\nPR-002\n")
        self.write(
            "doc/requirements.md",
            "# Requirements Index\n\n"
            "**Artifact bundle**: split\n\n"
            "## Domain Registry\n\n"
            "| Domain key | Detail path | Purpose |\n"
            "|---|---|---|\n"
            "| core | `doc/requirements/core.md` | Core requirements |\n\n"
            "## Approved Bundle\n\n"
            "| Path | SHA-256 |\n"
            "|---|---|\n"
            f"| `doc/requirements/core.md` | `{'0' * 64}` |\n",
        )
        before = (self.root / "doc" / "requirements.md").read_text("utf-8")
        mismatch = self.run_flow(
            "sync-bundle", "--artifact", "doc/requirements.md",
            "--member", "doc/requirements/core.md",
            "--member", "doc/requirements/extra.md",
            "--role", "requirements", succeeds=False,
        )
        self.assertIn("registr", mismatch.stderr.lower())
        self.assertIn("restored unchanged", mismatch.stderr)
        self.assertEqual((self.root / "doc" / "requirements.md").read_text("utf-8"), before)


if __name__ == "__main__":
    unittest.main()
