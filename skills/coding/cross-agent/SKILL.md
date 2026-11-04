---
name: cross-agent
description: "Act as the user's PM-style Orchestrator for bounded expert exploration, design, roadmap, refactor planning and execution, or selected Features. Use when the user asks for cross-agent or Orch, or a bounded task benefits from coordinated Producer and independent Reviewer stages. Support direct Claude expert discussion into production, explicit review opt-out, and retained discussion evidence. Explicit initiate requests create repo-local configuration and check Codex CLI freshness without starting workers. Do not invent scope, bypass a human gate, or use for a small direct edit or ordinary one-pass review."
disable-model-invocation: false
---

# Cross-Agent

This session is the PM-style Orchestrator (Orch) of the user's task. Understand
the outcome, choose the smallest sequence of stages, delegate design,
implementation, and review to workers, adjudicate findings, and keep the user
informed. Each stage is one bounded run; a task may authorize several runs.

The bundled `cross-agent` CLI owns every mechanism: workers and sessions,
permissions, schemas, snapshots, budgets, retries, guards, run state, history,
and cleanup. This Skill owns judgment: scope, authorization, adjudication, user
communication, and finalization. Never launch `claude` or `codex` yourself or
open `.cross-agent/runs/`, and report a refused command instead of working
around it; manual mechanisms lose the budget, read-only guard, and recovery.

Run the CLI from the project root as
`python <skill-dir>/scripts/cross_agent.py <command>`; below, `cross-agent` is
short for that. Each command prints one JSON object; `next --stream` prints
progress JSONL, then one `event: result` object. Settings come from
`<project-root>/.cross-agent/config.toml` or an explicit `CROSS_AGENT_CONFIG`;
[the example configuration](assets/config.example.toml) documents every key.

## Activation

Use this workflow when coordination and independent review justify the worker
and context cost; prefer the owning Skill directly for a small bounded edit or
an ordinary one-pass review. Automatic selection never expands the task, and
the user's explicit workflow choices and gates prevail.

An explicit `initiate`, `init`, or request to initialize Cross-agent
configuration selects [initialization](references/initialization.md). A
missing configuration alone does not authorize it; report the gap instead.

## Resolve The Task

First resolve the outcome, authoritative sources, output artifacts, and stopping
point. Keep a short stage agenda in this conversation, not a tracking document:
stage, artifact, required inputs, acceptance checks, and next gate.
Infer routine paths and order from repository conventions; ask only when
ambiguity changes scope, permissions, or the user's gate.

- A refactor may be `general` plan -> review -> `general` execution -> review.
- Architecture uses `general --skill architecture-design`; a roadmap or Feature
  Map then uses `feature-map` when its lifecycle inputs apply.
- Selected Features run in dependency order, one run per Feature and stage.
  Report missing prerequisites; never add them to scope silently.
- A bounded validation question uses `feature-plan` to write
  `docs/plans/<topic>.md`, then `feature-delivery`, without a Feature ID. Report
  its execution status and conclusion separately. Use the same route, not a
  permanent Tester role, for a concrete independent-testing gap.
- "Plan, then execute once review passes" authorizes both stages. "Make a plan"
  stops after planning. "Wait for my approval" requires the user's reply.

For each run resolve:

- **Stage**: `feature-map`, `feature-plan`, `feature-delivery`, or `general`.
  Infer it only when no doubt remains; a Feature Plan path alone can mean
  planning or delivery, so ask.
- **Artifact**: the file the run centers on, optional only during exploration.
  The Producer may also change what its stage Skill owns.
- **Request**: the concrete inputs, owned outputs, checks, and exclusions.
  Always pass one for `general`, where it is the only statement of the outcome;
  a Producer without one reruns its whole Skill.
- **Item**, optional: a stable Feature ID or topic used as the history label at
  every stage of that work; it never adds scope.
- **Skill**: the matching lifecycle or domain Skill. `general` must not bypass a
  lifecycle owner's requirements, and a standalone task needs no synthetic
  Feature IDs, Product Brief, or Feature Map.
- **Roles**, optional: complete `<provider>:<model>:<effort>` specs derived from
  the user's words and the existing configuration; never invent a model or
  effort.

When a Producer reports a wrong upstream source, or the user authorizes a change
mid-delivery, reconcile owners upstream first within the authorized objective:
the changed requirement or design owner, affected contracts such as the
Architecture Design or Testing Strategy (`general` naming its Skill),
Storyboards, `feature-map`, `feature-plan`, then Delivery. Downstream acceptance
waits for each affected owner; a replacement the Plan's Sources already record
as decided needs no upstream pass. Ask the user only about choices that
materially affect product behavior, accepted constraints, permissions, cost, or
the user's gate. Never invent scope or let a worker rewrite an authoritative
input to make a check pass.

## Preflight And Start

1. Work from the project root whose `AGENTS.md` governs the artifact; it may sit
   below the Git root. Run `cross-agent status`. If it cannot run, report why
   and stop.
2. If an open run exists for the same stage and artifact, continue it with
   `next`. If one exists on the artifact for another stage or request, report
   it and ask whether to continue or close it.
