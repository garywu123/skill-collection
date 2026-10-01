"""The run state machine behind start, next, decide, answer, status, and close.

A run moves through these phases:

    produce -> review -> awaiting-decision -> produce -> ... -> finalizing -> done

`awaiting-answer` interrupts a Producer step until the user answers, and a run
ends early in `done` when an adjudicated review leaves nothing accepted.
`failed` and `blocked` keep the run open until the user abandons it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from . import __version__, backlog, gitops, prompts, providers, schemas, store
from . import config as cfg
from .errors import GitError, UsageError

TERMINAL = ("done", "failed", "blocked")
BACKLOG_FILE = "docs/review-backlog.md"
CHECK_EXCERPT_LINES = 40
EXCERPT_CHARS = 4000

NEXT_ACTION = {
    "produce": "Call next to run the Producer.",
    "review": "Call next to run the Reviewer.",
    "awaiting-decision": "Adjudicate every pending finding, then call decide.",
    "awaiting-answer": "Relay the questions to the user, then call answer.",
    "finalizing": "Fix accepted local problems in one batch, record unfixed ones with decide, then call next.",
    "done": "Report the result, then call close.",
    "failed": "Report the error. Close the run only when the user abandons it.",
    "blocked": "Report the blocker. Close the run only when the user abandons it.",
}


class StepFailed(Exception):
    """A worker, schema, or snapshot failure that ends the run as failed."""

    def __init__(self, message: str, raw: str = ""):
        super().__init__(message)
        self.raw = raw


# ---------------------------------------------------------------- commands


def start(project_root: Path, *, stage, artifact, first, request, producer, reviewer, dry_run) -> dict:
    project_root = project_root.resolve()
    gitops.require_work_tree(project_root)
    config = cfg.load_config(project_root)
    request = (request or "").strip() or None
    if first == "produce" and not request:
        raise UsageError("--first produce needs --request with a concrete change")
    if stage == "general" and not request:
        raise UsageError("Stage general needs --request; it is the only statement of the intended outcome")
    artifact_path = (project_root / artifact).resolve()
    if first == "review" and not artifact_path.is_file():
        raise UsageError(f"Artifact {artifact} does not exist; start with --first produce to create it")
    repo = gitops.repo_root(project_root)
    if not artifact_path.is_relative_to(repo):
        raise UsageError(f"Artifact {artifact} is outside the Git repository {repo}")
    artifact_rel = Path(os.path.relpath(artifact_path, project_root)).as_posix()
    roles = {
        "producer": cfg.parse_spec(producer or config["defaults"]["producer"]),
        "reviewer": cfg.parse_spec(reviewer or config["defaults"]["reviewer"]),
    }
    for spec in roles.values():
        providers.get(spec.provider).check()
    skill = cfg.find_stage_skill(config, stage)
    for run in store.open_runs(project_root):
        if run.get("artifact") == artifact_rel:
            raise UsageError(
                f"Run {run.get('run_id')} is already open on {artifact_rel} (phase {run.get('phase')}); "
                "continue it with next, or close it first"
            )
    state = {
        "state_version": store.STATE_VERSION,
        "cli_version": __version__,
        "run_id": store.new_run_id(stage),
        "created_at": store.now(),
        "project_root": str(project_root),
        "repo_root": str(repo),
        "stage": stage,
        "skill": str(skill) if skill else None,
        "artifact": artifact_rel,
        "first": first,
        "request": request,
        "settings": {key: config[key] for key in cfg.RUN_SETTINGS},
        "project": cfg.project_settings(config, project_root),
        "roles": {role: spec.as_dict() for role, spec in roles.items()},
        "workers": {
            role: {"session_id": None, "generation": 0, "context_tokens": None, "sessions": []} for role in roles
        },
        "phase": "produce" if first == "produce" else "review",
        "reviews_done": 0,
        "producer_steps": 0,
        "findings": [],
        "notes": [],
        "pending": [],
        "questions": [],
        "answer": None,
        "answers": [],
        "producer_summaries": [],
        "checks": [],
        "trees": {"baseline": None, "last_review": None, "finalizing": None},
        "finalization": None,
        "final_status": None,
        "error": None,
    }
    if dry_run:
        return _dry_run(state)
    gitops.ensure_excluded(project_root)
    _run_dir(state).mkdir(parents=True)
    try:
        state["trees"]["baseline"] = gitops.snapshot(project_root, _index(state))
    except GitError as exc:
        shutil.rmtree(_run_dir(state), ignore_errors=True)
        raise UsageError(f"Cannot snapshot the work tree: {exc}") from exc
    store.save(state)
    return _event(state, "Run started.")


def next_step(project_root: Path, run_id: str, progress=None) -> dict:
    state = store.load(project_root, run_id)
    try:
        if state["phase"] == "produce":
            return _producer_step(state, progress)
        if state["phase"] == "review":
            return _review_step(state, progress)
        if state["phase"] == "finalizing":
            return _finish(state)
    except StepFailed as exc:
        return _fail(state, str(exc), exc.raw)
    except GitError as exc:
        return _fail(state, str(exc))
    return _event(state, "No step to run; this is the pending event.")


def retry_review(project_root: Path, run_id: str) -> dict:
    """Retry only a Reviewer execution failure without losing Producer context."""
    state = store.load(project_root, run_id)
    message = (state.get("error") or {}).get("message", "")
    if state["phase"] != "failed" or not message.startswith("The reviewer ("):
        raise UsageError("Only a failed Reviewer execution can be retried; validation failures stay closed")
    if state["reviews_done"] >= state["settings"]["max_reviews"]:
        raise UsageError("The review budget is exhausted")
    providers.get(state["roles"]["reviewer"]["provider"]).check()
    # Keep the failed session in cleanup history; only the Reviewer starts fresh.
    state["workers"]["reviewer"]["session_id"] = None
    state["workers"]["reviewer"]["context_tokens"] = None
    state["phase"] = "review"
    state["final_status"] = None
    state["error"] = None
    store.save(state)
    return _event(state, "Reviewer execution retry armed; Producer session and review budget preserved.")


def decide(project_root: Path, run_id: str, input_path: str) -> dict:
    state = store.load(project_root, run_id)
    phase = state["phase"]
    if phase not in ("awaiting-decision", "finalizing"):
        raise UsageError(f"Run {run_id} is not waiting for decisions (phase {phase})")
    try:
        payload = json.loads(Path(input_path).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UsageError(f"Cannot read decisions from {input_path}: {exc}") from exc
    errors = schemas.validate(payload, schemas.DECIDE)
    if errors:
        raise UsageError("The decisions do not match the schema: " + "; ".join(errors[:5]))
    decisions = payload["decisions"]
    ids = [decision["finding_id"] for decision in decisions]
    if len(ids) != len(set(ids)):
        raise UsageError("Decide each finding at most once per call")
    findings = _findings(state)
    if phase == "awaiting-decision":
        expected = set(state["pending"])
        missing, extra = sorted(expected - set(ids)), sorted(set(ids) - expected)
        if missing or extra:
            raise UsageError(f"Decide exactly the pending findings; missing {missing}, not pending {extra}")
    else:
        extra = sorted(set(ids) - {finding["id"] for finding in _work_list(state)})
        if extra:
            raise UsageError(f"In finalization, decide only remaining accepted findings; not remaining: {extra}")
        if any(decision["disposition"] != "needs-user-decision" for decision in decisions):
            raise UsageError("In finalization, record only the findings left for the user, as needs-user-decision")
    for decision in decisions:
        _check_decision(decision, findings[decision["finding_id"]])
    for decision in decisions:
        finding = findings[decision["finding_id"]]
        finding["history"].append({"review": state["reviews_done"], **{k: v for k, v in decision.items() if k != "finding_id"}})
        finding["disposition"] = decision["disposition"]
        finding["rationale"] = (decision["rationale"] or "").strip() or None
        finding["priority"] = decision["priority"]
        if phase == "finalizing":
            finding["left_open"] = True
    if phase == "finalizing":
        store.save(state)
        return _event(state, "Recorded the findings left for the user.")
    state["pending"] = []
    if _work_list(state):
        state["phase"] = "produce"
        store.save(state)
        return _event(state, "Accepted findings go to the Producer.")
    state["phase"] = "done"
    state["final_status"] = "needs-user-decision" if any(c["exit_code"] != 0 for c in state["checks"]) else "independently-passed"
    store.save(state)
    return _event(state, "No finding was accepted.")


def answer(project_root: Path, run_id: str, text: str) -> dict:
    state = store.load(project_root, run_id)
    if state["phase"] not in ("awaiting-answer", "blocked"):
        raise UsageError(f"Run {run_id} is not waiting for an answer (phase {state['phase']})")
    text = text.strip()
    if not text:
        raise UsageError("The answer is empty")
    questions = state["questions"]
    if state["phase"] == "blocked":
        # Only Producer-reported blockers use this phase; failed guards stay closed.
        questions = [(state.get("error") or {}).get("message") or "The Producer is blocked."]
    state["answer"] = {"questions": questions, "text": text}
    state["answers"].append(state["answer"])
    state["questions"] = []
    state["phase"] = "produce"
    state["final_status"] = None
    state["error"] = None
    store.save(state)
    return _event(state, "Answer recorded.")


def status(project_root: Path, run_id: str | None) -> dict:
    if run_id:
        return _event(store.load(project_root, run_id), "Current status.")
    config = cfg.load_config(project_root)
    return {
        "open_runs": [
            {key: run.get(key) for key in ("run_id", "stage", "artifact", "phase", "final_status", "updated_at")}
            for run in store.open_runs(project_root)
        ],
        "settings": {key: config[key] for key in cfg.RUN_SETTINGS},
        "defaults": config["defaults"],
        "config_path": str(cfg.config_path(project_root)),
        "config_exists": cfg.config_path(project_root).is_file(),
        "project_root": str(project_root.resolve()),
        "project_configured": cfg.project_configured(config, project_root),
        "project": cfg.project_settings(config, project_root),
        "cli_version": __version__,
    }


def close(project_root: Path, run_id: str, abandon: bool) -> dict:
    state = store.load(project_root, run_id)
    if state["phase"] not in TERMINAL:
        if not abandon:
            raise UsageError(
                f"Run {run_id} is in phase {state['phase']}; finish it, or pass --abandon when the user abandons it"
            )
        state["final_status"] = "abandoned"
    items = _backlog_items(state)
    written = []
    if items:
        try:
            written = backlog.append(_root(state) / BACKLOG_FILE, items)
        except OSError as exc:
            raise UsageError(f"Cannot write {BACKLOG_FILE}; the run stays open: {exc}") from exc
    deleted = []
    for role, worker in state["workers"].items():
        adapter = providers.get(state["roles"][role]["provider"])
        for session_id in worker["sessions"]:
            deleted += adapter.cleanup(session_id)
    report = _report(state)
    store.delete_run(_root(state), run_id)
    return {
        "run_id": run_id,
        "phase": "closed",
        "message": "Run closed and its state deleted.",
        "final_status": state["final_status"],
        "report": report,
        "backlog_file": BACKLOG_FILE if written else None,
        "backlog_items": written,
        "deleted_session_files": deleted,
    }


# ---------------------------------------------------------------- steps


def _producer_step(state: dict, progress=None) -> dict:
    root = _root(state)
    label = f"P{state['reviews_done']}"
    work = _work_list(state)
    data = _invoke(state, "producer", lambda summary: _producer_prompt(state, summary), schemas.PRODUCER, progress)
    state["answer"] = None
    if data["summary"].strip():
        state["producer_summaries"].append(f"{label}: {data['summary'].strip()}")
    if data["status"] == "needs-user-decision":
        questions = [question for question in data["questions"] if question.strip()]
        state["questions"] = questions or [data["summary"].strip() or "The Producer needs a user decision."]
        state["phase"] = "awaiting-answer"
        store.save(state)
        return _event(state, f"{label}: the Producer needs a user decision.")
    if data["status"] == "blocked":
        state["phase"] = "blocked"
        state["final_status"] = "blocked"
        reason = (data["blocker"] or data["summary"] or "The Producer is blocked.").strip()
        state["error"] = {"message": reason, "raw_excerpt": ""}
        store.save(state)
        return _event(state, f"{label}: the Producer is blocked.")
    outcomes = {outcome["finding_id"]: outcome for outcome in data["outcomes"]}
    for finding in work:
        outcome = outcomes.get(finding["id"])
        finding["outcome"] = outcome["result"] if outcome else "not-fixed"
        finding["outcome_rationale"] = outcome["rationale"] if outcome else "The Producer reported no outcome."
    state["producer_steps"] += 1
    if state["stage"] in ("feature-delivery", "general"):
        state["checks"] = _run_checks(state, label)
    tree = gitops.snapshot(root, _index(state))
    changed = gitops.changed_files(root, _review_base(state), tree)
    if state["reviews_done"] >= state["settings"]["max_reviews"]:
        state["trees"]["finalizing"] = tree
        state["phase"] = "finalizing"
        store.save(state)
        return _event(state, f"{label} used the last revision; finalization belongs to the Orchestrator.")
    state["phase"] = "review"
    store.save(state)
    return _event(state, f"{label} finished.", changed_files=changed)


def _review_step(state: dict, progress=None) -> dict:
    root = _root(state)
    number = state["reviews_done"] + 1
    before = gitops.snapshot(root, _index(state))
    diff = gitops.diff(root, _review_base(state), before)
    if len(diff.encode("utf-8")) > state["settings"]["max_diff_kb"] * 1024:
        raise StepFailed(f"The changes for review {number} exceed max_diff_kb ({state['settings']['max_diff_kb']} KB)")
    to_check = _work_list(state)
    data = _invoke(state, "reviewer", lambda summary: _reviewer_prompt(state, number, diff, summary), schemas.REVIEW, progress)
    after = gitops.snapshot(root, _index(state))
    if after != before:
        files = gitops.changed_files(root, before, after)
        raise StepFailed(f"The Reviewer changed files, which fails the run: {', '.join(files[:10])}")
    state["reviews_done"] = number
    state["trees"]["last_review"] = before
    reported = {item["finding_id"]: item["result"] for item in data["earlier_results"]}
    pending = []
    for finding in to_check:
        if reported.get(finding["id"]) == "resolved":
            finding["resolution"] = "resolved"
        else:
            pending.append(finding["id"])  # open, or silently skipped by the Reviewer
    notes = [str(note).strip() for note in data["notes"] if str(note).strip()]
    count = 0
    for raw in data["findings"]:
        evidence = [entry.strip() for entry in raw["evidence"] if entry.strip()]
        if not evidence:
            notes.append(f"Demoted, no evidence: {raw['claim']}")
            continue
        if number > 1 and raw["severity"] != "blocker" and raw["category"] != "regression":
            notes.append(f"Demoted, only blockers and regressions count after the first review: {raw['claim']}")
            continue
        count += 1
        finding = {
            "id": f"R{number}-{count:03d}",
            "review": number,
            "category": raw["category"],
            "severity": raw["severity"],
            "claim": raw["claim"],
            "evidence": evidence,
            "recommendation": raw["recommendation"],
            "disposition": None,
            "rationale": None,
            "priority": None,
            "outcome": None,
            "outcome_rationale": None,
            "resolution": None,
            "history": [],
        }
        state["findings"].append(finding)
        pending.append(finding["id"])
    state["notes"] += [{"review": number, "text": note} for note in notes]
    if not pending:
        state["phase"] = "done"
        state["final_status"] = "needs-user-decision" if any(c["exit_code"] != 0 for c in state["checks"]) else "independently-passed"
        store.save(state)
        return _event(state, f"Review {number} left nothing to adjudicate.")
    state["pending"] = pending
    state["phase"] = "awaiting-decision"
    store.save(state)
    return _event(state, f"Review {number} finished.")


def _finish(state: dict) -> dict:
    root = _root(state)
    tree = gitops.snapshot(root, _index(state))
    changed = gitops.changed_files(root, state["trees"]["finalizing"], tree)
    if state["stage"] in ("feature-delivery", "general"):
        state["checks"] = _run_checks(state, "finalization")
    failing = [check["command"] for check in state["checks"] if check["after"] == "finalization" and check["exit_code"] != 0]
    left_open = [finding["id"] for finding in state["findings"] if finding.get("left_open")]
    for finding in _work_list(state):
        finding["resolution"] = "orchestrator"
    state["finalization"] = {"changed_files": changed, "left_open": left_open, "failing_checks": failing}
    state["final_status"] = "needs-user-decision" if left_open or failing else "completed-by-orchestrator"
    state["phase"] = "done"
    store.save(state)
    return _event(state, "Finalization recorded.")


# ---------------------------------------------------------------- workers


def _invoke(state: dict, role: str, build_prompt, schema: dict, progress=None) -> dict:
    """Run one worker call, replacing the worker once when its session cannot resume."""
    worker = state["workers"][role]
    provider = providers.get(state["roles"][role]["provider"])
    rotate_at = state["settings"]["rotate_at_tokens"]
    fresh = worker["session_id"] is None or bool(rotate_at and (worker["context_tokens"] or 0) > rotate_at)
    reason = "new-run" if worker["session_id"] is None else "context-threshold" if fresh else "resume"
    result = _attempt(state, role, provider, build_prompt, schema, fresh, progress, reason)
    if result.error and not fresh:
        result = _attempt(state, role, provider, build_prompt, schema, True, progress, "resume-failed")
    if result.error:
        raise StepFailed(f"The {role} ({state['roles'][role]['provider']}) {result.error}", result.raw)
    errors = schemas.validate(result.data, schema)
    if errors:
        raw = json.dumps(result.data, ensure_ascii=False)[:EXCERPT_CHARS]
        raise StepFailed(f"The {role} output does not match its schema: {'; '.join(errors[:5])}", raw)
    return result.data


def _attempt(state: dict, role: str, provider, build_prompt, schema: dict, fresh: bool, progress=None, reason=None):
    worker = state["workers"][role]
    if fresh:
        worker["generation"] += 1
    summary = _run_summary(state) if fresh and worker["generation"] > 1 else None
    call = _call(state, role, build_prompt(summary), schema, None if fresh else worker["session_id"])
    def observe(event):
        if "telemetry" in event:
            worker["telemetry"] = event["telemetry"]
        if event.get("session_id"):
            worker["session_id"] = event["session_id"]
            if event["session_id"] not in worker["sessions"]:
                worker["sessions"].append(event["session_id"])
        worker["last_event"] = event["event"]
        store.save(state)
        if progress:
            progress({"run_id": state["run_id"], "role": role, "generation": worker["generation"], **event})
    call.progress = observe
    observe({"event": "worker-started", "fresh": fresh, "reason": reason, "configured": state["roles"][role],
             "previous_context_tokens": worker["context_tokens"],
             "rotate_at_tokens": state["settings"]["rotate_at_tokens"]})
    result = provider.run(call)
    if result.session_id:
        worker["session_id"] = result.session_id
        if result.session_id not in worker["sessions"]:
            worker["sessions"].append(result.session_id)
    worker["context_tokens"] = result.context_tokens
    if result.context_tokens is not None:
        call.telemetry["context_tokens"] = result.context_tokens
    worker["telemetry"] = call.telemetry
    observe({"event": "worker-finished", "context_tokens": result.context_tokens, "failed": bool(result.error)})
    return result


def _call(state: dict, role: str, prompt: str, schema: dict, session_id: str | None) -> providers.Call:
    project = state["project"]
    producer = role == "producer"
    read_dirs = [str(Path(state["skill"]).parent)] if state["skill"] else []
    if not producer:
        read_dirs += project["extra_dirs"]
    return providers.Call(
        role=role,
        model=state["roles"][role]["model"],
        effort=state["roles"][role]["effort"],
        prompt=prompt,
        schema=schema,
        session_id=session_id,
        cwd=_root(state),
        read_dirs=read_dirs,
        write_dirs=project["extra_dirs"] if producer else [],
        allowed_commands=[*cfg.PRODUCER_BASE_COMMANDS, *project["allowed_commands"]] if producer else [],
        timeout=state["settings"]["timeout_minutes"] * 60,
        work_dir=_run_dir(state),
    )


def _producer_prompt(state: dict, summary: str | None) -> str:
    answer_state = state["answer"]
    answer_text = None
    if answer_state:
        questions = "\n".join(f"- {question}" for question in answer_state["questions"])
        answer_text = f"Questions:\n{questions}\nAnswer: {answer_state['text']}"
    return prompts.producer_prompt(
        stage=state["stage"],
        project_root=state["project_root"],
        artifact=state["artifact"],
        skill=state["skill"],
        request=state["request"],
        initial=state["first"] == "produce" and state["producer_steps"] == 0,
        work=[_work_item(finding) for finding in _work_list(state)],
        answer=answer_text,
        summary=summary,
    )


def _reviewer_prompt(state: dict, number: int, diff: str, summary: str | None) -> str:
    to_check = [
        {
            "id": finding["id"],
            "severity": finding["severity"],
            "claim": finding["claim"],
            "evidence": finding["evidence"],
            "guidance": finding["rationale"],
            "producer_outcome": finding["outcome"],
            "producer_rationale": finding["outcome_rationale"],
        }
        for finding in _work_list(state)
    ]
    closed = [
        {key: finding[key] for key in ("id", "claim", "disposition", "rationale")}
        for finding in state["findings"]
        if finding["disposition"] in ("note-only", "rejected", "needs-user-decision")
    ]
    return prompts.reviewer_prompt(
        stage=state["stage"],
        review=number,
        max_reviews=state["settings"]["max_reviews"],
        project_root=state["project_root"],
        repo_root=state["repo_root"],
        artifact=state["artifact"],
        skill=state["skill"],
        request=state["request"],
        diff=diff,
        earlier={"to_check": to_check, "closed": closed} if to_check or closed else None,
        checks=state["checks"],
        summary=summary,
    )


def _work_item(finding: dict) -> dict:
    item = {key: finding[key] for key in ("id", "severity", "category", "claim", "evidence", "recommendation")}
    item["guidance"] = finding["rationale"]
    if finding["outcome"]:
        item["previous_outcome"] = {"result": finding["outcome"], "rationale": finding["outcome_rationale"]}
    return item


def _run_summary(state: dict) -> str:
    """The short history that seeds a replacement worker."""
    lines = [
        f"Reviews done: {state['reviews_done']} of {state['settings']['max_reviews']}; "
        f"Producer steps: {state['producer_steps']}."
    ]
    for finding in state["findings"]:
        status = finding["disposition"] or "pending"
        if finding["outcome"]:
            status += f", Producer {finding['outcome']}"
        if finding["resolution"]:
            status += f", {finding['resolution']}"
        lines.append(f"- {finding['id']} [{finding['severity']}] {finding['claim']} ({status})")
    lines += [f"- {summary}" for summary in state["producer_summaries"][-3:]]
    return "\n".join(lines)


def _run_checks(state: dict, label: str) -> list[dict]:
    results = []
    for command in state["project"]["delivery_checks"]:
        try:
            process = subprocess.run(
                command,
                shell=True,
                cwd=state["project_root"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=state["settings"]["timeout_minutes"] * 60,
            )
            code, output = process.returncode, process.stdout + process.stderr
        except subprocess.TimeoutExpired:
            code, output = None, "Timed out."
        excerpt = "\n".join(output.splitlines()[-CHECK_EXCERPT_LINES:])[-EXCERPT_CHARS:]
        results.append({"after": label, "command": command, "exit_code": code, "excerpt": excerpt})
    return results


# ---------------------------------------------------------------- helpers


def _dry_run(state: dict) -> dict:
    role = "producer" if state["first"] == "produce" else "reviewer"
    if role == "producer":
        prompt, schema = _producer_prompt(state, None), schemas.PRODUCER
    else:
        prompt, schema = _reviewer_prompt(state, 1, "", None), schemas.REVIEW
    call = _call(state, role, prompt, schema, None)
    return {
        "dry_run": True,
        "message": "Nothing was started or saved.",
        "stage": state["stage"],
        "artifact": state["artifact"],
        "first": state["first"],
        "skill": state["skill"],
        "roles": state["roles"],
        "settings": state["settings"],
        "first_worker": role,
        "command": providers.preview_command(state["roles"][role]["provider"], call),
        "prompt": prompt,
    }


def _fail(state: dict, message: str, raw: str = "") -> dict:
    state["phase"] = "failed"
    state["final_status"] = "failed"
    state["error"] = {"message": message, "raw_excerpt": (raw or "")[-EXCERPT_CHARS:]}
    store.save(state)
    return _event(state, message)


def _check_decision(decision: dict, finding: dict) -> None:
    if decision["disposition"] == "accepted":
        if finding["severity"] not in ("blocker", "major"):
            raise UsageError(f"{finding['id']} is {finding['severity']}; only blocker and major findings can be accepted")
        return
    if not (decision["rationale"] or "").strip():
        raise UsageError(f"{finding['id']} needs a rationale")
    if decision["priority"] is None:
        raise UsageError(f"{finding['id']} needs a priority")


def _backlog_items(state: dict) -> list[dict]:
    kinds = {"note-only", "needs-user-decision"} | ({"rejected"} if state["settings"]["backlog_rejected"] else set())
    selected = [finding for finding in state["findings"] if finding["disposition"] in kinds]
    if not selected:
        return []
    base = gitops.base_description(_root(state), state["artifact"])
    return [
        {
            "type": finding["disposition"],
            "priority": finding["priority"] or "none",
            "claim": finding["claim"],
            "evidence": finding["evidence"],
            "recommendation": finding["recommendation"],
            "rationale": finding["rationale"] or "",
            "run_id": state["run_id"],
            "finding_id": finding["id"],
            "artifact": state["artifact"],
            "stage": state["stage"],
            "base": base,
        }
        for finding in selected
    ]


def _report(state: dict) -> dict:
    counts: dict[str, int] = {}
    for finding in state["findings"]:
        key = finding["disposition"] or "pending"
        counts[key] = counts.get(key, 0) + 1
    return {
        "final_status": state["final_status"],
        "reviews_used": state["reviews_done"],
        "max_reviews": state["settings"]["max_reviews"],
        "producer_steps": state["producer_steps"],
        "findings_by_disposition": counts,
        "open_accepted_findings": [finding["id"] for finding in _work_list(state)],
        "left_for_user": [finding["id"] for finding in state["findings"] if finding["disposition"] == "needs-user-decision"],
        "finalization": state["finalization"],
        "checks": [{key: check[key] for key in ("after", "command", "exit_code")} for check in state["checks"]],
        "notes": [note["text"] for note in state["notes"]],
        "error": state["error"],
        "roles": state["roles"],
        "workers": state["workers"],
        "producer_summary": state["producer_summaries"][-1] if state["producer_summaries"] else None,
    }


def _event(state: dict, message: str, **extra) -> dict:
    phase = state["phase"]
    event = {
        "run_id": state["run_id"],
        "phase": phase,
        "message": message,
        "next_action": NEXT_ACTION[phase],
        "stage": state["stage"],
        "artifact": state["artifact"],
        "reviews_done": state["reviews_done"],
        "max_reviews": state["settings"]["max_reviews"],
        "producer_steps": state["producer_steps"],
        "settings": state["settings"],
        "roles": state["roles"],
        "workers": state["workers"],
        "producer_summary": state["producer_summaries"][-1] if state["producer_summaries"] else None,
    }
    if phase == "awaiting-decision":
        findings = _findings(state)
        event["pending_findings"] = [_view(findings[finding_id]) for finding_id in state["pending"]]
        event["notes"] = [note["text"] for note in state["notes"] if note["review"] == state["reviews_done"]]
        event["decision_rules"] = (
            "Decide every pending finding exactly once. accepted is allowed only for blocker or major findings; "
            "its rationale is optional guidance for the Producer. note-only, rejected, and needs-user-decision "
            "need a rationale and a priority."
        )
    elif phase == "awaiting-answer":
        event["questions"] = state["questions"]
    elif phase == "finalizing":
        root = _root(state)
        diff = gitops.diff(root, _review_base(state), state["trees"]["finalizing"])
        too_large = len(diff.encode("utf-8")) > state["settings"]["max_diff_kb"] * 1024
        event["unreviewed_changes"] = gitops.changed_files(root, _review_base(state), state["trees"]["finalizing"])
        event["unreviewed_diff"] = "(too large to show; inspect the changed files)" if too_large else diff
        event["remaining_accepted_findings"] = [_view(finding) for finding in _work_list(state)]
    if phase in TERMINAL:
        event["final_status"] = state["final_status"]
        event["report"] = _report(state)
    if phase in ("failed", "blocked"):
        event["error"] = state["error"]
        event["state_path"] = str(_run_dir(state) / "state.json")
    if state["checks"]:
        event["checks"] = state["checks"]
    event.update(extra)
    return event


def _view(finding: dict) -> dict:
    view = {key: finding[key] for key in ("id", "severity", "category", "claim", "evidence", "recommendation")}
    if finding["history"]:
        view["previous"] = {
            "disposition": finding["disposition"],
            "rationale": finding["rationale"],
            "producer_outcome": finding["outcome"],
            "producer_rationale": finding["outcome_rationale"],
        }
    return view


def _root(state: dict) -> Path:
    return Path(state["project_root"])


def _run_dir(state: dict) -> Path:
    return store.run_path(_root(state), state["run_id"])


def _index(state: dict) -> Path:
    return _run_dir(state) / "snap.index"


def _review_base(state: dict) -> str:
    return state["trees"]["last_review"] or state["trees"]["baseline"]


def _findings(state: dict) -> dict:
    return {finding["id"]: finding for finding in state["findings"]}


def _work_list(state: dict) -> list[dict]:
    """Accepted findings that no review or finalization has resolved yet."""
    return [
        finding for finding in state["findings"] if finding["disposition"] == "accepted" and finding["resolution"] is None
    ]
