# Project Agent Instructions

## Scope

This file owns agent behavior, document routing, verified commands, and working
boundaries. It does not own product, architecture, feature, or delivery truth;
those live in the documents routed below.

## State

`roadmap.yaml` is the single state file. Read it first in every conversation; it
records the current stage, every function, and where each document lives. Do not
reconstruct state from conversation history or from a previous agent's summary.
Its state is descriptive, not permission to start another operation.

## Document routing

| Need | Read |
|---|---|
| Current stage, function list, document paths | `roadmap.yaml` |
| Product outcomes, scope, rules | `[prd path]` |
| Function boundaries and sequence | `[roadmap doc path]` |
| Cross-function technical decisions | `[architecture path]` |
| One function's behavior and acceptance | that function's `spec` in `roadmap.yaml` |
| One function's delivery bar | that function's `checklist` in `roadmap.yaml` |
| Legacy behavior | `[legacy path]`, as evidence only |

Read only the entries the named step needs. When sources conflict, stop and
report the evidence; never silently prefer current code over approved documents.

## The four rules

1. Read `roadmap.yaml` first. It is where the project is.
2. Do exactly the one step the user named. Report the result and stop. Never
   continue into the next stage because it looks obvious.
3. After changing a routed artifact or a function's real delivery state, update
   only the affected `roadmap.yaml` fields in the same turn.
4. A function reaches `accepted` only when its checklist is verified in a fresh
   conversation, by explicit human decision.

## Map write-back contract

`project-map` owns the schema. The currently authorized operation may update
only the route or function entry its work directly changed.

| Established fact | Required map write-back |
|---|---|
| A routed product, architecture, or UI document now exists | Add or correct its `docs.*` path |
| The approved product roadmap adds a function | Add its `planned` entry |
| A function spec and checklist now exist | Set `specified`; record both paths |
| The human starts implementation | Set `implementing` |
| Implementation evidence is ready for independent checking | Set `verifying` |
| A fresh conversation verifies every box and the human accepts | Set `accepted`; add `verified` |
| Accepted behavior changes | Reset to `specified`; remove `verified`; clear stale checklist results |

Do not update the map when no routed fact changed. Before the final response,
reconcile it with changes made in this turn; never advance unrelated entries.

## Function lifecycle

`planned` -> `specified` -> `implementing` -> `verifying` -> `accepted`

`as-built` sits outside that line: the function exists in the repository but has
no spec and was never verified here. Convert it to `specified` when it next
needs to change; do not retro-specify functions nobody is touching.

Specifying a function writes both its spec and its delivery checklist. The
checklist is derived from that spec's acceptance criteria plus the standing
quality bar below; write it while the spec is being written, not at delivery
time. A context that implemented a function does not tick its own boxes. When
accepted behavior changes, clear all boxes, Evidence, Decision, reviewer, and
date before the function can be verified again.

## Verified commands

- Setup: `[verified command]`
- Run: `[verified command]`
- Targeted test: `[verified command]`
- Full validation: `[verified command]`

Omit any command not verified by a manifest, CI configuration, or a successful
run in this repository.

## Change rules

- Make the smallest change that satisfies the active function spec.
- Preserve explicit non-goals; avoid unrelated refactors and dependency bumps.
- Add or update tests for changed behavior.
- Report conflicts, unknowns, unverified assumptions, and remaining risk.
- Never commit secrets or production data.
