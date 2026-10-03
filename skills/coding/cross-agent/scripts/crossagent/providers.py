"""Provider adapters for Claude Code and Codex, plus a scripted fake for tests.

Each adapter owns its volatile command-line flags, output parsing, session IDs,
context measurement, and local session cleanup. The engine sees only `Call`
and `CallResult`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable
from pathlib import Path

from .errors import UsageError
from .progress import Observer, codex_usage, token_counts

EXCERPT_CHARS = 4000
SESSION_ID = re.compile(r"^[0-9A-Za-z][0-9A-Za-z_-]{7,}$")


@dataclass
class Call:
    role: str  # "producer" or "reviewer"
    model: str | None
    effort: str | None
    prompt: str
    schema: dict
    session_id: str | None  # None starts a new session
    cwd: Path
    read_dirs: list[str]
    write_dirs: list[str]
    allowed_commands: list[str]
    timeout: int  # seconds
    work_dir: Path
    progress: Callable | None = None
    telemetry: dict = field(default_factory=dict)
    executable: str | None = None
    loaded_skill: dict | None = None
    token_baseline: dict | None = None


@dataclass
class CallResult:
    data: dict | None = None
    session_id: str | None = None
    context_tokens: int | None = None
    error: str | None = None
    raw: str = ""


def _excerpt(text: str | bytes | None) -> str:
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return (text or "")[-EXCERPT_CHARS:]


def _parse_json_text(text: str):
    """Read a JSON object from a final message, tolerating a Markdown fence."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


def _delete(paths) -> list[str]:
    deleted = []
    for path in paths:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            else:
                continue
            deleted.append(str(path))
        except OSError:
            continue
    return deleted


def _run(command: list[str], call: Call, env: dict | None = None):
    observer = Observer(call)
    process = subprocess.Popen(command, cwd=call.cwd, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               encoding="utf-8", errors="replace", bufsize=1)
    lines = queue.Queue()
    output = []

    def read():
        try:
            for line in process.stdout:
                lines.put(line)
        finally:
            lines.put(None)

    def write():
        try:
            process.stdin.write(call.prompt)
        except (BrokenPipeError, OSError):
            pass
        finally:
            process.stdin.close()

    threading.Thread(target=read, daemon=True).start()
    threading.Thread(target=write, daemon=True).start()
    deadline = time.monotonic() + call.timeout
    heartbeat = time.monotonic() + 30
    rollout_session = None
    rollout_path = None
    rollout_offset = 0
    poll_at = 0
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, call.timeout, output="".join(output))
            try:
                line = lines.get(timeout=min(1, remaining))
            except queue.Empty:
                line = ""
            if line is None:
                break
            if line:
                output.append(line)
                try:
                    event = json.loads(line)
                    observer.observe(event)
                    if isinstance(event, dict) and event.get("type") == "thread.started":
                        rollout_session = event.get("thread_id")
                except json.JSONDecodeError:
                    pass
            if rollout_session and time.monotonic() >= poll_at:
                poll_at = time.monotonic() + 5
                try:
                    if rollout_path is None:
                        paths = _codex_rollouts(rollout_session)
                        rollout_path = paths[-1] if paths else None
                    if rollout_path:
                        with rollout_path.open(encoding="utf-8", errors="replace") as handle:
                            handle.seek(rollout_offset)
                            while chunk := handle.readline():
                                if not chunk.endswith("\n"):
                                    break
                                rollout_offset = handle.tell()
                                try:
                                    observer.observe(json.loads(chunk))
                                except json.JSONDecodeError:
                                    pass
                except OSError:
                    pass  # Private rollouts are optional observations, never a prerequisite.
            if time.monotonic() >= heartbeat:
                observer.emit("heartbeat")
                heartbeat = time.monotonic() + 30
        process.wait(timeout=max(0.01, deadline - time.monotonic()))
    finally:
        if process.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
            process.kill()
            process.wait()
        process.stdout.close()
    return subprocess.CompletedProcess(command, process.returncode, "".join(output), "")