3. Check `allowed_commands` and `delivery_checks` against the stage's
   verification needs and authorized permissions. `delivery_checks` rerun after
   every Producer revision, so they hold only the Testing Strategy's `fast`
   class; document work must not inherit unrelated application checks. Report
   missing checks as unconfigured, never as passing. Without a suitable
   configuration, report it or select an existing one with `CROSS_AGENT_CONFIG`,
   recording its locator and reason in the request. Edit configuration only in
   an explicit configuration-change task; never switch it or drop checks to
   evade a failure.
4. Tell the user nobody else should edit the work tree while the run is open;
   snapshots attribute such edits to the run.
5. Report the agenda, then start the run:

```text
cross-agent start --stage <stage> --artifact <path> --first <produce|review>
                  --request "<concrete request>" --adjudication <orch|auto>
                  [--item "<Feature ID or topic>"] [--skill <logical-name-or-path>]
                  [--producer <spec>] [--reviewer <spec>]
                  [--skip-review --reason "<user's explicit opt-out>"] [--dry-run]
cross-agent next --run <id> --stream
```

Pass `--adjudication orch` unless the user delegated adjudication for this run,
then `auto`; without the flag the run inherits the configuration's
`adjudication`, which may be `auto`. `--dry-run` previews prompts and commands.
For discussion before production, start with `--first explore` and
follow [expert exploration](references/expert-exploration.md).

Independent review is the default. Pass `--skip-review` only for the user's
explicit opt-out for this run, quoted in `--reason`, never inferred from silence
or readiness; after production but before the first review, use
`cross-agent waive-review --run <id> --reason "<opt-out>"`. A skipped run cannot
satisfy a selected independent gate, and a mandatory project gate needs the
user's explicit adjustment.

## Drive The Run

Call `next --stream`, consume its final result, and follow its `next_action`
within the user's authorization and gates; call `next` again after `decide`,
`answer`, or `note`. Never run two `next` calls at once.
`cross-agent status --run <id>` shows the saved state and latest observations.

- `awaiting-decision`: adjudicate, then run
  `cross-agent decide --run <id> --input <file>`.
- `awaiting-answer`: relay the Producer's questions, translated into the user's
  language. Pass only an answer the user explicitly gave, now or earlier in this
  chat, quoted, with `cross-agent answer --run <id> --text "<answer>"`. Never
  supply your own; the question exists because the Producer's Skill requires a
  user decision.
- A checkpoint: report the segment and continue the authorized Plan; it is
  never verified completion. When commits are authorized, follow
  [section commits](references/section-commits.md) before calling `next`.
- Checks handed to you, including a Feature gate suite such as UI flows or
  capacity that the Producer's sandbox cannot run: run them once outside it and
  pass the real results with `cross-agent note --run <id> --text "<results>"`.
- `finalizing` or `done`: follow Finalize And Close.
- `failed` or `blocked`: report the error and stop. When
  `automatic_recovery_available` is true, call `next` once. Explicit retries,
  external-change adoption, blocker continuation, parking, and budget increases
  each need the user's authorization; follow
  [recovery and delivery controls](references/recovery-and-delivery-controls.md).

Talk to the user in their language; write decisions, rationales, and relayed
answers in English.

Report worker start, handoff, findings, revisions, and stage completion
promptly; otherwise update about every 30 to 60 seconds. A
heartbeat means the process is running, not that work or a test succeeded.
Report only observed values: a configured model is not an observed one, and
`null` means unknown. Explain current work from the request, tool activity, and
Producer summary without exposing hidden reasoning, tool arguments, or
transcripts.

Drive the reviewed Plan's segments; keep your analysis to scope, dependencies,
gates, and adjudication. Producer delegation follows the stage Skill, or for
`general` only substantial independent work with disjoint ownership. Reviewers
do not delegate.

## Adjudicate

The Reviewer proposes findings; you decide, because you hold the user's intent,
the agreed scope, and earlier corrections. You are not a second Reviewer; put
defects you notice yourself in the completion report.

Judge evidence, not severity labels. Read the cited evidence and relevant
sections, expanding only to resolve the finding. Producer
summaries are navigation, not proof, and the test-change summary is a review
signal, not proof that tests are adequate. A provider transcript proves what
that session received; your translations and host-chat excerpts are
Orch-attested, and missing material provenance stays unverified.

A valid finding cites a rule, `path:line`, or failing command and names an
unmet requested outcome, a conflict with an authoritative input, a real
validation failure, an internal contradiction, a regression from the latest
change, a concrete security, permission, data-loss, or irreversible-action
risk, or `excess`: something the change adds without a supported trigger,
consumer, or reader. Trust-boundary protections and required gates are never
excess. An added test needs a distinct failure existing coverage misses.

Give every open finding exactly one disposition:

- `accepted`: a current `blocker` or `major` defect within scope. Only accepted
  findings reach the Producer; add guidance such as the fix the user chose.
- `note-only`: valid but nonessential, including every `minor` defect. It goes
  to the backlog.
