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

Use a fresh conversation, fork, or worker for this operation. Reconstruct truth
from the pointer/index and owning artifacts; do not rely on another Skill body,
an old pointer, or excerpts inherited across a gate.

Read `.specify/flow-state.yaml` first. Query the generated index with deterministic
`resolve --id` or `resolve --path`; never load the complete index into semantic
context. Full agreement belongs to deterministic `validate --check-paths`. Read
only target IDs and relevant sections. Stop on conflicting IDs,
paths, revisions, or truth sources.

Keep each opened semantic slice at or below 8 KiB and the initial target payload at or
below 24 KiB. If complete coverage requires more, process stable-ID batches in fresh
worker contexts and merge only citations, findings, and a coverage ledger into the owned
output. A truncated query or uncovered required batch can never produce `Pass` or a
ready result.

Use documented deterministic state commands for starts, validation, artifact/hash
recording, transitions, and index rebuilds. Never hand-edit state or index YAML.

## Operation-to-start mapping

| Operation | Deterministic start |
|---|---|
| `pre-implement <work-id> <kind>` | For `feature`, `bug`, `maintenance`, `migration`, or `security`, may run `start --expect-revision N --kind <kind> --work-id <work-id> --stage pre_implement` after prerequisites pass and no gate is pending. Never infer kind from an ID. |
| `change-request <request-id>` | If a durable CR path is configured, may run `start --expect-revision N --kind change_request --work-id <request-id> --stage change_request` after prerequisites pass. If output is response-only, do not start or mutate pointer state. |
| `post-implement <work-id> <kind>` | Never starts work; it must match the already authorized active work item/kind and records stage `post_implement`. |

Product, roadmap, architecture, UI, and guidance changes belong to their owning Skills.
Spec Kit owns horizontal `spec.md`/`plan.md`/`tasks.md` analysis. This Skill owns only the
pre-implementation review, vertical verification record, and proposed change route.

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
the common matrix and the selected kind's applicability row. Require hash-matching
approved `spec`, `plan`, `tasks`, and `requirements_checklist` roles. Apply feature-only
roadmap/UI checks only to `feature`; use the kind-specific constraints for all other
supported kinds. Cite both sides by ID, anchor, or line. Classify findings as
`Blocking`, `Advisory`, or `Skipped`; a skipped required check prevents `Pass`.

Create or update the work item's `pre-implementation-review.md` from
[the pre-implementation template](./assets/pre-implementation-review.template.md) with one
concrete result: `Pass` or `Blocked`.

- For `Pass`, register role `pre_implementation` with `record-output
  --expect-revision N --stage pre_implement --status ready_for_review --artifact
  pre_implementation=<path>`, report the pending human review, and stop. Only a later
  explicit human generic `decide --decision approved --decided-by ...
  --decision-date ... --decision-evidence ...` makes that role `approved` and writes a
  durable indexed decision receipt.
- For `Blocked`, run `block --expect-revision N --stage pre_implement --artifact
  pre_implementation=<path>` with every concrete blocker, report the required owner action,
  and stop.

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
5. For `kind: feature`, register role `verification` with `record-output
   --expect-revision N --stage post_implement --status ready_for_acceptance
   --artifact verification=<path>`. For `bug`, `maintenance`, `migration`, or
   `security`, use `--status ready_for_review`; a later explicit generic human
   decision approves or rejects that evidence, with a durable receipt, without pretending
   it is feature acceptance. If blocking drift remains, instead use
   `block --expect-revision N --stage post_implement --artifact
   verification=<path>` with each concrete blocker.

Never put mutable delivery state or acceptance fields in the roadmap. Feature
work stops at `ready_for_acceptance`; a separate explicit acceptance operation
owns delivery. Other supported implementation kinds stop at `ready_for_review`
and never use the feature-decision command.

## `change-request`

Use [the routing rules](./references/change-routing.md). Determine the highest affected
layer and IDs with evidence, preserve approved IDs/history, and order proposed actions
top-down with one owner/output each. Create a pending record from
[the CR template](./assets/change-request.template.md) when configured; otherwise return
the same fields. When materialized, register role `change_request` with `record-output
--expect-revision N --stage change_request --status ready_for_review --artifact
change_request=<path>`.
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