def _executable(provider: str, configured: str | None = None) -> str:
    """Require the selected configuration path; never fall back to PATH."""
    if not configured:
        raise UsageError(f"Missing configured {provider} CLI executable path")
    selected = shutil.which(configured)
    if not selected:
        raise UsageError(f"Configured {provider} CLI does not exist or is not executable: {configured}")
    return selected


def _require_role(call: Call) -> None:
    if not all(isinstance(value, str) and value.strip() for value in (call.model, call.effort)):
        raise UsageError(f"The {call.role} must explicitly configure model and effort; incomplete saved roles cannot fall back to CLI defaults")


class Claude:
    name = "claude"

    def check(self, executable: str | None = None) -> None:
        _executable("claude", executable)

    def command(self, call: Call, session_id: str, new: bool) -> list[str]:
        _require_role(call)
        command = [
            _executable("claude", call.executable),
            "-p",
            "--output-format",
            "stream-json",
            "--verbose",
            "--json-schema",
            json.dumps(call.schema),
            "--strict-mcp-config",
            "--permission-prompts",
            "none",
        ]
        command += ["--session-id", session_id] if new else ["--resume", session_id]
        if call.model:
            command += ["--model", call.model]
        if call.effort:
            command += ["--effort", call.effort]
        for directory in [*call.read_dirs, *call.write_dirs]:
            command += ["--add-dir", directory]
        if call.role == "reviewer":
            command += ["--tools", "Read,Grep,Glob"]
        else:
            command += ["--permission-mode", "acceptEdits"]
            if call.allowed_commands:
                tools = [f"Bash({item}:*)" for item in call.allowed_commands]
                if os.name == "nt":
                    tools += [f"PowerShell({item}:*)" for item in call.allowed_commands]
                command += ["--allowedTools", ",".join(tools)]
        return command

    def run(self, call: Call) -> CallResult:
        new = call.session_id is None
        session_id = str(uuid.uuid4()) if new else call.session_id
        env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_EFFORT_LEVEL": call.effort}
        try:
            process = _run(self.command(call, session_id, new), call, env)
        except subprocess.TimeoutExpired as exc:
            return CallResult(session_id=session_id, error=f"timed out after {call.timeout} s", raw=_excerpt(exc.stdout))
        result = CallResult(session_id=session_id, raw=_excerpt(process.stdout + process.stderr))
        final = None
        for line in process.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = event.get("type")
            if kind == "system" and event.get("session_id"):
                result.session_id = event["session_id"]
            elif kind == "assistant" and not event.get("parent_tool_use_id"):
                usage = (event.get("message") or {}).get("usage") or {}
                size = sum(
                    usage.get(key) or 0
                    for key in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
                )
                if size:
                    result.context_tokens = size  # the latest request's context size
            elif kind == "result":
                final = event
        if process.returncode != 0 or final is None or final.get("is_error"):
            detail = f": {final.get('subtype')} {final.get('result') or ''}".rstrip() if final else ""
            result.error = f"exited with code {process.returncode}{detail}"
            return result
        data = final.get("structured_output")
        if data is None:
            data = _parse_json_text(final.get("result") or "")
        if not isinstance(data, dict):
            result.error = "returned no structured output"
            return result
        result.data = data
        return result

    def cleanup(self, session_id: str) -> list[str]:
        if not SESSION_ID.match(session_id):
            return []
        home = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        return _delete(
            [
                *home.glob(f"projects/*/{session_id}.jsonl"),
                *home.glob(f"projects/*/{session_id}"),
                home / "file-history" / session_id,
                home / "session-env" / session_id,
            ]
        )


def _codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def _codex_rollouts(session_id: str) -> list[Path]:
    if not session_id or not SESSION_ID.match(session_id):
        return []
    home = _codex_home()
    files = []
    for folder in ("sessions", "archived_sessions"):
        if (home / folder).is_dir():
            files += (home / folder).rglob(f"rollout-*{session_id}.jsonl")
    return sorted(files, key=lambda path: path.stat().st_mtime)


