"""Git helpers: work tree checks, the local exclude, snapshots, and diffs."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .errors import GitError, UsageError

EXCLUDE_LINE = ".cross-agent/"


def git(args: list[str], cwd: Path, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def require_work_tree(cwd: Path) -> None:
    result = git(["rev-parse", "--is-inside-work-tree"], cwd, check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise UsageError("Run cross-agent from a project root inside a Git work tree")


def repo_root(cwd: Path) -> Path:
    return Path(git(["rev-parse", "--show-toplevel"], cwd).stdout.strip()).resolve()


def _git_path(cwd: Path, name: str) -> Path:
    path = Path(git(["rev-parse", "--git-path", name], cwd).stdout.strip())
    return path if path.is_absolute() else Path(cwd) / path


def ensure_excluded(cwd: Path) -> None:
    """Keep run state out of every snapshot without changing a tracked file."""
    path = _git_path(cwd, "info/exclude")
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if EXCLUDE_LINE in (line.strip() for line in text.splitlines()):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    separator = "" if not text or text.endswith("\n") else "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{separator}{EXCLUDE_LINE}\n")


def snapshot(cwd: Path, index_file: Path) -> str:
    """Record the whole work tree as a tree object, using a private index.

    The first call copies the user's index so later `add -A` calls only rehash
    changed files; the user's index and files are never modified.
    """
    env = {**os.environ, "GIT_INDEX_FILE": str(index_file)}
    if not index_file.exists():
        real_index = _git_path(cwd, "index")
        if real_index.is_file():
            shutil.copyfile(real_index, index_file)
        elif git(["rev-parse", "--verify", "-q", "HEAD"], cwd, check=False).returncode == 0:
            git(["read-tree", "HEAD"], cwd, env=env)
        else:
            git(["read-tree", "--empty"], cwd, env=env)
    git(["add", "-A"], cwd, env=env)
    return git(["write-tree"], cwd, env=env).stdout.strip()


def diff(cwd: Path, before: str, after: str) -> str:
    if before == after:
        return ""
    return git(["diff", "--no-color", "--no-ext-diff", before, after], cwd).stdout


def changed_files(cwd: Path, before: str, after: str) -> list[str]:
    if before == after:
        return []
    output = git(["diff", "--name-only", before, after], cwd).stdout
    return [line for line in output.splitlines() if line]


def base_description(cwd: Path, path: str) -> str:
    """Describe the commit an item was found against, for the backlog."""
    head = git(["rev-parse", "--short", "HEAD"], cwd, check=False)
    if head.returncode != 0:
        return "`uncommitted`"
    dirty = git(["status", "--porcelain", "--", path], cwd, check=False).stdout.strip()
    commit = f"`{head.stdout.strip()}`"
    return f"{commit} with uncommitted changes" if dirty else commit
