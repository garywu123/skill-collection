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

# Settings copied into each run, so a later config edit never changes an open run.
RUN_SETTINGS = ("max_reviews", "timeout_minutes", "rotate_at_tokens", "backlog_rejected", "max_diff_kb")
CONFIG_KEYS = (*RUN_SETTINGS, "defaults", "cli", "stages", "projects")
REQUIRED_KEYS = (*RUN_SETTINGS, "defaults", "cli", "projects")

# Read-only Git commands a Producer may run besides the project's allowed_commands.
PRODUCER_BASE_COMMANDS = ("git status", "git diff", "git log", "git show")

PROJECT_KEYS = ("allowed_commands", "delivery_checks", "extra_dirs")


def config_path(project_root: Path | None = None) -> Path:
    override = os.environ.get("CROSS_AGENT_CONFIG")
    path = Path(override).expanduser() if override else (project_root or Path.cwd()) / ".cross-agent" / "config.toml"
    if not path.is_file():
        return path
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        if "config_file" not in data:
            return path
        reference = data["config_file"]
        if set(data) != {"config_file"} or not isinstance(reference, str) or not reference.strip():
            raise UsageError(f"Config pointer {path} must contain only a nonempty 'config_file'")
        target = (path.parent / reference).resolve()
        if not target.is_file():
            raise UsageError(f"Shared config {target} referenced by {path} does not exist")
        if "config_file" in tomllib.loads(target.read_text(encoding="utf-8-sig")):
            raise UsageError(f"Config pointers cannot be chained: {path} -> {target}")
        return target
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise UsageError(f"Cannot read config {path}: {exc}") from exc


def load_config(project_root: Path | None = None) -> dict:
    """Read a complete project configuration; never fill in runtime defaults."""
    path = config_path(project_root)
    if not path.is_file():
        raise UsageError(f"Configuration file does not exist: {path}; run init explicitly")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise UsageError(f"Cannot read config {path}: {exc}") from exc
    return _parse_config(text, path)


def _parse_config(text: str, path: Path) -> dict:
    try:
        config = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise UsageError(f"Cannot read config {path}: {exc}") from exc
    unknown = set(config) - set(CONFIG_KEYS)
    if unknown:
        raise UsageError(f"Unknown config keys {sorted(unknown)} in {path}")
    missing = set(REQUIRED_KEYS) - set(config)
    if missing:
        raise UsageError(f"Missing required config keys {sorted(missing)} in {path}")
    # Stage-path overrides are optional; sibling Skill discovery is unchanged.
    config.setdefault("stages", {})
    for key in ("defaults", "cli", "stages", "projects"):
        if not isinstance(config[key], dict):
            raise UsageError(f"'{key}' in {path} must be a table")
    _check(config, path)
    return config


def _render_config(config: dict) -> str:
    """Serialize this configuration's scalar settings and named tables."""
    lines = ["# Initialized from cross-agent/assets/config.example.toml."]
    lines += [f"{key} = {json.dumps(config[key])}" for key in RUN_SETTINGS]
    for table in ("defaults", "cli"):
        lines += ["", f"[{table}]"]
        lines += [f"{key} = {json.dumps(value)}" for key, value in config[table].items()]
    for table in ("stages", "projects"):
        for name, settings in config[table].items():
            lines += ["", f"[{table}.{json.dumps(name)}]"]
            lines += [f"{key} = {json.dumps(value)}" for key, value in settings.items()]
    return "\n".join(lines) + "\n"


