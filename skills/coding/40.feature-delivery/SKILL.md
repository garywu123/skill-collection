---
name: feature-delivery
description: Implement one planned feature, test its happy paths before relevant failure paths, and record real results in the existing Feature Plan. Use when the user asks to build, complete, or fix a planned feature. Do not invent product scope or create additional lifecycle documents.
---

# Feature Delivery

Implement one Feature Plan end to end. The same plan is the work guide and the
result record; do not create a second checklist or verification report.

## Required Input

Read repository guidance, `docs/product-brief.md`, `docs/feature-map.md`, the
target `docs/features/<feature-id>-<slug>.md`, and only the code and tests needed
for that feature.

Stop and report the missing item when the feature has no plan, its sources
conflict, or an unresolved decision changes observable behavior. Do not invoke
another Skill automatically.

## Delivery Loop

1. Work through the plan's happy paths first. For each behavior, add or update a
   focused test, confirm it fails for the intended reason when practical,
   implement the smallest change, and rerun it.
2. Work through each relevant failure path in the same way. Do not add generic
   edge cases unrelated to the feature.
3. Run the plan's focused commands, then the relevant broader regression,
   build, lint, or type checks required by the repository.
4. Record each real result in the Feature Plan and update the Feature Map once.
   Include the command and concise outcome; never claim a result that did not
   run. Mark a row passed only when the test asserts the stated expected
   result; otherwise correct the test or the expected result.
5. Set both statuses to `verified` only when every planned scenario passes and
   no blocker remains. Otherwise set `blocked` and state the concrete blocker.
6. Run the consistency check.

## Consistency Check

Before finishing, re-read this feature's map row and plan. Record each result
once, in the plan, and keep the map row to status only. Fix stale IDs, names,
commands, and paths in the same task; ask the user only when the conflict needs
a product or technical decision.

## Completion

Report code and documents changed, happy- and failure-path results, broader
validation, consistency edits, and remaining blockers. Do not require a
separate sync or fresh-context approval step.