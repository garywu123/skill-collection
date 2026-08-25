---
name: feature-plan
description: Create or revise one concise Feature Plan that states what to implement and how happy and failure paths will be tested. Use when the user asks to plan or revise implementation or verification for one Feature Map item. Do not select it merely because planning is the next workflow stage, implement production code, or create separate checklists and task files.
---

# Feature Plan

Prepare one feature for implementation in one document. The plan holds both the
planned checks and, later, their actual results.

## Output

Create or update `docs/features/<feature-id>-<slug>.md` from
[the template](assets/feature-plan.template.md). Create no separate spec,
tasks, checklist, research, or verification report.

Keep the whole plan under 60 lines, focused on:

- the observable feature outcome and scope;
- affected components and the smallest implementation sequence;
- happy-path tests first;
- relevant failure-path tests second; and
- executable validation commands and their results.

Link to the Product Brief and Feature Map instead of copying them. When a
related `docs/storyboards/<feature-id>-*.html` exists, link it and reference its
stable `S*` state and `T*` transition IDs where relevant; do not copy its visual
content. A Storyboard is otherwise optional and this Skill does not create one.

Leave actual results `not run` until a command has really run. Keep each real
result to one short table-cell outcome and never paste raw logs into the plan.
List a failure path only when this feature can actually cause it or must handle
it; two to four rows is normal. Do not work through a category checklist.

A new Plan starts as `planned`. When revising an existing Plan, keep its status
synchronized with the Feature Map and preserve results only when the verified
behavior and expected result are unchanged. Reset affected results to `not run`;
if this invalidates `verified`, set both documents to `planned` until delivery or
revalidation begins. Pure wording or link corrections do not change status.

## Workflow

1. Read repository guidance, the brief, the target map row, shared technical
   constraints, nearby code and tests, and any related Storyboard.
2. Confirm the feature has one independently useful outcome. If not, propose a
   Feature Map split and stop only when user input is needed.
3. Define the smallest implementation sequence and concrete tests. Reference
   relevant Storyboard states and transitions by ID. Prefer behavior-level
   language over speculative class inventories.
4. Write the plan and run the consistency check.

Do not require or start a Storyboard solely because one is absent. Stop and
report the unresolved UI decision only when it prevents a reliable plan.

## Consistency Check

Before finishing, re-read the brief, this feature's map row, and any linked
Storyboard. Keep only feature-specific implementation, tests, and results here;
link instead of repeating product, shared architecture, or visual-flow content.
Fix stale references, names, dependencies, commands, and paths in this Plan and
its Map row when the correction is mechanical. Report Storyboard behavior
conflicts without editing the Storyboard; ask only when resolution needs a
product, UI, or technical decision.

## Completion

Report the plan path, implementation outline, planned tests, consistency edits,
open blockers, and validation performed.
