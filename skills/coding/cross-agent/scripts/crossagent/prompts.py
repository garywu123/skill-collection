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
    checkpoint_session: str = "fresh",
    segment_review: bool = False,
    repair: dict | None = None,
) -> str:
    lines = [
        f'You are the Producer in a cross-agent review run for stage "{stage}".',
        "You cannot ask the user anything directly; the Orchestrator relays questions and answers.",
        "",
        f"Project root and working directory: {project_root}",
        f"Artifact: {artifact}",
    ]
    if skill:
        lines.append(f"Stage Skill: {skill}. Its complete content is supplied below by the CLI; follow it, including its consistency check, and read referenced resources as needed.")
    else:
        lines.append("No lifecycle Skill applies: follow AGENTS.md and the request.")
    if stage == "feature-delivery":
        lines.append("Work in auto mode: write the tests and the implementation yourself.")
    if initial:
        lines += ["", "Request:", request or ""]
    elif repair:
        lines += ["", f"Original request: {request or 'none'}",
                  "Current step: repair the accepted segment-review findings below for this segment only. "
                  "Return status segment-repaired with an outcome for every listed finding. Run only the focused "
                  "checks for the repaired behavior; whole-stage checks run after done. Do not start the next "
                  "segment.", "Segment under repair:", _json(repair)]
    else:
        lines += ["", f"Original request: {request or 'none'}", "Current step: continue unfinished authorized work and address the accepted findings below. "
                  "Rerun only the tests that cover each fix; the CLI reruns the configured delivery checks "
                  "after you return done."]
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
        "- Read confirmed decisions before asking. If a safeguard depends on an unresolved usage choice, "
        "return needs-user-decision with the question and its consequence before making dependent edits; "
        "do not invent guarantees or repeat answered questions.",
        "- Reuse adequate tests; strengthen or add them for a distinct coverage gap, preserving required checks.",
        "- While editing, compile and run only the focused tests for the changed behavior, and after a fix rerun "
        "only the failing tests. Do not run the configured delivery checks yourself: the CLI runs them outside "
        "your sandbox after you return done. Before done, run once any Feature gate suite the Plan names, "
        "such as UI flows or capacity, and never per segment or after a small nearby edit; never run a "
        "stage suite unless the request asks for it.",
        "- If a build or test command fails before executing any test, such as a sandbox, restore or testhost "
        "startup failure, do not retry variants or diagnose it: note it once in the summary as an environment "
        "limitation and leave execution to the CLI checks. An Orchestrator note below supplies results it ran "
        "or command guidance for the current tree: rely on those results and follow that guidance instead.",
        "- Record a check result as one line bound to its revision; never write file hashes, manifests, receipt "
        "files, log paths or failed-attempt history into a document.",
        "- Keep the summary to current decisions and sources, changed behavior, completed/next work, "
        "open failures or gates, and tested-evidence locators; do not replay earlier rounds or raw logs.",
        "- Do not commit, and do not start another lifecycle stage.",
        "- For an execution stage, return checkpoint only after a planned segment and its focused checks, "
        "when more authorized work remains. Focused checks are the Plan's checks for that segment plus tests "
        "of consumers of a contract it changed, not the whole suite. Summarize acceptance evidence, stable contracts, and the next "
        "unfinished segment; use empty questions/outcomes and null blocker. " + (
            "The same session continues after a checkpoint" if checkpoint_session == "resume"
            else "A checkpoint starts a new session") + " without resetting review or revision budgets. "
        "Do not return done before whole-stage validation.",
        "- " + ("For a checkpoint, list the finished segment's planned outcomes in segment_outcomes and the "
                "unfinished authorized work in remaining_work; an independent segment review judges only those "
                "outcomes before the next segment. For any other status return both lists empty."
                if segment_review else "Return empty segment_outcomes and remaining_work lists."),
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
    test_changes: str | None = None,
    attempt: int | None = None,
    segment: dict | None = None,
    diff_label: str = "Changes since the previous review",
    external: list[dict] | None = None,
) -> str:
    attempt = review if attempt is None else attempt
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
    if segment:
        lines += [
            "",
            "This is a segment review, not the whole-stage review. Judge only whether the diff below meets the "
            "finished segment's planned outcomes, and report regressions or risks it introduces. Do not report "
            "unfinished later work listed as remaining; the whole-stage review judges completeness after the "
            "Producer finishes. Delivery checks have not run yet; judge the Producer's focused-check evidence. A missing broad or "
            "whole-suite run is not a finding at a segment.",
            _json(segment),
        ]
    if summary:
        lines += ["", "Run summary so far:", summary]
    if diff:
        lines += [
            "",
            f"{diff_label} (git diff; paths are relative to the repository root {repo_root}):",
            "```diff",
            diff.rstrip(),
            "```",
        ]
    else:
        lines += ["", f"{diff_label}: none. Review the artifact as it stands."]
    if external:
        lines += ["", "The Orchestrator adopted these changes made outside the Producer into the reviewed diff. "
                  "Judge them like the rest of the diff, but do not attribute them to the Producer:", _json(external)]
    if earlier:
        lines += [
            "",
            "Earlier findings. In earlier_results, report every finding under to_check as resolved or open. "
            "Do not raise a finding under closed again:",
            _json(earlier),
        ]
    if checks:
        lines += ["", "Check results after the latest change:", _json(checks)]
    if test_changes:
        lines += ["", "CLI test-change summary (fixed input for this revision; detection signals, not a verdict):",
                  test_changes]
    lines += [
        "",
        "Report only findings in these categories:",
        "- unmet-outcome: a requested outcome is not met;",
        "- authoritative-conflict: a direct conflict with an authoritative input;",
        "- validation-failure: a real validation or check failure;",
        "- contradiction: an internal contradiction;",
        "- regression: a regression caused by the latest change;",
        "- risk: a concrete security, permission, data-loss, or irreversible-action risk;",
        "- excess: code, a guard, an option, a test, or document text that the reviewed change adds or expands "
        "with no supported trigger, consumer, or reader, such as a run report, tool limitation or task-scope "
        "disclaimer written into a document; recommend deleting it. Protections at a trust boundary and "
        "required gates are not excess.",
        "Give each finding evidence: a rule citation, a path:line, or a failing command. "
        "Rate its severity as blocker, major, or minor.",
        "Set needs_user_decision to true only when the fix changes product behavior, requested scope, technical "
        "direction or an authoritative document, or when the authority to decide is missing; otherwise false. "
        "A clear compliance or security fix within the requested scope is an ordinary finding.",
        "Use claim, evidence, and recommendation to explain the supported trigger, unmet promise or concrete "
        "risk, user consequence, and smallest adequate correction. Concrete code-supported security or "
        "data-loss risks need no invented product requirement. Distinguish product, test, and environment "
        "failures; unknown causes stay unknown.",
        "Before requesting another test or test layer, name the distinct failure existing coverage misses; "
        "prefer strengthening an existing case. Preserve necessary protections and required gates.",
        "For a missing authoritative decision that prevents judging a requested outcome, state the acceptance "
        "gap, checked sources, consequence, and question for Orch in the existing finding fields. Do not "
        "invent a defect, guarantee, or severity just to transport a question; optional uncertainty is notes. "
        "Do not represent a necessary unresolved acceptance gap as satisfied.",
        "Start with the supplied artifact, diff, findings and check evidence; inspect relevant source sections "
        "as needed to verify them, without reconstructing unrelated project history.",
        "A Producer summary is navigation, never sole proof of intent or correctness. Independently inspect "
        "material discussion evidence and upstream sources: for product work verify goals, scope and confirmed "
        "constraints; for architecture trace boundaries/contracts to product constraints and code/config; "
        "for delivery inspect affected business paths, implementation and test evidence. Treat assistant ideas "
        "as candidates unless accepted. Original provider messages prove what that session received, not host-chat "
        "wording; mark Orch-only quotations/translations as Orch-attested. In notes name material areas/sources "
        "checked and missing evidence or tool limitations; no findings alone does not establish coverage.",
        "Put alternative designs, style preferences without a rule, speculative future concerns, unrelated "
        "cleanup, optional refactoring, and improvement ideas in notes. Unneeded additions in the reviewed "
        "change are excess findings, not notes.",
    ]
    if attempt > 1:
        lines.append(
            f"This is not the first {'review of this segment' if segment else 'review'}: add a new finding only for a blocker, or for a regression or excess "
            "caused by the latest changes."
        )
    lines += ["Write all output in English.", "Your final message must be only the review result JSON object."]
    return "\n".join(lines)