def _codex_context_tokens(session_id: str | None) -> int | None:
    """Read the latest request's input tokens from the session rollout; None when unknown."""
    rollouts = _codex_rollouts(session_id or "")
    if not rollouts:
        return None
    latest = None
    for line in rollouts[-1].read_text(encoding="utf-8", errors="replace").splitlines():
        if '"token_count"' not in line:
            continue
        try:
            latest = json.loads(line)["payload"]["info"]["last_token_usage"]["input_tokens"]
        except (KeyError, TypeError, json.JSONDecodeError):
            continue
    return latest


def _codex_token_totals(session_id: str | None) -> dict | None:
    """Optional baseline/partial usage from this worker's own rollout, never a transcript export."""
    try:
        rollouts = _codex_rollouts(session_id or "")
        if not rollouts:
            return None
        latest = None
        for line in rollouts[-1].read_text(encoding="utf-8", errors="replace").splitlines():
            if '"token_count"' not in line:
                continue
            try:
                info = json.loads(line)["payload"]["info"]
                counts = token_counts(info.get("total_token_usage"))
                if counts:
                    latest = counts
            except (KeyError, TypeError, json.JSONDecodeError):
                continue
        return latest
    except OSError:
        return None


class Codex:
    name = "codex"

    def check(self, executable: str | None = None) -> None:
        _executable("codex", executable)

    def command(self, call: Call, schema_file: Path, output_file: Path) -> list[str]:
        _require_role(call)
        mode = "read-only" if call.role == "reviewer" else "workspace-write"
        command = [_executable("codex", call.executable), "exec"]
        if call.session_id:
            # `exec resume` has no --sandbox flag, so the mode is always set through -c.
            command += ["resume", call.session_id]
        command += [
            "--json",
            "--skip-git-repo-check",
            "-c",
            f'sandbox_mode="{mode}"',
            # Never escalate: a user config with on-request approvals and an automatic
            # approvals reviewer would otherwise let a worker leave its sandbox.
            "-c",
            'approval_policy="never"',
            "--disable",
            "memories",
            "--output-schema",
            str(schema_file),
            "-o",
            str(output_file),
        ]
        if call.role == "producer" and call.write_dirs:
            roots = [directory.replace("\\", "/") for directory in call.write_dirs]
            command += ["-c", "sandbox_workspace_write.writable_roots=" + json.dumps(roots)]
        if call.role == "reviewer":
            command += ["--disable", "multi_agent"]
        if call.model:
            command += ["-m", call.model]
        if call.effort:
            command += ["-c", f'model_reasoning_effort="{call.effort}"']
        command.append("-")  # read the prompt from stdin
        return command

    def run(self, call: Call) -> CallResult:
        if call.session_id:
            call.token_baseline = _codex_token_totals(call.session_id) or call.token_baseline
        schema_file = call.work_dir / f"{call.role}.schema.json"
        output_file = call.work_dir / f"{call.role}.last-message.json"
        schema_file.write_text(json.dumps(call.schema), encoding="utf-8")
        if output_file.exists():
            output_file.unlink()
        try:
            process = _run(self.command(call, schema_file, output_file), call)
        except subprocess.TimeoutExpired as exc:
            session_id = call.telemetry.get("session_id") or call.session_id
            totals = _codex_token_totals(session_id)
            if totals:
                codex_usage(call, totals, "codex-rollout-delta", "partial")
            return CallResult(session_id=session_id, error=f"timed out after {call.timeout} s", raw=_excerpt(exc.stdout))
        result = CallResult(session_id=call.session_id, raw=_excerpt(process.stdout + process.stderr))
        failure = None
        terminal_failure = False
        for line in process.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = event.get("type")
            if kind == "thread.started" and event.get("thread_id"):
                result.session_id = event["thread_id"]
            elif kind in ("turn.failed", "error"):
                terminal_failure = terminal_failure or kind == "turn.failed"
                error = event.get("error")
                failure = (error.get("message") if isinstance(error, dict) else error) or event.get("message") or kind
            elif kind == "turn.completed" and not terminal_failure:
                codex_usage(call, event.get("usage"), "codex-session-delta", "reported")
                # A completed turn recovers transient errors, never a terminal turn failure.
                failure = None
        if process.returncode != 0 or failure:
            result.error = f"exited with code {process.returncode}" + (f": {failure}" if failure else "")
            return result
        text = output_file.read_text(encoding="utf-8", errors="replace") if output_file.is_file() else ""
        data = _parse_json_text(text)
        if not isinstance(data, dict):
            result.error = "returned no structured output"
            return result
        result.data = data
        result.context_tokens = _codex_context_tokens(result.session_id)
        return result

    def cleanup(self, session_id: str) -> list[str]:
        return _delete(_codex_rollouts(session_id))


