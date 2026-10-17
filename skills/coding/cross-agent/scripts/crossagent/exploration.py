"""Direct expert control and explicit handoff into the existing run loop."""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from . import evidence, gitops, history, providers, schemas, store
from .errors import UsageError


def command(state: dict) -> tuple[list[str], providers.Call]:
    from . import engine
    prompt = ("You are the domain expert speaking directly with the user, in their language. "
              "Explore only: do not write project files or start other agents. Read AGENTS.md, CLAUDE.md "
              "when present, and relevant project sources. Use the supplied Skill's exploration boundary. "
              "Continue from the supplied context; ask only consequential unanswered questions. "
              "No project title, codename or test token is required. Distinguish user-confirmed decisions "
              "from your candidates and superseded choices. Writing needs explicit user authorization and "
              "Orch promotion; when ready, ask the user to return control to Orch. Exiting is not approval.\n\n"
              "Discussion request and known background:\n" + state["request"])
    call = engine._call(state, "producer", prompt, schemas.PRODUCER, None)
    args = [providers._executable("claude", call.executable)]
    info = state["exploration"]
    sources = evidence.claude_sources(info["session_id"])
    if len(sources) > 1:
        raise UsageError("Claude discussion source is ambiguous for this session.")
    args += ["--resume" if sources else "--session-id", info["session_id"]]
    args += ["--model", call.model, "--effort", call.effort, "--tools", "Read,Grep,Glob",
             "--permission-mode", "plan", "--strict-mcp-config"]
    for directory in call.read_dirs:
        args += ["--add-dir", directory]
    args += ["--", call.prompt]  # --add-dir is variadic; the prompt must stay positional.
    if os.name == "nt" and len(subprocess.list2cmdline(args)) > 30000:
        raise UsageError("Interactive context exceeds Windows command-line capacity; shorten the request or use relay")
    return args, call


def _process_alive(pid: int) -> bool:
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True
    # Windows os.kill(pid, 0) sends CTRL_C_EVENT instead of probing liveness.
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE only; no signalling rights.
    if not handle:
        error = ctypes.get_last_error()
        if error == 87:  # ERROR_INVALID_PARAMETER: the PID no longer exists.
            return False
        raise ctypes.WinError(error)
    try:
        result = kernel.WaitForSingleObject(handle, 0)
        if result not in (0, 258):  # WAIT_OBJECT_0 (exited), WAIT_TIMEOUT (running).
            raise ctypes.WinError(ctypes.get_last_error())
        return result == 258
    finally:
        kernel.CloseHandle(handle)


def expert(root: Path, run_id: str, *, release=False) -> dict:
    from . import engine
    state = store.load(root, run_id)
    lock = engine._run_dir(state) / "interactive.lock"
    if release:
        if state["phase"] != "interacting":
            raise UsageError("Only an interrupted interactive session needs release")
        pid = state["exploration"].get("pid")
        if pid:
            try:
                alive = _process_alive(pid)
            except OSError as exc:
                raise UsageError("Cannot verify the interrupted expert has stopped") from exc
            if alive:
                raise UsageError("The expert process is still alive; stop it before releasing control")
        # The caller confirms the terminal is stopped. Never kill it.
        state["phase"] = "explore"
        state["exploration"]["released_after_interruption"] = store.now()
        lock.unlink(missing_ok=True)
        store.save(state)
        return engine._event(state, "Control released by explicit operator confirmation; inspect before promotion.")
    if state["phase"] != "explore":
        raise UsageError("Only an explore run can open an expert terminal")
    args, call = command(state)
    try:
        handle = lock.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise UsageError("An expert terminal owns this run; wait for it to return") from exc
    with handle:
        handle.write(str(os.getpid()))
    state["phase"] = "interacting"
    state["protected_sessions"] = list(set(state.get("protected_sessions", []) + [state["exploration"]["session_id"]]))
    state["exploration"]["launched"] = True
    state["exploration"].setdefault("orch_prompt_sha256", []).append(
        hashlib.sha256(call.prompt.encode("utf-8")).hexdigest())
    store.save(state)
    started = time.monotonic()
    code = None
    try:
        env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_EFFORT_LEVEL": call.effort}
        process = subprocess.Popen(args, cwd=root, env=env)
        state["exploration"]["pid"] = process.pid
        store.save(state)
        try:
            code = process.wait()
        except KeyboardInterrupt:
            try:
                code = process.wait(timeout=1)
            except subprocess.TimeoutExpired as exc:
                raise UsageError("Expert still running; stop the terminal process before expert --release") from exc
    except OSError as exc:
        code = -1
        raise UsageError(f"Cannot launch the expert terminal: {exc}") from exc
    finally:
        if code is not None:
            state["phase"] = "explore"
            state["exploration"].pop("pid", None)
            state["exploration"]["returned_at"] = store.now()
            lock.unlink(missing_ok=True)
        state["exploration"]["elapsed_seconds"] = round(time.monotonic() - started, 3)
        state["exploration"]["usage_status"] = "unknown"
        store.save(state)
    return engine._event(state, "Expert process returned; no writing or submission inferred.", exit_code=code)


