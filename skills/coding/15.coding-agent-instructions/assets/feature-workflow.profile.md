# Feature Workflow Profile

Use only after the user explicitly selects this profile for the current
project. Selection establishes reusable workflow and local Git authorization;
it does not start a Feature or expand the user's task. Preserve stronger
existing gates and approved naming differences. Replace `<app-name>` with the
project's approved prefix, remove authoring notes, and reconcile the default
commit prohibition in `agents.template.md` when inserting the rules below.

## Rules to Insert

- For user-authorized planned Feature work, use `cross-agent` to coordinate
  `feature-plan` and `feature-delivery`. Planning requires independent review
  before dependent implementation; a planning-only request stops after planning.
  Small unrelated edits follow the project's ordinary workflow.
- Define each delivery Step as a bounded, independently verifiable segment,
  using `Step 10`, `Step 20`, and so on. Follow the Plan's prerequisites and
  finish with whole-Feature integration and regression checks. Individual TDD
  iterations are not separate Steps.
- The Producer follows incremental TDD in `feature-delivery`, using the smallest
  adequate behavior checks; trivial scaffolding uses an appropriate build or
  inspectable check rather than artificial tests. The independent read-only
  Reviewer judges acceptance, test adequacy, meaningful coverage gaps, test
  weakening/skips, and `ponytail` simplicity within the current scope.
- For each authorized Feature or bug, create or reuse one task branch before
  planning or implementation: `<app-name>/<kind>/<id>-<slug>`. Use the actual
  Feature/issue ID and approved work kind, such as `feature`, `bug`, or
  `refactor`. Work with no ID uses `<app-name>/<kind>/<topic-slug>`; never invent
  a Feature ID for standalone validation. Check Git namespace collisions and
  report them instead of changing names silently.
- This project authorizes task-scoped branch creation/switching and local
  commits for the user-authorized work above. Preserve unrelated changes;
  report mixed changes or a switch conflict instead of stashing or discarding
  them. In cross-agent, only the Orchestrator commits while workers are stopped,
  using the owning Skill's path-scoped section-commit procedure. Direct
  authorized Delivery follows its own segment-commit procedure.
- Commit each completed delivery Step before dependent work. Use
  `<kind>-step-<number>: <id-or-topic> <actual outcome>`, for example
  `feature-step-10: F01 application builds and launches`. Planning, review fixes,
  and finalization use separate descriptive commits such as `feature-plan`,
  `feature-review-fix`, and `feature-verify`; do not rewrite prior Step commits.
  Record actual checks and pending independent review in the commit body.
- A Step commit is a recovery point, not independent acceptance. Mark a Feature
  `verified` only after all required checks and selected independent gates pass
  against the final relevant content. Keep failure and missing evidence truthful.
- Push, merge, tag, amend, rebase/reset, empty commits, and worktree operations
  require separate authorization; this profile authorizes none of them. Never
  commit credentials, private configuration, raw logs, or unrelated files.

## Ownership

Keep only these selected project rules in `AGENTS.md`. Model/provider/effort,
CLI paths, and runtime settings belong to `.cross-agent/config.toml`; actual
steps, results, and current position belong to the Feature Plan. Detailed
execution, review, context handoff, and commit mechanics stay in their owning
Skills. Link only project documents that actually exist.
