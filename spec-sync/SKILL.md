---
name: spec-sync
description: Perform one explicitly requested vertical alignment review for a named implementation work item before implementation, record post-implementation evidence without accepting or approving delivery, or propose the highest-impact route for a change request. Never infer authority from state, invoke another lifecycle skill, or edit another owner's artifacts.
---

# Spec Sync

## Contract and routing

Require the current user to name exactly one operation and target:
`pre-implement`, `post-implement`, or `change-request`. Pointer readiness is not
authority. Never implement code, run Spec Kit, perform code/security/acceptance/release
review, approve a gate, invoke another lifecycle skill, or continue into a suggested
operation.

One named lifecycle authorization may span turns. A context that creates or
resolves a human gate, or emits a blocked/terminal handoff, must stop after
read-only reporting. Any gate decision, downstream lifecycle operation, or
independent review must begin in a new minimal context explicitly authorized by
the user and rebuilt from canonical state; a fork or worker does not grant new
authorization.

Read `.specify/flow-state.yaml` first. Query the index only through
`resolve --id` or `resolve --path`, and read only target IDs and relevant
sections. Stop on conflicting IDs, paths, revisions, or truth sources.

Keep each opened slice at or below 8 KiB and the initial target payload at or
below 24 KiB. Beyond that, process stable-ID batches in fresh workers and merge
only citations, findings, and a coverage ledger
(`| Batch | Stable IDs / paths | Result | Evidence |`) into the owned output. A
truncated query or uncovered required batch can never produce `Pass` or a ready
result.

## Deterministic state command

```text
python <this-skill-dir>/../flow-state/scripts/flow_state.py --root . <operation> [options]
```

`flow-state/` deploys as this directory's sibling. Use `--help` for options;
never hand-edit state, index, or bundle tables. Use `<revision-from-status>`
for the first write in a context, then the revision each command returns; on
`stale revision` stop and report the conflict rather than retrying.

```text
start --expect-revision <revision-from-status> \
  --kind <kind> --work-id <work-id> --stage pre_implement

record-output --expect-revision <revision-returned-by-start> \
  --stage pre_implement --status ready_for_review \
  --artifact pre_implementation=<path>

block --expect-revision <revision-from-status> --stage <stage> \
  --artifact <role>=<path> --blocker "<concrete blocker>"
```

Add `--check-only` to `record-output` to validate a transition before writing.

| Operation | Deterministic start |
|---|---|
| `pre-implement <work-id> <kind>` | For `feature`, `bug`, `maintenance`, `migration`, or `security`, may run `start` at stage `pre_implement` after prerequisites pass and no gate is pending. Never infer kind from an ID. |
| `change-request <request-id>` | If a durable CR path is configured, may run `start --kind change_request --stage change_request`. If output is response-only, do not start or mutate pointer state. |
| `post-implement <work-id> <kind>` | Never starts work; it must match the already authorized active work item/kind and records stage `post_implement`. |

Product, roadmap, architecture, UI, and guidance changes belong to their owning Skills.
Spec Kit owns horizontal `spec.md`/`plan.md`/`tasks.md` analysis. This Skill owns only the
pre-implementation review, vertical verification record, and proposed change route.

## Spec Kit upstream handoff

`pre-implement` requires approved, hash-matching `spec`, `plan`, `tasks`, and
`requirements_checklist` roles for the same work item. Spec Kit and the human
register them; this skill never does:

```text
start --expect-revision <revision-from-status> \
  --kind <kind> --work-id <work-id> --stage specify
record-output --expect-revision <revision-returned-by-start> --stage specify \
  --artifact spec=specs/NNN-slug/spec.md
decide --expect-revision <revision-returned-by-record-output> --decision approved \
  --decided-by <actor> --decision-date YYYY-MM-DD --decision-evidence <statement>

start --expect-revision <revision-from-status> \
  --kind <kind> --work-id <work-id> --stage plan
record-output --expect-revision <revision-returned-by-start> --stage plan \
  --artifact plan=specs/NNN-slug/plan.md \
  --artifact requirements_checklist=specs/NNN-slug/checklists/requirements.md \
  --artifact tasks=specs/NNN-slug/tasks.md
decide --expect-revision <revision-returned-by-record-output> --decision approved \
  --decided-by <actor> --decision-date YYYY-MM-DD --decision-evidence <statement>
```

