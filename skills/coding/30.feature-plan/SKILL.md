---
name: feature-plan
description: Create or revise one concise Feature Plan that states what to implement and how happy and failure paths will be tested. Use before implementing one Feature Map item or when that feature's scope or verification changes. Do not implement production code or create separate checklists and task files.
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

Link to the Product Brief and Feature Map instead of copying them. Leave actual
results `not run` until a command has really run. List a failure path only when
this feature can actually cause it or must handle it; two to four rows is
normal. Do not work through a category checklist.

## Workflow

1. Read repository guidance, the brief, the target map row, shared technical
   constraints, nearby code, and nearby tests.
2. Confirm the feature has one independently useful outcome. If not, propose a
   Feature Map split and stop only when user input is needed.
3. Define the smallest implementation sequence and concrete tests. Prefer
   behavior-level language over speculative class inventories.
4. Write the plan and run the consistency check.

## Consistency Check

Before finishing, re-read the brief and this feature's map row. Keep only
feature-specific design, tests, and results here and link instead of repeating
product or shared architecture prose. Fix stale IDs, names, dependencies,
commands, and paths in the same task; ask the user only when the conflict needs
a product or technical decision.

Report the plan path, implementation outline, planned tests, consistency edits,
open blockers, and validation performed.