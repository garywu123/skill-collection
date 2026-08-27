---
name: feature-delivery
description: Implement one planned feature, test its happy paths before relevant failure paths, and record real results in the existing Feature Plan. Use when the user asks in natural language to build, complete, fix, or be coached through a planned feature. Work automatically by default or let the user write core implementation when that intent is clear. Do not invent product scope or create additional lifecycle documents.
---

# Feature Delivery

Implement one Feature Plan end to end. The same plan is the work guide and the
result record; do not create a second checklist or verification report.

## Required Input

Read repository guidance, `docs/product-brief.md`, `docs/feature-map.md`, the
target `docs/features/<feature-id>-<slug>.md`, any Storyboard linked by that
plan, and only the code and tests needed for the feature.

Stop and report the missing item when the feature has no plan, its sources
conflict, or an unresolved decision changes observable behavior. Do not start
an adjacent workflow merely because an input is missing. Use multiple Skills
only when the user's original request covers their outcomes.

## Mode

Default to `auto`, where the agent writes tests and implementation. Use
`guided` when the user's natural language clearly says they want to write the
core implementation or be coached; no literal mode keyword is required. The
user may reassign file ownership or switch modes at any step. State the new
division briefly and continue from the current behavior.

In `guided` mode, for each behavior:

1. Normally write or update the focused test and fixtures, run them, and confirm
   the intended failure when practical.
2. Tell the user the implementation file, symbol or signature, and required
   behavior. For a user-assigned function, provide a complete function-body
   draft that the user can type into the file: include the expected control
   flow, key calls, error handling, return values, and concise `TODO` markers
   only where repository-specific details remain unknown. Keep it scoped to
   the current behavior and consistent with nearby code.
3. Do not edit user-assigned implementation files. Wait while the user types
   the body, then inspect the relevant change and rerun the focused test.
   Continue to answer questions or give bounded hints as needed.
4. Explain a remaining mismatch concisely and repeat, or advance when it passes.

## Status

Keep the Feature Plan and Feature Map row synchronized. The normal flow is
`planned` -> `in_progress` -> `verified`. Keep `in_progress` for failing tests,
unfinished work, or an expected wait for the user while work can continue. Use
`blocked` only for a concrete condition that prevents progress, state that
condition in the Plan's `## Blockers`, and return both statuses to `in_progress`
when it clears. Remove the resolved blocker or restore `- None.` at that time.

## Delivery Loop

1. When implementation work begins, set both the Feature Plan and Feature Map
   row to `in_progress`. Work through the plan's happy paths first. For each
   behavior, add or update a focused test, confirm it fails for the intended
   reason when practical, make the smallest change under the selected mode, and
   rerun it.
2. Work through each relevant failure path in the same way. Do not add generic
   edge cases unrelated to the feature.
3. Run the plan's focused commands, then the relevant broader regression,
   build, lint, or type checks required by the repository.
4. Record each real result in the Feature Plan and keep the Feature Map status
   synchronized. Use one short table-cell outcome and never paste raw logs or
   claim a result that did not run. Mark a row passed only when the test asserts
   the stated expected result; otherwise correct the test or expected result.
5. Set both statuses to `verified` only when every planned scenario passes and
   no blocker remains.
6. Run the consistency check.

## Consistency Check

Before finishing, re-read this feature's map row, plan, and any linked
Storyboard. Record each result once, in the plan, and keep the map row to status
only. Keep visual flow in the Storyboard and reference stable `S*` and `T*` IDs
instead of copying it. Fix stale references, names, commands, and paths in the
Plan, Map status, or implementation when the correction is mechanical. Report
Storyboard behavior conflicts without editing the Storyboard; ask only when
resolution needs a product, UI, or technical decision.

## Completion

Report code and documents changed, happy- and failure-path results, broader
validation, consistency edits, and remaining blockers. Do not require a
separate sync or fresh-context approval step.
