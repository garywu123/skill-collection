# Project Agent Instructions

## Scope and precedence

This file owns agent behavior, routing, verified commands, and working
boundaries. Product, architecture, function, and delivery truth live in the
artifacts routed by `roadmap.yaml`.

Resolve conflicts in this order: current explicit user instruction, approved
product truth, the selected roadmap entry and function spec, applicable
architecture, repository evidence, then legacy material. Report conflicts;
never silently promote current or legacy behavior into desired behavior.

## Routing

Read `roadmap.yaml` first in every conversation. Its state is descriptive, not
permission to start work. Follow only the route needed for the named operation.

| Need | Resolve from `roadmap.yaml` |
|---|---|
| Product outcomes, scope, rules | `docs.prd` |
| Function boundaries and sequence | `docs.roadmap`, then one selected entry |
| Cross-function technical decisions | `docs.architecture` |
| Product UI structure | `docs.ui`, when present |
| One function's behavior or delivery bar | that entry's `spec` or `checklist` |
| Legacy evidence | `docs.legacy`, when present; evidence only |

Do not load unrelated function specs or reconstruct state from chat history.

## Working contract

1. Do exactly the one operation the user named, report, and stop.
2. Modify only the authorized owner artifacts and directly affected map fields.
3. Do not infer approval, acceptance, release authority, or the next Skill.
4. Before the final response, reconcile `roadmap.yaml` entries changed by this operation.
5. A function reaches `accepted` only after fresh-context checklist verification
   and an explicit human decision.

## Map write-back

`project-map` owns the schema. The authorized operation may update only the
route or function entry whose underlying fact it directly changed.

| Established fact | Required write-back |
|---|---|
| A routed product, architecture, or UI document now exists | Add or correct its `docs.*` path |
| The approved product roadmap adds a function | Add `planned`, or evidence-backed `as-built` during adoption |
| A function spec and checklist now exist | Set `specified`; record both paths |
| The human starts implementation | Set `implementing` |
| Implementation evidence is ready for independent checking | Set `verifying` |
| Fresh verification passes and the human accepts | Set `accepted`; add `verified` |
| Accepted behavior changes | Reset to `specified`; remove `verified`; clear stale checklist results |

Do not change the map merely because an operation ran, and never advance
unrelated entries.

## Function lifecycle

`planned -> specified -> implementing -> verifying -> accepted`

`as-built` means an implementation was observed but not specified or accepted
under this process. Convert only the function being changed. When accepted
behavior changes, clear old checklist boxes, Evidence, Decision, reviewer, and
date before reverification.

## Verified commands

- Setup: `[verified command]`
- Run: `[verified command]`
- Targeted test: `[verified command]`
- Full validation: `[verified command]`

Omit commands not verified by a manifest, CI, or a successful repository run.

## Change rules

- Make the smallest change satisfying the selected function spec.
- Preserve explicit non-goals; avoid unrelated refactors and dependency bumps.
- Add or update tests for changed behavior.
- Report unknowns, conflicts, assumptions, and remaining risk.
- Never commit secrets or production data.
