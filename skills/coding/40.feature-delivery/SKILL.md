---
name: feature-delivery
description: Implement or behavior-preservingly simplify one planned feature, test happy paths before relevant failure paths, and record real results in its Feature Plan; or execute one standalone validation Plan and record its evidence and conclusion. Use when the user asks to build, complete, fix, simplify, refactor, or be coached through a planned feature, or to run a planned experiment or feasibility check. Work automatically by default or let the user write core implementation when that intent is clear. Do not invent product scope, clean up the whole repository, or create additional lifecycle documents.
disable-model-invocation: false
---

# Feature Delivery

Implement one Feature Plan end to end. The same plan is the work guide and the
result record; do not create a second checklist or verification report. Delivery
also supports behavior-preserving simplification. Before adding abstractions or
dependencies, check in order: reuse/delete/change existing code; existing
repository facility; stdlib/framework/native platform; installed dependency;
then minimum new code. Preserve validation, security, accessibility, and
data-loss protections.

## Required Input

Read repository guidance, `docs/product-brief.md`, the Feature Map that owns
the row, the target `docs/features/<feature-id>-<slug>.md`, any Storyboard
linked by that plan, and only the code and tests needed for the feature. Read
every cited `FS-*` requirement and linked Architecture Design and Testing
Strategy section. Read the
Roadmap only when dependency order is material. Resolve the owning Map from the
Plan link rather than assuming `docs/feature-map.md`. For a standalone
validation Plan, follow Standalone Validation instead.

For behavior-preserving simplification, these sources define intended behavior;
existing code is evidence, not authority.

Stop and report the missing item when the feature has no plan, its sources
conflict, or an unresolved decision changes observable behavior. Delivery never
edits the Functional Specification, Architecture Design, Testing Strategy, or
Roadmap, and never rewrites an authoritative input or expected result to make a
failing test pass. When implementation shows one of them is wrong, or an
authorized change arrives mid-delivery, stop work on the affected behavior and
report the conflict or change. The user, or an Orchestrator authorized for the
objective, routes the update to the owner first, then every affected
intermediate contract such as the Architecture Design or Testing Strategy,
then the Map row, then the Plan. Continue only after linked sources agree with
the change, from the revised Plan, rerunning only the invalidated
results and the relevant regressions. Do not start an adjacent workflow merely
because an input is missing. Use multiple Skills only when the user's original
request covers their outcomes.

For a reopened Feature, require the existing Plan and Map row to describe the
current behavior and design before implementation. Reuse that Feature ID. If
the request is actually a separate independently useful outcome, stop and
report that it needs a new Map row and Plan; do not hide it inside the reopened
task.

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

## Execution Segments

Follow the Plan's segment order, prerequisites, ownership, and acceptance. A
small Feature needs no additional execution table. Reassess a proposed split
when evidence invalidates its boundaries; update the same Plan within its scope
and report a product or design conflict instead of silently expanding the Feature.

Within cross-agent, finish one planned segment and its focused checks before
returning `status: checkpoint` when more authorized work remains. The summary
must state the segment completed, actual acceptance/check evidence, changed
areas and stable contracts, next unfinished segment, and relevant limitations.
Use empty questions/outcomes and null blocker. This hands off to a new Producer
session in the same run; it is not completion, an independent review pass, or a
new revision. Do not checkpoint trivial work just to create sessions.

At every segment boundary and before any checkpoint, update the Plan's current
position: completed and next segment, remaining checks, and material blockers.
Record a decision that changes the Plan in its `## Decisions` with the reason.

Commit only with explicit authorization from the user's request or a project
rule; this Skill grants none. Within cross-agent, never commit: the
Orchestrator owns section commits, so record the real checks and next work and
return the checkpoint or result. When directly invoked with authorization,
commit each finished segment before the next: stage only its own paths,
preserve unrelated, staged and private files, never amend, push, reset or make
an empty commit unless asked, and name the Feature, segment and actual outcome
without implying `verified` before every gate passes. A failed segment may be
kept in a local recovery commit labeled as failed; stop dependent work instead
of rolling back.

On recovery or a checkpoint continuation, inspect the current revision
(`git log -1 --format=%h`), the uncommitted diff, Plan results, and checkpoint
before doing more work; a failed call may have left useful edits, and segments
committed since the checkpoint no longer appear in the uncommitted diff. Resume incomplete work
without repeating a completed segment or inventing successful checks. Finish
with whole-feature integration, regression checks, and the consistency check;
only then report `done` and update status according to real acceptance results.

