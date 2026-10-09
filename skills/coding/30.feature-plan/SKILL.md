---
name: feature-plan
description: Create, revise, or reopen one concise Feature Plan for new implementation or behavior-preserving simplification, including happy- and failure-path tests, or one standalone validation Plan for a bounded technical question. Use when the user asks to plan, review, reopen, or simplify implementation or verification for one Feature Map item, or to plan a bounded experiment, spike, or feasibility check without a Feature. Do not implement production code, run the experiment, or create separate checklists and task files.
disable-model-invocation: false
---

# Feature Plan

Prepare one Feature outcome, or one bounded validation question, for execution
in one document. The Plan holds the planned checks and, later, their actual
results. A Feature Plan may cover new implementation or a behavior-preserving
simplification.

## Mode

- `feature`, the default: one Feature Map row.
- `validation`: one bounded question, such as feasibility, performance, or a
  library or algorithm comparison, that a decision depends on. Use it when the
  request asks for an experiment, spike, or feasibility check rather than a
  Feature. See Standalone Validation.

## Output

Create or update `docs/features/<feature-id>-<slug>.md` from
[the Feature template](assets/feature-plan.template.md), or for `validation`
`docs/plans/<topic>.md` from
[the validation template](assets/validation-plan.template.md), unless the
project already has a canonical location. Create no separate spec, tasks,
checklist, research, verification report, per-checkpoint file, or Delivery Plan.

Size follows the work, not a line count. Stay concise: link upstream content
instead of repeating it, delete empty template sections, describe behavior
rather than speculative class or file inventories, and keep each result to one
short table cell. When a Plan becomes hard to scan, first remove repetition and
speculation. Extract a substantial segment's detail into a linked file under
`docs/features/<feature-id>-<slug>/` only when that improves navigation and
ownership; status, current position, and acceptance results stay in the Plan.

The Plan begins with a short current position: status, completed and next
segment, remaining checks, and material blockers. Keep it true whenever a
segment, check, blocker, or source changes. Record key decisions and changes
with one-line reasons in `## Decisions`; keep transcripts, prompts, and routine
activity logs out. A fresh executor must be able to resume from the Plan and the
repository references it names, without the prior conversation. Replace
superseded instructions in the active view with a short decision and source
locator; preserve unique evidence in existing history or retained references,
including unresolved failures. Do not accumulate a narrative of every round.

Link to the Product Brief, the owning Feature Map, and the applicable
Architecture Design and Testing Strategy sections instead of copying them. A
legacy General Design or not-yet-migrated Map technical direction serves as the
Architecture Design until `architecture-design` migrates it. Use the owning
Map's actual path; a child map is under `docs/feature-maps/`, not
`docs/feature-map.md`. When the map row cites `FS-*` requirements, list those
IDs on the Sources line and express only this Feature's observable contribution
in the Outcome; never copy or edit the Functional Specification from a Plan.
When a related Storyboard exists, either `docs/storyboards/<feature-id>-*.html`
or an early topic Storyboard that the request names for this Feature, link it and
reference its stable `S*` state and `T*` transition IDs where relevant; do not
copy its visual content. A Storyboard is otherwise optional and this Skill does
not create one. For a UI Feature in a project whose design document defines an
app shell, add one short UI placement line naming the shell regions this Feature
uses and linking that document instead of restating it.

Leave actual results `not run` until a command has really run, and never paste
raw logs into the Plan. List a failure path only when this Feature can actually
cause it or must handle it. There is no case-count target; do not work through
a category checklist.

## Status And Changes

A new Plan starts as `planned`. Reopen the existing Plan when the user asks to
correct, extend, or revalidate the same Feature outcome; do not create a second
Plan or a versioned Feature ID. Keep its status synchronized with the Feature
Map and preserve results only when the tested behavior, source requirements,
design contracts, and evidence remain valid. Reset affected results to
`not run`; if this invalidates `verified`, set both documents to `planned` until
delivery or revalidation begins. Pure wording or link corrections do not change
status. A separate independently useful outcome belongs in a new Map row before
it is planned.

For an authorized change, the changed requirement or design is updated first
by its owner, then every affected intermediate contract such as the
Architecture Design or Testing Strategy by its owner, then affected
Storyboards and Map rows, then this Plan. When a linked source still
contradicts the change, report it for its owner instead of planning against
either version. Add
one `## Decisions` line with the reason and impact, link an external
change-request record when the organization requires one, and reset only the
results and segments the change invalidates. Never rewrite an authoritative
input or an expected result to make a failing test pass.

## Risks And Questions

Read the Testing Strategy when present and apply its test levels, oracles,
fixture scale, measurement methods, skip rules, and regression conditions by
linking them. Then derive this Feature's risks from its actual users,
workloads, data, failure consequences, and changed boundaries, inspecting
project evidence first. Plan tests for the risks that matter; do not restate the
strategy.

Read prior decisions before asking; preserve confirmed answers unless new
evidence conflicts. Ask only unresolved questions whose answers change design
or acceptance, in user terms, explaining the consequence: where and by whom
the app is used, whether edits overlap, what data must survive a failure, or
whether retrying manually is acceptable. Select only material questions, not
a fixed interview. In existing scenario rows or decision prose, connect a
proposed safeguard or test to its supported trigger, source, user consequence,
and simplest acceptable behavior. Do not assume local use means trusted input
or dispensable data. Search external sources only for a relevant uncertainty,
cite primary sources, and mark applicability.