def initialize(project_root: Path, input_file: str, *, producer=None, reviewer=None, check_version=True) -> dict:
    """Append a missing project without rewriting existing TOML or starting a run."""
    from . import gitops
    from .versions import check_codex_version

    project_root = project_root.resolve()
    gitops.require_work_tree(project_root)
    path = config_path(project_root).resolve()
    requested_roles = {key: value for key, value in {"producer": producer, "reviewer": reviewer}.items() if value is not None}
    for value in requested_roles.values():
        parse_spec(value)
    temporary = None
    try:
        proposed = json.loads(Path(input_file).read_text(encoding="utf-8-sig"))
        if not isinstance(proposed, dict) or set(proposed) - {*PROJECT_KEYS, "cli"}:
            raise UsageError("Initialization input accepts only allowed_commands, delivery_checks, extra_dirs, and cli")
        proposed_cli = proposed.get("cli", {})
        if not isinstance(proposed_cli, dict):
            raise UsageError("Initialization 'cli' must be a table")
        original = path.read_bytes() if path.exists() else None
        if original is None:
            template_path = Path(__file__).resolve().parents[2] / "assets" / "config.example.toml"
            config = _parse_config(template_path.read_text(encoding="utf-8-sig"), template_path)
            if "." not in config["projects"]:
                raise UsageError(f"Initialization template requires [projects.\".\"] in {template_path}")
            project_template = config["projects"]["."]
        else:
            config = _parse_config(original.decode("utf-8-sig"), path)
            project_template = next((value for key, value in config["projects"].items()
                                     if key == "." or _same_path(key, project_root)), {})
        exists = original is not None and project_configured(config, project_root)
        proposed = {**project_template, **{key: value for key, value in proposed.items() if key != "cli"}}
        _check_project(proposed, path, str(project_root))
        proposed_settings = copy.deepcopy(config)
        proposed_settings["cli"].update(proposed_cli)
        proposed_settings["defaults"].update(requested_roles)
        _check(proposed_settings, path)
        if not exists:
            # Local files use '.' so moving a checkout does not invalidate its settings.
            project_key = "." if path == project_root / ".cross-agent" / "config.toml" else project_root.as_posix()
            section = ""
            if original is None:
                proposed_settings["projects"] = {project_key: proposed}
                updated = _render_config(proposed_settings).encode("utf-8")
            else:
                section += f'\n[projects.{json.dumps(project_key, ensure_ascii=False)}]\n'
                section += "".join(f"{key} = {json.dumps(value, ensure_ascii=False)}\n" for key, value in proposed.items())
                updated = original + section.encode("utf-8")
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
        if path.is_relative_to(gitops.repo_root(project_root)):
            gitops.ensure_excluded(project_root)
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
            "proposed_role_differences": {
                key: value for key, value in requested_roles.items() if value != config["defaults"][key]
            },
            "proposed_cli_differences": {
                key: value for key, value in proposed_cli.items() if value != config["cli"].get(key)
            },
            "providers_on_path": {provider: shutil.which(provider) is not None for provider in ("claude", "codex")},
            "cli_executables": cli_executables(config),
            "codex_version": check_codex_version(config["cli"].get("codex")) if check_version else {
                "status": "skipped", "installed": None, "latest": None,
            },
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
    for provider, executable in config["cli"].items():
        if provider not in ("claude", "codex") or not isinstance(executable, str) or not Path(executable).is_absolute():
            raise UsageError(f"[cli] in {path} accepts only absolute 'claude' or 'codex' executable paths")
    for role in ("producer", "reviewer"):
        value = config["defaults"].get(role)
        if not isinstance(value, str):
            raise UsageError(f"Missing or invalid [defaults] {role} in {path}")
        spec = parse_spec(value)
        configured_executable(config, spec.provider, path)
    for project, settings in config["projects"].items():
        _check_project(settings, path, project)


def _check_project(settings: dict, path: Path, project: str) -> None:
    if not isinstance(settings, dict):
        raise UsageError(f"[projects.\"{project}\"] in {path} must be a table")
    missing = set(PROJECT_KEYS) - set(settings)
    if missing:
        raise UsageError(f"Missing required project keys {sorted(missing)} in [projects.\"{project}\"] of {path}")
    for key, value in settings.items():
        if key not in PROJECT_KEYS:
            raise UsageError(f"Unknown key '{key}' in [projects.\"{project}\"] of {path}")
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise UsageError(f"'{key}' in [projects.\"{project}\"] of {path} must be a list of strings")


def configured_executable(config: dict, provider: str, path: Path | None = None) -> str | None:
    if provider == "fake":
        return None
    executable = config["cli"].get(provider)
    if not executable:
        raise UsageError(f"Missing required [cli] {provider} in {path or 'configuration'}; specify an absolute executable path")
    return executable


def cli_executables(config: dict) -> dict:
    """Report configured executables only, without implicit PATH selection."""
    return {provider: shutil.which(executable) for provider, executable in config["cli"].items()}


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True)
class RoleSpec:
    provider: str
    model: str
    effort: str

    def as_dict(self) -> dict:
        return {"provider": self.provider, "model": self.model, "effort": self.effort}


def parse_spec(text: str) -> RoleSpec:
    """Require an explicit provider, model, and effort for every role."""
    parts = text.strip().split(":")
    if len(parts) != 3 or not all(part.strip() for part in parts):
        raise UsageError(f"Role spec '{text}' must provide <provider>:<model>:<effort>; all three are required")
    provider = parts[0].lower()
    if provider not in PROVIDERS:
        raise UsageError(f"Unknown provider '{parts[0]}'; use claude or codex")
    model, effort = parts[1].strip(), parts[2].strip()
    return RoleSpec(provider, model, effort)


def _same_path(left: str | Path, right: str | Path) -> bool:
    def norm(path):
        return os.path.normcase(str(Path(path).expanduser().resolve()))

    return norm(left) == norm(right)


def project_settings(config: dict, project_root: Path) -> dict:
    """Return the project's commands and extra directories, keyed by its root path."""
    settings = next(
        (value for key, value in config["projects"].items() if key == "." or _same_path(key, project_root)),
        None,
    )
    if settings is None:
        raise UsageError(f"Missing project configuration for {project_root}; run init explicitly")
    return {
        "allowed_commands": list(settings["allowed_commands"]),
        "delivery_checks": list(settings["delivery_checks"]),
        "extra_dirs": [str((project_root / item).resolve()) for item in settings["extra_dirs"]],
    }


def project_configured(config: dict, project_root: Path) -> bool:
    return any(key == "." or _same_path(key, project_root) for key in config["projects"])


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
