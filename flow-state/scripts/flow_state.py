#!/usr/bin/env python3
"""Deterministic human-gated workflow pointer and artifact index utility."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date as calendar_date
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment-specific
    print("flow-state requires PyYAML: python -m pip install PyYAML", file=sys.stderr)
    raise SystemExit(2)


SCHEMA_VERSION = 1
KINDS = {
    "project",
    "feature",
    "bug",
    "maintenance",
    "spike",
    "migration",
    "security",
    "change_request",
    "release",
}
STATUSES = {
    "not_started",
    "in_progress",
    "ready_for_review",
    "approved",
    "blocked",
    "ready_for_acceptance",
    "accepted",
    "ready_for_release",
    "release_authorized",
    "released",
    "rejected",
}
CANDIDATE_STATUSES = {"ready_for_review", "ready_for_acceptance", "ready_for_release"}
GATE_STATUSES = {"not_required", "pending", "approved", "rejected"}
PROFILE_STATUSES = {"provisional", "confirmed"}
PROJECT_CANONICAL_KEYS = {
    "discovery",
    "requirements",
    "roadmap",
    "architecture",
    "agent_guidance",
    "ui_structure",
    "artifact_index",
}
PROJECT_ARTIFACT_KEYS = PROJECT_CANONICAL_KEYS - {"artifact_index"}
SEMANTIC_CANONICAL_KEYS = {"discovery", "requirements", "roadmap", "architecture"}
BUNDLE_DECLARATION_ROLES = SEMANTIC_CANONICAL_KEYS | {"ui_structure"}
ARTIFACT_STATUSES = STATUSES | {"derived"}
ACTIVE_ARTIFACT_LIMIT = 24
CONTEXT_ID_LIMIT = 32
EVIDENCE_LIMIT = 24
BLOCKER_LIMIT = 20
NEXT_ACTION_LIMIT = 8
POINTER_TEXT_LIMIT = 500
ROLE_TEXT_LIMIT = 64
POINTER_FILE_SIZE_LIMIT = 32 * 1024
INDEX_FILE_SIZE_LIMIT = 16 * 1024 * 1024
RESOLVE_OUTPUT_BYTE_LIMIT = 16 * 1024
RESOLVE_OCCURRENCE_LIMIT = 12
STATE_KEYS = {
    "schema_version",
    "revision",
    "project",
    "active_work",
    "human_gate",
    "canonical",
    "canonical_status",
    "canonical_hashes",
    "active_artifacts",
    "context_ids",
    "next",
    "evidence",
    "blockers",
    "last_transition",
}
ID_PATTERN = re.compile(
    r"\b(?:PR-\d+|F-?\d+|AC-\d+|ADR-\d+|CR-\d+|TD-\d+|SC-\d+|T-\d+|SM-\d+|BUG-\d+|MAINT-\d+|MIG-\d+|SEC-\d+|SPK-\d+|REL-[A-Z0-9._-]+)\b",
    re.IGNORECASE,
)
ROLE_PATTERN = re.compile(r"[a-z][a-z0-9_-]*")
AMENDMENT_ROLES = {"product_amendment", "architecture_amendment", "change_request"}
SPECIAL_DECISION_RECEIPT_TYPES = {
    "feature_acceptance_decision",
    "release_authorization",
    "release_result",
}
IMPLEMENTATION_KINDS = {"feature", "bug", "maintenance", "migration", "security"}
CANONICAL_ROLE_STAGES = {
    "discovery": "discovery",
    "requirements": "prd",
    "roadmap": "roadmap",
    "architecture": "architecture",
    "agent_guidance": "agent_guidance",
    "ui_structure": "product_ui",
}
REFRESHABLE_CANONICAL_ROLES = {"agent_guidance", "ui_structure"}
WORK_ROLE_STAGES = {
    "spec": {"specify"},
    "wireframes": {"feature_ui"},
    "plan": {"plan"},
    "tasks": {"plan"},
    "requirements_checklist": {"plan"},
    "verification": {"post_implement"},
    "spike_result": {"spike_result"},
}
STAGE_KINDS = {
    "discovery": {"project"},
    "prd": {"project"},
    "roadmap": {"project"},
    "architecture": {"project", "change_request"},
    "agent_guidance": {"project", "change_request"},
    "product_ui": {"project", "change_request"},
    "specify": {"feature", "bug", "maintenance", "migration", "security"},
    "feature_ui": {"feature"},
    "plan": {"feature", "bug", "maintenance", "migration", "security"},
    "pre_implement": IMPLEMENTATION_KINDS,
    "implementation": {"feature", "bug", "maintenance", "migration", "security"},
    "post_implement": IMPLEMENTATION_KINDS,
    "acceptance": {"feature"},
    "change_request": {"change_request"},
    "release_readiness": {"release"},
    "spike_result": {"spike"},
}
NON_STARTABLE_STAGES = {"post_implement", "acceptance"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def pointer_path(root: Path) -> Path:
    return root / ".specify" / "flow-state.yaml"


def index_path(root: Path) -> Path:
    return root / ".specify" / "artifact-index.yaml"


def index_digest_path(root: Path) -> Path:
    return root / ".specify" / "artifact-index.sha256"


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing file: {path}")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"invalid YAML in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected a YAML mapping in {path}")
    return value


def read_state(root: Path) -> dict[str, Any]:
    path = pointer_path(root)
    if path.is_file() and path.stat().st_size > POINTER_FILE_SIZE_LIMIT:
        fail(f"workflow pointer exceeds {POINTER_FILE_SIZE_LIMIT} bytes")
    return read_yaml(path)


def read_index(root: Path) -> dict[str, Any]:
    path = index_path(root)
    if path.is_file() and path.stat().st_size > INDEX_FILE_SIZE_LIMIT:
        fail(
            f"artifact index exceeds {INDEX_FILE_SIZE_LIMIT} bytes; split large domain artifacts/indexes"
        )
    if not path.is_file():
        fail(f"missing file: {path}")
    digest_path = index_digest_path(root)
    if not digest_path.is_file():
        fail("artifact index digest is missing; run rebuild-index")
    recorded_digest = digest_path.read_text(encoding="utf-8").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", recorded_digest):
        fail("artifact index digest is invalid; run rebuild-index")
    if sha256_file(path) != recorded_digest:
        fail("artifact index digest mismatch; run rebuild-index")
    return read_yaml(path)


def bounded_text(value: Any, *, allow_none: bool = False) -> bool:
    if value is None:
        return allow_none
    return (
        isinstance(value, str)
        and bool(value)
        and len(value) <= POINTER_TEXT_LIMIT
        and "\n" not in value
        and "\r" not in value
    )


def atomic_write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=1000)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def state_template(project_id: str, profile: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "revision": 0,
        "project": {"id": project_id, "profile": profile, "profile_status": "provisional"},
        "active_work": {
            "kind": "project",
            "id": project_id,
            "stage": "discovery",
            "status": "not_started",
        },
        "human_gate": {
            "name": "start_discovery",
            "status": "pending",
            "owner": "human",
            "artifact_roles": [],
            "artifact_hashes": {},
        },
        "canonical": {
            "discovery": None,
            "requirements": None,
            "roadmap": None,
            "architecture": None,
            "agent_guidance": None,
            "ui_structure": None,
            "artifact_index": ".specify/artifact-index.yaml",
        },
        "canonical_status": {
            "discovery": "not_started",
            "requirements": "not_started",
            "roadmap": "not_started",
            "architecture": "not_started",
            "agent_guidance": "not_started",
            "ui_structure": "not_started",
        },
        "canonical_hashes": {
            "discovery": None,
            "requirements": None,
            "roadmap": None,
            "architecture": None,
            "agent_guidance": None,
            "ui_structure": None,
        },
        "active_artifacts": [],
        "context_ids": [],
        "next": {"allowed": [], "recommended": None, "auto_invoke": False},
        "evidence": [],
        "blockers": [],
        "last_transition": None,
    }


def validate_state(state: dict[str, Any], root: Path, check_paths: bool) -> list[str]:
    errors: list[str] = []
    if set(state) != STATE_KEYS:
        errors.append(
            f"pointer keys must exactly match schema; missing={sorted(STATE_KEYS - set(state))}, "
            f"unknown={sorted(set(state) - STATE_KEYS)}"
        )
    if type(state.get("schema_version")) is not int or state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if type(state.get("revision")) is not int or state.get("revision", -1) < 0:
        errors.append("revision must be a non-negative integer")
    project = state.get("project")
    if not isinstance(project, dict) or set(project) != {"id", "profile", "profile_status"}:
        errors.append("project must contain exactly id, profile, and profile_status")
    elif not bounded_text(project.get("id")):
        errors.append("project.id must be a bounded single-line string")
    elif project.get("profile") not in {"full", "lite"}:
        errors.append("project.profile must be full or lite")
    elif project.get("profile_status") not in PROFILE_STATUSES:
        errors.append(f"project.profile_status must be one of {sorted(PROFILE_STATUSES)}")
    active = state.get("active_work")
    if not isinstance(active, dict) or set(active) != {"kind", "id", "stage", "status"}:
        errors.append("active_work must contain exactly kind, id, stage, and status")
    else:
        if active.get("kind") not in KINDS:
            errors.append(f"active_work.kind must be one of {sorted(KINDS)}")
        if not bounded_text(active.get("id")):
            errors.append("active_work.id must be a bounded single-line string")
        if not bounded_text(active.get("stage")):
            errors.append("active_work.stage must be a bounded single-line string")
        elif active.get("stage") not in STAGE_KINDS:
            errors.append(f"active_work.stage must be one of {sorted(STAGE_KINDS)}")
        elif active.get("kind") in KINDS and active.get("kind") not in STAGE_KINDS[active["stage"]]:
            errors.append(
                f"active_work.stage {active['stage']} is not valid for kind {active.get('kind')}"
            )
        if active.get("status") not in STATUSES:
            errors.append(f"active_work.status must be one of {sorted(STATUSES)}")
    gate = state.get("human_gate")
    gate_roles_list: list[Any] = []
    gate_hashes: dict[str, Any] = {}
    if not isinstance(gate, dict) or set(gate) != {
        "name", "status", "owner", "artifact_roles", "artifact_hashes"
    }:
        errors.append(
            "human_gate must contain exactly name, status, owner, artifact_roles, and artifact_hashes"
        )
    else:
        if not bounded_text(gate.get("name")):
            errors.append("human_gate.name must be a bounded single-line string")
        if gate.get("owner") != "human":
            errors.append("human_gate.owner must be human")
        if gate.get("status") not in GATE_STATUSES:
            errors.append(f"human_gate.status must be one of {sorted(GATE_STATUSES)}")
        if not isinstance(gate.get("artifact_roles"), list):
            errors.append("human_gate.artifact_roles must be a list")
        else:
            gate_roles_list = gate["artifact_roles"]
            if any(
                not isinstance(role, str)
                or len(role) > ROLE_TEXT_LIMIT
                or not ROLE_PATTERN.fullmatch(role)
                for role in gate_roles_list
            ):
                errors.append("human_gate.artifact_roles must contain valid role strings")
            if len(gate_roles_list) != len(set(role for role in gate_roles_list if isinstance(role, str))):
                errors.append("human_gate.artifact_roles must not contain duplicates")
        if not isinstance(gate.get("artifact_hashes"), dict):
            errors.append("human_gate.artifact_hashes must be a mapping")
        else:
            gate_hashes = gate["artifact_hashes"]
    next_value = state.get("next")
    if not isinstance(next_value, dict) or set(next_value) != {
        "allowed", "recommended", "auto_invoke"
    }:
        errors.append("next must contain exactly allowed, recommended, and auto_invoke")
    elif next_value.get("auto_invoke") is not False:
        errors.append("next.auto_invoke must be false")
    elif not isinstance(next_value.get("allowed"), list) or any(
        not isinstance(item, dict) or item.get("requires_human") is not True
        for item in next_value.get("allowed", [])
    ):
        errors.append("every next.allowed item must require human authorization")
    else:
        if any(set(item) != {"command", "requires_human"} for item in next_value["allowed"]):
            errors.append("every next.allowed item must contain exactly command and requires_human")
        allowed_commands = [item.get("command") for item in next_value.get("allowed", [])]
        if len(allowed_commands) > NEXT_ACTION_LIMIT:
            errors.append(f"next.allowed must contain at most {NEXT_ACTION_LIMIT} commands")
        if any(not isinstance(command, str) or not command for command in allowed_commands):
            errors.append("every next.allowed item must contain a non-empty command")
        elif any(
            len(command) > POINTER_TEXT_LIMIT or "\n" in command or "\r" in command
            for command in allowed_commands
        ):
            errors.append(
                f"next.allowed commands must be single-line and at most {POINTER_TEXT_LIMIT} characters"
            )
        recommended = next_value.get("recommended")
        if recommended is not None and recommended not in allowed_commands:
            errors.append("next.recommended must be null or one of next.allowed commands")
    canonical = state.get("canonical")
    if not isinstance(canonical, dict):
        errors.append("canonical must be a mapping")
    else:
        if set(canonical) != PROJECT_CANONICAL_KEYS:
            errors.append("canonical keys must exactly match the canonical schema")
        for key, raw_path in canonical.items():
            if raw_path is not None and not bounded_text(raw_path):
                errors.append(f"canonical.{key} must be null or a bounded single-line path")
        if check_paths:
            for key, raw_path in canonical.items():
                if raw_path is None:
                    continue
                try:
                    _normalized, resolved = resolve_repo_path(root, raw_path)
                except ValueError as exc:
                    errors.append(f"canonical.{key}: {exc}")
                    continue
                if not resolved.is_file():
                    errors.append(f"canonical.{key} does not exist: {raw_path}")
    canonical_status = state.get("canonical_status")
    if not isinstance(canonical_status, dict):
        errors.append("canonical_status must be a mapping")
    else:
        if set(canonical_status) != PROJECT_ARTIFACT_KEYS:
            errors.append("canonical_status keys must exactly match semantic canonical keys")
        for key in PROJECT_ARTIFACT_KEYS:
            if canonical_status.get(key) not in ARTIFACT_STATUSES:
                errors.append(f"canonical_status.{key} must be a known artifact status")
    canonical_hashes = state.get("canonical_hashes")
    if not isinstance(canonical_hashes, dict):
        errors.append("canonical_hashes must be a mapping")
    else:
        if set(canonical_hashes) != PROJECT_ARTIFACT_KEYS:
            errors.append("canonical_hashes keys must equal canonical semantic artifact keys")
        for key in PROJECT_ARTIFACT_KEYS:
            digest = canonical_hashes.get(key)
            if digest is not None and (
                not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            ):
                errors.append(f"canonical_hashes.{key} must be null or sha256")
            raw_path = canonical.get(key) if isinstance(canonical, dict) else None
            status = canonical_status.get(key) if isinstance(canonical_status, dict) else None
            if status == "not_started":
                if raw_path is not None or digest is not None:
                    errors.append(
                        f"canonical.{key} path/hash must be null while status is not_started"
                    )
            elif not raw_path or digest is None:
                errors.append(
                    f"canonical.{key} requires both path and hash while status is {status}"
                )
            if check_paths and raw_path and digest:
                try:
                    _normalized, resolved = resolve_repo_path(root, raw_path)
                except ValueError:
                    continue
                if resolved.is_file() and sha256_file(resolved) != digest:
                    errors.append(f"canonical artifact hash is stale: {raw_path}")
                elif resolved.is_file() and status != "not_started":
                    errors.extend(
                        f"canonical.{key} bundle: {error}"
                        for error in validate_approved_bundle(
                            resolved,
                            root,
                            role=key,
                            require_declaration=key in BUNDLE_DECLARATION_ROLES,
                        )
                    )
    active_artifacts = state.get("active_artifacts")
    if not isinstance(active_artifacts, list) or len(active_artifacts) > ACTIVE_ARTIFACT_LIMIT:
        errors.append(f"active_artifacts must be a list with at most {ACTIVE_ARTIFACT_LIMIT} items")
    else:
        seen_roles: set[str] = set()
        for item in active_artifacts:
            if (
                not isinstance(item, dict)
                or set(item) != {"role", "path", "status", "sha256"}
                or not item.get("role")
                or not item.get("path")
                or item.get("status") not in ARTIFACT_STATUSES
                or not isinstance(item.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", ""))
            ):
                errors.append(
                    "every active_artifacts item must contain role, path, status, and sha256"
                )
                continue
            role = item["role"]
            if (
                not isinstance(role, str)
                or len(role) > ROLE_TEXT_LIMIT
                or not ROLE_PATTERN.fullmatch(role)
            ):
                errors.append("active artifact roles must match the role pattern")
            elif role in seen_roles:
                errors.append(f"active_artifacts contains duplicate role: {role}")
            if isinstance(role, str) and len(role) <= ROLE_TEXT_LIMIT and ROLE_PATTERN.fullmatch(role):
                seen_roles.add(role)
            if not bounded_text(item["path"]):
                errors.append(f"active artifact path is not bounded: {role}")
            if check_paths:
                try:
                    _normalized, resolved = resolve_repo_path(root, item["path"])
                except ValueError as exc:
                    errors.append(f"active_artifacts.{item.get('role')}: {exc}")
                    continue
                if not resolved.is_file():
                    errors.append(f"active artifact does not exist: {item['path']}")
                elif sha256_file(resolved) != item["sha256"]:
                    errors.append(f"active artifact hash is stale: {item['path']}")
    gate_roles = {
        role for role in gate_roles_list if isinstance(role, str) and ROLE_PATTERN.fullmatch(role)
    }
    active_roles = {
        item.get("role")
        for item in active_artifacts
        if isinstance(item, dict) and isinstance(item.get("role"), str) and item.get("role")
    } if isinstance(active_artifacts, list) else set()
    unknown_gate_roles = gate_roles - PROJECT_ARTIFACT_KEYS - active_roles
    if unknown_gate_roles:
        errors.append(f"human_gate references unknown artifact roles: {sorted(unknown_gate_roles)}")
    if set(gate_hashes) != gate_roles:
        errors.append("human_gate.artifact_hashes keys must equal artifact_roles")
    elif any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
        for value in gate_hashes.values()
    ):
        errors.append("human_gate.artifact_hashes values must be sha256 strings")
    elif check_paths:
        for role in sorted(gate_roles):
            role_path = artifact_role_path(state, role)
            if not role_path:
                errors.append(f"human_gate role has no artifact path: {role}")
                continue
            try:
                _normalized, resolved = resolve_repo_path(root, role_path)
            except ValueError as exc:
                errors.append(f"human_gate.{role}: {exc}")
                continue
            if not resolved.is_file():
                errors.append(f"human_gate artifact does not exist: {role_path}")
            elif sha256_file(resolved) != gate_hashes[role]:
                errors.append(f"human_gate artifact hash is stale: {role_path}")
    context_ids = state.get("context_ids")
    if not isinstance(context_ids, list):
        errors.append("context_ids must be a list")
    elif len(context_ids) > CONTEXT_ID_LIMIT:
        errors.append(f"context_ids must contain at most {CONTEXT_ID_LIMIT} IDs")
    elif any(not isinstance(value, str) or not ID_PATTERN.fullmatch(value) for value in context_ids):
        errors.append("every context_ids value must be a supported stable ID")
    evidence = state.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
    elif len(evidence) > EVIDENCE_LIMIT:
        errors.append(f"evidence must contain at most {EVIDENCE_LIMIT} paths")
    else:
        for item in evidence:
            if (
                not isinstance(item, dict)
                or set(item) != {"path", "sha256"}
                or not bounded_text(item.get("path"))
                or not isinstance(item.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", ""))
            ):
                errors.append("every evidence item must contain exactly a bounded path and sha256")
                continue
            if check_paths:
                try:
                    _normalized, resolved = resolve_repo_path(root, item["path"])
                except ValueError as exc:
                    errors.append(f"evidence path: {exc}")
                    continue
                if not resolved.is_file():
                    errors.append(f"evidence does not exist: {item['path']}")
                elif sha256_file(resolved) != item["sha256"]:
                    errors.append(f"evidence hash is stale: {item['path']}")
    blockers = state.get("blockers")
    if not isinstance(blockers, list):
        errors.append("blockers must be a list")
    elif len(blockers) > BLOCKER_LIMIT:
        errors.append(f"blockers must contain at most {BLOCKER_LIMIT} items")
    elif any(
        not isinstance(value, str) or not value or len(value) > POINTER_TEXT_LIMIT
        or "\n" in value or "\r" in value
        for value in blockers
    ):
        errors.append(
            f"every blocker must be single-line and at most {POINTER_TEXT_LIMIT} characters"
        )
    last_transition = state.get("last_transition")
    if last_transition is not None:
        if not isinstance(last_transition, dict) or set(last_transition) != {
            "revision", "stage", "status", "operation"
        }:
            errors.append(
                "last_transition must be null or contain exactly revision, stage, status, and operation"
            )
        else:
            if type(last_transition.get("revision")) is not int or last_transition["revision"] < 0:
                errors.append("last_transition.revision must be a non-negative integer")
            for key in ("stage", "status", "operation"):
                if not bounded_text(last_transition.get(key)):
                    errors.append(f"last_transition.{key} must be a bounded single-line string")

    if isinstance(active, dict) and isinstance(gate, dict):
        status = active.get("status")
        gate_status = gate.get("status")
        if status in CANDIDATE_STATUSES | {"release_authorized"} and gate_status != "pending":
            errors.append(f"active status {status} requires a pending human gate")
        if status == "in_progress" and gate_status != "not_required":
            errors.append("in_progress work requires human_gate.status not_required")
        if status in {"accepted", "released"} and gate_status != "approved":
            errors.append(f"final status {status} requires an approved human gate")
    return errors


def read_valid_state(root: Path, *, check_paths: bool = True) -> dict[str, Any]:
    state = read_state(root)
    errors = validate_state(state, root, check_paths)
    if errors:
        fail("invalid workflow pointer: " + "; ".join(errors[:8]))
    return state


def write_valid_state(path: Path, state: dict[str, Any], root: Path) -> None:
    errors = validate_state(state, root, False)
    if errors:
        fail("refusing to write invalid workflow pointer: " + "; ".join(errors[:8]))
    atomic_write_yaml(path, state)


def require_revision(state: dict[str, Any], expected: int) -> None:
    actual = state.get("revision")
    if actual != expected:
        fail(f"stale revision: expected {expected}, current {actual}")


def resolve_repo_path(root: Path, raw_path: Any) -> tuple[str, Path]:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("path must be a non-empty string")
    candidate = Path(raw_path.replace("\\", "/"))
    if candidate.is_absolute():
        raise ValueError("path must be repository-relative")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        normalized = resolved.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise ValueError("path escapes the project root") from exc
    return normalized, resolved


def require_repo_file(root: Path, raw_path: Any, label: str) -> str:
    try:
        normalized, resolved = resolve_repo_path(root, raw_path)
    except ValueError as exc:
        fail(f"invalid {label}: {exc}")
    if not resolved.is_file():
        fail(f"{label} does not exist: {normalized}")
    return normalized


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_role_path(state: dict[str, Any], role: str) -> str | None:
    if role in PROJECT_ARTIFACT_KEYS:
        value = state.get("canonical", {}).get(role)
        return value if isinstance(value, str) and value else None
    for artifact in state.get("active_artifacts", []):
        if isinstance(artifact, dict) and artifact.get("role") == role:
            value = artifact.get("path")
            return value if isinstance(value, str) and value else None
    return None


def require_active_artifact_status(
    state: dict[str, Any], root: Path, role: str, statuses: set[str]
) -> None:
    artifact = next(
        (
            item
            for item in state.get("active_artifacts", [])
            if isinstance(item, dict) and item.get("role") == role
        ),
        None,
    )
    if not artifact or artifact.get("status") not in statuses:
        fail(f"operation requires active artifact role {role} in status {sorted(statuses)}")
    normalized = require_repo_file(root, artifact.get("path"), role)
    if sha256_file(root / normalized) != artifact.get("sha256"):
        fail(f"{role} hash changed after recorded state")


def require_approved_active_artifact(state: dict[str, Any], root: Path, role: str) -> None:
    require_active_artifact_status(state, root, role, {"approved"})


def update_artifact_role(
    state: dict[str, Any], role: str, status: str, digest: str | None = None
) -> None:
    if role in PROJECT_ARTIFACT_KEYS:
        state["canonical_status"][role] = status
        if digest is not None:
            state["canonical_hashes"][role] = digest
        return
    for artifact in state.get("active_artifacts", []):
        if artifact.get("role") == role:
            artifact["status"] = status
            if digest is not None:
                artifact["sha256"] = digest
            return
    fail(f"artifact role is not registered: {role}")


def verify_gate_hashes(
    state: dict[str, Any], root: Path, allow_changed: set[str] | None = None
) -> dict[str, tuple[str, str]]:
    allow_changed = allow_changed or set()
    gate = state.get("human_gate", {})
    roles = gate.get("artifact_roles", [])
    expected = gate.get("artifact_hashes", {})
    verified: dict[str, tuple[str, str]] = {}
    for role in roles:
        role_path = artifact_role_path(state, role)
        if not role_path:
            fail(f"pending gate role has no registered path: {role}")
        normalized = require_repo_file(root, role_path, f"gate artifact {role}")
        digest = sha256_file(root / normalized)
        if role not in allow_changed and digest != expected.get(role):
            fail(f"gate artifact changed after review: {normalized}; record-output again")
        verified[role] = (normalized, digest)
    return verified


def require_approved_canonical_integrity(
    state: dict[str, Any], root: Path, allow_changed: set[str] | None = None
) -> None:
    allow_changed = allow_changed or set()
    for role in sorted(PROJECT_ARTIFACT_KEYS):
        if state.get("canonical_status", {}).get(role) != "approved":
            continue
        if role in allow_changed:
            continue
        role_path = state.get("canonical", {}).get(role)
        expected = state.get("canonical_hashes", {}).get(role)
        if not role_path or not expected:
            fail(f"approved canonical role lacks a path/hash: {role}")
        normalized = require_repo_file(root, role_path, f"approved canonical {role}")
        if sha256_file(root / normalized) != expected:
            fail(f"approved canonical artifact changed outside a reviewed operation: {normalized}")
        bundle_errors = validate_approved_bundle(
            root / normalized,
            root,
            role=role,
            require_declaration=role in BUNDLE_DECLARATION_ROLES,
        )
        if bundle_errors:
            fail(f"approved canonical bundle is stale: {'; '.join(bundle_errors[:3])}")


FIELD_PATTERN = re.compile(r"^\*\*([^*]+)\*\*:\s*(.*?)\s*$")
PLACEHOLDER_VALUES = {"pending", "not run", "not available", "yyyy-mm-dd"}


def markdown_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FIELD_PATTERN.match(line.strip())
        if not match:
            continue
        label, value = match.group(1).strip(), match.group(2).strip()
        if label in fields:
            fail(f"duplicate decision field in {path.name}: {label}")
        fields[label] = value
    return fields


def require_decision_field(
    fields: dict[str, str], label: str, expected: str | None = None, date: bool = False
) -> str:
    value = fields.get(label, "").strip()
    if (
        not value
        or value.lower() in PLACEHOLDER_VALUES
        or "{{" in value
        or "}}" in value
        or " | " in value
        or re.fullmatch(r"\[[^\]]+\]", value)
        or re.fullmatch(r"<[^>]+>", value)
    ):
        fail(f"decision artifact field is unresolved: {label}")
    if expected is not None and value.lower() != expected.lower():
        fail(f"decision artifact field {label} must be {expected!r}, got {value!r}")
    if date:
        try:
            parsed_date = calendar_date.fromisoformat(value)
        except ValueError:
            fail(f"decision artifact field {label} must be a real YYYY-MM-DD date")
        if parsed_date.isoformat() != value:
            fail(f"decision artifact field {label} must be a real YYYY-MM-DD date")
    return value


def require_integer_field(fields: dict[str, str], label: str, minimum: int = 0) -> int:
    value = require_decision_field(fields, label)
    if not re.fullmatch(r"0|[1-9][0-9]*", value):
        fail(f"decision artifact field {label} must be a non-negative integer")
    parsed = int(value)
    if parsed < minimum:
        fail(f"decision artifact field {label} must be at least {minimum}")
    return parsed


def require_unresolved_field(fields: dict[str, str], label: str) -> None:
    value = fields.get(label, "").strip()
    if not (
        value.lower() in PLACEHOLDER_VALUES
        or "{{" in value
        or "}}" in value
    ):
        fail(f"candidate artifact field must remain unresolved: {label}")


def markdown_section_body(text: str, heading: str) -> str | None:
    match = re.search(rf"(?m)^## {re.escape(heading)}\s*$", text)
    if not match:
        return None
    next_heading = re.search(r"(?m)^## ", text[match.end():])
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end].strip()


def section_has_concrete_findings(text: str, heading: str) -> bool:
    body = markdown_section_body(text, heading)
    if body is None:
        return False
    none_values = {"none", "n/a", "not applicable", "no blockers"}
    for line in body.splitlines():
        value = re.sub(r"^[\s>*+-]+", "", line).strip().rstrip(".").lower()
        if value and value not in none_values:
            return True
    return False


def require_markdown_sections(text: str, headings: tuple[str, ...], table: bool = False) -> None:
    for heading in headings:
        matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\s*$", text))
        if len(matches) > 1:
            fail(f"candidate artifact contains duplicate required section: {heading}")
        body = markdown_section_body(text, heading)
        if body is None:
            fail(f"candidate artifact is missing required section: {heading}")
        if not body:
            fail(f"candidate artifact section is empty: {heading}")
        if table:
            rows = [
                line.strip()
                for line in body.splitlines()
                if line.strip().startswith("|") and line.strip().endswith("|")
            ]
            data_rows = [
                row for row in rows
                if not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", row)
            ]
            if len(data_rows) < 2:
                fail(f"candidate artifact section requires a header and data row: {heading}")


def markdown_table_rows(text: str, heading: str) -> list[list[str]]:
    body = markdown_section_body(text, heading)
    if body is None:
        return []
    rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", stripped):
            continue
        rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
    return rows


def normalized_table_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def require_allowed_result_rows(
    text: str, heading: str, result_column: int, allowed: set[str]
) -> None:
    rows = markdown_table_rows(text, heading)
    for position, row in enumerate(rows[1:], start=1):
        if len(row) <= result_column:
            fail(f"{heading} row {position} lacks a result column")
        result = normalized_table_token(row[result_column])
        if result not in allowed:
            fail(f"{heading} row {position} has non-ready result: {row[result_column]}")


def require_gate_categories(
    text: str, heading: str, categories: dict[str, set[str]]
) -> None:
    rows = markdown_table_rows(text, heading)
    labels = [normalized_table_token(row[0]) for row in rows[1:] if row]
    for category, aliases in categories.items():
        count = sum(label in aliases for label in labels)
        if count != 1:
            fail(f"{heading} must contain exactly one {category} gate row")


def require_gate_applicability(
    text: str, heading: str, aliases: set[str], expected: str, label: str
) -> None:
    rows = markdown_table_rows(text, heading)
    matches = [
        row for row in rows[1:]
        if row and normalized_table_token(row[0]) in aliases
    ]
    if len(matches) != 1 or len(matches[0]) < 2:
        fail(f"{heading} must contain exactly one complete {label} gate row")
    applicability = normalized_table_token(matches[0][1])
    if applicability != expected:
        fail(f"{heading} {label} applicability must be {expected}")


def require_exact_scenario_coverage(
    text: str, root: Path, spec_path: str
) -> None:
    spec_text = (root / spec_path).read_text(encoding="utf-8")
    spec_ids = {
        match.upper()
        for match in re.findall(r"\bSC-\d+\b", spec_text, re.IGNORECASE)
    }
    if not spec_ids:
        fail("acceptance spec must define at least one stable SC-### scenario ID")
    evidence_ids: list[str] = []
    for position, row in enumerate(
        markdown_table_rows(text, "Scenario Evidence")[1:], start=1
    ):
        if not row:
            fail(f"Scenario Evidence row {position} is incomplete")
        scenario_id = row[0].strip().strip("`").upper()
        if not re.fullmatch(r"SC-\d+", scenario_id):
            fail(f"Scenario Evidence row {position} must start with one SC-### ID")
        evidence_ids.append(scenario_id)
    if len(evidence_ids) != len(set(evidence_ids)):
        fail("Scenario Evidence contains duplicate scenario IDs")
    if set(evidence_ids) != spec_ids:
        missing = sorted(spec_ids - set(evidence_ids))
        extra = sorted(set(evidence_ids) - spec_ids)
        fail(
            "Scenario Evidence must exactly cover the registered spec scenario IDs; "
            f"missing={missing[:8]}, extra={extra[:8]}"
        )


def table_has_concrete_data_row(text: str, heading: str) -> bool:
    none_values = {
        "", "none", "n_a", "not_applicable", "not_required", "no", "false",
    }
    return any(
        any(normalized_table_token(cell) not in none_values for cell in row)
        for row in markdown_table_rows(text, heading)[1:]
    )


def require_concrete_table_column(
    text: str, heading: str, column: int, label: str
) -> None:
    none_values = {"", "none", "n_a", "not_applicable", "not_available", "missing"}
    for position, row in enumerate(markdown_table_rows(text, heading)[1:], start=1):
        if len(row) <= column:
            fail(f"{heading} row {position} lacks {label}")
        value = row[column].strip().strip("`")
        if (
            normalized_table_token(value) in none_values
            or "{{" in value
            or "}}" in value
            or re.fullmatch(r"\[[^\]]+\]", value)
            or re.fullmatch(r"<[^>]+>", value)
        ):
            fail(f"{heading} row {position} requires concrete {label}")


def approved_spike_definition(
    state: dict[str, Any], root: Path, spike_id: str
) -> tuple[str, str, str]:
    if not re.fullmatch(r"SPK-\d+", spike_id, re.IGNORECASE):
        fail("spike work-id must use SPK-###")
    architecture = state.get("canonical", {}).get("architecture")
    if not architecture or state.get("canonical_status", {}).get("architecture") != "approved":
        fail("spike_result requires an approved architecture baseline containing the spike")
    normalized = require_repo_file(root, architecture, "approved architecture")
    text = (root / normalized).read_text(encoding="utf-8")
    definitions: list[tuple[str, str, str]] = []
    for heading in ("Spikes", "Deferred Decisions and Spikes"):
        rows = markdown_table_rows(text, heading)
        if not rows:
            continue
        headers = [normalized_table_token(cell) for cell in rows[0]]
        for row in rows[1:]:
            if not row or row[0].strip().strip("`").lower() != spike_id.lower():
                continue
            try:
                if heading == "Spikes":
                    question = row[headers.index("question")]
                    time_box = row[headers.index("time_box")]
                    blocks = row[headers.index("blocks")]
                else:
                    kind = row[headers.index("kind")]
                    if normalized_table_token(kind) != "spike":
                        fail(f"{spike_id} must be typed Spike in the architecture registry")
                    question = row[headers.index("question_or_decision")]
                    time_box = row[headers.index("trigger_time_box")]
                    blocks = row[headers.index("blocks")]
            except (ValueError, IndexError):
                fail(f"architecture spike table has an invalid schema for {spike_id}")
            definitions.append((question.strip(), time_box.strip(), blocks.strip()))
    if len(definitions) != 1:
        fail(f"approved architecture must define {spike_id} exactly once in a spike table")
    question, time_box, blocks = definitions[0]
    for label, value in (("question", question), ("time box", time_box), ("blocked owner/work", blocks)):
        if (
            not value
            or normalized_table_token(value) in {"none", "n_a", "unknown"}
            or "{{" in value
            or "}}" in value
            or re.fullmatch(r"\[[^\]]+\]", value)
            or re.fullmatch(r"<[^>]+>", value)
        ):
            fail(f"architecture spike {spike_id} requires a concrete {label}")
    return question, time_box, normalized


def feature_numbers_from_scope(scope: str) -> set[int]:
    numbers = {int(value) for value in re.findall(r"\bF-?(\d+)\b", scope, re.IGNORECASE)}
    for start_raw, end_raw in re.findall(
        r"\bF-?(\d+)\s*(?:\.\.|-)\s*F-?(\d+)\b", scope, re.IGNORECASE
    ):
        start, end = int(start_raw), int(end_raw)
        if end < start or end - start > 100:
            fail("release Scope contains an invalid or over-broad feature range")
        numbers.update(range(start, end + 1))
    if not numbers:
        fail("release Scope must name at least one F-ID")
    return numbers


def validate_included_acceptance_decisions(
    text: str, root: Path, scope: str
) -> None:
    rows = markdown_table_rows(text, "Included Acceptance Decisions")
    decision_receipts = special_decision_receipts(root)
    included_numbers: set[int] = set()
    for position, row in enumerate(rows[1:], start=1):
        if len(row) < 3:
            fail(f"Included Acceptance Decisions row {position} is incomplete")
        feature_id = row[0].strip().strip("`")
        if not re.fullmatch(r"F-?\d+", feature_id, re.IGNORECASE):
            fail(f"Included Acceptance Decisions row {position} has an invalid feature ID")
        feature_number = int(re.search(r"\d+", feature_id).group(0))
        if feature_number in included_numbers:
            fail(f"Included Acceptance Decisions contains duplicate feature {feature_id}")
        included_numbers.add(feature_number)
        if normalized_table_token(row[1]) != "accepted":
            fail(f"Included Acceptance Decisions row {position} is not human Accepted")
        raw_evidence = row[2].strip().strip("`")
        link_match = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", raw_evidence)
        if link_match:
            raw_evidence = link_match.group(1).split("#", 1)[0]
        evidence_path = require_repo_file(root, raw_evidence, "feature acceptance decision")
        evidence_fields = markdown_fields(root / evidence_path)
        require_decision_field(evidence_fields, "Work item", feature_id)
        require_decision_field(evidence_fields, "Human decision", "Accepted")
        require_accepted_feature_decision_receipt(
            root, feature_id, evidence_path, decision_receipts
        )
    scoped_numbers = feature_numbers_from_scope(scope)
    if included_numbers != scoped_numbers:
        fail("Included Acceptance Decisions must exactly cover the fixed release Scope")


def require_passing_result_rows(
    text: str, heading: str, result_column: int, review_status: str
) -> None:
    if review_status not in {"ready", "conditional"}:
        return
    rows = markdown_table_rows(text, heading)
    for position, row in enumerate(rows[1:], start=1):
        if len(row) <= result_column:
            fail(f"{heading} row {position} lacks a result column")
        if normalized_table_token(row[result_column]) not in {"pass", "passed", "accepted"}:
            fail(f"{heading} row {position} is not passing for Review status {review_status}")


def validate_applicability_rows(text: str, heading: str, review_status: str) -> None:
    rows = markdown_table_rows(text, heading)
    allowed_applicability = {"required", "applicable", "not_applicable"}
    allowed_results = {"pass", "passed", "fail", "failed", "missing", "not_run", "not_applicable"}
    for position, row in enumerate(rows[1:], start=1):
        if len(row) < 4:
            fail(f"{heading} row {position} must contain gate, applicability, result, and evidence")
        applicability = normalized_table_token(row[1])
        result = normalized_table_token(row[2])
        evidence = row[3].strip()
        if applicability not in allowed_applicability:
            fail(f"{heading} row {position} has invalid applicability: {row[1]}")
        if result not in allowed_results:
            fail(f"{heading} row {position} has invalid result: {row[2]}")
        if not evidence or "{{" in evidence or "}}" in evidence:
            fail(f"{heading} row {position} requires concrete evidence or an N/A reason")
        if review_status in {"ready", "conditional"}:
            if applicability == "not_applicable" and result != "not_applicable":
                fail(f"{heading} row {position} must record result not_applicable")
            if applicability != "not_applicable" and result not in {"pass", "passed"}:
                fail(f"{heading} row {position} is not passing for Review status {review_status}")


def validate_approved_bundle(
    root_artifact: Path,
    root: Path,
    *,
    role: str | None = None,
    require_declaration: bool = False,
) -> list[str]:
    """Validate a root-bound list of split canonical files when declared."""
    text = root_artifact.read_text(encoding="utf-8", errors="replace")
    mode_values = [
        match.group(1).strip().lower()
        for match in re.finditer(r"(?m)^\*\*Artifact bundle\*\*:\s*(.*?)\s*$", text)
    ]
    if len(mode_values) > 1:
        return ["Artifact bundle field must appear at most once"]
    mode = mode_values[0] if mode_values else None
    if require_declaration and mode is None:
        return ["Artifact bundle field must declare single or split"]
    if mode is not None and mode not in {"single", "split"}:
        return ["Artifact bundle must be single or split"]
    if role == "discovery" and mode == "split":
        return ["discovery is a single-file canonical artifact"]
    body = markdown_section_body(text, "Approved Bundle")
    if mode == "single" and body is not None:
        return ["single artifacts must not contain an Approved Bundle table"]
    if mode == "split" and body is None:
        return ["split artifacts require an Approved Bundle table"]
    if body is None:
        return []
    rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", stripped):
            continue
        rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
    if not rows or [cell.lower() for cell in rows[0]] != ["path", "sha-256"]:
        return ["Approved Bundle must use exactly the table columns Path and SHA-256"]
    if len(rows) < 2:
        return ["Approved Bundle must list at least one split artifact"]
    errors: list[str] = []
    seen: set[str] = set()
    root_relative = root_artifact.resolve().relative_to(root.resolve()).as_posix()
    for position, row in enumerate(rows[1:], start=1):
        if len(row) != 2:
            errors.append(f"row {position} must contain exactly Path and SHA-256")
            continue
        raw_path = row[0].strip("`")
        digest = row[1].strip("`").lower()
        try:
            normalized, resolved = resolve_repo_path(root, raw_path)
        except ValueError as exc:
            errors.append(f"row {position}: {exc}")
            continue
        if normalized == root_relative:
            errors.append(f"row {position} must not list the canonical root itself")
        if normalized in seen:
            errors.append(f"duplicate bundle path: {normalized}")
        seen.add(normalized)
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"invalid bundle hash: {normalized}")
            continue
        if not resolved.is_file():
            errors.append(f"bundle path does not exist: {normalized}")
        elif sha256_file(resolved) != digest:
            errors.append(f"bundle hash is stale: {normalized}")
    registry_specs = {
        "requirements": (("Domain Registry", "Detail path"),),
        "roadmap": (("Domain Registry", "Detail path"),),
        "architecture": (
            ("Domain Detail Registry", "Detail path"),
            ("Decision Record Registry", "Path"),
        ),
        "ui_structure": (("Domain Registry", "Detail path"),),
    }
    if mode == "split" and role in registry_specs:
        registry_paths: list[str] = []
        for heading, path_column in registry_specs[role]:
            registry_rows = markdown_table_rows(text, heading)
            if not registry_rows:
                errors.append(f"split {role} root is missing {heading}")
                continue
            headers = [normalized_table_token(cell) for cell in registry_rows[0]]
            try:
                path_index = headers.index(normalized_table_token(path_column))
            except ValueError:
                errors.append(f"{heading} is missing column {path_column}")
                continue
            for position, row in enumerate(registry_rows[1:], start=1):
                if len(row) <= path_index:
                    errors.append(f"{heading} row {position} lacks {path_column}")
                    continue
                raw_registry_path = row[path_index].strip().strip("`")
                link_match = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", raw_registry_path)
                if link_match:
                    raw_registry_path = link_match.group(1).split("#", 1)[0]
                try:
                    normalized_registry, _resolved = resolve_repo_path(root, raw_registry_path)
                except ValueError as exc:
                    errors.append(f"{heading} row {position}: {exc}")
                    continue
                registry_paths.append(normalized_registry)
        duplicate_registry_paths = sorted(
            path for path in set(registry_paths) if registry_paths.count(path) > 1
        )
        if duplicate_registry_paths:
            errors.append(f"duplicate registry paths: {duplicate_registry_paths[:3]}")
        registry_set = set(registry_paths)
        if registry_set != seen:
            missing_from_bundle = sorted(registry_set - seen)
            missing_from_registry = sorted(seen - registry_set)
            if missing_from_bundle:
                errors.append(f"registry paths missing from Approved Bundle: {missing_from_bundle[:3]}")
            if missing_from_registry:
                errors.append(f"Approved Bundle paths missing from registries: {missing_from_registry[:3]}")
    return errors


def reject_unresolved_placeholders(text: str, allowed_field_labels: set[str]) -> None:
    for line in text.splitlines():
        if "{{" not in line and "}}" not in line:
            continue
        match = FIELD_PATTERN.match(line.strip())
        if not match or match.group(1).strip() not in allowed_field_labels:
            fail("candidate artifact contains an unresolved non-decision placeholder")


def require_work_item(fields: dict[str, str], work_id: str, label: str = "Work item") -> None:
    value = require_decision_field(fields, label)
    if value.lower() != work_id.lower():
        fail(f"candidate artifact {label} must match active work {work_id}, got {value}")


def validate_candidate_artifact(
    role: str, resolved: Path, root: Path, work_id: str, work_kind: str,
    expected_inputs: dict[str, str] | None = None,
) -> None:
    if role not in {
        "pre_implementation", "verification", "spike_result", "acceptance", "release_readiness"
    }:
        return
    text = resolved.read_text(encoding="utf-8")
    fields = markdown_fields(resolved)
    if role == "pre_implementation":
        require_work_item(fields, work_id)
        require_decision_field(fields, "Work kind", work_kind)
        require_decision_field(fields, "Review result", "Pass")
        require_decision_field(fields, "Reviewed revision")
        require_decision_field(fields, "Reviewed by")
        require_decision_field(fields, "Reviewed on", date=True)
        require_markdown_sections(
            text, ("Inputs", "Alignment Checks", "Coverage Batches"), table=True
        )
        require_markdown_sections(
            text,
            ("Blocking Findings", "Advisory Findings", "Skipped Checks", "Outcome Rationale"),
        )
        if section_has_concrete_findings(text, "Blocking Findings"):
            fail("a passing pre-implementation review cannot contain blocking findings")
        if section_has_concrete_findings(text, "Skipped Checks"):
            fail("a passing pre-implementation review cannot contain skipped checks")
        require_allowed_result_rows(
            text, "Alignment Checks", 1, {"pass", "passed", "not_applicable"}
        )
        require_allowed_result_rows(
            text, "Coverage Batches", 2, {"pass", "passed", "complete", "completed", "covered"}
        )
        for column, label in ((0, "batch ID"), (1, "stable IDs or paths"), (3, "evidence")):
            require_concrete_table_column(text, "Coverage Batches", column, label)
        reject_unresolved_placeholders(text, set())
        input_rows = markdown_table_rows(text, "Inputs")
        input_by_label = {
            row[0].lower(): row[1]
            for row in input_rows[1:]
            if len(row) >= 2 and row[0] and row[1]
        }
        required_inputs = {
            "work-item spec": "spec",
            "plan": "plan",
            "tasks": "tasks",
            "requirements checklist": "requirements_checklist",
        }
        for label, input_role in required_inputs.items():
            raw_path = input_by_label.get(label)
            if not raw_path:
                fail(f"pre-implementation Inputs is missing {label}")
            normalized = require_repo_file(root, raw_path, f"pre-implementation {label}")
            if expected_inputs and normalized != expected_inputs.get(input_role):
                fail(
                    f"pre-implementation {label} must match approved registered {input_role}: "
                    f"{expected_inputs.get(input_role)}"
                )
        return
    if role == "verification":
        require_work_item(fields, work_id)
        require_decision_field(fields, "Work kind", work_kind)
        require_decision_field(fields, "Reviewed revision")
        require_decision_field(fields, "Reviewed on", date=True)
        expected_candidate = (
            "Ready for Acceptance" if work_kind == "feature" else "Ready for Review"
        )
        require_decision_field(fields, "Candidate state", expected_candidate)
        require_markdown_sections(
            text,
            (
                "Inputs", "Proof Evidence", "Tasks, Checks, and Deferrals",
                "Constraint and Scope Drift", "Coverage Batches",
            ),
            table=True,
        )
        require_markdown_sections(
            text, ("Blocking Findings", "Skipped Checks", "Readiness Conclusion")
        )
        if section_has_concrete_findings(text, "Blocking Findings"):
            fail("a ready verification candidate cannot contain blocking findings")
        if section_has_concrete_findings(text, "Skipped Checks"):
            fail("a ready verification candidate cannot contain skipped checks")
        require_allowed_result_rows(
            text, "Proof Evidence", 2, {"pass", "passed", "accepted"}
        )
        require_allowed_result_rows(
            text,
            "Tasks, Checks, and Deferrals",
            1,
            {"complete", "completed", "pass", "passed", "deferred", "not_applicable"},
        )
        require_allowed_result_rows(
            text,
            "Constraint and Scope Drift",
            1,
            {"aligned", "pass", "passed", "accepted", "deferred", "not_applicable"},
        )
        require_allowed_result_rows(
            text, "Coverage Batches", 2, {"pass", "passed", "complete", "completed", "covered"}
        )
        for column, label in ((0, "batch ID"), (1, "stable IDs or paths"), (3, "evidence")):
            require_concrete_table_column(text, "Coverage Batches", column, label)
        reject_unresolved_placeholders(text, set())
        return
    if role == "spike_result":
        if work_kind != "spike":
            fail("spike_result requires active work kind spike")
        require_work_item(fields, work_id)
        question = require_decision_field(fields, "Question")
        source_architecture = require_decision_field(fields, "Source architecture")
        time_box = require_decision_field(fields, "Time box")
        for label in ("Investigated revision", "Investigated by"):
            require_decision_field(fields, label)
        require_decision_field(fields, "Investigated on", date=True)
        outcome = require_decision_field(fields, "Outcome").lower()
        if outcome not in {"answered", "inconclusive"}:
            fail("spike_result Outcome must be answered or inconclusive")
        approved_question, approved_time_box, architecture_path = approved_spike_definition(
            read_valid_state(root, check_paths=True), root, work_id
        )
        if question != approved_question or time_box != approved_time_box:
            fail("spike_result question and time box must match the approved spike definition")
        source_path, separator, source_anchor = source_architecture.partition("#")
        normalized_source = require_repo_file(root, source_path, "spike source architecture")
        if normalized_source != architecture_path or not separator or work_id.lower() not in source_anchor.lower():
            fail("spike_result Source architecture must cite the canonical path and SPK anchor")
        require_markdown_sections(text, ("Evidence",), table=True)
        require_markdown_sections(text, ("Findings", "Answer", "Follow-up Routing"))
        require_concrete_table_column(text, "Evidence", 0, "activity")
        require_concrete_table_column(text, "Evidence", 1, "result")
        require_concrete_table_column(text, "Evidence", 2, "evidence reference")
        reject_unresolved_placeholders(text, set())
        return
    review_status = require_decision_field(fields, "Review status").lower()
    if review_status not in {"ready", "conditional", "not_ready"}:
        fail(f"{role} Review status must be ready, conditional, or not_ready")
    if role == "acceptance":
        require_work_item(fields, work_id)
        require_decision_field(fields, "Reviewed by")
        require_decision_field(fields, "Reviewed on", date=True)
        require_decision_field(fields, "Independence", "non-implementer")
        spec_path = require_decision_field(fields, "Spec")
        spec_path = require_repo_file(root, spec_path, "acceptance spec")
        require_decision_field(fields, "Implementation revision")
        decision_labels = {"Human decision", "Decided by", "Decision date", "Decision evidence"}
        for label in decision_labels:
            require_unresolved_field(fields, label)
        require_markdown_sections(
            text, ("Scenario Evidence", "Applicable Quality Gates"), table=True
        )
        require_markdown_sections(text, ("Blockers", "Follow-ups", "Human Decision Notes"))
        if review_status in {"ready", "conditional"} and section_has_concrete_findings(
            text, "Blockers"
        ):
            fail(f"acceptance Review status {review_status} cannot contain blockers")
        if review_status == "not_ready" and not section_has_concrete_findings(text, "Blockers"):
            fail("acceptance Review status not_ready requires a concrete blocker")
        if review_status == "conditional" and not table_has_concrete_data_row(
            text, "Follow-ups"
        ):
            fail("conditional acceptance requires a concrete follow-up condition")
        require_gate_categories(
            text,
            "Applicable Quality Gates",
            {
                "tests/deterministic verification": {
                    "tests", "deterministic_verification", "tests_deterministic_verification"
                },
                "coverage policy": {"coverage", "coverage_policy"},
                "CI": {"ci"},
                "code review": {"code_review"},
                "security review": {"security_review"},
            },
        )
        require_passing_result_rows(text, "Scenario Evidence", 1, review_status)
        require_concrete_table_column(text, "Scenario Evidence", 2, "scenario evidence")
        require_exact_scenario_coverage(text, root, spec_path)
        require_gate_applicability(
            text,
            "Applicable Quality Gates",
            {"tests", "deterministic_verification", "tests_deterministic_verification"},
            "required",
            "tests / deterministic verification",
        )
        validate_applicability_rows(text, "Applicable Quality Gates", review_status)
        reject_unresolved_placeholders(text, decision_labels)
        return
    require_work_item(fields, work_id, "Release ID")
    require_decision_field(fields, "Reviewed by")
    require_decision_field(fields, "Reviewed on", date=True)
    require_decision_field(fields, "Independence", "non-implementer")
    release_scope = require_decision_field(fields, "Scope")
    require_decision_field(fields, "Artifact revision")
    decision_labels = {
        "Human readiness decision",
        "Authorization evidence",
        "Authorized by",
        "Authorized on",
        "Execution",
        "Execution evidence",
        "Execution evidence SHA-256",
        "Confirmed by",
        "Confirmed on",
    }
    for label in decision_labels:
        require_unresolved_field(fields, label)
    require_markdown_sections(
        text, ("Included Acceptance Decisions", "Release Gates"), table=True
    )
    require_markdown_sections(
        text, ("Blockers", "Deferred Items", "Release Execution Result")
    )
    if review_status in {"ready", "conditional"} and section_has_concrete_findings(
        text, "Blockers"
    ):
        fail(f"release readiness Review status {review_status} cannot contain blockers")
    if review_status == "not_ready" and not section_has_concrete_findings(text, "Blockers"):
        fail("release readiness Review status not_ready requires a concrete blocker")
    if review_status == "conditional" and not table_has_concrete_data_row(
        text, "Deferred Items"
    ):
        fail("conditional release readiness requires a concrete deferred condition")
    require_gate_categories(
        text,
        "Release Gates",
        {
            "build provenance": {"build_provenance"},
            "CI": {"ci"},
            "code review": {"code_review"},
            "dependency review": {"dependency_review"},
            "security review": {"security_review"},
            "migration": {"migration"},
            "compatibility": {"compatibility"},
            "rollback": {"rollback"},
            "observability/operations": {
                "observability", "operations", "observability_operations"
            },
            "user/operator documentation": {
                "documentation", "user_documentation", "operator_documentation",
                "user_operator_documentation",
            },
        },
    )
    require_passing_result_rows(text, "Included Acceptance Decisions", 1, review_status)
    validate_included_acceptance_decisions(text, root, release_scope)
    require_gate_applicability(
        text, "Release Gates", {"build_provenance"}, "required", "build provenance"
    )
    validate_applicability_rows(text, "Release Gates", review_status)
    reject_unresolved_placeholders(text, decision_labels)


def validate_block_artifact(
    role: str, resolved: Path, root: Path, work_id: str, work_kind: str
) -> None:
    if role not in {"pre_implementation", "verification", "release_readiness"}:
        return
    if role == "release_readiness":
        validate_candidate_artifact(role, resolved, root, work_id, work_kind)
        require_decision_field(markdown_fields(resolved), "Review status", "not_ready")
        return
    text = resolved.read_text(encoding="utf-8")
    fields = markdown_fields(resolved)
    require_work_item(fields, work_id)
    if role == "verification":
        require_decision_field(fields, "Work kind", work_kind)
        require_decision_field(fields, "Reviewed revision")
        require_decision_field(fields, "Reviewed on", date=True)
        require_decision_field(fields, "Candidate state", "Blocked")
        require_markdown_sections(
            text,
            (
                "Inputs", "Proof Evidence", "Tasks, Checks, and Deferrals",
                "Constraint and Scope Drift", "Coverage Batches",
            ),
            table=True,
        )
        require_markdown_sections(
            text, ("Blocking Findings", "Skipped Checks", "Readiness Conclusion")
        )
        if not section_has_concrete_findings(text, "Blocking Findings"):
            fail("a blocked verification review requires a concrete blocking finding")
        reject_unresolved_placeholders(text, set())
        return
    require_decision_field(fields, "Review result", "Blocked")
    require_decision_field(fields, "Work kind", work_kind)
    require_decision_field(fields, "Reviewed revision")
    require_decision_field(fields, "Reviewed by")
    require_decision_field(fields, "Reviewed on", date=True)
    require_markdown_sections(
        text, ("Inputs", "Alignment Checks", "Coverage Batches"), table=True
    )
    require_markdown_sections(
        text,
        ("Blocking Findings", "Advisory Findings", "Skipped Checks", "Outcome Rationale"),
    )
    if not section_has_concrete_findings(text, "Blocking Findings"):
        fail("a blocked pre-implementation review requires a concrete blocking finding")
    reject_unresolved_placeholders(text, set())


def validated_decision_value(label: str, value: str, date: bool = False) -> str:
    normalized = value.strip()
    if (
        not normalized
        or normalized.lower() in PLACEHOLDER_VALUES
        or "{{" in normalized
        or "}}" in normalized
        or " | " in normalized
        or re.fullmatch(r"\[[^\]]+\]", normalized)
        or re.fullmatch(r"<[^>]+>", normalized)
        or "\n" in normalized
        or "\r" in normalized
        or len(normalized) > POINTER_TEXT_LIMIT
    ):
        fail(f"decision value is unresolved: {label}")
    if date:
        try:
            parsed_date = calendar_date.fromisoformat(normalized)
        except ValueError:
            fail(f"decision value {label} must be a real YYYY-MM-DD date")
        if parsed_date.isoformat() != normalized:
            fail(f"decision value {label} must be a real YYYY-MM-DD date")
    return normalized


def validate_release_receipt(
    root: Path, raw_path: str, release_id: str, expected_result: str
) -> tuple[str, str]:
    normalized = require_repo_file(root, raw_path, "release execution receipt")
    receipt = read_yaml(root / normalized)
    required_keys = {
        "schema_version",
        "release_id",
        "result",
        "producer",
        "run_id",
        "completed_at",
        "artifact_sha256",
    }
    if set(receipt) != required_keys:
        fail("release execution receipt keys do not match the required schema")
    if type(receipt.get("schema_version")) is not int or receipt.get("schema_version") != SCHEMA_VERSION:
        fail(f"release execution receipt schema_version must be {SCHEMA_VERSION}")
    if str(receipt.get("release_id", "")).lower() != release_id.lower():
        fail("release execution receipt release_id does not match active work")
    if receipt.get("result") != expected_result:
        fail("release execution receipt result does not match --result")
    for key in ("producer", "run_id"):
        if not bounded_text(receipt.get(key)) or "{{" in receipt[key] or "}}" in receipt[key]:
            fail(f"release execution receipt {key} must be concrete and bounded")
    completed_at = receipt.get("completed_at")
    if not isinstance(completed_at, str) or not completed_at.endswith("Z"):
        fail("release execution receipt completed_at must be an ISO-8601 UTC timestamp")
    try:
        parsed_timestamp = datetime.fromisoformat(completed_at[:-1] + "+00:00")
    except ValueError:
        fail("release execution receipt completed_at must be an ISO-8601 UTC timestamp")
    if parsed_timestamp.tzinfo != timezone.utc:
        fail("release execution receipt completed_at must be an ISO-8601 UTC timestamp")
    artifact_digest = receipt.get("artifact_sha256")
    if artifact_digest is not None and (
        not isinstance(artifact_digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", artifact_digest)
    ):
        fail("release execution receipt artifact_sha256 must be null or sha256")
    if expected_result == "succeeded" and artifact_digest is None:
        fail("successful release receipt requires artifact_sha256")
    return normalized, sha256_file(root / normalized)


def validate_special_decision_receipt(
    receipt: dict[str, Any], path: Path, root: Path
) -> list[str]:
    errors: list[str] = []
    required_keys = {
        "schema_version", "receipt_type", "pointer_revision", "work_kind", "work_id",
        "stage", "decision", "decided_by", "decided_on", "evidence", "artifacts",
    }
    if set(receipt) != required_keys:
        return [f"special decision receipt schema mismatch: {path.name}"]
    receipt_type = receipt.get("receipt_type")
    expected = {
        "feature_acceptance_decision": (
            "feature", "acceptance", {"accepted", "rejected", "changes_requested"}, "acceptance"
        ),
        "release_authorization": (
            "release", "release_readiness", {"authorized"}, "release_readiness"
        ),
        "release_result": (
            "release", "release_readiness", {"succeeded", "failed", "held", "cancelled"},
            "release_readiness",
        ),
    }
    if receipt_type not in SPECIAL_DECISION_RECEIPT_TYPES:
        return [f"special decision receipt type is invalid: {path.name}"]
    work_kind, stage, decisions, role = expected[receipt_type]
    if type(receipt.get("schema_version")) is not int or receipt["schema_version"] != SCHEMA_VERSION:
        errors.append(f"special decision receipt schema_version must be {SCHEMA_VERSION}: {path.name}")
    if type(receipt.get("pointer_revision")) is not int or receipt["pointer_revision"] < 1:
        errors.append(f"special decision receipt pointer_revision must be positive: {path.name}")
    if receipt.get("work_kind") != work_kind or receipt.get("stage") != stage:
        errors.append(f"special decision receipt work kind/stage is invalid: {path.name}")
    if receipt.get("decision") not in decisions:
        errors.append(f"special decision receipt decision is invalid: {path.name}")
    for key in ("work_id", "decided_by", "evidence"):
        value = receipt.get(key)
        if (
            not bounded_text(value)
            or "{{" in str(value)
            or "}}" in str(value)
            or re.fullmatch(r"\[[^\]]+\]", str(value))
            or re.fullmatch(r"<[^>]+>", str(value))
        ):
            errors.append(f"special decision receipt {key} must be concrete: {path.name}")
    decided_on = receipt.get("decided_on")
    if not isinstance(decided_on, str):
        errors.append(f"special decision receipt decided_on must be YYYY-MM-DD: {path.name}")
    else:
        try:
            parsed_date = calendar_date.fromisoformat(decided_on)
        except ValueError:
            errors.append(f"special decision receipt decided_on must be YYYY-MM-DD: {path.name}")
        else:
            if parsed_date.isoformat() != decided_on:
                errors.append(f"special decision receipt decided_on must be YYYY-MM-DD: {path.name}")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        errors.append(f"special decision receipt must bind exactly one artifact: {path.name}")
    else:
        artifact = artifacts[0]
        artifact_keys = {"role", "path", "reviewed_sha256", "result_sha256"}
        if not isinstance(artifact, dict) or set(artifact) != artifact_keys:
            errors.append(f"special decision receipt artifact schema mismatch: {path.name}")
        else:
            if artifact.get("role") != role:
                errors.append(f"special decision receipt artifact role is invalid: {path.name}")
            try:
                _normalized, resolved = resolve_repo_path(root, artifact.get("path"))
            except ValueError as exc:
                errors.append(f"special decision receipt artifact path is invalid: {exc}")
            else:
                if not resolved.is_file():
                    errors.append(f"special decision receipt artifact is missing: {artifact.get('path')}")
            for key in ("reviewed_sha256", "result_sha256"):
                if not isinstance(artifact.get(key), str) or not re.fullmatch(
                    r"[0-9a-f]{64}", artifact.get(key, "")
                ):
                    errors.append(f"special decision receipt {key} is invalid: {path.name}")
    return errors


def validate_decision_receipt_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    digest = sha256_file(path)
    suffix = path.stem.rsplit("-", 1)[-1]
    if not re.fullmatch(r"[0-9a-f]{64}", suffix) or suffix != digest:
        errors.append(f"decision receipt filename does not match content hash: {path.name}")
    try:
        receipt = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return errors + [f"invalid decision receipt YAML {path.name}: {exc}"]
    if isinstance(receipt, dict) and "receipt_type" in receipt:
        return errors + validate_special_decision_receipt(receipt, path, root)
    required_keys = {
        "schema_version", "pointer_revision", "work_kind", "work_id", "stage", "gate",
        "decision", "decided_by", "decided_on", "evidence", "artifacts",
    }
    if not isinstance(receipt, dict) or set(receipt) != required_keys:
        return errors + [f"decision receipt schema mismatch: {path.name}"]
    if type(receipt.get("schema_version")) is not int or receipt["schema_version"] != SCHEMA_VERSION:
        errors.append(f"decision receipt schema_version must be {SCHEMA_VERSION}: {path.name}")
    if type(receipt.get("pointer_revision")) is not int or receipt["pointer_revision"] < 1:
        errors.append(f"decision receipt pointer_revision must be a positive integer: {path.name}")
    work_kind = receipt.get("work_kind")
    stage = receipt.get("stage")
    if work_kind not in KINDS or stage not in STAGE_KINDS or work_kind not in STAGE_KINDS[stage]:
        errors.append(f"decision receipt work kind/stage is invalid: {path.name}")
    for key in ("work_id", "gate", "decided_by", "evidence"):
        if not bounded_text(receipt.get(key)):
            errors.append(f"decision receipt {key} must be bounded: {path.name}")
    if receipt.get("decision") not in {"approved", "rejected"}:
        errors.append(f"decision receipt decision is invalid: {path.name}")
    decided_on = receipt.get("decided_on")
    if not isinstance(decided_on, str):
        errors.append(f"decision receipt decided_on must be YYYY-MM-DD: {path.name}")
    else:
        try:
            parsed_date = calendar_date.fromisoformat(decided_on)
        except ValueError:
            errors.append(f"decision receipt decided_on must be YYYY-MM-DD: {path.name}")
        else:
            if parsed_date.isoformat() != decided_on:
                errors.append(f"decision receipt decided_on must be YYYY-MM-DD: {path.name}")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or len(artifacts) > ACTIVE_ARTIFACT_LIMIT:
        errors.append(f"decision receipt artifacts must be a non-empty bounded list: {path.name}")
    else:
        roles: set[str] = set()
        for position, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict) or set(artifact) != {
                "role", "path", "reviewed_sha256"
            }:
                errors.append(f"decision receipt artifact {position} schema mismatch: {path.name}")
                continue
            role = artifact.get("role")
            if not isinstance(role, str) or not ROLE_PATTERN.fullmatch(role) or role in roles:
                errors.append(f"decision receipt artifact role is invalid or duplicate: {path.name}")
            else:
                roles.add(role)
            try:
                resolve_repo_path(root, artifact.get("path"))
            except ValueError as exc:
                errors.append(f"decision receipt artifact path is invalid: {exc}")
            reviewed_digest = artifact.get("reviewed_sha256")
            if not isinstance(reviewed_digest, str) or not re.fullmatch(
                r"[0-9a-f]{64}", reviewed_digest
            ):
                errors.append(f"decision receipt artifact hash is invalid: {path.name}")
    return errors


def special_decision_receipts(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    decision_directory = root / ".specify" / "decisions"
    if not decision_directory.is_dir():
        return []
    receipts: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(decision_directory.rglob("*.yaml")):
        receipt = read_yaml(path)
        if receipt.get("receipt_type") not in SPECIAL_DECISION_RECEIPT_TYPES:
            continue
        errors = validate_decision_receipt_file(path, root)
        if errors:
            fail("; ".join(errors[:3]))
        receipts.append((path, receipt))
    return receipts


def normalized_receipt_artifact_path(root: Path, receipt: dict[str, Any]) -> str:
    artifact = receipt["artifacts"][0]
    normalized, _resolved = resolve_repo_path(root, artifact["path"])
    return normalized


def latest_special_receipt(
    candidates: list[tuple[Path, dict[str, Any]]], label: str
) -> tuple[Path, dict[str, Any]]:
    if not candidates:
        fail(f"missing durable {label} receipt")
    highest_revision = max(receipt["pointer_revision"] for _path, receipt in candidates)
    latest = [
        item for item in candidates
        if item[1]["pointer_revision"] == highest_revision
    ]
    if len(latest) != 1:
        fail(f"durable {label} receipts have an ambiguous latest revision")
    return latest[0]


def require_accepted_feature_decision_receipt(
    root: Path, feature_id: str, artifact_path: str,
    receipts: list[tuple[Path, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    normalized_artifact = require_repo_file(
        root, artifact_path, "feature acceptance decision"
    )
    candidates = [
        (path, receipt)
        for path, receipt in (
            special_decision_receipts(root) if receipts is None else receipts
        )
        if receipt["receipt_type"] == "feature_acceptance_decision"
        and str(receipt["work_id"]).lower() == feature_id.lower()
        and normalized_receipt_artifact_path(root, receipt) == normalized_artifact
    ]
    receipt_path, receipt = latest_special_receipt(
        candidates, f"accepted feature decision for {feature_id}"
    )
    if receipt["decision"] != "accepted":
        fail(f"latest durable feature decision for {feature_id} is not accepted")
    artifact = receipt["artifacts"][0]
    current_digest = sha256_file(root / normalized_artifact)
    if current_digest != artifact["result_sha256"]:
        fail(f"durable accepted feature decision artifact hash is stale: {normalized_artifact}")
    fields = markdown_fields(root / normalized_artifact)
    require_decision_field(fields, "Work item", feature_id)
    require_decision_field(fields, "Human decision", "Accepted")
    require_decision_field(fields, "Decided by", str(receipt["decided_by"]))
    require_decision_field(fields, "Decision date", str(receipt["decided_on"]), date=True)
    require_decision_field(fields, "Decision evidence", str(receipt["evidence"]))
    if not receipt_path.is_file():
        fail(f"durable accepted feature decision receipt is missing: {receipt_path}")
    return receipt


def validate_release_result_receipt_evidence(
    root: Path, receipt: dict[str, Any]
) -> tuple[str, str]:
    raw_path, separator, recorded_digest = str(receipt["evidence"]).rpartition("#")
    if not separator or not re.fullmatch(r"[0-9a-f]{64}", recorded_digest):
        fail("release-result decision receipt evidence must be PATH#SHA256")
    normalized, actual_digest = validate_release_receipt(
        root, raw_path, str(receipt["work_id"]), str(receipt["decision"])
    )
    if actual_digest != recorded_digest:
        fail(f"release-result decision receipt evidence hash is stale: {normalized}")
    return normalized, actual_digest


def validate_special_decision_bindings(
    root: Path,
    receipts: list[tuple[Path, dict[str, Any]]] | None = None,
) -> None:
    if receipts is None:
        receipts = special_decision_receipts(root)
    feature_groups: dict[
        tuple[str, str], list[tuple[Path, dict[str, Any]]]
    ] = {}
    release_groups: dict[
        tuple[str, str], list[tuple[Path, dict[str, Any]]]
    ] = {}
    for path, receipt in receipts:
        key = (
            str(receipt["work_id"]).lower(),
            normalized_receipt_artifact_path(root, receipt),
        )
        if receipt["receipt_type"] == "feature_acceptance_decision":
            feature_groups.setdefault(key, []).append((path, receipt))
        else:
            release_groups.setdefault(key, []).append((path, receipt))

    for (feature_id, artifact_path), candidates in feature_groups.items():
        _path, latest = latest_special_receipt(
            candidates, f"feature decision for {feature_id}"
        )
        if latest["decision"] == "accepted":
            require_accepted_feature_decision_receipt(
                root, feature_id, artifact_path, receipts
            )

    for (release_id, artifact_path), candidates in release_groups.items():
        ordered = sorted(
            candidates, key=lambda item: (item[1]["pointer_revision"], item[0].name)
        )
        for _path, receipt in ordered:
            if receipt["receipt_type"] != "release_result":
                continue
            validate_release_result_receipt_evidence(root, receipt)
            reviewed_digest = receipt["artifacts"][0]["reviewed_sha256"]
            prior_authorizations = [
                candidate
                for candidate in ordered
                if candidate[1]["receipt_type"] == "release_authorization"
                and candidate[1]["pointer_revision"] < receipt["pointer_revision"]
                and candidate[1]["artifacts"][0]["result_sha256"] == reviewed_digest
            ]
            if not prior_authorizations:
                fail(
                    f"release-result receipt for {release_id} is not chained to a prior authorization"
                )

        _latest_path, latest = latest_special_receipt(
            candidates, f"release decision for {release_id}"
        )
        artifact = latest["artifacts"][0]
        must_bind_current = (
            latest["receipt_type"] == "release_authorization"
            or latest["decision"] == "succeeded"
        )
        if not must_bind_current:
            continue
        current_digest = sha256_file(root / artifact_path)
        if current_digest != artifact["result_sha256"]:
            fail(f"durable release decision artifact hash is stale: {artifact_path}")
        fields = markdown_fields(root / artifact_path)
        require_decision_field(fields, "Release ID", release_id)
        if latest["receipt_type"] == "release_authorization":
            authorization = latest
        else:
            authorization = max(
                (
                    candidate[1]
                    for candidate in ordered
                    if candidate[1]["receipt_type"] == "release_authorization"
                    and candidate[1]["pointer_revision"] < latest["pointer_revision"]
                    and candidate[1]["artifacts"][0]["result_sha256"]
                    == artifact["reviewed_sha256"]
                ),
                key=lambda receipt: receipt["pointer_revision"],
            )
        require_decision_field(fields, "Human readiness decision", "Authorized")
        require_decision_field(
            fields, "Authorization evidence", str(authorization["evidence"])
        )
        require_decision_field(fields, "Authorized by", str(authorization["decided_by"]))
        require_decision_field(
            fields, "Authorized on", str(authorization["decided_on"]), date=True
        )
        if latest["receipt_type"] == "release_result":
            execution_path, execution_digest = validate_release_result_receipt_evidence(
                root, latest
            )
            require_decision_field(
                fields, "Execution", str(latest["decision"]).replace("_", " ").title()
            )
            require_decision_field(fields, "Execution evidence", execution_path)
            require_decision_field(
                fields, "Execution evidence SHA-256", execution_digest
            )
            require_decision_field(fields, "Confirmed by", str(latest["decided_by"]))
            require_decision_field(
                fields, "Confirmed on", str(latest["decided_on"]), date=True
            )


def append_evidence(state: dict[str, Any], path: str, digest: str) -> None:
    evidence_by_path = {
        item["path"]: dict(item)
        for item in state.get("evidence", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    evidence_by_path[path] = {"path": path, "sha256": digest}
    if len(evidence_by_path) > EVIDENCE_LIMIT:
        fail(f"evidence limit exceeded ({EVIDENCE_LIMIT})")
    state["evidence"] = [evidence_by_path[key] for key in sorted(evidence_by_path)]


def decision_receipt_path(state: dict[str, Any], receipt_digest: str) -> str:
    active = state["active_work"]
    raw_parts = [str(active["kind"]), str(active["id"]), str(active["stage"])]
    slug_parts = [
        re.sub(r"[^a-z0-9._-]+", "-", value.lower()).strip("-.") or "item"
        for value in raw_parts
    ]
    slug = "-".join(slug_parts)[:80].rstrip("-.") or "decision"
    return (
        f".specify/decisions/{state['revision'] + 1:06d}-{slug}-"
        f"{receipt_digest}.yaml"
    )


def build_special_decision_receipt(
    state: dict[str, Any], *, receipt_type: str, decision: str,
    decided_by: str, decided_on: str, evidence: str, role: str,
    artifact: str, reviewed_sha256: str, result_sha256: str,
) -> tuple[str, bytes, str]:
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": receipt_type,
        "pointer_revision": state["revision"] + 1,
        "work_kind": state["active_work"]["kind"],
        "work_id": state["active_work"]["id"],
        "stage": state["active_work"]["stage"],
        "decision": decision,
        "decided_by": decided_by,
        "decided_on": decided_on,
        "evidence": evidence,
        "artifacts": [
            {
                "role": role,
                "path": artifact,
                "reviewed_sha256": reviewed_sha256,
                "result_sha256": result_sha256,
            }
        ],
    }
    rendered = yaml.safe_dump(
        receipt, sort_keys=False, allow_unicode=True, width=1000
    ).encode("utf-8")
    digest = hashlib.sha256(rendered).hexdigest()
    return decision_receipt_path(state, digest), rendered, digest


def commit_decision_receipt_and_state(
    root: Path,
    state: dict[str, Any],
    relative_receipt: str,
    receipt_rendered: bytes,
) -> None:
    errors = validate_state(state, root, False)
    if errors:
        fail("refusing to commit invalid workflow pointer: " + "; ".join(errors[:8]))
    receipt_path = root / relative_receipt
    if receipt_path.exists():
        fail(f"decision receipt already exists: {relative_receipt}")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    state_path = pointer_path(root)
    receipt_temporary = receipt_path.with_suffix(receipt_path.suffix + ".tmp")
    state_temporary = state_path.with_suffix(state_path.suffix + ".tmp")
    receipt_temporary.write_bytes(receipt_rendered)
    state_temporary.write_bytes(
        yaml.safe_dump(state, sort_keys=False, allow_unicode=True, width=1000).encode("utf-8")
    )
    os.replace(receipt_temporary, receipt_path)
    try:
        os.replace(state_temporary, state_path)
    except BaseException:
        receipt_path.unlink(missing_ok=True)
        raise


def render_unresolved_markdown_fields(
    path: Path, replacements: dict[str, str], expected_digest: str
) -> tuple[bytes, str]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_digest:
        fail(f"gate artifact changed while applying decision: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"decision artifact must be UTF-8: {path}: {exc}")
    lines = text.splitlines(keepends=True)
    found: set[str] = set()
    for position, raw_line in enumerate(lines):
        body = raw_line.rstrip("\r\n")
        ending = raw_line[len(body) :]
        match = FIELD_PATTERN.match(body.strip())
        if not match:
            continue
        label, current = match.group(1).strip(), match.group(2).strip()
        if label not in replacements:
            continue
        if label in found:
            fail(f"duplicate decision field in {path.name}: {label}")
        if not (
            current.lower() in PLACEHOLDER_VALUES
            or "{{" in current
            or "}}" in current
        ):
            fail(f"decision field is already resolved: {label}")
        lines[position] = f"**{label}**: {replacements[label]}{ending}"
        found.add(label)
    missing = sorted(set(replacements) - found)
    if missing:
        fail(f"decision artifact is missing fields: {missing}")
    rendered = "".join(lines).encode("utf-8")
    return rendered, hashlib.sha256(rendered).hexdigest()


def commit_decision_artifact_and_state(
    root: Path, state: dict[str, Any], artifact_path: Path, rendered: bytes
) -> None:
    state_path = pointer_path(root)
    errors = validate_state(state, root, False)
    if errors:
        fail("refusing to commit invalid workflow pointer: " + "; ".join(errors[:8]))
    original = artifact_path.read_bytes()
    artifact_temporary = artifact_path.with_suffix(artifact_path.suffix + ".decision.tmp")
    state_temporary = state_path.with_suffix(state_path.suffix + ".tmp")
    state_rendered = yaml.safe_dump(
        state, sort_keys=False, allow_unicode=True, width=1000
    ).encode("utf-8")
    artifact_temporary.write_bytes(rendered)
    state_temporary.write_bytes(state_rendered)
    os.replace(artifact_temporary, artifact_path)
    try:
        os.replace(state_temporary, state_path)
    except BaseException:
        restore = artifact_path.with_suffix(artifact_path.suffix + ".restore.tmp")
        restore.write_bytes(original)
        os.replace(restore, artifact_path)
        raise
    rebuild_index(root)


def commit_decision_artifact_receipt_and_state(
    root: Path, state: dict[str, Any], artifact_path: Path, artifact_rendered: bytes,
    relative_receipt: str, receipt_rendered: bytes,
) -> None:
    errors = validate_state(state, root, False)
    if errors:
        fail("refusing to commit invalid workflow pointer: " + "; ".join(errors[:8]))
    receipt_path = root / relative_receipt
    if receipt_path.exists():
        fail(f"decision receipt already exists: {relative_receipt}")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    state_path = pointer_path(root)
    original_artifact = artifact_path.read_bytes()
    artifact_temporary = artifact_path.with_suffix(artifact_path.suffix + ".decision.tmp")
    receipt_temporary = receipt_path.with_suffix(receipt_path.suffix + ".tmp")
    state_temporary = state_path.with_suffix(state_path.suffix + ".tmp")
    artifact_temporary.write_bytes(artifact_rendered)
    receipt_temporary.write_bytes(receipt_rendered)
    state_temporary.write_bytes(
        yaml.safe_dump(state, sort_keys=False, allow_unicode=True, width=1000).encode("utf-8")
    )
    artifact_replaced = False
    receipt_replaced = False
    try:
        os.replace(artifact_temporary, artifact_path)
        artifact_replaced = True
        os.replace(receipt_temporary, receipt_path)
        receipt_replaced = True
        os.replace(state_temporary, state_path)
    except BaseException:
        if receipt_replaced:
            receipt_path.unlink(missing_ok=True)
        if artifact_replaced:
            restore = artifact_path.with_suffix(artifact_path.suffix + ".restore.tmp")
            restore.write_bytes(original_artifact)
            os.replace(restore, artifact_path)
        raise
    rebuild_index(root)


def require_gate_artifact(
    state: dict[str, Any], root: Path, role: str, requested_path: str
) -> tuple[str, str, dict[str, str]]:
    gate_roles = set(state.get("human_gate", {}).get("artifact_roles", []))
    if role not in gate_roles:
        fail(f"pending gate requires artifact role: {role}")
    registered = artifact_role_path(state, role)
    if not registered:
        fail(f"artifact role has no registered path: {role}")
    requested = require_repo_file(root, requested_path, role)
    normalized_registered = require_repo_file(root, registered, role)
    if requested != normalized_registered:
        fail(f"--artifact must match the registered {role} path: {normalized_registered}")
    digest = sha256_file(root / requested)
    expected = state.get("human_gate", {}).get("artifact_hashes", {}).get(role)
    if digest != expected:
        fail(f"gate artifact changed after review: {requested}; restore or record-output again")
    verify_gate_hashes(state, root)
    return requested, digest, markdown_fields(root / requested)


def transition(state: dict[str, Any], operation: str) -> None:
    previous = {
        "revision": state["revision"],
        "stage": state["active_work"]["stage"],
        "status": state["active_work"]["status"],
        "operation": operation,
    }
    state["revision"] += 1
    state["last_transition"] = previous


def parse_pairs(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        key, separator, path = value.partition("=")
        if not separator or not key or not path:
            fail(f"expected KEY=PATH, got: {value}")
        if not ROLE_PATTERN.fullmatch(key):
            fail(f"artifact role must match {ROLE_PATTERN.pattern}: {key}")
        if len(key) > ROLE_TEXT_LIMIT:
            fail(f"artifact role must be at most {ROLE_TEXT_LIMIT} characters: {key}")
        if key in parsed:
            fail(f"duplicate artifact role: {key}")
        parsed[key] = path.replace("\\", "/")
    return parsed


def resolve_limit(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit must be an integer") from exc
    if not 1 <= parsed <= 50:
        raise argparse.ArgumentTypeError("limit must be between 1 and 50")
    return parsed


def allowed_actions(values: list[str]) -> list[dict[str, Any]]:
    if len(values) > NEXT_ACTION_LIMIT:
        fail(f"at most {NEXT_ACTION_LIMIT} next actions may be recorded")
    if any(
        not value
        or len(value) > POINTER_TEXT_LIMIT
        or "\n" in value
        or "\r" in value
        for value in values
    ):
        fail(
            f"next actions must be non-empty, single-line, and at most {POINTER_TEXT_LIMIT} characters"
        )
    return [{"command": value, "requires_human": True} for value in values]


def command_init(args: argparse.Namespace, root: Path) -> None:
    path = pointer_path(root)
    if path.exists() and not args.force:
        fail(f"pointer already exists: {path}; use --force only with explicit authorization")
    if not bounded_text(args.project_id):
        fail("project-id must be a bounded single-line string")
    state = state_template(args.project_id, args.profile)
    write_valid_state(path, state, root)
    rebuild_index(root)
    print(path.relative_to(root).as_posix())


def command_status(_args: argparse.Namespace, root: Path) -> None:
    state = read_valid_state(root, check_paths=False)
    view = {
        "revision": state.get("revision"),
        "project": state.get("project"),
        "active_work": state.get("active_work"),
        "human_gate": state.get("human_gate"),
        "canonical": {key: value for key, value in state.get("canonical", {}).items() if value},
        "canonical_status": state.get("canonical_status"),
        "canonical_hashes": state.get("canonical_hashes"),
        "active_artifacts": state.get("active_artifacts"),
        "context_ids": state.get("context_ids"),
        "next": state.get("next"),
        "blockers": state.get("blockers"),
    }
    print(yaml.safe_dump(view, sort_keys=False, allow_unicode=True).rstrip())


def command_validate(args: argparse.Namespace, root: Path) -> None:
    state = read_state(root)
    errors = validate_state(state, root, args.check_paths)
    if args.check_paths:
        errors.extend(validate_index(read_index(root), root))
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("valid")


def command_start(args: argparse.Namespace, root: Path) -> None:
    path = pointer_path(root)
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    require_approved_canonical_integrity(state, root)
    if args.kind not in KINDS:
        fail(f"unknown work kind: {args.kind}")
    if args.stage not in STAGE_KINDS:
        fail(f"unknown lifecycle stage: {args.stage}")
    if args.stage in NON_STARTABLE_STAGES:
        fail(f"stage {args.stage} is recorded by its owning review and cannot be started")
    if args.kind not in STAGE_KINDS[args.stage]:
        fail(f"stage {args.stage} is not valid for work kind {args.kind}")
    if args.stage == "spike_result":
        approved_spike_definition(state, root, args.work_id)
    current_work = state.get("active_work", {})
    current_status = current_work.get("status")
    current_gate = state.get("human_gate", {}).get("status")
    if current_gate == "pending" and current_status != "not_started":
        fail("resolve the pending human gate before starting different work")
    if current_status in CANDIDATE_STATUSES:
        fail(f"resolve candidate state {current_status} before starting different work")
    same_work = current_work.get("kind") == args.kind and current_work.get("id") == args.work_id
    if not same_work and current_status == "in_progress":
        fail("block or complete the active work before switching to a different work item")
    if same_work and current_status == "in_progress":
        if current_work.get("stage") == args.stage:
            print(state["revision"])
            return
        fail("the requested work item is already in progress at a different stage")
    if same_work and current_status in {"accepted", "released"}:
        fail("accepted or released work is immutable; start a successor work item")
    if args.stage == "implementation":
        if not same_work:
            fail("implementation must continue the same work item after pre-implementation review")
        require_approved_active_artifact(state, root, "pre_implementation")
    state["active_work"] = {
        "kind": args.kind,
        "id": args.work_id,
        "stage": args.stage,
        "status": "in_progress",
    }
    state["human_gate"] = {
        "name": f"review_{args.stage}",
        "status": "not_required",
        "owner": "human",
        "artifact_roles": [],
        "artifact_hashes": {},
    }
    state["next"] = {"allowed": [], "recommended": None, "auto_invoke": False}
    if not same_work:
        state["active_artifacts"] = []
        state["context_ids"] = []
    state["evidence"] = []
    state["blockers"] = []
    transition(state, "start")
    write_valid_state(path, state, root)
    print(state["revision"])


def command_confirm_profile(args: argparse.Namespace, root: Path) -> None:
    path = pointer_path(root)
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    require_approved_canonical_integrity(state, root)
    if state.get("human_gate", {}).get("status") == "pending":
        fail("resolve the pending human gate before confirming the project profile")
    roadmap = state.get("canonical", {}).get("roadmap")
    if not roadmap or state.get("canonical_status", {}).get("roadmap") != "approved":
        fail("confirm-profile requires an indexed approved roadmap for sizing")
    roadmap_path = require_repo_file(root, roadmap, "roadmap")
    sizing_fields = markdown_fields(root / roadmap_path)
    require_decision_field(sizing_fields, "Profile sizing", args.profile)
    sizing_evidence = require_decision_field(sizing_fields, "Sizing evidence")
    if not (
        ID_PATTERN.search(sizing_evidence)
        or re.search(r"https?://\S+", sizing_evidence)
        or re.search(r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+(?:#[A-Za-z0-9_.-]+)?", sizing_evidence)
        or re.search(r"\b[0-9a-f]{7,64}\b", sizing_evidence, re.IGNORECASE)
    ):
        fail("Sizing evidence must cite a stable ID, path/anchor, URL, or revision hash")
    feature_count = require_integer_field(sizing_fields, "Feature count", minimum=1)
    deployable_count = require_integer_field(sizing_fields, "Deployable count", minimum=1)
    datastore_count = require_integer_field(sizing_fields, "Datastore count")
    team_count = require_integer_field(sizing_fields, "Owning team count", minimum=1)
    constraint = require_decision_field(
        sizing_fields, "Regulatory/audit/contractual constraint"
    ).lower()
    if constraint not in {"yes", "no", "unknown"}:
        fail("Regulatory/audit/contractual constraint must be yes, no, or unknown")
    roadmap_text = (root / roadmap_path).read_text(encoding="utf-8", errors="replace")
    indexed_features = {value.upper() for value in re.findall(r"\bF-?\d+\b", roadmap_text)}
    if len(indexed_features) != feature_count:
        fail(
            f"Feature count is {feature_count} but roadmap contains "
            f"{len(indexed_features)} unique feature IDs"
        )
    if args.profile == "lite":
        lite_failures: list[str] = []
        if feature_count > 8:
            lite_failures.append("feature count exceeds 8")
        if deployable_count != 1:
            lite_failures.append("deployable count is not 1")
        if datastore_count > 1:
            lite_failures.append("datastore count exceeds 1")
        if team_count != 1:
            lite_failures.append("owning team count is not 1")
        if constraint != "no":
            lite_failures.append("regulatory/audit/contractual constraint is not no")
        if lite_failures:
            fail("roadmap is not eligible for lite: " + "; ".join(lite_failures))
    state["project"]["profile"] = args.profile
    state["project"]["profile_status"] = "confirmed"
    transition(state, "confirm-profile")
    write_valid_state(path, state, root)
    print(state["revision"])


def command_record_output(args: argparse.Namespace, root: Path) -> None:
    path = pointer_path(root)
    state = read_valid_state(root, check_paths=False)
    require_revision(state, args.expect_revision)
    next_actions = allowed_actions(args.next)
    if args.status not in CANDIDATE_STATUSES:
        fail(f"record-output status must be one of {sorted(CANDIDATE_STATUSES)}")
    if len(args.evidence) > EVIDENCE_LIMIT:
        fail(f"at most {EVIDENCE_LIMIT} evidence paths may be recorded")
    if len(args.context_id) > CONTEXT_ID_LIMIT:
        fail(f"at most {CONTEXT_ID_LIMIT} context IDs may be recorded")
    if len(args.blocker) > BLOCKER_LIMIT or any(
        not value
        or len(value) > POINTER_TEXT_LIMIT
        or "\n" in value
        or "\r" in value
        for value in args.blocker
    ):
        fail(
            f"at most {BLOCKER_LIMIT} non-empty single-line blockers of {POINTER_TEXT_LIMIT} characters may be recorded"
        )
    active_kind = state.get("active_work", {}).get("kind")
    if args.stage not in STAGE_KINDS or active_kind not in STAGE_KINDS[args.stage]:
        fail(f"stage {args.stage} is not valid for work kind {active_kind}")
    current_status = state.get("active_work", {}).get("status")
    current_stage = state.get("active_work", {}).get("stage")
    if current_status != "in_progress" and current_status != args.status:
        fail(f"cannot record {args.status} from current status {current_status}")
    allowed_stage_advance = (
        current_status == "in_progress"
        and current_stage == "implementation"
        and args.stage == "post_implement"
    ) or (
        current_status == "ready_for_acceptance"
        and current_stage == "post_implement"
        and args.stage == "acceptance"
    )
    if args.stage != current_stage and not allowed_stage_advance:
        fail(f"cannot record stage {args.stage} from active stage {current_stage}")
    artifacts = parse_pairs(args.artifact)
    artifact_roles = set(artifacts)
    for role in artifact_roles & set(WORK_ROLE_STAGES):
        if args.stage not in WORK_ROLE_STAGES[role]:
            fail(f"artifact role {role} is not owned by stage {args.stage}")
    if args.stage == "pre_implement" and artifact_roles != {"pre_implementation"}:
        fail("pre_implement candidate must contain exactly role pre_implementation")
    if args.stage == "post_implement":
        expected_status = "ready_for_acceptance" if active_kind == "feature" else "ready_for_review"
        if args.status != expected_status or artifact_roles != {"verification"}:
            fail(
                "post_implement candidate must contain exactly role verification "
                f"with status {expected_status}"
            )
        require_approved_active_artifact(state, root, "pre_implementation")
    if args.stage == "acceptance" and artifact_roles != {"acceptance"}:
        fail("acceptance candidate must contain exactly role acceptance")
    if args.stage == "release_readiness" and (
        active_kind != "release"
        or args.status != "ready_for_release"
        or artifact_roles != {"release_readiness"}
    ):
        fail(
            "release-readiness candidate requires kind release, status ready_for_release, "
            "and exactly role release_readiness"
        )
    if args.stage == "spike_result" and (
        args.status != "ready_for_review" or artifact_roles != {"spike_result"}
    ):
        fail("spike-result candidate must contain exactly role spike_result at ready_for_review")
    prior_gate_roles = set(state["human_gate"]["artifact_roles"])
    amendment_roles = {
        role for role in artifacts if role in AMENDMENT_ROLES or role.startswith("adr-")
    }
    promoted_roles = {
        role for role in artifacts
        if role in SEMANTIC_CANONICAL_KEYS
        and state.get("canonical_status", {}).get(role) == "approved"
    }
    refresh_roles = {
        role for role in artifacts
        if role in REFRESHABLE_CANONICAL_ROLES
        and state.get("canonical_status", {}).get(role) == "approved"
    }
    promotes_canonical = bool(promoted_roles)
    for role in refresh_roles:
        if args.stage != CANONICAL_ROLE_STAGES[role]:
            fail(f"canonical refresh role {role} requires stage {CANONICAL_ROLE_STAGES[role]}")
    require_approved_canonical_integrity(state, root, promoted_roles | refresh_roles)
    if promotes_canonical:
        if (
            active_kind != "change_request"
            or current_status != "ready_for_review"
            or state.get("human_gate", {}).get("status") != "pending"
        ):
            fail("approved canonical artifacts require a reviewed change-request candidate")
        if state.get("blockers"):
            fail("cannot apply a canonical amendment while blockers remain")
        expected_promotion_stages = {
            "change_request" if role in {"discovery", "requirements", "roadmap"}
            else "architecture"
            for role in promoted_roles
        }
        if args.stage not in expected_promotion_stages or len(expected_promotion_stages) != 1:
            fail("canonical amendment stage does not match its owning product/architecture route")
        required_primary: set[str] = set()
        if promoted_roles & {"discovery", "requirements", "roadmap"}:
            required_primary.add("product_amendment")
        if "architecture" in promoted_roles:
            required_primary.add("architecture_amendment")
        prior_amendment_roles = {
            role for role in prior_gate_roles
            if role in AMENDMENT_ROLES or role.startswith("adr-")
        }
        if not required_primary.issubset(prior_gate_roles):
            fail("canonical amendment gate lacks its owning reviewed amendment proposal")
        if prior_gate_roles != prior_amendment_roles:
            fail("canonical amendment gate contains a non-amendment role")
        if amendment_roles != prior_amendment_roles:
            fail("canonical promotion cannot add or omit amendment roles after proposal review")
        if artifact_roles != prior_gate_roles | promoted_roles:
            fail(
                "canonical promotion must contain exactly the reviewed amendment roles "
                "and promoted canonical roles"
            )
        for primary_role in required_primary:
            proposal_path = artifact_role_path(state, primary_role)
            if not proposal_path:
                fail(f"reviewed amendment proposal has no path: {primary_role}")
            normalized = require_repo_file(root, proposal_path, primary_role)
            expected = state["human_gate"]["artifact_hashes"].get(primary_role)
            if sha256_file(root / normalized) != expected:
                fail(f"reviewed amendment proposal changed before canonical promotion: {normalized}")
    if args.status == "ready_for_release" and (
        active_kind != "release"
        or args.stage != "release_readiness"
        or "release_readiness" not in artifacts
    ):
        fail("ready_for_release requires release/release_readiness and role release_readiness")
    for canonical_role in set(artifacts) & PROJECT_ARTIFACT_KEYS:
        if canonical_role in promoted_roles or canonical_role in refresh_roles:
            continue
        expected_stage = CANONICAL_ROLE_STAGES[canonical_role]
        if active_kind != "project" or args.stage != expected_stage:
            fail(
                f"canonical role {canonical_role} is owned by project stage {expected_stage}"
            )
    if "pre_implementation" in artifacts and (
        args.stage != "pre_implement"
        or args.status != "ready_for_review"
        or active_kind not in IMPLEMENTATION_KINDS
    ):
        fail("pre_implementation is only valid for an implementation item at pre_implement ready_for_review")
    if "pre_implementation" in artifacts:
        for prerequisite_role in ("spec", "plan", "tasks", "requirements_checklist"):
            require_approved_active_artifact(state, root, prerequisite_role)
    if "acceptance" in artifacts and (
        args.stage != "acceptance"
        or args.status != "ready_for_acceptance"
        or active_kind != "feature"
    ):
        fail("acceptance is only valid for feature/acceptance ready_for_acceptance")
    if args.status == "ready_for_acceptance":
        if active_kind != "feature":
            fail("ready_for_acceptance is reserved for kind feature")
        required_role = "acceptance" if args.stage == "acceptance" else "verification"
        if args.stage not in {"post_implement", "acceptance"} or required_role not in artifacts:
            fail(
                f"ready_for_acceptance at stage {args.stage} requires artifact role {required_role}"
            )
        if args.stage == "post_implement":
            if (
                current_status == "in_progress"
                and state.get("active_work", {}).get("stage") != "implementation"
            ):
                fail("post_implement must continue the active implementation stage")
            require_approved_active_artifact(state, root, "pre_implementation")
        else:
            if current_status != "ready_for_acceptance":
                fail("acceptance review must extend the active post_implement candidate")
            require_approved_active_artifact(state, root, "spec")
            require_active_artifact_status(
                state, root, "verification", {"ready_for_acceptance"}
            )
    active_by_role = {
        item["role"]: dict(item)
        for item in state.get("active_artifacts", [])
        if (
            isinstance(item, dict)
            and item.get("role")
            and item.get("path")
            and item.get("status")
            and item.get("sha256")
        )
    }
    output_roles: list[str] = []
    output_hashes: dict[str, str] = {}
    for key, relative in artifacts.items():
        normalized = require_repo_file(root, relative, "artifact")
        if key in PROJECT_ARTIFACT_KEYS:
            bundle_errors = validate_approved_bundle(
                root / normalized,
                root,
                role=key,
                require_declaration=key in BUNDLE_DECLARATION_ROLES,
            )
            if bundle_errors:
                fail(f"invalid canonical bundle: {'; '.join(bundle_errors[:3])}")
        expected_inputs = None
        if key == "pre_implementation":
            expected_inputs = {
                role: artifact_role_path(state, role) or ""
                for role in ("spec", "plan", "tasks", "requirements_checklist")
            }
        validate_candidate_artifact(
            key,
            root / normalized,
            root,
            state["active_work"]["id"],
            state["active_work"]["kind"],
            expected_inputs,
        )
        if key == "release_readiness" and require_decision_field(
            markdown_fields(root / normalized), "Review status"
        ).lower() == "not_ready":
            fail("not_ready release readiness must use block, not a pending release gate")
        if key == "acceptance":
            candidate_spec = require_decision_field(markdown_fields(root / normalized), "Spec")
            candidate_spec_path = require_repo_file(root, candidate_spec, "acceptance spec")
            registered_spec = artifact_role_path(state, "spec")
            if candidate_spec_path != registered_spec:
                fail(
                    f"acceptance Spec must match approved registered spec: {registered_spec}"
                )
        digest = sha256_file(root / normalized)
        if key == "artifact_index":
            fail("artifact_index is derived and cannot be recorded as semantic output")
        if key in PROJECT_ARTIFACT_KEYS:
            if state.get("canonical_status", {}).get(key) == "approved":
                if normalized != state.get("canonical", {}).get(key):
                    fail(f"canonical amendment cannot redirect approved role {key}")
            state.setdefault("canonical", {})[key] = normalized
            state.setdefault("canonical_status", {})[key] = args.status
            state.setdefault("canonical_hashes", {})[key] = digest
        else:
            existing = active_by_role.get(key)
            if existing and existing.get("status") in {"accepted", "released"}:
                fail(f"cannot downgrade final artifact role: {key}")
            active_by_role[key] = {
                "role": key,
                "path": normalized,
                "status": args.status,
                "sha256": digest,
            }
        output_roles.append(key)
        output_hashes[key] = digest
    if len(active_by_role) > ACTIVE_ARTIFACT_LIMIT:
        fail(f"active artifact limit exceeded ({ACTIVE_ARTIFACT_LIMIT})")
    state["active_artifacts"] = [active_by_role[role] for role in sorted(active_by_role)]
    evidence: list[dict[str, str]] = []
    for relative in args.evidence:
        normalized = require_repo_file(root, relative, "evidence")
        evidence.append({"path": normalized, "sha256": sha256_file(root / normalized)})
    state["active_work"]["stage"] = args.stage
    state["active_work"]["status"] = args.status
    state["human_gate"] = {
        "name": args.gate or f"approve_{args.stage}",
        "status": "pending",
        "owner": "human",
        "artifact_roles": sorted(output_roles),
        "artifact_hashes": {role: output_hashes[role] for role in sorted(output_roles)},
    }
    state["next"] = {
        "allowed": next_actions,
        "recommended": args.next[0] if args.next else None,
        "auto_invoke": False,
    }
    state["evidence"] = evidence
    context_ids = {value.upper() for value in args.context_id}
    invalid_ids = sorted(value for value in context_ids if not ID_PATTERN.fullmatch(value))
    if invalid_ids:
        fail(f"invalid context IDs: {invalid_ids}")
    if context_ids:
        state["context_ids"] = sorted(context_ids)
    state["blockers"] = list(args.blocker)
    transition(state, "record-output")
    write_valid_state(path, state, root)
    rebuild_index(root)
    print(state["revision"])


def command_block(args: argparse.Namespace, root: Path) -> None:
    path = pointer_path(root)
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    next_actions = allowed_actions(args.next)
    if state.get("human_gate", {}).get("status") == "pending":
        fail("resolve the pending human gate before recording a different blocker")
    if not args.blocker:
        fail("at least one --blocker is required")
    if len(args.blocker) > BLOCKER_LIMIT or any(
        not value
        or len(value) > POINTER_TEXT_LIMIT
        or "\n" in value
        or "\r" in value
        for value in args.blocker
    ):
        fail(
            f"at most {BLOCKER_LIMIT} non-empty single-line blockers of {POINTER_TEXT_LIMIT} characters may be recorded"
        )
    if state.get("active_work", {}).get("status") not in {"in_progress", "blocked"}:
        fail("block only applies to active in-progress or already blocked work")
    stage = args.stage or state["active_work"]["stage"]
    kind = state["active_work"]["kind"]
    if stage not in STAGE_KINDS or kind not in STAGE_KINDS[stage]:
        fail(f"stage {stage} is not valid for work kind {kind}")
    artifacts = parse_pairs(args.artifact)
    artifact_roles = set(artifacts)
    for role in artifact_roles & set(WORK_ROLE_STAGES):
        if stage not in WORK_ROLE_STAGES[role]:
            fail(f"artifact role {role} is not owned by stage {stage}")
    if stage == "pre_implement" and artifact_roles not in (
        set(), {"pre_implementation"}
    ):
        fail("blocked pre_implement may contain only role pre_implementation")
    if stage == "post_implement" and artifact_roles not in (set(), {"verification"}):
        fail("blocked post_implement may contain only role verification")
    if stage == "spike_result" and artifact_roles not in (set(), {"spike_result"}):
        fail("blocked spike_result may contain only role spike_result")
    if stage == "release_readiness" and artifact_roles not in (
        set(), {"release_readiness"}
    ):
        fail("blocked release_readiness may contain only role release_readiness")
    active_by_role = {
        item["role"]: dict(item)
        for item in state.get("active_artifacts", [])
        if isinstance(item, dict) and item.get("role") and item.get("path")
    }
    for role, relative in artifacts.items():
        if role in PROJECT_CANONICAL_KEYS:
            fail(f"block artifacts must use a work-item role, got: {role}")
        normalized = require_repo_file(root, relative, "block artifact")
        validate_block_artifact(
            role,
            root / normalized,
            root,
            state["active_work"]["id"],
            state["active_work"]["kind"],
        )
        active_by_role[role] = {
            "role": role,
            "path": normalized,
            "status": "blocked",
            "sha256": sha256_file(root / normalized),
        }
    if len(active_by_role) > ACTIVE_ARTIFACT_LIMIT:
        fail(f"active artifact limit exceeded ({ACTIVE_ARTIFACT_LIMIT})")
    state["active_artifacts"] = [active_by_role[role] for role in sorted(active_by_role)]
    state["active_work"]["stage"] = stage
    state["active_work"]["status"] = "blocked"
    state["human_gate"] = {
        "name": f"resolve_{state['active_work']['stage']}",
        "status": "not_required",
        "owner": "human",
        "artifact_roles": [],
        "artifact_hashes": {},
    }
    state["next"] = {
        "allowed": next_actions,
        "recommended": args.next[0] if args.next else None,
        "auto_invoke": False,
    }
    state["blockers"] = list(args.blocker)
    transition(state, "block")
    write_valid_state(path, state, root)
    if artifacts:
        rebuild_index(root)
    print(state["revision"])


def command_decide(args: argparse.Namespace, root: Path) -> None:
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    next_actions = allowed_actions(args.next)
    if state.get("human_gate", {}).get("status") != "pending":
        fail("there is no pending human gate")
    current_status = state.get("active_work", {}).get("status")
    if current_status != "ready_for_review":
        fail("generic decide only resolves ready_for_review; use the specialized delivery command")
    if args.decision == "approved" and state.get("blockers"):
        fail("cannot approve while blockers remain")
    verified = verify_gate_hashes(state, root)
    gate_roles = set(state.get("human_gate", {}).get("artifact_roles", []))
    if not gate_roles:
        fail("pending review gate has no artifact roles")
    if args.decision == "approved":
        for role in sorted(gate_roles & PROJECT_ARTIFACT_KEYS):
            bundle_errors = validate_approved_bundle(
                root / verified[role][0],
                root,
                role=role,
                require_declaration=role in BUNDLE_DECLARATION_ROLES,
            )
            if bundle_errors:
                fail(f"cannot approve invalid canonical bundle: {'; '.join(bundle_errors[:3])}")
    decided_by = validated_decision_value("Decided by", args.decided_by)
    decision_date = validated_decision_value(
        "Decision date", args.decision_date, date=True
    )
    decision_evidence = validated_decision_value(
        "Decision evidence", args.decision_evidence
    )
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "pointer_revision": state["revision"] + 1,
        "work_kind": state["active_work"]["kind"],
        "work_id": state["active_work"]["id"],
        "stage": state["active_work"]["stage"],
        "gate": state["human_gate"]["name"],
        "decision": args.decision,
        "decided_by": decided_by,
        "decided_on": decision_date,
        "evidence": decision_evidence,
        "artifacts": [
            {
                "role": role,
                "path": verified[role][0],
                "reviewed_sha256": verified[role][1],
            }
            for role in sorted(gate_roles)
        ],
    }
    receipt_rendered = yaml.safe_dump(
        receipt, sort_keys=False, allow_unicode=True, width=1000
    ).encode("utf-8")
    receipt_digest = hashlib.sha256(receipt_rendered).hexdigest()
    receipt_path = decision_receipt_path(state, receipt_digest)
    result_status = "rejected" if args.decision == "rejected" else "approved"
    state["human_gate"]["status"] = args.decision
    state["active_work"]["status"] = result_status
    for role in gate_roles:
        update_artifact_role(state, role, result_status, verified[role][1])
    state["next"] = {
        "allowed": next_actions,
        "recommended": args.next[0] if args.next else None,
        "auto_invoke": False,
    }
    transition(state, "decide")
    append_evidence(state, receipt_path, receipt_digest)
    commit_decision_receipt_and_state(root, state, receipt_path, receipt_rendered)
    rebuild_index(root)
    print(state["revision"])


def command_record_feature_decision(args: argparse.Namespace, root: Path) -> None:
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    next_actions = allowed_actions(args.next)
    active = state.get("active_work", {})
    if state.get("human_gate", {}).get("status") != "pending":
        fail("there is no pending human gate")
    if active.get("status") != "ready_for_acceptance" or active.get("stage") != "acceptance":
        fail("feature decision requires the active acceptance candidate")
    if active.get("kind") != "feature":
        fail("record-feature-decision requires active work kind feature")
    if set(state.get("human_gate", {}).get("artifact_roles", [])) != {"acceptance"}:
        fail("feature decision gate must contain exactly artifact role acceptance")
    artifact, reviewed_digest, fields = require_gate_artifact(
        state, root, "acceptance", args.artifact
    )
    expected_decision = {
        "accepted": "Accepted",
        "rejected": "Rejected",
        "changes_requested": "Changes requested",
    }[args.decision]
    review_status = require_decision_field(fields, "Review status").lower()
    if review_status not in {"ready", "conditional", "not_ready"}:
        fail("Review status must be ready, conditional, or not_ready")
    if args.decision == "accepted":
        if state.get("blockers"):
            fail("cannot accept while blockers remain")
        if review_status == "not_ready":
            fail("cannot accept an acceptance review marked not_ready")
    decided_by = validated_decision_value("Decided by", args.decided_by)
    decision_date = validated_decision_value(
        "Decision date", args.decision_date, date=True
    )
    decision_evidence = validated_decision_value(
        "Decision evidence", args.decision_evidence
    )
    replacements = {
        "Human decision": expected_decision,
        "Decided by": decided_by,
        "Decision date": decision_date,
        "Decision evidence": decision_evidence,
    }
    rendered, digest = render_unresolved_markdown_fields(
        root / artifact, replacements, reviewed_digest
    )
    receipt_path, receipt_rendered, receipt_digest = build_special_decision_receipt(
        state,
        receipt_type="feature_acceptance_decision",
        decision=args.decision,
        decided_by=decided_by,
        decided_on=decision_date,
        evidence=decision_evidence,
        role="acceptance",
        artifact=artifact,
        reviewed_sha256=reviewed_digest,
        result_sha256=digest,
    )
    result_status = "accepted" if args.decision == "accepted" else "rejected"
    gate_status = "approved" if args.decision == "accepted" else "rejected"
    state["human_gate"]["status"] = gate_status
    state["human_gate"]["artifact_hashes"]["acceptance"] = digest
    state["active_work"]["status"] = result_status
    update_artifact_role(state, "acceptance", result_status, digest)
    state["next"] = {
        "allowed": next_actions,
        "recommended": args.next[0] if args.next else None,
        "auto_invoke": False,
    }
    transition(state, "record-feature-decision")
    append_evidence(state, receipt_path, receipt_digest)
    commit_decision_artifact_receipt_and_state(
        root, state, root / artifact, rendered, receipt_path, receipt_rendered
    )
    print(state["revision"])


def command_authorize_release(args: argparse.Namespace, root: Path) -> None:
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    next_actions = allowed_actions(args.next)
    active = state.get("active_work", {})
    if state.get("human_gate", {}).get("status") != "pending":
        fail("there is no pending human gate")
    if (
        active.get("kind") != "release"
        or active.get("stage") != "release_readiness"
        or active.get("status") != "ready_for_release"
    ):
        fail("release authorization requires the active release-readiness candidate")
    if state.get("blockers"):
        fail("cannot authorize release while blockers remain")
    if set(state.get("human_gate", {}).get("artifact_roles", [])) != {"release_readiness"}:
        fail("release authorization gate must contain exactly artifact role release_readiness")
    artifact, reviewed_digest, fields = require_gate_artifact(
        state, root, "release_readiness", args.artifact
    )
    review_status = require_decision_field(fields, "Review status").lower()
    if review_status not in {"ready", "conditional"}:
        fail("release authorization requires Review status ready or conditional")
    authorization_evidence = validated_decision_value(
        "Authorization evidence", args.authorization_evidence
    )
    authorized_by = validated_decision_value("Authorized by", args.authorized_by)
    authorized_on = validated_decision_value(
        "Authorized on", args.authorized_on, date=True
    )
    replacements = {
        "Human readiness decision": "Authorized",
        "Authorization evidence": authorization_evidence,
        "Authorized by": authorized_by,
        "Authorized on": authorized_on,
    }
    rendered, digest = render_unresolved_markdown_fields(
        root / artifact, replacements, reviewed_digest
    )
    receipt_path, receipt_rendered, receipt_digest = build_special_decision_receipt(
        state,
        receipt_type="release_authorization",
        decision="authorized",
        decided_by=authorized_by,
        decided_on=authorized_on,
        evidence=authorization_evidence,
        role="release_readiness",
        artifact=artifact,
        reviewed_sha256=reviewed_digest,
        result_sha256=digest,
    )
    state["active_work"]["status"] = "release_authorized"
    update_artifact_role(state, "release_readiness", "release_authorized", digest)
    state["human_gate"] = {
        "name": "confirm_release_result",
        "status": "pending",
        "owner": "human",
        "artifact_roles": ["release_readiness"],
        "artifact_hashes": {"release_readiness": digest},
    }
    state["next"] = {
        "allowed": next_actions,
        "recommended": args.next[0] if args.next else None,
        "auto_invoke": False,
    }
    transition(state, "authorize-release")
    append_evidence(state, receipt_path, receipt_digest)
    commit_decision_artifact_receipt_and_state(
        root, state, root / artifact, rendered, receipt_path, receipt_rendered
    )
    print(state["revision"])


def command_record_release_result(args: argparse.Namespace, root: Path) -> None:
    state = read_valid_state(root, check_paths=True)
    require_revision(state, args.expect_revision)
    next_actions = allowed_actions(args.next)
    active = state.get("active_work", {})
    if state.get("human_gate", {}).get("status") != "pending":
        fail("there is no pending human gate")
    if (
        active.get("kind") != "release"
        or active.get("stage") != "release_readiness"
        or active.get("status") != "release_authorized"
    ):
        fail("release result requires a previously authorized active release")
    if set(state.get("human_gate", {}).get("artifact_roles", [])) != {"release_readiness"}:
        fail("release result gate must contain exactly artifact role release_readiness")
    artifact, authorized_digest, fields = require_gate_artifact(
        state, root, "release_readiness", args.artifact
    )
    expected_execution = {
        "succeeded": "Succeeded",
        "failed": "Failed",
        "held": "Held",
        "cancelled": "Cancelled",
    }[args.result]
    require_decision_field(fields, "Human readiness decision", "Authorized")
    require_decision_field(fields, "Authorization evidence")
    if args.result == "succeeded" and state.get("blockers"):
        fail("cannot mark release succeeded while blockers remain")
    execution_receipt_path, execution_receipt_digest = validate_release_receipt(
        root, args.execution_evidence, active["id"], args.result
    )
    confirmed_by = validated_decision_value("Confirmed by", args.confirmed_by)
    confirmed_on = validated_decision_value(
        "Confirmed on", args.confirmed_on, date=True
    )
    replacements = {
        "Execution": expected_execution,
        "Execution evidence": execution_receipt_path,
        "Execution evidence SHA-256": execution_receipt_digest,
        "Confirmed by": confirmed_by,
        "Confirmed on": confirmed_on,
    }
    rendered, digest = render_unresolved_markdown_fields(
        root / artifact, replacements, authorized_digest
    )
    receipt_path, receipt_rendered, receipt_digest = build_special_decision_receipt(
        state,
        receipt_type="release_result",
        decision=args.result,
        decided_by=confirmed_by,
        decided_on=confirmed_on,
        evidence=f"{execution_receipt_path}#{execution_receipt_digest}",
        role="release_readiness",
        artifact=artifact,
        reviewed_sha256=authorized_digest,
        result_sha256=digest,
    )
    result_status = "released" if args.result == "succeeded" else "rejected"
    gate_status = "approved" if args.result == "succeeded" else "rejected"
    state["human_gate"]["status"] = gate_status
    state["human_gate"]["artifact_hashes"]["release_readiness"] = digest
    state["active_work"]["status"] = result_status
    update_artifact_role(state, "release_readiness", result_status, digest)
    append_evidence(state, execution_receipt_path, execution_receipt_digest)
    state["next"] = {
        "allowed": next_actions,
        "recommended": args.next[0] if args.next else None,
        "auto_invoke": False,
    }
    transition(state, "record-release-result")
    append_evidence(state, receipt_path, receipt_digest)
    commit_decision_artifact_receipt_and_state(
        root, state, root / artifact, rendered, receipt_path, receipt_rendered
    )
    print(state["revision"])


def candidate_artifacts(root: Path) -> list[Path]:
    results: set[Path] = set()
    for relative in ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"):
        path = root / relative
        if path.is_file():
            results.add(path)
    for directory in ("doc", "specs"):
        base = root / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".toml"}:
                results.add(path)
    constitution = root / ".specify" / "memory" / "constitution.md"
    if constitution.is_file():
        results.add(constitution)
    decision_directory = root / ".specify" / "decisions"
    if decision_directory.is_dir():
        for path in decision_directory.rglob("*.yaml"):
            if path.is_file():
                results.add(path)
    contained: list[Path] = []
    resolved_root = root.resolve()
    for path in results:
        try:
            path.resolve().relative_to(resolved_root)
        except ValueError:
            continue
        contained.append(path)
    return sorted(contained, key=lambda item: item.relative_to(root).as_posix())


def validate_historical_release_result_file(path: Path, root: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "**Release ID**:" not in text or "**Execution**:" not in text:
        return
    fields = markdown_fields(path)
    execution = fields.get("Execution", "").strip()
    if (
        not execution
        or execution.lower() in PLACEHOLDER_VALUES | {"not run", "not available"}
        or "{{" in execution
        or "}}" in execution
    ):
        return
    result_by_execution = {
        "succeeded": "succeeded",
        "failed": "failed",
        "held": "held",
        "cancelled": "cancelled",
    }
    normalized_execution = normalized_table_token(execution)
    if normalized_execution not in result_by_execution:
        fail(f"historical release artifact has invalid Execution: {path}")
    release_id = require_decision_field(fields, "Release ID")
    evidence_path = require_decision_field(fields, "Execution evidence")
    recorded_digest = require_decision_field(fields, "Execution evidence SHA-256")
    if not re.fullmatch(r"[0-9a-f]{64}", recorded_digest):
        fail(f"historical release artifact has invalid evidence SHA-256: {path}")
    _normalized, actual_digest = validate_release_receipt(
        root, evidence_path, release_id, result_by_execution[normalized_execution]
    )
    if actual_digest != recorded_digest:
        fail(f"historical release execution evidence hash is stale: {evidence_path}")


def validate_durable_history(root: Path) -> None:
    decision_directory = root / ".specify" / "decisions"
    specialized: list[tuple[Path, dict[str, Any]]] = []
    if decision_directory.is_dir():
        for path in sorted(decision_directory.rglob("*.yaml")):
            errors = validate_decision_receipt_file(path, root)
            if errors:
                fail("; ".join(errors[:3]))
            receipt = read_yaml(path)
            if receipt.get("receipt_type") in SPECIAL_DECISION_RECEIPT_TYPES:
                specialized.append((path, receipt))
    validate_special_decision_bindings(root, specialized)
    release_directory = root / "doc" / "releases"
    if release_directory.is_dir():
        for path in sorted(release_directory.rglob("*.md")):
            validate_historical_release_result_file(path, root)


def expected_index(root: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    for path in candidate_artifacts(root):
        if root / ".specify" / "decisions" in path.parents:
            receipt_errors = validate_decision_receipt_file(path, root)
            if receipt_errors:
                fail("; ".join(receipt_errors[:3]))
        if path.suffix.lower() == ".md":
            validate_historical_release_result_file(path, root)
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        artifacts.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "ids": sorted({match.upper() for match in ID_PATTERN.findall(text)}),
            }
        )
    return {"schema_version": SCHEMA_VERSION, "artifact_count": len(artifacts), "artifacts": artifacts}


def validate_index(index: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    if set(index) != {"schema_version", "artifact_count", "artifacts"}:
        errors.append("artifact index keys do not match the schema")
    if type(index.get("schema_version")) is not int or index.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"artifact index schema_version must be {SCHEMA_VERSION}")
    artifacts = index.get("artifacts")
    if not isinstance(artifacts, list):
        return errors + ["artifact index artifacts must be a list"]
    if type(index.get("artifact_count")) is not int or index.get("artifact_count") != len(artifacts):
        errors.append("artifact index artifact_count does not match artifacts")
    seen: set[str] = set()
    for position, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append(f"artifact index entry {position} must be a mapping")
            continue
        if set(artifact) != {"path", "sha256", "ids"}:
            errors.append(f"artifact index entry {position} does not match the schema")
            continue
        raw_path = artifact.get("path")
        try:
            normalized, resolved = resolve_repo_path(root, raw_path)
        except ValueError as exc:
            errors.append(f"artifact index entry {position}: {exc}")
            continue
        if normalized in seen:
            errors.append(f"artifact index contains duplicate path: {normalized}")
        seen.add(normalized)
        if not resolved.is_file():
            errors.append(f"artifact index path does not exist: {normalized}")
            continue
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"artifact index hash is invalid: {normalized}")
        elif sha256_file(resolved) != digest:
            errors.append(f"artifact index hash is stale: {normalized}")
        ids = artifact.get("ids")
        text = resolved.read_text(encoding="utf-8", errors="replace")
        expected_ids = sorted({match.upper() for match in ID_PATTERN.findall(text)})
        if not isinstance(ids, list) or ids != expected_ids:
            errors.append(f"artifact index IDs are stale or invalid: {normalized}")
    expected_paths = {item["path"] for item in expected_index(root)["artifacts"]}
    if seen != expected_paths:
        missing = sorted(expected_paths - seen)
        extra = sorted(seen - expected_paths)
        if missing:
            errors.append(f"artifact index is missing paths: {missing[:5]}")
        if extra:
            errors.append(f"artifact index contains unsupported paths: {extra[:5]}")
    return errors


def validate_index_structure(index: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    if set(index) != {"schema_version", "artifact_count", "artifacts"}:
        errors.append("artifact index keys do not match the schema")
    if type(index.get("schema_version")) is not int or index.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"artifact index schema_version must be {SCHEMA_VERSION}")
    artifacts = index.get("artifacts")
    if not isinstance(artifacts, list):
        return errors + ["artifact index artifacts must be a list"]
    if type(index.get("artifact_count")) is not int or index.get("artifact_count") != len(artifacts):
        errors.append("artifact index artifact_count does not match artifacts")
    seen: set[str] = set()
    for position, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256", "ids"}:
            errors.append(f"artifact index entry {position} does not match the schema")
            continue
        try:
            normalized, _resolved = resolve_repo_path(root, artifact["path"])
        except (KeyError, ValueError) as exc:
            errors.append(f"artifact index entry {position}: {exc}")
            continue
        if not bounded_text(normalized):
            errors.append(f"artifact index path is not bounded: {position}")
        if normalized in seen:
            errors.append(f"artifact index contains duplicate path: {normalized}")
        seen.add(normalized)
        if not isinstance(artifact.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-f]{64}", artifact.get("sha256", "")
        ):
            errors.append(f"artifact index hash is invalid: {normalized}")
        ids = artifact.get("ids")
        if not isinstance(ids, list) or any(
            not isinstance(value, str) or not ID_PATTERN.fullmatch(value) for value in ids
        ):
            errors.append(f"artifact index IDs are invalid: {normalized}")
    return errors


def rebuild_index(root: Path) -> None:
    index = expected_index(root)
    rendered = yaml.safe_dump(
        index, sort_keys=False, allow_unicode=True, width=1000
    ).encode("utf-8")
    if len(rendered) > INDEX_FILE_SIZE_LIMIT:
        fail(
            f"generated artifact index exceeds {INDEX_FILE_SIZE_LIMIT} bytes; split large domain artifacts/indexes"
        )
    path = index_path(root)
    digest_path = index_digest_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    index_temporary = path.with_suffix(path.suffix + ".tmp")
    digest_temporary = digest_path.with_suffix(digest_path.suffix + ".tmp")
    index_temporary.write_bytes(rendered)
    digest_temporary.write_text(
        hashlib.sha256(rendered).hexdigest() + "\n", encoding="utf-8", newline="\n"
    )
    os.replace(index_temporary, path)
    os.replace(digest_temporary, digest_path)


def command_rebuild_index(_args: argparse.Namespace, root: Path) -> None:
    if pointer_path(root).is_file():
        read_valid_state(root, check_paths=True)
    rebuild_index(root)
    print(index_path(root).relative_to(root).as_posix())


def command_resolve(args: argparse.Namespace, root: Path) -> None:
    read_valid_state(root, check_paths=True)
    index = read_index(root)
    index_errors = validate_index_structure(index, root)
    if index_errors:
        fail(
            "artifact index is structurally unsafe; run validate/rebuild-index: "
            + "; ".join(index_errors[:3])
        )
    artifacts = index.get("artifacts")
    if not isinstance(artifacts, list):
        fail("artifact index has no artifacts list")
    if not args.id and not args.path:
        fail("resolve requires --id or --path")
    target_id = args.id.upper() if args.id else None
    target_path = args.path.lower().replace("\\", "/") if args.path else None
    matches: list[dict[str, Any]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        ids = {str(value).upper() for value in artifact.get("ids", [])}
        artifact_path = str(artifact.get("path", ""))
        if target_id and target_id not in ids:
            continue
        if target_path and target_path not in artifact_path.lower():
            continue
        matches.append(artifact)
    compact_matches: list[dict[str, Any]] = []
    for artifact in matches[: args.limit]:
        normalized, resolved = resolve_repo_path(root, artifact["path"])
        if not resolved.is_file() or sha256_file(resolved) != artifact["sha256"]:
            fail(f"matched artifact is stale or missing: {normalized}; run rebuild-index")
        text_value = resolved.read_text(encoding="utf-8", errors="replace")
        occurrences: list[dict[str, Any]] = []
        occurrence_count = 0
        if target_id:
            current_heading: str | None = None
            for number, line in enumerate(text_value.splitlines(), start=1):
                if line.lstrip().startswith("#"):
                    current_heading = line.strip()
                line_ids = {value.upper() for value in ID_PATTERN.findall(line)}
                if target_id in line_ids:
                    occurrence_count += 1
                    if len(occurrences) < RESOLVE_OCCURRENCE_LIMIT:
                        occurrences.append({"line": number, "heading": current_heading})
            if occurrence_count == 0:
                fail(f"artifact index ID is stale for matched artifact: {normalized}")
        compact_matches.append(
            {
                "path": normalized,
                "sha256": artifact["sha256"],
                "matched_id": target_id,
                "line": occurrences[0]["line"] if occurrences else None,
                "heading": occurrences[0]["heading"] if occurrences else None,
                "occurrence_count": occurrence_count,
                "occurrences_truncated": occurrence_count > RESOLVE_OCCURRENCE_LIMIT,
                "occurrences": occurrences,
                "artifact_unique_id_count": len(artifact["ids"]),
            }
        )
    result = {
        "query": {"id": args.id, "path": args.path, "limit": args.limit},
        "match_count": len(matches),
        "truncated": len(matches) > args.limit,
        "matches": compact_matches,
    }
    rendered = yaml.safe_dump(result, sort_keys=False, allow_unicode=True).rstrip()
    if len(rendered.encode("utf-8")) > RESOLVE_OUTPUT_BYTE_LIMIT:
        fail("resolved context slice exceeds output limit; narrow --id/--path or lower --limit")
    print(rendered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    subparsers = parser.add_subparsers(dest="operation", required=True)

    init = subparsers.add_parser("init", help="initialize pointer and index")
    init.add_argument("--project-id", required=True)
    init.add_argument("--profile", choices=("full", "lite"), required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(handler=command_init)

    status = subparsers.add_parser("status", help="print compact current state")
    status.set_defaults(handler=command_status)

    validate = subparsers.add_parser("validate", help="validate the pointer")
    validate.add_argument("--check-paths", action="store_true")
    validate.set_defaults(handler=command_validate)

    start = subparsers.add_parser("start", help="start explicitly authorized work")
    start.add_argument("--expect-revision", type=int, required=True)
    start.add_argument("--kind", required=True)
    start.add_argument("--work-id", required=True)
    start.add_argument("--stage", required=True)
    start.set_defaults(handler=command_start)

    profile = subparsers.add_parser("confirm-profile", help="confirm the human-selected profile")
    profile.add_argument("--expect-revision", type=int, required=True)
    profile.add_argument("--profile", choices=("full", "lite"), required=True)
    profile.set_defaults(handler=command_confirm_profile)

    record = subparsers.add_parser("record-output", help="record candidate output and pending gate")
    record.add_argument("--expect-revision", type=int, required=True)
    record.add_argument("--stage", required=True)
    record.add_argument("--status", choices=sorted(CANDIDATE_STATUSES), default="ready_for_review")
    record.add_argument("--gate")
    record.add_argument("--artifact", action="append", required=True, metavar="KEY=PATH")
    record.add_argument("--evidence", action="append", default=[])
    record.add_argument("--context-id", action="append", default=[])
    record.add_argument("--next", action="append", default=[])
    record.add_argument("--blocker", action="append", default=[])
    record.set_defaults(handler=command_record_output)

    block = subparsers.add_parser("block", help="record concrete blockers without a gate decision")
    block.add_argument("--expect-revision", type=int, required=True)
    block.add_argument("--stage")
    block.add_argument("--artifact", action="append", default=[], metavar="KEY=PATH")
    block.add_argument("--blocker", action="append", required=True)
    block.add_argument("--next", action="append", default=[])
    block.set_defaults(handler=command_block)

    decide = subparsers.add_parser("decide", help="resolve a generic ready_for_review gate")
    decide.add_argument("--expect-revision", type=int, required=True)
    decide.add_argument("--decision", choices=("approved", "rejected"), required=True)
    decide.add_argument("--decided-by", required=True)
    decide.add_argument("--decision-date", required=True)
    decide.add_argument("--decision-evidence", required=True)
    decide.add_argument("--next", action="append", default=[])
    decide.set_defaults(handler=command_decide)

    feature_decision = subparsers.add_parser(
        "record-feature-decision", help="persist a reviewed feature acceptance decision"
    )
    feature_decision.add_argument("--expect-revision", type=int, required=True)
    feature_decision.add_argument(
        "--decision", choices=("accepted", "rejected", "changes_requested"), required=True
    )
    feature_decision.add_argument("--artifact", required=True)
    feature_decision.add_argument("--decided-by", required=True)
    feature_decision.add_argument("--decision-date", required=True)
    feature_decision.add_argument("--decision-evidence", required=True)
    feature_decision.add_argument("--next", action="append", default=[])
    feature_decision.set_defaults(handler=command_record_feature_decision)

    release_authorization = subparsers.add_parser(
        "authorize-release", help="persist human release authorization before external tooling"
    )
    release_authorization.add_argument("--expect-revision", type=int, required=True)
    release_authorization.add_argument("--artifact", required=True)
    release_authorization.add_argument("--authorized-by", required=True)
    release_authorization.add_argument("--authorized-on", required=True)
    release_authorization.add_argument("--authorization-evidence", required=True)
    release_authorization.add_argument("--next", action="append", default=[])
    release_authorization.set_defaults(handler=command_authorize_release)

    release_result = subparsers.add_parser(
        "record-release-result", help="persist the confirmed external release result"
    )
    release_result.add_argument("--expect-revision", type=int, required=True)
    release_result.add_argument(
        "--result", choices=("succeeded", "failed", "held", "cancelled"), required=True
    )
    release_result.add_argument("--artifact", required=True)
    release_result.add_argument(
        "--execution-evidence",
        required=True,
        help="repository-relative structured release-result receipt YAML",
    )
    release_result.add_argument("--confirmed-by", required=True)
    release_result.add_argument("--confirmed-on", required=True)
    release_result.add_argument("--next", action="append", default=[])
    release_result.set_defaults(handler=command_record_release_result)

    index = subparsers.add_parser("rebuild-index", help="rebuild the derived artifact index")
    index.set_defaults(handler=command_rebuild_index)

    resolve = subparsers.add_parser("resolve", help="return a small artifact-index slice")
    resolve.add_argument("--id")
    resolve.add_argument("--path")
    resolve.add_argument("--limit", type=resolve_limit, default=20)
    resolve.set_defaults(handler=command_resolve)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        fail(f"project root does not exist: {root}")
    if args.operation != "init":
        validate_durable_history(root)
    args.handler(args, root)


if __name__ == "__main__":
    main()
