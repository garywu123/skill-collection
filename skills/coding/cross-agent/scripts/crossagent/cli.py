"""Command-line interface of the CLI bundled with the cross-agent Skill."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__

STAGES = ("feature-map", "feature-plan", "feature-delivery", "general")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cross-agent",
        description="Run one bounded Producer and Reviewer loop for the cross-agent Skill, "
        "from the project root. Commands print JSON; next --stream emits progress JSONL.",
    )
    parser.add_argument("--version", action="version", version=f"cross-agent {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="add this project's configuration; do not start workers")
    init.add_argument("--input", required=True, help="JSON object with project commands and optional cli path overrides; other values come from the template")
    init.add_argument("--producer", help="persist <provider>:<model>:<effort> in a new config")
    init.add_argument("--reviewer", help="persist <provider>:<model>:<effort> in a new config")
    init.add_argument("--skip-version-check", action="store_true", help="skip Codex version detection and latest-release lookup")

    start = commands.add_parser("start", help="create a run")
    start.add_argument("--stage", required=True, choices=STAGES)
    start.add_argument("--artifact", help="path relative to the project root; optional during exploration")
    start.add_argument("--first", required=True, choices=("explore", "produce", "review"))
    start.add_argument("--skill", help="domain Skill logical name or explicit SKILL.md path")
    start.add_argument("--skip-review", action="store_true", help="explicit user opt-out of independent review")
    start.add_argument("--reason", help="source and wording of the user's review opt-out")
    start.add_argument("--request", help="the concrete change or intended outcome")
    start.add_argument("--producer", help="complete <provider>:<model>:<effort> override")
    start.add_argument("--reviewer", help="complete <provider>:<model>:<effort> override")
    start.add_argument("--item", help="stable Feature ID or topic shared across stages; defaults to artifact")
    start.add_argument("--dry-run", action="store_true", help="print the first prompt and command only")

    expert = commands.add_parser("expert", help="run the direct Claude expert in this foreground terminal")
    expert.add_argument("--run", required=True)
    expert.add_argument("--release", action="store_true", help="confirm an interrupted expert terminal has stopped")
    promote = commands.add_parser("promote", help="authorize production after direct exploration")
    promote.add_argument("--run", required=True)
    promote.add_argument("--artifact", required=True)
    promote.add_argument("--request", required=True, help="explicit user write authorization and concrete scope")
    promote.add_argument("--skip-review", action="store_true")
    promote.add_argument("--reason")
    promote.add_argument("--reconcile", help="explicit user reconciliation for changes since exploration began")
    waive = commands.add_parser("waive-review", help="record the user's opt-out before the first review starts")
    waive.add_argument("--run", required=True)
    waive.add_argument("--reason", required=True)
    commands.add_parser("forget-history", help="delete one closed run's local evidence/history, preserving provider sessions").add_argument("--run", required=True)

    next_command = commands.add_parser("next", help="run the next step or print the pending event")
    next_command.add_argument("--run", required=True)
    next_command.add_argument("--stream", action="store_true", help="emit sanitized progress JSONL before the final result")
    commands.add_parser("retry-producer", help="retry a failed Producer execution, preserving its session").add_argument("--run", required=True)
    commands.add_parser("retry-review", help="retry a failed Reviewer execution, preserving Producer context").add_argument("--run", required=True)
    park = commands.add_parser("park", help="hold a failed Delivery run for replanning without deleting history")
    park.add_argument("--run", required=True)
    park.add_argument("--reason", required=True)
    resume = commands.add_parser("resume-delivery", help="continue a parked Delivery after independent Plan review")
    resume.add_argument("--run", required=True)
    resume.add_argument("--plan-run", required=True)
    resume.add_argument("--request", required=True)
    resume.add_argument("--max-diff-kb", type=int, help="explicitly increase saved review input capacity")
    decide = commands.add_parser("decide", help="record adjudications from a JSON file")
    decide.add_argument("--run", required=True)
    decide.add_argument("--input", required=True, help="JSON file outside the work tree")
    answer = commands.add_parser("answer", help="pass the user's answer or blocker recovery decision to the Producer")
    answer.add_argument("--run", required=True)
    answer.add_argument("--text", required=True)
    commands.add_parser("status", help="show one run, or list open runs and settings").add_argument("--run")
    commands.add_parser("history", help="export retained worker calls to .cross-agent/history.csv")
    close = commands.add_parser("close", help="write the backlog, delete the run, clean up sessions")
    close.add_argument("--run", required=True)
    close.add_argument("--abandon", action="store_true", help="close a run that is not finished")
    return parser


def _emit(value: dict) -> None:
    # ASCII-only JSON reads the same in every Windows console code page.
    print(json.dumps(value, indent=2, ensure_ascii=True))


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 11):
        _emit({"error": "cross-agent needs Python 3.11 or later"})
        return 2
    from . import engine
    from .errors import GitError, UsageError

    args = _parser().parse_args(argv)
    root = Path.cwd()
    try:
        if args.command == "init":
            from . import config

            result = config.initialize(
                root, args.input, producer=args.producer, reviewer=args.reviewer,
                check_version=not args.skip_version_check,
            )
        elif args.command == "start":
            result = engine.start(
                root,
                stage=args.stage,
                artifact=args.artifact,
                first=args.first,
                request=args.request,
                producer=args.producer,
                reviewer=args.reviewer,
                dry_run=args.dry_run,
                item=args.item,
                skill=args.skill,
                skip_review=args.skip_review,
                reason=args.reason,
            )
        elif args.command in ("expert", "promote", "waive-review", "forget-history"):
            from . import exploration
            if args.command == "expert":
                result = exploration.expert(root, args.run, release=args.release)
            elif args.command == "promote":
                result = exploration.promote(root, args.run, artifact=args.artifact, request=args.request,
                                             skip_review=args.skip_review, reason=args.reason, reconcile=args.reconcile)
            elif args.command == "waive-review":
                result = exploration.waive_review(root, args.run, args.reason)
            else:
                result = exploration.forget_history(root, args.run)
        elif args.command == "next":
            progress = (lambda event: print(json.dumps(event, ensure_ascii=True), flush=True)) if args.stream else None
            result = engine.next_step(root, args.run, progress=progress)
        elif args.command == "retry-producer":
            result = engine.retry_producer(root, args.run)
        elif args.command == "retry-review":
            result = engine.retry_review(root, args.run)
        elif args.command == "park":
            result = engine.park(root, args.run, args.reason)
        elif args.command == "resume-delivery":
            result = engine.resume_delivery(root, args.run, args.plan_run, args.request, args.max_diff_kb)
        elif args.command == "decide":
            result = engine.decide(root, args.run, args.input)
        elif args.command == "answer":
            result = engine.answer(root, args.run, args.text)
        elif args.command == "status":
            result = engine.status(root, args.run)
        elif args.command == "history":
            from . import gitops, history
            gitops.require_work_tree(root)
            gitops.ensure_excluded(root)
            result = history.export(root)
        else:
            result = engine.close(root, args.run, args.abandon)
    except (UsageError, GitError) as exc:
        _emit({"error": str(exc)})
        return 2
    if args.command == "next" and args.stream:
        print(json.dumps({"event": "result", **result}, ensure_ascii=True), flush=True)
    else:
        _emit(result)
    return 0
