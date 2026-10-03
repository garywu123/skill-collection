"""Read-only Codex CLI comparison against the published npm latest release."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from urllib.request import urlopen

CODEX_LATEST_URL = "https://registry.npmjs.org/@openai/codex/latest"


def check_codex_version(executable: str | None = None) -> dict:
    result = {"status": "unknown", "installed": None, "latest": None, "source": CODEX_LATEST_URL, "reason": None}
    executable = shutil.which(executable) if executable else None
    if not executable:
        return {**result, "status": "not-installed", "reason": "Selected Codex CLI is unavailable"}
    try:
        process = subprocess.run(
            [executable, "--version"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=5,
        )
        match = re.search(r"\b(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\b", process.stdout)
        if process.returncode or not match:
            return {**result, "reason": "codex --version did not report a recognized version"}
        result["installed"] = match.group(1)
        with urlopen(CODEX_LATEST_URL, timeout=5) as response:
            latest = json.loads(response.read(1_000_000))["version"]
        if not isinstance(latest, str) or not re.fullmatch(r"\d+\.\d+\.\d+", latest):
            return {**result, "reason": "npm latest did not report a stable version"}
        result["latest"] = latest
        if "-" in result["installed"]:
            return {**result, "reason": "Installed prerelease cannot be classified as the latest stable release"}
        installed_numbers = tuple(map(int, result["installed"].split("+")[0].split(".")))
        latest_numbers = tuple(map(int, latest.split(".")))
        result["status"] = "current" if installed_numbers == latest_numbers else (
            "update-available" if installed_numbers < latest_numbers else "ahead"
        )
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as exc:
        result["reason"] = f"Version comparison unavailable ({type(exc).__name__})"
    return result