## Delegation

Work in the current context by default. Subagents are not free: each one repays
its cost only when it replaces work that the parent would otherwise do serially,
and a brief plus re-reading the feature's sources is itself real cost. Do not
launch a subagent to isolate context, to look parallel, or to split a single
plan step. Serial execution is the norm. Meeting the conditions below permits
delegation; it does not make delegation preferable. Delegate only when the
expected execution saving clearly exceeds briefing, rereading, review, and
integration cost. Never reshape a Plan merely to create parallel work.

Delegate only when every condition holds:

- Two or more remaining Plan steps are genuinely independent and touch
  disjoint files and symbols.
- Shared contracts and shared change points are already stable. Database
  migrations, shared types, API contracts, routes, dependency registration,
  and other work that later steps build on stay in the parent.
- Each delegated step is verifiable on its own with a focused command or a
  bounded, inspectable output.
- Each step is substantial enough that the delegation brief is a small part of
  its work, not a one-file edit or a single test row.

Otherwise implement serially. Run at most three subagents at once, and use fewer
when their boundaries are close to overlapping. Do not concurrently run work
that can modify the same files or generated outputs, or compete for a database,
port, service, or other shared resource. When isolation is uncertain, serialize
the affected edits or commands. The execution environment may use an isolated
workspace when it provides one; this Skill does not require or manage a
particular isolation mechanism.

Give only necessary task context, contracts, and applicable instructions; do
not copy the full parent transcript or require a whole-repository reread.
Each brief states the Plan step boundary, the files the subagent owns and must
not leave, the smallest-change and avoid-speculative-abstraction constraints,
and the focused verification it must perform. When two subagents turn out to
need the same file, stop that split and finish it in the parent.

The parent always keeps integration, the broader validation run, the consistency
check, and every Feature Plan and Feature Map status update. Report a delegated
result only after the parent has seen the diff and the real command output.

## Status

Keep the Feature Plan and Feature Map row synchronized. The normal flow is
`planned` -> `in_progress` -> `verified`. Keep `in_progress` for failing tests,
unfinished work, or an expected wait for the user while work can continue. Use
`blocked` only for a concrete condition that prevents progress, state that
condition in the Plan's `## Blockers`, and return both statuses to `in_progress`
when it clears. Remove the resolved blocker or restore `- None.` at that time.

When the request, project rules, or the Feature Plan's Validation table select
an independent review or testing gate, finishing implementation and self-tests
is readiness for that gate, not final acceptance. Record your own results, leave
the gate row `not run`, keep both statuses `in_progress`, and report readiness.
Set `verified` only after every selected gate has passed against the final
relevant revision; that write belongs to the Producer in a later call or to a
narrow status-only finalization step the requester authorizes, never to a
read-only Reviewer, and it permits no further repair. Orchestrator acceptance of
an unfinished review, such as cross-agent `completed-by-orchestrator`, is not an
independent pass. Without a selected gate, the completion path below applies.

## Standalone Validation

A validation Plan, normally `docs/plans/<topic>.md` written by `feature-plan`,
needs no Product Brief, Feature Map, or Feature ID. Read it, the sources it
names, and the Testing Strategy when present. Run only its procedure within its
budget and stop conditions; keep experiment code where the Plan places it and
change production code only when the Plan includes it. Record each evidence
result with its tested tree, and any failed run before its rerun, as in
Delivery Loop steps 4 and 5, and keep the current position true. Set the
Plan's status to `in_progress`, then `completed` when every planned evidence
item exists, or
`incomplete` when a stop condition, exhausted budget, or failure ends execution
first; use `blocked` only for a concrete condition. Set the conclusion from the
decision criteria only after `completed`. A `not supported` conclusion is a
completed experiment, not a failed delivery. When a gate is selected, leave
its Evidence row `not run` and report readiness; the status and conclusion are
your result, not yet independently reviewed, and the later gate write changes
only that row and the current position. Never write a Map status or
`verified`, and report the conclusion to the requester without editing the
decision owner's document.

## Delivery Loop

1. When implementation work begins, set both the Feature Plan and Feature Map
   row to `in_progress`. For simplification, first establish and run the
   focused baseline for intended behavior. Report a baseline failure before
   changing implementation unless the Plan explicitly includes fixing it. Work
   through the plan's happy paths first. For each behavior, add or update a
   focused test, confirm it fails for the intended reason when practical, make
   the smallest change under the selected mode, and rerun it. Build tests
   incrementally rather than writing and freezing all tests first. Confirm the
   runner actually discovers and executes each new test and that its
   assertions check the expected result.
