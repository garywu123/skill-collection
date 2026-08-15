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
status, optional `spec`, and `checklist` paths. Read only the target IDs and the
relevant sections. The absence of `spec` selects the direct feature route; its
presence selects the detailed route. Stop on conflicting IDs, paths, or truth
sources.

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
| `pre-implement <id> feature`, direct | Function at `planned`; approved roadmap behavior source and checklist present; no `spec` path | `Pass` or `Blocked` response only | None on `Pass`; record the blocker in `notes` on `Blocked` |
| `pre-implement <id> <kind>`, detailed | Function at `planned`; spec, plan, tasks, and checklist present | `pre-implementation-review.md` in the work-item directory | None on `Pass`; record the blocker in `notes` on `Blocked` |
| `post-implement <id> <kind>` | Converged implementation, checklist, and named evidence; approved pre-review additionally required for the detailed route | Evidence rows and check results inside that function's `checklist.md` | `status: verifying` when no blocker remains |
| `change-request <CR-ID>` | Source request text | `doc/change-requests/<CR-ID>.md`, or a response when the project keeps no CR records | None |

`pre-implement` never moves a function to `implementing`; the human does that
when authorizing implementation. `post-implement` never moves a function to
`accepted`; only a human verifying the checklist in a fresh conversation does.

Supported kinds: `feature`, `bug`, `maintenance`, `migration`, `security`. Never
infer the kind from an ID.

Product, roadmap, architecture, UI, and project-map changes belong to their
owning skills. Spec Kit may own detailed-route `spec.md`/`plan.md`/`tasks.md`
analysis. This skill owns only route-aware alignment results, the verification
evidence it writes into the checklist, and the proposed change route.

## Delivery routes

Use the direct route only for a `feature` whose approved roadmap description and
acceptance are sufficient to implement and verify. It requires a checklist
derived from that roadmap entry and no `spec` path in `roadmap.yaml`.

Use the detailed route when a feature has an optional `spec` path, and for every
non-feature kind. It requires `spec.md`, `plan.md`, `tasks.md`, and
`checklist.md`. A partial detailed bundle blocks; never silently fall back to
the direct route. Both routes enter pre-implementation at `status: planned`.

## `pre-implement`

Read only [the pre-implementation contract](./references/alignment-matrix.md);
it includes the common matrix and the selected kind's applicability row. Apply
feature-only roadmap/UI checks only to `feature`; use the kind-specific
constraints for every other supported kind. Cite both sides by ID, anchor, or
line. Classify findings as `Blocking`, `Advisory`, or `Skipped`; a skipped
required check prevents `Pass`.

For the direct feature route, return one concrete `Pass` or `Blocked` result in
the response and create no review artifact. For the detailed route, create or
update `pre-implementation-review.md` from
[the template](./assets/pre-implementation-review.template.md).

- For `Pass`, report the pending human implementation authorization and stop.
   Detailed-route implementation also requires explicit approval of its review;
   a direct-route `Pass` is not implementation authorization by itself.
- For `Blocked`, list every concrete blocker in the direct response or detailed
   review, note it in the function's `roadmap.yaml` entry, report the required
   owner action, and stop.

## `post-implement`

First resolve the same direct or detailed route used before implementation. For
the detailed route, confirm the pre-implementation review exists and was
approved. Then read only
[the post-implementation contract](./references/post-implementation-contract.md).
Then:

1. For a detailed route, confirm every task and check is complete or has an
   explicit deferred-work destination. For a direct route, confirm every
   checklist criterion has named evidence.
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
why. The default is editing in place: reset it to `planned`, remove
`verified`, and clear old checklist boxes, Evidence, Decision, reviewer, and
date. Use a successor only when the old and new capabilities need independent
deployment, support, acceptance, migration, or long-term tracking.

## Completion check

Report operation and target, prerequisites, sections read, files changed,
validation, findings and skips, the `roadmap.yaml` lines you changed, and the
next allowed human action. Confirm that only owned output changed and that no
skill, approval, or acceptance was inferred. Then stop.
