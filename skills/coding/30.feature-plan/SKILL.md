---
name: feature-plan
description: Create, revise, or reopen one concise Feature Plan for new implementation or behavior-preserving simplification, including happy- and failure-path tests. Invoke explicitly, by name, to plan, review, reopen, or simplify implementation or verification for one Feature Map item. Do not implement production code or create separate checklists and task files.
disable-model-invocation: true
---

# Feature Plan

Prepare one feature for implementation in one document. The plan holds both the
planned checks and, later, their actual results. It may cover new implementation
or a behavior-preserving simplification.

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

Link to the Product Brief, the owning Feature Map, and any applicable General
Design instead of copying them. Use the owning Map's actual path; a child map is
under `docs/feature-maps/`, not `docs/feature-map.md`. When the map row cites
`FS-*` requirements, list those IDs on the Sources line and express only this
Feature's observable contribution in the Outcome; never copy or edit the
Functional Specification from a Plan. When a related
`docs/storyboards/<feature-id>-*.html` exists, link it and reference its
stable `S*` state and `T*` transition IDs where relevant; do not copy its visual
content. A Storyboard is otherwise optional and this Skill does not create one.

Leave actual results `not run` until a command has really run. Keep each real
result to one short table-cell outcome and never paste raw logs into the plan.
List a failure path only when this feature can actually cause it or must handle
it; two to four rows is normal. Do not work through a category checklist.

A new Plan starts as `planned`. Reopen the existing Plan when the user asks to
correct, extend, or revalidate the same Feature outcome; do not create a second
Plan or a versioned Feature ID. Keep its status synchronized with the Feature
Map and preserve results only when the tested behavior, source requirements,
design contracts, and evidence remain valid. Reset affected results to
`not run`; if this invalidates `verified`, set both documents to `planned` until
delivery or revalidation begins. Pure wording or link corrections do not change
status. A separate independently useful outcome belongs in a new Map row before
it is planned.

## Workflow

1. Read repository guidance, the brief, the target map row and its cited
   requirements, every linked General Design or map technical direction, nearby
   code and tests, and any related Storyboard. Resolve links from the actual
   owning Map rather than assuming `docs/feature-map.md`.
2. Confirm the feature has one independently useful outcome. If not, propose a
   Feature Map split and stop only when user input is needed.
3. Before proposing new code, check in order: delete, change, or reuse existing
   code; an existing repository facility; the standard library, framework, or
   native platform; an installed dependency; then the minimum new code. Stop at
   the first option that satisfies the intended outcome and current constraints.
4. Define the smallest implementation sequence and concrete tests. For a
   behavior-preserving simplification, plan revalidation of the intended
   observable behavior without promoting accidental code behavior into a
   requirement. Reference relevant Storyboard states and transitions by ID.
   Prefer behavior-level language over speculative class inventories.
5. Write the plan and run the consistency check.

Do not require or start a Storyboard solely because one is absent. Stop and
report the unresolved UI decision only when it prevents a reliable plan.

## Consistency Check

Before finishing, re-read the brief, this feature's map row and cited
requirements, every linked General Design, and any linked Storyboard. Keep only
feature-specific implementation, tests, and results here; link instead of
repeating product, requirement, shared architecture, or visual-flow content.
Report a requirement the row cites but this Plan cannot deliver; do not weaken
it.
Fix stale references, names, dependencies, commands, and paths in this Plan and
its Map row when the correction is mechanical. Report Storyboard behavior
conflicts without editing the Storyboard; ask only when resolution needs a
product, UI, or technical decision.

## Completion

Report the plan path, implementation outline, planned tests, consistency edits,
open blockers, and validation performed.
