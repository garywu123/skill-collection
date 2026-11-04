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
validation Plan, follow Standalone Validation instead. For a Change Plan, read
its decision source and every affected Map row and Feature Plan it names;
statuses below then mean the Change Plan's own status, and affected Map rows
keep theirs.

For behavior-preserving simplification, these sources define intended behavior;
existing code is evidence, not authority.

Stop and report the missing item when the feature has no plan, its sources
conflict, or an unresolved decision changes observable behavior. A replacement
that the Plan's Sources record as already decided is not a conflict; implement
it and promote it in Delivery Loop step 6. Delivery never edits the Functional
Specification, Architecture Design, Testing Strategy, Roadmap or other owner
documents, except that promotion, and never rewrites an authoritative input or
expected result to make a failing test pass. When implementation shows one of
them is wrong, or an authorized change arrives mid-delivery, stop work on the
affected behavior and report it. Continue from the revised Plan once linked
sources agree, rerunning only the invalidated results and the relevant
regressions. Do not start an adjacent workflow merely
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

1. Reuse an adequate focused test, or strengthen/add it and its fixtures for
   a coverage gap. Run it and confirm the intended failure when practical.
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
Keep handoffs to current decisions, completed/next work, open failures and
gates, and tested-evidence locators. Replace superseded instructions with a
short reason and recoverable source; preserve unique evidence instead of
repeating the conversation or every earlier result.

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

Work serially in the current context by default. Delegate only when the
expected saving clearly exceeds briefing, rereading, review, and integration
cost, and every condition holds:

- Two or more remaining Plan steps are genuinely independent and touch
  disjoint files and symbols.
- Shared contracts and shared change points are already stable. Database
  migrations, shared types, API contracts, routes, dependency registration,
  and other work that later steps build on stay in the parent.
- Each delegated step is verifiable on its own with a focused command or a
  bounded, inspectable output.
- Each step is substantial enough that the delegation brief is a small part of
  its work, not a one-file edit or a single test row.

Run at most three subagents at once, never two that can modify the same files
or compete for a database, port, or other shared resource; when unsure,
serialize. Each brief states the Plan step boundary, the files the subagent
owns, the smallest-change constraint, necessary contracts, and its focused
verification; no full transcript. When two subagents turn out to need the same
file, finish that work in the parent.

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
relevant revision; that write, with the Plan retirement in Delivery Loop step
6, belongs to the Producer in a later call or to a narrow finalization step the
requester authorizes, never to a read-only Reviewer, and it permits no further
repair. Orchestrator acceptance of
an unfinished review, such as cross-agent `completed-by-orchestrator`, is not an
independent pass. Without a selected gate, the completion path below applies.

## Standalone Validation

A validation Plan, normally `docs/plans/<topic>.md` written by `feature-plan`,
needs no Product Brief, Feature Map, or Feature ID. Read it, the sources it
names, and the Testing Strategy when present. Run only its procedure within its
budget and stop conditions; keep experiment code where the Plan places it and
change production code only when the Plan includes it. Record each evidence
result bound to its revision as in Delivery Loop steps 4 and 5, and keep the
current position true. Set the
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
   through the plan's happy paths first. For each behavior, reuse adequate
   focused coverage; strengthen or add a test only for a gap, using the
   Testing Strategy's smallest adequate level. Confirm the intended failure
   when practical, make the smallest change under the selected mode, and
   rerun the relevant test. Build tests incrementally rather than writing and
   freezing all tests first. Confirm the
   runner actually discovers and executes each new test and that its
   assertions check the expected result.
2. Work through each relevant failure path in the same way. Do not add generic
   edge cases unrelated to the feature.
3. Throughout steps 1 and 2, before adding a limit, safeguard, fallback or
   broader check that the Plan does not name, identify its supported scenario
   and simplest adequate alternative. Add focused checks within existing
   requirements; pause the affected work only when resolution needs a new
   business rule, a contract change, a material scope or cost decision, or a
   change to a selected gate. Then inspect only the current diff for delegation-only wrappers,
   one-implementation interfaces, one-product factories, constant
   configuration, unused flexibility, and unnecessary dependencies. Remove an
   item only when current intended behavior and constraints do not require it;
   do not perform repo-wide cleanup.