Upstream handoff contract only. `spec-sync` must not run Spec Kit, register
missing upstream artifacts, or approve them. When a required role is missing,
stale, or unapproved, block and report the exact command its owner must run.

## Operation I/O

| Operation | Prerequisites | Owned output | Maximum outcome |
|---|---|---|---|
| `pre-implement` | Approved `spec`, `plan`, `tasks`, and `requirements_checklist` roles for one supported kind | Work-item `pre-implementation-review.md` | `ready_for_review` or `blocked` |
| `post-implement` | Approved `pre_implementation`; converged implementation and named evidence | Work-item `verification.md` | Feature: `ready_for_acceptance`; other supported kinds: `ready_for_review` |
| `change-request` | Source request text | Configured CR or response | `proposed`; `ready_for_review` when materialized |

State an owned output path before writing and preserve an existing record unless the user
authorized updating it.

## `pre-implement`

Read only [the pre-implementation contract](./references/alignment-matrix.md); it includes
the common matrix and the selected kind's applicability row. Apply feature-only
roadmap/UI checks only to `feature`; use the kind-specific constraints for all other
supported kinds. Cite both sides by ID, anchor, or line. Classify findings as
`Blocking`, `Advisory`, or `Skipped`; a skipped required check prevents `Pass`.

Create or update the work item's `pre-implementation-review.md` from
[the pre-implementation template](./assets/pre-implementation-review.template.md) with one
concrete result: `Pass` or `Blocked`.

- For `Pass`, `record-output` role `pre_implementation` at `ready_for_review`,
  report the pending human review, and stop. Only a later explicit human
  `decide --decision approved` makes that role `approved` and writes a durable
  indexed receipt.
- For `Blocked`, run `block` with every concrete blocker, report the required
  owner action, and stop.

Implementation may start only when the exact `pre_implementation` artifact role is
`approved`, its recorded hash still matches, and its work ID/revision matches the
implementation target. `Pass` or `ready_for_review` alone is insufficient.

## `post-implement`

First enforce the approved `pre_implementation` prerequisite above and read only
[the post-implementation contract](./references/post-implementation-contract.md).
Then:

1. Confirm every task/check is complete or has an explicit deferred-work destination.
2. Trace every applicable requirement, scenario, regression, migration invariant, or
   security control to named implementation evidence; a green build alone does not
   demonstrate behavior.
3. Check only vertical drift: out-of-scope behavior, violated constraints, or undeclared
   cross-feature decisions; do not review general code style.
4. Create or update [verification.md](./assets/verification-report.template.md) with
   commands, results, links, blockers, and skips. Never manufacture proof.
5. `record-output` role `verification` at stage `post_implement`, using status
   `ready_for_acceptance` for `kind: feature` and `ready_for_review` for `bug`,
   `maintenance`, `migration`, or `security`. A later explicit generic human
   decision approves or rejects that evidence, with a durable receipt, without
   pretending it is feature acceptance. If blocking drift remains, `block` with
   each concrete blocker instead.

Never put mutable delivery state or acceptance fields in the roadmap. Feature
work stops at `ready_for_acceptance`; a separate explicit acceptance operation
owns delivery. Other supported implementation kinds stop at `ready_for_review`
and never use the feature-decision command.

## `change-request`

Use [the routing rules](./references/change-routing.md). Determine the highest affected
layer and IDs with evidence, preserve approved IDs/history, and order proposed actions
top-down with one owner/output each. Create a pending record from
[the CR template](./assets/change-request.template.md) when configured; otherwise return
the same fields. When materialized, `record-output` role `change_request` at
`ready_for_review`.

The human must resolve that generic review gate before a routed owner can start
the same CR for amendment. A response-only proposal leaves pointer state
unchanged and therefore has no gate to resolve.
List exact suggested human prompts but run none. Do not edit routed artifacts; stop with
every action pending.

## Completion check

Report operation/target, prerequisites, sections read, files changed, validation,
findings/skips, state before/candidate after, and the next allowed human action. Confirm
that only owned output changed, every state write used the shared command, and no Skill or
gate was inferred. Then stop.
