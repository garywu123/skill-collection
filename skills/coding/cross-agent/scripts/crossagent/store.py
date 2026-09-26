"""Run state: one atomically written state.json per run under .cross-agent/runs."""

from __future__ import annotations

import json
import os
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .errors import UsageError

STATE_VERSION = 1
STATE_DIR = ".cross-agent"


def runs_root(project_root: Path) -> Path:
    return Path(project_root) / STATE_DIR / "runs"


def run_path(project_root: Path, run_id: str) -> Path:
    return runs_root(project_root) / run_id


def new_run_id(stage: str) -> str:
    return f"{datetime.now():%Y%m%d-%H%M%S}-{stage}-{secrets.token_hex(2)}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(project_root: Path, run_id: str) -> dict:
    path = run_path(project_root, run_id) / "state.json"
    if not path.is_file():
        raise UsageError(f"No open run '{run_id}' under {runs_root(project_root)}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UsageError(f"Cannot read {path}: {exc}") from exc
    if state.get("state_version") != STATE_VERSION:
        raise UsageError(f"{path} has state version {state.get('state_version')}; this CLI reads {STATE_VERSION}")
    return state


def save(state: dict) -> None:
    """Write state.json through a temporary file so a crash never leaves it half written."""
    path = run_path(state["project_root"], state["run_id"]) / "state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now()
    temporary = path.with_name("state.json.tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, path)


def open_runs(project_root: Path) -> list[dict]:
    """Every run directory that still holds state; closed runs are deleted."""
    runs = []
    root = runs_root(project_root)
    if root.is_dir():
        for child in sorted(root.iterdir()):
            path = child / "state.json"
            if not path.is_file():
                continue
            try:
                runs.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                runs.append({"run_id": child.name, "phase": "unreadable"})
    return runs


def delete_run(project_root: Path, run_id: str) -> None:
    shutil.rmtree(run_path(project_root, run_id))