class Fake:
    """Scripted provider for tests.

    `CROSS_AGENT_FAKE_SCRIPT` names a JSON file `{"producer": [...], "reviewer": [...]}`.
    Each step may hold `output`, `write` ({path: content}), `context_tokens`,
    `fail`, or `fail_on_resume` (fail only when resuming, without consuming the step).
    Positions and a call log live next to the script.
    """

    name = "fake"

    def check(self, executable: str | None = None) -> None:
        if not os.environ.get("CROSS_AGENT_FAKE_SCRIPT"):
            raise UsageError("The fake provider needs CROSS_AGENT_FAKE_SCRIPT")

    def command(self, call: Call, *_args) -> list[str]:
        return ["fake", call.role]

    def run(self, call: Call) -> CallResult:
        script_path = Path(os.environ["CROSS_AGENT_FAKE_SCRIPT"])
        script = json.loads(script_path.read_text(encoding="utf-8"))
        position_path = script_path.with_name(script_path.name + ".pos.json")
        positions = json.loads(position_path.read_text(encoding="utf-8")) if position_path.is_file() else {}
        index = positions.get(call.role, 0)
        with script_path.with_name(script_path.name + ".log.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps({"role": call.role, "session_id": call.session_id, "prompt": call.prompt}) + "\n")
        steps = script.get(call.role, [])
        if index >= len(steps):
            return CallResult(error=f"no scripted {call.role} step {index + 1}")
        step = steps[index]
        if step.get("fail_on_resume") and call.session_id:
            return CallResult(session_id=call.session_id, error=step["fail_on_resume"])
        positions[call.role] = index + 1
        position_path.write_text(json.dumps(positions), encoding="utf-8")
        for relative, content in step.get("write", {}).items():
            target = call.cwd / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        session_id = call.session_id or f"fake-{call.role}-{uuid.uuid4().hex[:8]}"
        if call.progress:
            call.progress({"event": "worker-ready", "session_id": session_id})
        if step.get("telemetry"):
            call.telemetry.update(step["telemetry"])
            if call.progress:
                call.progress({"event": "usage", "telemetry": dict(call.telemetry)})
        if step.get("fail"):
            return CallResult(session_id=session_id, error=step["fail"])
        return CallResult(data=step["output"], session_id=session_id, context_tokens=step.get("context_tokens"))

    def cleanup(self, session_id: str) -> list[str]:
        return []


ADAPTERS = {"claude": Claude(), "codex": Codex(), "fake": Fake()}


def get(name: str):
    return ADAPTERS[name]


def preview_command(provider: str, call: Call) -> list[str]:
    """The command a new session would run, for --dry-run."""
    adapter = get(provider)
    if provider == "claude":
        return adapter.command(call, "<new-session-id>", True)
    if provider == "codex":
        return adapter.command(
            call, call.work_dir / f"{call.role}.schema.json", call.work_dir / f"{call.role}.last-message.json"
        )
    return adapter.command(call)
