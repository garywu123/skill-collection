"""Configuration, role specs, and stage Skill discovery."""

from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
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
    return Path(override).expanduser() if override else Path.home() / ".cross-agent" / "config.toml"


def load_config() -> dict:
    """Return the defaults overlaid with the user's config file, when it exists."""
    path = config_path()
    try:
        text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    except (OSError, UnicodeError) as exc:
        raise UsageError(f"Cannot read config {path}: {exc}") from exc
    return _parse_config(text, path)


def _parse_config(text: str, path: Path) -> dict:
    config = copy.deepcopy(DEFAULTS)
    if text:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
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


def initialize(project_root: Path, input_file: str) -> dict:
    """Append a missing project without rewriting existing TOML or starting a run."""
    from . import gitops

    project_root = project_root.resolve()
    gitops.require_work_tree(project_root)
    path = config_path().expanduser().resolve()
    temporary = None
    try:
        proposed = json.loads(Path(input_file).read_text(encoding="utf-8-sig"))
        # Reuse the normal project schema before touching the configuration file.
        _check({**copy.deepcopy(DEFAULTS), "projects": {project_root.as_posix(): proposed}}, path)
        proposed = {key: proposed.get(key, []) for key in PROJECT_KEYS}
        original = path.read_bytes() if path.exists() else None
        config = _parse_config((original or b"").decode("utf-8-sig"), path)
        exists = project_configured(config, project_root)
        if not exists:
            section = f'\n[projects.{json.dumps(project_root.as_posix(), ensure_ascii=False)}]\n'
            section += "".join(f"{key} = {json.dumps(value, ensure_ascii=False)}\n" for key, value in proposed.items())
            updated = (original or b"# Cross-agent settings; omitted keys use built-in defaults.\n") + section.encode("utf-8")
            config = _parse_config(updated.decode("utf-8-sig"), path)
            path.parent.mkdir(parents=True, exist_ok=True)
            if original is None:
                # Exclusive creation preserves a configuration created by another session.
                with path.open("xb") as handle:
                    handle.write(updated)
            else:
                with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".cross-agent-", delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(updated)
                if path.read_bytes() != original:
                    raise UsageError("Config changed during initialization; retry without overwriting it")
                os.replace(temporary, path)
        effective = project_settings(config, project_root)
        proposed_effective = project_settings({"projects": {project_root.as_posix(): proposed}}, project_root)
        return {
            "action": "unchanged" if exists else ("created" if original is None else "project-added"),
            "config_path": str(path),
            "project_root": str(project_root),
            "project": effective,
            "defaults": config["defaults"],
            "settings": {key: config[key] for key in RUN_SETTINGS},
            "proposed_differences": {
                key: value for key, value in proposed.items()
                if proposed_effective[key] != effective[key]
            },
            "providers_on_path": {provider: shutil.which(provider) is not None for provider in ("claude", "codex")},
            "checks_configured": bool(effective["delivery_checks"]),
            "checks_executed": False,
            "workers_started": False,
        }
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise UsageError(f"Cannot initialize config {path}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


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


def project_configured(config: dict, project_root: Path) -> bool:
    return any(_same_path(key, project_root) for key in config["projects"])


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
