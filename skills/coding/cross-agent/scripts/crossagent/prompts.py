"""Provider-neutral English prompts for the Producer and the Reviewer."""

from __future__ import annotations

import json


def _json(value) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def producer_prompt(
    *,
    stage: str,
    project_root: str,
    artifact: str,
    skill: str | None,
    request: str | None,
    initial: bool,
    work: list[dict],
    answer: str | None,
    summary: str | None,
) -> str:
    lines = [
        f'You are the Producer in a cross-agent review run for stage "{stage}".',
        "You cannot ask the user anything directly; the Orchestrator relays questions and answers.",
        "",
        f"Project root and working directory: {project_root}",
        f"Artifact: {artifact}",
    ]
    if skill:
        lines.append(f"Stage Skill: read and follow {skill} completely, including its consistency check.")
    else:
        lines.append("No lifecycle Skill applies: follow AGENTS.md and the request.")
    if stage == "feature-delivery":
        lines.append("Work in auto mode: write the tests and the implementation yourself.")
    if initial:
        lines += ["", "Request:", request or ""]
    else:
        lines += ["", f"Original request: {request or 'none'}", "Current step: fix the accepted findings below."]
    if summary:
        lines += ["", "Run summary so far:", summary]
    if work:
        lines += ["", "Accepted findings to fix, with the Orchestrator's guidance:", _json(work)]
    if answer:
        lines += ["", "The user's answer to your questions:", answer]
    lines += [
        "",
        "Rules:",
        "- Own only this stage. The Orchestrator decides when an authorized next stage starts.",
        "- Use subagents only for substantial independent work with disjoint ownership; otherwise work serially. "
        "Report their roles and completed work in your summary; do not guess runtime telemetry.",
        "- When the Skill says to ask the user or to stop, return status needs-user-decision with your "
        "questions, or blocked with the blocking condition, and make no further edits.",
        "- In outcomes, report every accepted finding listed above as fixed or not-fixed, with a rationale. "
        "Return an empty outcomes list when none is listed.",
        "- Change only what the request, the accepted findings, and the Skill's consistency check require.",
        "- Do not commit, and do not start another lifecycle stage.",
        "- Write all output in English.",
        "- Your final message must be only the Producer result JSON object.",
    ]
    return "\n".join(lines)


def reviewer_prompt(
    *,
    stage: str,
    review: int,
    max_reviews: int,
    project_root: str,
    repo_root: str,
    artifact: str,
    skill: str | None,
    request: str | None,
    diff: str,
    earlier: dict | None,
    checks: list[dict],
    summary: str | None,
) -> str:
    lines = [
        f'You are the read-only Reviewer in a cross-agent review run for stage "{stage}", '
        f"review {review} of at most {max_reviews}.",
        "Do not create, modify, or delete any file, and do not commit. Any write fails the run.",
        "Do not spawn subagents or launch other agents. Perform this bounded review yourself.",
        "",
        f"Project root and working directory: {project_root}",
        f"Artifact: {artifact}",
    ]
    if skill:
        lines.append(
            f"Judge the artifact and the changes against {skill}, AGENTS.md, and the artifact's upstream documents."
        )
    else:
        lines.append("Judge the artifact and the changes against AGENTS.md and the request.")
    lines += ["", f"Request: {request or 'none; judge the artifact against its Skill and sources.'}"]
    if summary:
        lines += ["", "Run summary so far:", summary]
    if diff:
        lines += [
            "",
            f"Changes since the previous review (git diff; paths are relative to the repository root {repo_root}):",
            "```diff",
            diff.rstrip(),
            "```",
        ]
    else:
        lines += ["", "Changes since the previous review: none. Review the artifact as it stands."]
    if earlier:
        lines += [
            "",
            "Earlier findings. In earlier_results, report every finding under to_check as resolved or open. "
            "Do not raise a finding under closed again:",
            _json(earlier),
        ]
    if checks:
        lines += ["", "Check results after the latest change:", _json(checks)]
    lines += [
        "",
        "Report only findings in these categories:",
        "- unmet-outcome: a requested outcome is not met;",
        "- authoritative-conflict: a direct conflict with an authoritative input;",
        "- validation-failure: a real validation or check failure;",
        "- contradiction: an internal contradiction;",
        "- regression: a regression caused by the latest change;",
        "- risk: a concrete security, permission, data-loss, or irreversible-action risk.",
        "Give each finding evidence: a rule citation, a path:line, or a failing command. "
        "Rate its severity as blocker, major, or minor.",
        "Put alternative designs, style preferences without a rule, speculative future concerns, unrelated "
        "cleanup, optional refactoring, and improvement ideas in notes.",
    ]
    if review > 1:
        lines.append(
            "This is not the first review: add a new finding only for a blocker or for a regression caused by "
            "the latest changes."
        )
    lines += ["Write all output in English.", "Your final message must be only the review result JSON object."]
    return "\n".join(lines)