A missed case under an existing requirement belongs in this Plan. A new
business rule or resource budget needs a decision by its owning source: record
it as a blocker or open question instead of inventing a threshold. Report a
reusable testing rule for `testing-strategy`.

Record each independent review or testing gate that the user's request or
project rules make mandatory as a Validation row, or an Evidence row in a
validation Plan, whose result stays `not run` until that gate passes. When a Testing Strategy condition for independent
testing applies, propose the gate with its concrete verification gap; it
becomes mandatory only when the user or project rules select it.

## Workflow

1. Read repository guidance, the brief, the target map row and its cited
   requirements, the applicable Architecture Design sections, the Testing
   Strategy when present, nearby code and tests, and any related Storyboard.
   Resolve links from the actual owning Map rather than assuming
   `docs/feature-map.md`. For `validation`, read only the request, its named
   sources, and the evidence the question needs.
2. Confirm the Feature has one independently useful outcome. If it contains
   several, stop without planning them and return a scoped replanning request
   that names each outcome and the proposed Map change, for the user or an
   authorized Orchestrator to route to `feature-map`. Do not invent product
   scope.
3. Before proposing new code, check in order: delete, change, or reuse existing
   code; an existing repository facility; the standard library, framework, or
   native platform; an installed dependency; then the minimum new code. Stop at
   the first option that satisfies the intended outcome and current constraints.
4. Derive risks and questions as described above. Define the smallest
   implementation sequence and concrete tests. Number steps and segments
   `Step 10`, `Step 20`, leaving gaps for inserted steps; never use `S10`,
   which collides with Storyboard `S*` IDs. For a behavior-preserving
   simplification, plan revalidation of the intended observable behavior
   without promoting accidental code behavior into a requirement. Reference
   relevant Storyboard states and transitions by ID.
5. Assess execution size, dependencies, and delegation as described below.
6. Write the Plan and run the consistency check.

Do not require or start a Storyboard solely because one is absent. Stop and
report the unresolved UI decision only when it prevents a reliable Plan.

## Execution Planning

Keep one Plan per independently useful Feature outcome. Long execution alone
calls for segments in that Plan, not new Features or Plans.

Default to one serial segment. For substantial work, replace the implementation
list with a compact table: segment ID such as `Step 10`, outcome, owned areas, prerequisites and
shared contracts, applicable constraints, focused checks, and handoff with the
remaining integration. Place boundaries where a behavior is verifiable and the
work fits the executor's context and time allowance; with cross-agent, size each
segment for the configured worker timeout (default 30 minutes), leaving time for
verification and a checkpoint. This is an estimate; long commands may still time
out. Group by verifiable behavior and actual dependencies, not speculative class
inventories. A segment boundary is also a recovery point that an executor
authorized to commit can commit on its own; the Plan itself authorizes no
commit.

Propose subagents only for substantial independent tasks with stable contracts,
disjoint ownership and resources, and focused verification, when execution
savings exceed briefing, rereading, review, and integration costs. Keep shared
types, schemas, routes, and integration with the parent. State "serial" when
delegation is not worthwhile; do not launch implementation subagents here.
Give a proposed delegate only its task, owned paths, necessary contracts and
instructions, checks, and expected brief result with evidence. Delivery
reassesses these boundaries and owns the actual launches and concurrency limit.

Reserve a final integration segment for the whole Feature's acceptance and
regression checks. Multiple worker calls or sessions do not create new Feature
IDs, reset the original baseline, or replenish the run's review budget.

## Standalone Validation

Accept the question from the user, an authorized Orchestrator, or an open
decision reported by `architecture-design`. Do not require a Product Brief,
Feature Map, or Feature ID, and never invent one; use a stable topic slug. Write:

- the question or hypothesis and the decision it informs;
- inputs and representative data with provenance;
- the comparison baseline or oracle;
- the procedure and where experiment code lives, kept out of production code
  unless the request includes it;
- metrics and how they are measured, using Testing Strategy methods when
  present;
- the budget, such as time, model calls, or compute, and stop conditions;
- the evidence that must be collected; and
- decision criteria that map that evidence to a conclusion.

Take decision criteria from the requester or an owning source. When none exists,
record an open question instead of inventing a pass threshold.

Keep execution status separate from the conclusion. Status is `planned`,
`in_progress`, `blocked`, `completed` when every planned evidence item was
obtained, or `incomplete` when a stop condition, exhausted budget, or failure
ended execution first. Conclusion stays `pending` until `completed`, then becomes
`supported`, `not supported`, or `inconclusive` by the criteria. A negative
conclusion still completes the experiment; it never verifies a product Feature
or sets a Map status. Missing planned evidence is `incomplete`, not
`not supported` or `inconclusive`. Consuming the conclusion belongs to the
decision's owner, such as `architecture-design`.

## Consistency Check

Before finishing, re-read the brief, this Feature's map row and cited
requirements, the linked Architecture Design and Testing Strategy sections, and
any linked Storyboard; for `validation`, re-read the request and named sources.
Keep only Plan-specific execution, tests, and results here; link instead of
repeating product, requirement, architecture, testing-rule, or visual-flow
content. Confirm the current position matches the Plan's statuses, results, and
blockers. Report a requirement the row cites but this Plan cannot deliver; do
not weaken it. Fix stale references, names, dependencies, commands, and paths in
this Plan and its Map row when the correction is mechanical. Report Storyboard
behavior conflicts without editing the Storyboard; ask only when resolution
needs a product, UI, or technical decision.

## Completion

Report the Plan path, mode, implementation or procedure outline, planned tests
and gates, questions asked or open, consistency edits, open blockers or
replanning requests, and validation performed.