2. Work through each relevant failure path in the same way. Do not add generic
   edge cases unrelated to the feature.
3. Inspect only the current diff for delegation-only wrappers,
   one-implementation interfaces, one-product factories, constant
   configuration, unused flexibility, and unnecessary dependencies. Remove an
   item only when current intended behavior and constraints do not require it;
   do not perform repo-wide cleanup.
4. Run the plan's focused commands, then the relevant broader regression,
   build, lint, or type checks required by the repository. Before rerunning a
   failed check, preserve its command and scope, the failing test ID (or that
   none is available when discovery or the command itself failed; never invent
   one), the exit status, a concise failure excerpt, and relevant conditions,
   bound to the tested tree as in step 5. Keep raw output private; put a short
   locator in the Plan result or residual risk. When a later run passes and the
   cause is unidentified, record the first failure and the later outcome
   separately and name an unresolved risk with the smallest proposed
   reproduction or diagnostic step and its limits; a passing retry never makes
   the failure resolved. When cause and repair are evidenced, record the
   resolution and the affected checks rerun on the changed tree. A
   deterministic planned failure still prevents acceptance. Decide the effect
   on status from the Plan's criteria, remaining checks, selected gates, and
   the requester's risk scope, with an explicit, justified disposition; what
   they leave unknown or unmet stays so. This preserves evidence; it adds no
   gate, retry count, Tester, or user question per benign transient.
5. Record each real result in the Feature Plan and keep the Feature Map status
   synchronized. Use one short table-cell outcome and never paste raw logs or
   claim a result that did not run. Mark a row passed only when the test asserts
   the stated expected result; otherwise correct the test or expected result.
   Bind each final result to the tree it tested: the revision when the command
   ran (`git log -1 --format=%h`), the relevant source/test paths, and whether
   they had uncommitted changes. When they did, add a short locator that
   distinguishes that content, such as a digest of the `git hash-object` IDs
   of every relevant non-ignored file then present, tracked or untracked. Keep
   it in the cell or a linked private receipt; never commit raw logs or private
   data. A later change to those paths invalidates the affected result;
   committing the unchanged tested content or editing unrelated paths does not,
   and the result keeps its tested revision rather than a newer HEAD. After
   history is rewritten or paths move, keep cited identifiers and add an
   old -> new mapping in the owning Plan or Map only when correspondence is
   verified, for example by equal tree or blob content; otherwise record
   provenance as unknown and never infer it from a commit subject. This is bookkeeping, not a new gate, retest loop, pre-test
   commit, or authority to change Git history or upstream documents.
6. Set both statuses to `verified` only when every planned scenario passes, no
   blocker remains, and no selected independent gate is still pending.
7. Run the consistency check. Behavior-preserving implementation changes remain
   `in_progress` until affected validation is rerun and supports `verified`.

## Consistency Check

Before finishing, re-read this feature's map row, plan, cited requirements,
linked Architecture Design and Testing Strategy sections, and any linked
Storyboard; for validation, the Plan and the sources it names. Confirm the
current position matches the recorded statuses, results, and blockers. Record
each result once, in
the plan, and keep the map row to status only; a cited requirement is delivered
only when at least one Map row cites it and every citing Map row is `verified`,
so do not mark requirements anywhere else. Keep visual flow in the Storyboard
and reference stable `S*` and `T*` IDs
instead of copying it. Fix stale references, names, commands, and paths in the
Plan, Map status, or implementation when the correction is mechanical. Report
Storyboard behavior conflicts without editing the Storyboard; ask only when
resolution needs a product, UI, or technical decision.

## Completion

Report code and documents changed, any authorized commits, happy- and
failure-path results, broader validation, consistency edits, and remaining
blockers. List test, fixture,
skip or disable, and runner, filter, or configuration changes with a reason for
each removed, skipped, or loosened check, so a reviewer can inspect them in the
diff. State readiness and any pending selected gate, or for validation the
status and conclusion. When the work changed build or test commands, project
structure, or instruction routes, report that an instruction-impact assessment
by `coding-agent-instructions` is needed; do not edit `AGENTS.md` here. Do not
require a separate sync or fresh-context approval step.