4. Widen test scope only as the work grows. While editing, compile and run only the focused
   tests for the behavior at hand; after a fix, rerun only the failing tests.
   At a segment boundary, run the segment's owner tests plus the tests that
   consume a public type, contract or endpoint the segment changed; run
   another layer's suite, such as frontend tests after a backend change, only
   when a shared contract or DTO changed. Run the Testing Strategy's `fast`
   regression, build, lint, or type checks once, on the final tree, before
   reporting `done`; that run supersedes earlier broad runs, so do not repeat
   it per segment. Run each applicable `Feature gate` suite, such as UI flows
   or capacity, once after implementation and focused checks pass and before
   `done`; an edit near that code does not trigger it earlier. Run a `stage`
   suite only when a validation Plan requests it. A command that the
   cross-agent CLI runs as a delivery check is not run again by you. Rerun a
   broad or gate suite only after a later change to its declared inputs or
   an unresolved failure.
   Classify a failure as product, test, environment, or still unknown before
   choosing a repair; an environment failure is not proof of a product defect.
   When a command fails before executing any test, such as a sandbox, restore
   or test-host startup failure, do not retry variants or diagnose it: report
   it once as an environment limitation and hand execution to whoever can run
   it (the Orchestrator's checks within cross-agent, otherwise the user). When
   a later run passes and the cause is unidentified, name one unresolved risk
   with the smallest proposed reproduction step; a passing retry never makes
   the failure resolved. A deterministic planned failure still prevents
   acceptance. Decide the effect on status from the Plan's criteria, remaining
   checks, selected gates, and the requester's risk scope.
5. Record each real result in the Feature Plan and keep the Feature Map status
   synchronized. Use one short table-cell outcome, such as
   `passed 112/112 @ 1a2b3c4`, and never paste raw logs or claim a result that
   did not run. Mark a row passed only when the test asserts the stated
   expected result; otherwise correct the test or expected result. Bind a
   result to the commit it tested; when the tested content was uncommitted,
   write `@ <revision> + uncommitted` and replace it with the commit once the
   segment is committed. Never write file hashes, manifests, receipt files, log
   paths, attempt counts or resolved-failure history into the Plan; only an
   unresolved failure belongs there, in `## Blockers` or the result cell. A
   later change to the tested paths invalidates the affected result; editing
   unrelated paths does not.
6. When every planned scenario passes and no blocker remains, promote the
   Plan's durable decisions before reporting `done`, so a selected review sees
   them. A durable decision is a rule a later change must respect, such as a
   contract, default, limit, compatibility rule, or ownership choice; step
   order, test layout, and evidence are not. Write each into its owning
   long-lived document as the current rule, merged with what that document
   already says, in one or two sentences with a long-lived source link and no
   date or history, following that document's budget, format and edit rules.
   The owner is the document the project's `AGENTS.md` routes that kind of
   rule to, such as a domain page, report definition or research README;
   without a route, technical contracts go to the Architecture Design. When a
   durable decision has no identified owner or its route is ambiguous, keep
   the Plan and report the unresolved promotion. Replacing an existing rule is
   promotion when the Plan's Sources record it as already decided by the user
   or that document's owner, such as a decided review item; otherwise stop and
   report it to that document's owner. Move
   an open gate, such as a deferred measurement, to the Map row or Testing
   Strategy that owns it.
   Set the Map row `verified` only when every planned scenario passes, no
   blocker remains, and no selected independent gate is still pending. Then,
   once every durable decision is placed, retire the Plan: delete it and its detail folder, point the Map row and any
   link that named the Plan at the verifying revision, and leave the Plan's
   content to git history. Within a selected gate, this retirement is the
   Orchestrator's finalization edit after the gate passes. For a Change Plan,
   its own row in the plan index or review document takes that link. When the
   Plan's Sources name review items, check them off in the review checklist
   as `done in <revision>`. When that leaves every item of that review
   checked and no Plan it requested open, close the review: confirm its
   decisions live in their owners, then delete the review documents if their
   final contents are in a known commit, otherwise report them as
   uncommitted.
7. Run the consistency check. Behavior-preserving implementation changes remain
   `in_progress` until affected validation is rerun and supports `verified`.

## Consistency Check

Before finishing, re-read the Required Input sources this work touched, and
every document that received a promotion. Confirm the
current position matches the recorded statuses, results, and blockers. Confirm
each promoted decision reads as a current rule in its owning document and that
no promotion restates a value another document owns. Record each result once,
in the plan while it exists, and keep the map row to status and its link; a cited requirement is delivered
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
