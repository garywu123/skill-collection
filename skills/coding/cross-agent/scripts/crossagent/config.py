"""Configuration, role specs, and stage Skill discovery."""

from __future__ import annotations

import copy
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .errors import UsageError

STAGES = ("feature-map", "feature-plan", "feature-delivery", "general")
PROVIDERS = ("claude", "codex", "fake")

DEFAULTS: dict = {
    "max_reviews": 2,
    "timeout_minutes": 30,
    "rotate_at_tokens": 350_000,
    "backlog_rejected": True,
    "max_diff_kb": 200,
    "defaults": {"producer": "claude", "reviewer": "codex"},
    "stages": {},
    "projects": {},
}

# Settings copied into each run, so a later config edit never changes an open run.
RUN_SETTINGS = ("max_reviews", "timeout_minutes", "rotate_at_tokens", "backlog_rejected", "max_diff_kb")

# Read-only Git commands a Producer may run besides the project's allowed_commands.
PRODUCER_BASE_COMMANDS = ("git status", "git diff", "git log", "git show")

PROJECT_KEYS = ("allowed_commands", "delivery_checks", "extra_dirs")


def config_path() -> Path:
    override = os.environ.get("CROSS_AGENT_CONFIG")
    return Path(override) if override else Path.home() / ".cross-agent" / "config.toml"


def load_config() -> dict:
    """Return the defaults overlaid with the user's config file, when it exists."""
    config = copy.deepcopy(DEFAULTS)
    path = config_path()
    if path.is_file():
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise UsageError(f"Cannot read config {path}: {exc}") from exc
        for key, value in data.items():
            if key not in DEFAULTS:
                raise UsageError(f"Unknown config key '{key}' in {path}")
            if isinstance(DEFAULTS[key], dict):
                if not isinstance(value, dict):
                    raise UsageError(f"'{key}' in {path} must be a table")
                config[key].update(value)
            else:
                config[key] = value
    _check(config, path)
    return config


def _check(config: dict, path: Path) -> None:
    for key in ("max_reviews", "timeout_minutes", "max_diff_kb"):
        if not _is_int(config[key]) or config[key] < 1:
            raise UsageError(f"'{key}' in {path} must be a positive integer")
    if not _is_int(config["rotate_at_tokens"]) or config["rotate_at_tokens"] < 0:
        raise UsageError(f"'rotate_at_tokens' in {path} must be 0 (off) or a positive integer")
    if not isinstance(config["backlog_rejected"], bool):
        raise UsageError(f"'backlog_rejected' in {path} must be true or false")
    for role in ("producer", "reviewer"):
        parse_spec(str(config["defaults"].get(role, "")))
    for project, settings in config["projects"].items():
        if not isinstance(settings, dict):
            raise UsageError(f"[projects.\"{project}\"] in {path} must be a table")
        for key, value in settings.items():
            if key not in PROJECT_KEYS:
                raise UsageError(f"Unknown key '{key}' in [projects.\"{project}\"] of {path}")
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise UsageError(f"'{key}' in [projects.\"{project}\"] of {path} must be a list of strings")


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True)
class RoleSpec:
    provider: str
    model: str | None = None
    effort: str | None = None

    def as_dict(self) -> dict:
        return {"provider": self.provider, "model": self.model, "effort": self.effort}


def parse_spec(text: str) -> RoleSpec:
    """Parse `<provider>[:<model>[:<effort>]]`; an empty model keeps the provider's default."""
    parts = text.strip().split(":")
    if len(parts) > 3 or not parts[0]:
        raise UsageError(f"Role spec '{text}' must be <provider>[:<model>[:<effort>]]")
    provider = parts[0].lower()
    if provider not in PROVIDERS:
        raise UsageError(f"Unknown provider '{parts[0]}'; use claude or codex")
    model = parts[1] if len(parts) > 1 and parts[1] else None
    effort = parts[2] if len(parts) > 2 and parts[2] else None
    return RoleSpec(provider, model, effort)


def _same_path(left: str | Path, right: str | Path) -> bool:
    def norm(path):
        return os.path.normcase(str(Path(path).expanduser().resolve()))

    return norm(left) == norm(right)


def project_settings(config: dict, project_root: Path) -> dict:
    """Return the project's commands and extra directories, keyed by its root path."""
    settings = next(
        (value for key, value in config["projects"].items() if _same_path(key, project_root)),
        {},
    )
    return {
        "allowed_commands": list(settings.get("allowed_commands", [])),
        "delivery_checks": list(settings.get("delivery_checks", [])),
        "extra_dirs": [str((project_root / item).resolve()) for item in settings.get("extra_dirs", [])],
    }


def skills_root() -> Path:
    """The folder that holds this Skill and its sibling lifecycle Skills."""
    return Path(__file__).resolve().parents[3]


def find_stage_skill(config: dict, stage: str) -> Path | None:
    """Locate the stage's SKILL.md: a configured path, else a sibling Skill folder."""
    if stage == "general":
        return None
    override = config["stages"].get(stage, {}).get("skill")
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            raise UsageError(f"The configured {stage} Skill {path} does not exist")
        return path.resolve()
    root = skills_root()
    for child in sorted(root.iterdir()):
        # Deployed folders are named `<stage>`; authoring folders may be `<ordinal>.<stage>`.
        if child.is_dir() and (child.name == stage or child.name.endswith("." + stage)):
            skill = child / "SKILL.md"
            if skill.is_file():
                return skill
    raise UsageError(
        f"Cannot find the {stage} Skill next to cross-agent in {root}; "
        f"set [stages.{stage}] skill in {config_path()}"
    )
