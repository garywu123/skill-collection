"""JSON schemas shared by both providers, and a validator for their strict subset.

The schemas stay within what Claude Code `--json-schema` and Codex
`--output-schema` both accept: every property required,
`additionalProperties: false`, and nullable types instead of optional keys.
"""

from __future__ import annotations

CATEGORIES = [
    "unmet-outcome",
    "authoritative-conflict",
    "validation-failure",
    "contradiction",
    "regression",
    "risk",
]
SEVERITIES = ["blocker", "major", "minor"]
DISPOSITIONS = ["accepted", "note-only", "rejected", "needs-user-decision"]
PRIORITIES = ["high", "medium", "low", "none"]


def _object(properties: dict) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


_STRING = {"type": "string"}
_STRINGS = {"type": "array", "items": _STRING}

REVIEW = _object(
    {
        "findings": {
            "type": "array",
            "items": _object(
                {
                    "id": _STRING,
                    "category": {"type": "string", "enum": CATEGORIES},
                    "severity": {"type": "string", "enum": SEVERITIES},
                    "claim": _STRING,
                    "evidence": _STRINGS,
                    "recommendation": _STRING,
                }
            ),
        },
        "earlier_results": {
            "type": "array",
            "items": _object(
                {
                    "finding_id": _STRING,
                    "result": {"type": "string", "enum": ["resolved", "open"]},
                }
            ),
        },
        "notes": _STRINGS,
    }
)

PRODUCER = _object(
    {
        "status": {"type": "string", "enum": ["done", "needs-user-decision", "blocked"]},
        "summary": _STRING,
        "questions": _STRINGS,
        "blocker": {"type": ["string", "null"]},
        "outcomes": {
            "type": "array",
            "items": _object(
                {
                    "finding_id": _STRING,
                    "result": {"type": "string", "enum": ["fixed", "not-fixed"]},
                    "rationale": _STRING,
                }
            ),
        },
    }
)

DECIDE = _object(
    {
        "decisions": {
            "type": "array",
            "items": _object(
                {
                    "finding_id": _STRING,
                    "disposition": {"type": "string", "enum": DISPOSITIONS},
                    "rationale": {"type": ["string", "null"]},
                    "priority": {"type": ["string", "null"], "enum": [*PRIORITIES, None]},
                }
            ),
        }
    }
)

_TYPES = {"object": dict, "array": list, "string": str, "null": type(None)}


def _matches(value, name: str) -> bool:
    if name == "boolean":
        return isinstance(value, bool)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name])


def validate(value, schema: dict, path: str = "$") -> list[str]:
    """Return every violation of the strict subset used by the schemas above."""
    names = schema.get("type")
    if names is not None:
        names = names if isinstance(names, list) else [names]
        if not any(_matches(value, name) for name in names):
            return [f"{path}: expected {' or '.join(names)}"]
    errors = []
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, dict) and "properties" in schema:
        properties = schema["properties"]
        errors += [f"{path}: missing '{key}'" for key in schema.get("required", []) if key not in value]
        if schema.get("additionalProperties") is False:
            errors += [f"{path}: unexpected '{key}'" for key in value if key not in properties]
        for key, sub_schema in properties.items():
            if key in value:
                errors += validate(value[key], sub_schema, f"{path}.{key}")
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            errors += validate(item, schema["items"], f"{path}[{index}]")
    return errors