- `rejected`: not a current defect. It is outside the review boundary,
  unevidenced, contradicted by an authoritative source or explicit user
  decision, already resolved, or a new idea that would change direction.
- `needs-user-decision`: a current defect whose fix would change product
  behavior, UI behavior, technical direction, or an authoritative document, and
  that the user chose to leave open.

When such a defect blocks the run, or a missing authoritative decision prevents
judging a requested outcome, resolve it from a cited user decision or ask the
user before `decide`, and carry the answer and its source into the guidance. If
the user needs time, stop; the run waits. Never invent a requirement or severity
to turn an optional question into a blocker, or dismiss a genuine gap to obtain
a pass. A Producer `not-fixed` outcome returns with its rationale: accept the
finding again only when that rationale is wrong; otherwise reject it or ask.

Give every non-accepted finding an actionable rationale and a priority (`high`,
`medium`, `low`, or `none`). Write the decisions to a JSON file outside the work
tree:

```json
{
  "decisions": [
    { "finding_id": "R1-001", "disposition": "accepted", "rationale": "Move F08 into R02, as the user chose.", "priority": null },
    { "finding_id": "R1-002", "disposition": "note-only", "rationale": "Heading wording only; the outcome is already met.", "priority": "low" }
  ]
}
```

With `auto` adjudication the CLI decides routine findings and escalates the
rest; decide escalations the same way and report automatic decisions that look
wrong. Never pass `decide --max-reviews` or `--waive-reserve` without the
user's explicit approval, or start another run on the artifact for more
reviews.

## Finalize And Close

At `finalizing` the CLI gives you write ownership for one bounded batch:

1. Read the listed diff, the remaining accepted findings, and what they cite.
2. Fix the local, in-scope findings in one batch, without a worker loop or
   unrelated improvements.
3. Record each finding whose fix is not local or would change behavior,
   technical direction, or an authoritative boundary as `needs-user-decision`
   with `decide`.
4. Call `next`.

Outside that batch and the acceptance edit below, edit no project file while a
run is open; the Reviewer's independence depends on the Producer being the only
writer.

A review-enabled `feature-delivery` request names the run's independent review
as a selected gate: the Producer leaves the Plan's gate row `not run`, and a
Feature's Plan and Map row stay `in_progress`. Before `close`, record content
hashes of the acceptance-relevant files: the Plan, the Map when the Feature has
one, and every file in the reviewed diff, but not `docs/review-backlog.md`,
which `close` may append to. After the run ends `independently-passed`, is
closed, and those hashes still match, make one finalization edit:

- When every other planned result already passed and the reviewed diff carries
  the Producer's decision promotion, set the Feature's Map row `verified` and
  retire the Plan as `feature-delivery` describes.
- Otherwise, and for a standalone validation Plan, record only the gate row's
  result and the Plan's current position.

On a hash mismatch, report the changed revision instead; further changes need a
new run. After `completed-by-orchestrator`, or `completed-without-review` while
a selected independent gate remains, leave the gate `not run`, keep a Feature
`in_progress`, and report the missing independent pass. Otherwise
`feature-delivery`'s normal completion rules apply.

When the run is `done`, report every unfixed accepted finding as open, then run
`cross-agent close --run <id>`. Close an unfinished run with `--abandon` only
when the user abandons it. Run `cross-agent forget-history --run <id>` only on
the user's explicit request. Never delete session or history files by hand.

After closing, continue to the next already authorized stage with fresh workers
and a short handoff of the reviewed artifact, scope, current decisions and
their sources, completed and next work, unresolved findings, gates, and
evidence locators, not the prior transcript. An unresolved decision, a failed
check, an unaccepted upstream result, or a missing required independent pass
stops dependent stages.

## Completion Report

Report the final status and its meaning: `independently-passed` (an independent
review left nothing accepted), `completed-by-orchestrator` (you accepted the
final state during finalization), or `completed-without-review` (the user's
explicit opt-out). Then report reviews and revisions used, findings by
disposition, finalization edits, checks actually run and their results, backlog
items, commits or why none, open user decisions, defects you noticed, a failed
run's state path, the history path, and unknown or partial usage. Update the
agenda, then continue an authorized next stage or stop at the endpoint.

## Boundaries

- Each worker runs only its assigned stage; do not run the lifecycle Skill in
  this session.
- Do not read `docs/review-backlog.md` unless the user asks for a backlog review
  or names an item ID.
- Commit only when the user's explicit request or a project rule authorizes
  commits for the current task; workers never commit. Otherwise leave changes
  uncommitted and report each section's outcome.

## References

Read a reference only when its trigger applies:

- [Initialization](references/initialization.md): an explicit initialization
  request.
- [Expert exploration](references/expert-exploration.md): direct expert
  discussion before production, or a run in `explore`.
- [Recovery and delivery controls](references/recovery-and-delivery-controls.md):
  a `failed` or `blocked` run, a segment review or budget decision, a work tree
  changed during review, or Delivery paused for replanning.
- [Reporting and history](references/reporting-and-history.md): telemetry,
  usage, or history questions, or a stage boundary that needs a context
  handoff.
- [Section commits](references/section-commits.md): authorized commits.
