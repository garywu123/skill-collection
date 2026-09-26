"""Append adjudicated leftovers to the human-owned review backlog."""

from __future__ import annotations

import os
import re
from pathlib import Path

HEADER = """# Review Backlog

Human-owned, non-authoritative follow-up items from cross-agent runs. Agents
read this file only when the user asks for a backlog review or names an item
ID. An item becomes work only after the user promotes it into the current
request or the applicable Feature Map and Plan. Keep each item's status
current: `open`, `promoted`, `resolved`, or `dismissed`.
"""


def _one_line(text: str, limit: int = 100) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _render(item_id: str, item: dict) -> str:
    evidence = ", ".join(f"`{entry}`" for entry in item["evidence"]) or "none"
    return "\n".join(
        [
            f"## {item_id}: {_one_line(item['claim'])}",
            "",
            f"- Type: `{item['type']}`",
            "- Status: `open`",
            f"- Priority: `{item['priority']}`",
            f"- Source: run `{item['run_id']}`, finding `{item['finding_id']}`",
            f"- Artifact: `{item['artifact']}` ({item['stage']})",
            f"- Base: {item['base']}",
            f"- Claim: {item['claim']}",
            f"- Evidence: {evidence}",
            f"- Proposed change: {item['recommendation']}",
            f"- Rationale: {item['rationale']}",
            "",
        ]
    )


def append(path: Path, items: list[dict]) -> list[str]:
    """Append items with the next free `RB-NNNN` IDs and return those IDs."""
    text = path.read_text(encoding="utf-8") if path.is_file() else HEADER
    numbers = [int(number) for number in re.findall(r"^## RB-(\d+)", text, re.MULTILINE)]
    next_number = max(numbers, default=0) + 1
    ids, blocks = [], []
    for item in items:
        item_id = f"RB-{next_number:04d}"
        next_number += 1
        ids.append(item_id)
        blocks.append(_render(item_id, item))
    if not text.endswith("\n"):
        text += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text + "\n" + "\n".join(blocks), encoding="utf-8")
    os.replace(temporary, path)
    return ids
