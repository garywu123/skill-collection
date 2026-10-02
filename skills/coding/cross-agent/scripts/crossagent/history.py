"""Retained worker-call CSVs and an on-demand project-wide CSV export."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path

from .errors import UsageError

FIELDS = (
    "run_id", "item", "stage", "artifact", "call", "role", "round", "segment",
    "provider", "configured_model", "configured_effort", "observed_model", "observed_effort",
    "generation", "session_id", "session_reason", "started_at_utc", "ended_at_utc",
    "elapsed_seconds", "call_status", "run_status", "input_tokens", "cached_input_tokens",
    "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens",
    "usage_source", "usage_scope", "usage_status",
)


def run_file(project_root: Path, run_id: str) -> Path:
    return Path(project_root) / ".cross-agent" / "history" / f"{run_id}.csv"


def _write(path: Path, rows: list[dict]) -> None:
    """Replace a complete CSV; Excel locks fail without destroying the old copy."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", newline="",
                                         dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                # Keep arbitrary topic names and paths as text in spreadsheet readers.
                writer.writerow({key: "'" + value if isinstance(value, str) and
                                 value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else value
                                 for key, value in row.items() if key in FIELDS})
        os.replace(temporary, path)
    except OSError as exc:
        raise UsageError(f"Cannot write history CSV {path}: {exc}") from exc
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def save(state: dict) -> None:
    calls = state.get("worker_calls", [])
    if calls:
        rows = [{**call, "run_status": state.get("final_status") or state["phase"]} for call in calls]
        _write(run_file(state["project_root"], state["run_id"]), rows)


def export(project_root: Path) -> dict:
    """Read retained CSVs, including closed runs, without requiring live run state."""
    root = Path(project_root) / ".cross-agent"
    rows = []
    try:
        # Recover a CSV whose last replacement was blocked, using saved observations.
        for path in sorted((root / "runs").glob("*/state.json")):
            save(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((root / "history").glob("*.csv")):
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames != list(FIELDS):
                    raise UsageError(f"Unrecognized history CSV header: {path}")
                rows.extend(reader)
    except (OSError, ValueError) as exc:
        raise UsageError(f"Cannot read history CSVs: {exc}") from exc
    rows.sort(key=lambda row: (row["started_at_utc"], row["run_id"], int(row["call"])))
    path = root / "history.csv"
    _write(path, rows)
    return {"history_file": str(path), "calls": len(rows),
            "runs": len({row["run_id"] for row in rows}),
            "unknown_usage_calls": sum(row["usage_status"] == "unknown" for row in rows),
            "partial_usage_calls": sum(row["usage_status"] == "partial" for row in rows)}
