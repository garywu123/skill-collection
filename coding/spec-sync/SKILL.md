---
name: spec-sync
description: Perform one explicitly requested vertical alignment review for a named implementation work item before implementation, record post-implementation evidence into that work item's delivery checklist without accepting it, or propose the highest-impact route for a change request. Never infer authority from state, invoke another skill, or edit another owner's artifacts.
---

# Spec Sync

## Contract and routing

Require the current user to name exactly one operation and target:
`pre-implement`, `post-implement`, or `change-request`. Never implement code,
run Spec Kit, perform code/security/acceptance review, approve anything, invoke
another skill, or continue into a suggested operation.

A context that reaches a human decision point, or emits a blocked handoff, stops
after read-only reporting. The decision itself, and any downstream operation,
begins in a new conversation the user explicitly authorizes.

Read `roadmap.yaml` at the repository root first to find the target function's
status and its `spec` and `checklist` paths. Read only the target IDs and the
relevant sections. Stop on conflicting IDs, paths, or truth sources.

Keep each opened slice at or below 8 KiB and the initial target payload at or
below 24 KiB. Beyond that, process stable-ID batches separately and merge only
citations, findings, and a coverage ledger
(`| Batch | Stable IDs / paths | Result | Evidence |`) into the owned output. A
truncated query or an uncovered required batch can never produce `Pass` or a
ready result.

## Recording state

After writing its owned output, update `roadmap.yaml` in the same turn. Record
only; never approve, and never set a function to `accepted`.

| Operation | Prerequisites | Owned output | `roadmap.yaml` effect |
|---|---|---|---|
| `pre-implement <id> <kind>` | Function at `specified`, with spec, plan, tasks, and checklist present | `pre-implementation-review.md` in the work-item directory | None on `Pass`; record the blocker in `notes` on `Blocked` |
| `post-implement <id> <kind>` | An approved pre-implementation review; converged implementation and named evidence | Evidence rows and check results inside that function's `checklist.md` | `status: verifying` when no blocker remains |
| `change-request <CR-ID>` | Source request text | `doc/change-requests/<CR-ID>.md`, or a response when the project keeps no CR records | None |

`pre-implement` never moves a function to `implementing`; the human does that
when authorizing implementation. `post-implement` never moves a function to
`accepted`; only a human verifying the checklist in a fresh conversation does.

Supported kinds: `feature`, `bug`, `maintenance`, `migration`, `security`. Never
infer the kind from an ID.

Product, roadmap, architecture, UI, and project-map changes belong to their
owning skills. Spec Kit owns horizontal `spec.md`/`plan.md`/`tasks.md` analysis.
This skill owns only the pre-implementation review, the verification evidence it
writes into the checklist, and the proposed change route.

## Upstream prerequisites

`pre-implement` requires, for the same function: `spec.md`, `plan.md`,
`tasks.md`, and `checklist.md` all present, and a `roadmap.yaml` status of
`specified`. Spec Kit and the human produce those; this skill never writes them
and never marks them approved.

When a required file is missing or the status does not match, block and report
exactly which file its owner must produce. Do not proceed on a partial set.

## `pre-implement`

Read only [the pre-implementation contract](./references/alignment-matrix.md);
it includes the common matrix and the selected kind's applicability row. Apply
feature-only roadmap/UI checks only to `feature`; use the kind-specific
constraints for every other supported kind. Cite both sides by ID, anchor, or
line. Classify findings as `Blocking`, `Advisory`, or `Skipped`; a skipped
required check prevents `Pass`.

Create or update the work item's `pre-implementation-review.md` from
[the template](./assets/pre-implementation-review.template.md) with one concrete
result: `Pass` or `Blocked`.

- For `Pass`, report the pending human review and stop. Implementation starts
  only after the human explicitly approves this review; `Pass` alone is not
  approval.
- For `Blocked`, list every concrete blocker in the review, note it in the
  function's `roadmap.yaml` entry, report the required owner action, and stop.

## `post-implement`

First confirm the pre-implementation review exists and was approved, then read
only [the post-implementation contract](./references/post-implementation-contract.md).
Then:

1. Confirm every task and check is complete, or has an explicit deferred-work
   destination.
2. Trace every applicable requirement, scenario, regression, migration
   invariant, or security control to named implementation evidence. A green
   build alone does not demonstrate behavior.
3. Check only vertical drift: out-of-scope behavior, violated constraints, or
   undeclared cross-function decisions. Do not review general code style.
4. Write the results into the function's `checklist.md`:
   - add one row per traced requirement to the **Evidence** table, recording the
     command or method actually run and its real result;
   - record blockers and skips explicitly;
   - never manufacture proof.
5. Set `status: verifying` in `roadmap.yaml`. If a blocking drift remains,
   record the blocker in `notes` instead and leave the status where it was.

**Fill in evidence; do not grade.** Leave the checklist's acceptance-criteria
boxes unticked and its `Decision` section empty. Those belong to the fresh
conversation that verifies the work — the context that produced the evidence
does not judge whether the evidence is sufficient.

## `change-request`

Use [the routing rules](./references/change-routing.md). Determine the highest
affected layer and the affected IDs with evidence, preserve approved IDs and
history, and order the proposed actions top-down with one owner and one output
each.

Create a pending record from
[the CR template](./assets/change-request.template.md) when the project keeps
change-request records; otherwise return the same fields in the response. List
the exact suggested human prompts but run none of them. Do not edit routed
artifacts. Stop with every action pending.

For a change to a function already at `accepted`, state which route applies and
why. The default is editing in place: reset it to `specified`, remove
`verified`, and clear old checklist boxes, Evidence, Decision, reviewer, and
date. Use a successor only when the old and new capabilities need independent
deployment, support, acceptance, migration, or long-term tracking.

## Completion check

Report operation and target, prerequisites, sections read, files changed,
validation, findings and skips, the `roadmap.yaml` lines you changed, and the
next allowed human action. Confirm that only owned output changed and that no
skill, approval, or acceptance was inferred. Then stop.
