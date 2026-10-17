"""Import explicit Claude discussion evidence without tool results or reasoning."""

import hashlib
import json
import os
from pathlib import Path
import uuid

from .errors import UsageError


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _project(path):
    return os.path.normcase(str(Path(path).resolve()))


def claude_sources(session_id):
    """Locate provider transcripts without treating a launch attempt as a session."""
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    return list((config / "projects").glob(f"*/{session_id}.jsonl"))


def import_claude(project_root, session_id, destination):
    """Save a text-only, source-addressable snapshot of one project session."""
    try:
        if str(uuid.UUID(session_id)) != session_id:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise UsageError("Claude discussion session must be a canonical UUID.") from None
    project_root = Path(project_root).resolve()
    candidates = claude_sources(session_id)
    if len(candidates) != 1:
        raise UsageError("Claude discussion source is missing or ambiguous for this session.")
    source = candidates[0].resolve()
    try:
        raw = source.read_bytes()
        records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
        messages = []
        seen = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError()
            role = record.get("type")
            if role not in ("user", "assistant") or record.get("isSidechain"):
                continue
            if record.get("sessionId") != session_id or not isinstance(record.get("cwd"), str):
                raise ValueError()
            if _project(record["cwd"]) != _project(project_root):
                raise UsageError("Claude discussion source belongs to a different project.")
            message = record.get("message")
            if not isinstance(message, dict) or message.get("role") != role:
                raise ValueError()
            content = message.get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                if any(not isinstance(block, dict) for block in content):
                    raise ValueError()
                parts = [block.get("text") for block in content if block.get("type") == "text"]
                if any(not isinstance(part, str) for part in parts):
                    raise ValueError()
                text = "\n".join(parts)
            else:
                raise ValueError()
            if not text.strip():
                continue
            locator = record.get("uuid")
            timestamp = record.get("timestamp")
            if not isinstance(locator, str) or not locator or not isinstance(timestamp, str) or not timestamp:
                raise ValueError()
            if locator in seen:
                raise ValueError()
            seen.add(locator)
            messages.append({"uuid": locator, "parentUuid": record.get("parentUuid"),
                             "timestamp": timestamp, "role": role, "text": text,
                             "source_id": f"{session_id}:{locator}"})
        if not messages:
            raise UsageError("Claude discussion source has no attributable text messages.")
    except (OSError, UnicodeError, ValueError, TypeError):
        raise UsageError("Claude discussion source is malformed or unreadable; no evidence imported.") from None
    payload = {"provider": "claude", "session_id": session_id,
               "project_root": str(project_root), "source_path": str(source),
               "source_sha256": _digest(raw), "messages": messages}
    destination = Path(destination).resolve()
    if destination == source:
        raise UsageError("Evidence destination must not overwrite the provider source.")
    exported = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(exported)
    return {key: payload[key] for key in ("provider", "session_id", "project_root", "source_path", "source_sha256")} | {
        "file": str(destination), "sha256": _digest(exported), "message_count": len(messages)}


def read(manifest):
    """Read the frozen export; a live provider session may have continued since it."""
    try:
        raw = Path(manifest["file"]).read_bytes()
        if _digest(raw) != manifest["sha256"]:
            raise ValueError()
        payload = json.loads(raw)
        if (not isinstance(payload, dict) or not isinstance(payload.get("messages"), list)
                or len(payload["messages"]) != manifest["message_count"]
                or any(payload.get(key) != manifest[key] for key in
                       ("provider", "session_id", "project_root", "source_path", "source_sha256"))):
            raise ValueError()
        return payload
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        raise UsageError("Discussion evidence is missing, malformed or changed since import.") from None


verify = read
