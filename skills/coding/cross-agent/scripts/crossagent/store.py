"""Run state: one atomically written state.json per run under .cross-agent/runs."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from .errors import UsageError
from . import history

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
    for attempt in range(4):
        try:
            os.replace(temporary, path)
            break
        except PermissionError as exc:
            # Windows may briefly deny replacement while another handle reads the file.
            # Keep the old complete state and bound retries; permanent permissions still fail.
            if getattr(exc, "winerror", None) not in (5, 32, 33) or attempt == 3:
                raise
            time.sleep(0.05 * 2 ** attempt)
    history.save(state)


def open_runs(project_root: Path) -> list[dict]:
    """Runs holding the artifact lock; parked history is retained without that lock."""
    runs = []
    root = runs_root(project_root)
    if root.is_dir():
        for child in sorted(root.iterdir()):
            path = child / "state.json"
            if not path.is_file():
                continue
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
                if state.get("phase") != "parked":
                    runs.append(state)
            except (OSError, json.JSONDecodeError):
                runs.append({"run_id": child.name, "phase": "unreadable"})
    return runs


def delete_run(project_root: Path, run_id: str) -> None:
    shutil.rmtree(run_path(project_root, run_id))
