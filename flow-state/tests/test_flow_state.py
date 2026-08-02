from __future__ import annotations

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

    def run_flow(self, *args: str, succeeds: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *args],
            text=True,
            capture_output=True,
            check=False,
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
            f"## Blocking Findings\n\n- {blocker}\n\n"
            "## Advisory Findings\n\n- None\n\n"
            "## Skipped Checks\n\n- None\n\n"
            f"## Outcome Rationale\n\nConcrete review rationale.\n{suffix}"
        )

    def acceptance_review(self) -> str:
        return (
            "# Feature Acceptance: F001\n\n"
            "**Work item**: F001\n"
            "**Review status**: ready\n"
            "**Human decision**: {{PENDING_OR_DECISION}}\n"
            "**Decided by**: {{PENDING_OR_ACTOR}}\n"
            "**Decision date**: {{PENDING_OR_DATE}}\n"
            "**Decision evidence**: {{PENDING_OR_REFERENCE}}\n"
            "**Spec**: specs/001/spec.md\n"
            "**Implementation revision**: commit-abc\n\n"
            "## Scenario Evidence\n\n"
            "| Scenario | Result | Evidence | Notes |\n"
            "|---|---|---|---|\n"
            "| SC-001 | Pass | test-output.txt | Verified |\n\n"
            "## Applicable Quality Gates\n\n"
            "| Gate | Applicability | Result | Evidence / reason |\n"
            "|---|---|---|---|\n"
            "| Tests | required | Pass | test-output.txt |\n\n"
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
            "**Human readiness decision**: {{PENDING_OR_DECISION}}\n"
            "**Authorization evidence**: {{PENDING_OR_REFERENCE}}\n"
            "**Authorized by**: {{PENDING_OR_ACTOR}}\n"
            "**Authorized on**: {{PENDING_OR_DATE}}\n"
            "**Scope**: F001\n"
            "**Artifact revision**: build-sha-abc\n\n"
            "## Included Acceptance Decisions\n\n"
            "| Feature | Human decision | Evidence |\n"
            "|---|---|---|\n"
            "| F001 | Accepted | specs/001/acceptance.md |\n\n"
            "## Release Gates\n\n"
            "| Gate | Applicability | Result | Evidence / reason |\n"
            "|---|---|---|---|\n"
            "| Build provenance | required | Pass | build-42 |\n\n"
            "## Blockers\n\n- None\n\n"
            "## Deferred Items\n\n"
            "| Type | ID | Disposition | Owner |\n"
            "|---|---|---|---|\n"
            "| None | N/A | None | N/A |\n\n"
            "## Release Execution Result\n\n"
            "**Execution**: {{PENDING_OR_RESULT}}\n"
            "**Execution evidence**: {{PENDING_OR_EVIDENCE}}\n"
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

    def prepare_work_item(
        self, *, expected_revision: int, kind: str = "feature",
        work_id: str = "F001", directory: str = "specs/001",
    ) -> int:
        self.run_flow(
            "start", "--expect-revision", str(expected_revision), "--kind", kind,
            "--work-id", work_id, "--stage", "specify",
        )
        self.write(f"{directory}/spec.md", f"# Spec {work_id}\n")
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

    def test_human_gates_profile_and_feature_acceptance(self) -> None:
        self.run_flow("init", "--project-id", "WMS", "--profile", "full")
        self.run_flow(
            "start", "--expect-revision", "0", "--kind", "project",
            "--work-id", "WMS", "--stage", "discovery",
        )
        self.write("doc/discovery.md", "# Discovery\n\nF001 PR-001\n")
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
            "# Roadmap\n\n**Profile sizing**: full\n"
            "**Sizing evidence**: 12 features; 2 deployables; 2 teams\n\n"
            "F001 owns PR-001\n",
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
        self.write("specs/001/verification.md", "# Verification\n")
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

        resolved = self.run_flow("resolve", "--id", "F001")
        self.assertIn("doc/roadmap.md", resolved.stdout)
        self.run_flow("validate", "--check-paths")

    def test_release_requires_authorization_then_confirmed_execution(self) -> None:
        self.run_flow("init", "--project-id", "release-demo", "--profile", "lite")
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
        immutable = self.run_flow(
            "start", "--expect-revision", "4", "--kind", "release",
            "--work-id", "REL-2026.08", "--stage", "release_readiness", succeeds=False,
        )
        self.assertIn("immutable", immutable.stderr)
        resolved = self.run_flow("resolve", "--id", "REL-2026.08")
        self.assertIn("REL-2026.08-readiness.md", resolved.stdout)
        self.run_flow("validate", "--check-paths")

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
        self.assertIn("structurally unsafe", unsafe.stderr)
        invalid = self.run_flow("validate", "--check-paths", succeeds=False)
        self.assertIn("artifact index", invalid.stderr)

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
        self.write("doc/discovery.md", "# Discovery\n\nOriginal truth\n")
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
        self.write("doc/discovery.md", "# Discovery\n\nProposed truth\n")
        direct = self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "change_request",
            "--artifact", "product_amendment=doc/product-amendments/CR-0001.md",
            "--artifact", "discovery=doc/discovery.md", succeeds=False,
        )
        self.assertIn("reviewed change-request", direct.stderr)
        self.write("doc/discovery.md", "# Discovery\n\nOriginal truth\n")
        self.run_flow(
            "record-output", "--expect-revision", "4", "--stage", "change_request",
            "--artifact", "product_amendment=doc/product-amendments/CR-0001.md",
        )
        self.write("doc/discovery.md", "# Discovery\n\nApproved amended truth\n")
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
            "**Work item**: F001\n**Review result**: Pass\n"
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
            self.pre_review().replace("F001", "BUG-7").replace("specs/001/", "specs/bug-7/"),
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
        self.write("specs/bug-7/verification.md", "# BUG-7 Verification\n\nRegression passes.\n")
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
        self.write("doc/discovery.md", "# Discovery\n\nPR-001 original\n")
        self.run_flow(
            "record-output", "--expect-revision", "1", "--stage", "discovery",
            "--artifact", "discovery=doc/discovery.md",
        )
        self.run_flow("decide", "--expect-revision", "2", "--decision", "approved")
        self.write("doc/discovery.md", "# Discovery\n\nPR-001 unreviewed rewrite\n")
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
            self.write(f"doc/match-{number}.md", f"# Match {number}\n\nF001\n")
        self.run_flow("rebuild-index")
        result = self.run_flow("resolve", "--id", "F001", "--limit", "2")
        resolved = yaml.safe_load(result.stdout)
        self.assertEqual(resolved["match_count"], 3)
        self.assertTrue(resolved["truncated"])
        self.assertEqual(len(resolved["matches"]), 2)


if __name__ == "__main__":
    unittest.main()