def promote(root: Path, run_id: str, *, artifact: str, request: str,
            skip_review=False, reason=None, reconcile=None) -> dict:
    from . import engine
    state = store.load(root, run_id)
    if state["phase"] != "explore" or (engine._run_dir(state) / "interactive.lock").exists():
        raise UsageError("Return exclusive control from the expert terminal before promotion")
    if not request.strip():
        raise UsageError("Promotion requires --request citing explicit write authorization and the intended output")
    if skip_review and not (reason or "").strip():
        raise UsageError("Skipping review requires --reason citing the user's opt-out")
    target = (root / artifact).resolve()
    if not target.is_relative_to(Path(state["repo_root"])):
        raise UsageError("Artifact must stay inside this Git repository")
    relative = Path(os.path.relpath(target, root)).as_posix()
    for other in store.open_runs(root):
        if other["run_id"] != run_id and other.get("artifact") == relative:
            raise UsageError(f"Run {other['run_id']} already owns {relative}")
    tree = gitops.snapshot(root, engine._index(state))
    changed = gitops.changed_files(root, state["trees"]["baseline"], tree)
    if changed and not (reconcile or "").strip():
        raise UsageError("Worktree changed during exploration; explicit --reconcile user direction is required: "
                         + ", ".join(changed))
    manifest = evidence.import_claude(root, state["exploration"]["session_id"],
                                      engine._run_dir(state) / "discussion.json")
    state["discussion_evidence"] = manifest
    state["discussion_evidence"]["orch_prompt_sha256"] = state["exploration"].get("orch_prompt_sha256", [])
    state["exploration_transition"] = {"at": store.now(), "tree": tree, "changed_files": changed,
                                       "reconciliation": reconcile, "write_authorization": request.strip()}
    state["request"] = request.strip()
    state["artifact"] = relative
    state["first"] = "produce"
    state["review_policy"] = {"skip": bool(skip_review), "reason": reason}
    worker = state["workers"]["producer"]
    worker.update(session_id=state["exploration"]["session_id"], generation=1)
    worker["sessions"].append(worker["session_id"])
    state["protected_sessions"] = list(set(state.get("protected_sessions", []) + [worker["session_id"]]))
    state["phase"] = "produce"
    store.save(state)
    return engine._event(state, "Explicit write authorization recorded; next resumes the same expert as Producer.")


def waive_review(root: Path, run_id: str, reason: str) -> dict:
    from . import engine
    state = store.load(root, run_id)
    if state["phase"] != "review" or state["reviews_done"] or not reason.strip():
        raise UsageError("Waive only an unstarted first review, with the user's explicit reason; never bypass findings")
    state["review_policy"] = {"skip": True, "reason": reason.strip()}
    state["phase"] = "done"
    state["final_status"] = ("needs-user-decision" if any(c["exit_code"] != 0 for c in state["checks"])
                             else "completed-without-review")
    store.save(state)
    return engine._event(state, "Independent review explicitly waived; checks and their failures remain recorded.")


def retain(state: dict) -> str | None:
    """Freeze evidence and handoff before any session or live state is deleted."""
    if not state.get("exploration"):
        return None
    from . import engine
    root = engine._root(state)
    destination = history.run_file(root, state["run_id"]).with_suffix("")
    destination.mkdir(parents=True, exist_ok=True)
    manifest = state.get("discussion_evidence")
    if manifest:
        evidence.read(manifest)
        shutil.copyfile(manifest["file"], destination / "discussion.json")
        manifest = {**manifest, "file": str(destination / "discussion.json")}
        evidence.read(manifest)
    elif state["exploration"].get("launched"):
        try:
            manifest = evidence.import_claude(root, state["exploration"]["session_id"], destination / "discussion.json")
        except (UsageError, OSError) as exc:
            if state.get("exploration_transition"):
                raise
            state["discussion_evidence_gap"] = {
                "provider": "claude", "session_id": state["exploration"]["session_id"], "reason": str(exc)}
    handoff = {"run_id": state["run_id"], "stage": state["stage"], "artifact": state["artifact"],
               "request": state["request"], "exploration": state["exploration"],
               "transition": state.get("exploration_transition"), "evidence": manifest,
               "evidence_gap": state.get("discussion_evidence_gap"),
               "report": engine._report(state)}
    (destination / "handoff.json").write_text(json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(destination)


def forget_history(root: Path, run_id: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{7,100}", run_id):
        raise UsageError("Invalid run ID")
    if store.run_path(root, run_id).exists():
        raise UsageError("Close the run before deleting retained evidence/history")
    csv = history.run_file(root, run_id)
    folder = csv.with_suffix("")
    if folder.is_symlink() or (hasattr(folder, "is_junction") and folder.is_junction()):
        raise UsageError("Refusing a linked history directory")
    if folder.exists():
        shutil.rmtree(folder)
    csv.unlink(missing_ok=True)
    history.export(root)  # Remove the same rows from the aggregate CSV too.
    return {"run_id": run_id, "deleted_local_history": True, "provider_sessions_deleted": False}
