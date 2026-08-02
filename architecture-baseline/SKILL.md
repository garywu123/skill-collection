---
name: architecture-baseline
description: "Use only when the current user request explicitly authorizes architecture-baseline work: create a full or lite cross-feature baseline, recover the demonstrated architecture of an existing repository, amend a challenged decision, or approve reviewed baseline/ADR artifacts. Do not select this skill merely because a workflow pointer recommends it, a roadmap is approved, or another phase has completed."
---

# Architecture Baseline

Own technical decisions that multiple features must share. Record evidence and
trade-offs without deciding feature-internal design.

## Lifecycle Contract

- Require the current user request to authorize one named operation. Pointer
  readiness, a recommended next action, or completion of a prerequisite is not
  authorization.
- Perform one operation at a time. At each review or approval boundary, report
  allowed next human commands and stop.
- Never invoke another lifecycle skill, Spec Kit command, planning workflow, or
  implementation workflow.
- Never write production code, product requirements, roadmap semantics,
  feature specifications, wireframes, plans, tasks, tests, or agent guidance.

When present, read `.specify/flow-state.yaml` first. Use it only to verify the
active scope, current revision, profile, gates, and canonical paths; it does not
contain architecture truth or grant permission. Query the artifact index next
through the deterministic `resolve` command by ID or path. Open
`.specify/artifact-index.yaml` in full only when it is clearly small. If state,
the resolved index slice, and an approved artifact disagree, stop and report
the conflict.

Do not hand-edit shared state or index YAML. After validation, use the
repository's deterministic state/index command when configured; otherwise
report the proposed transition for the human to record.

Map an already-authorized operation to deterministic `start` exactly as follows:

| Operation | `kind` | `work-id` | `stage` |
|---|---|---|---|
| `full` | `project` | `pointer.project.id` | `architecture` |
| `lite` | `project` | `pointer.project.id` | `architecture` |
| `recover` | `project` | `pointer.project.id` | `architecture` |
| `amend` | `change_request` | the explicitly authorized `CR-ID` | `architecture` |

These mappings do not grant authority. Run `start` only when the current user
explicitly names that operation and its prerequisites pass; never infer it from
the pointer or a recommendation. For `amend`, require the current request to
identify the CR-ID; never allocate or guess one. Read the expected revision
immediately before each state-changing command and use the revision returned by
the preceding command; never hard-code or calculate it.

Before `full` or `lite`, require `pointer.project.profile_status` to be
`confirmed` and `pointer.project.profile` to equal the requested mode. A
`full` or `lite` request does not authorize `confirm-profile`. On a provisional
or mismatched profile, stop and report the separate human authorization needed.

`approve` never runs `start`. Require a pending `ready_for_review` gate for the
named roles and paths. If recording approval fields or supersession evidence
changes any candidate artifact, validate the edited files, then run
`record-output` again for the complete approval set with the same roles, paths,
and active stage at `ready_for_review` so the gate stores the reviewed hashes.
Use the revision returned by that command for the generic `decide`. If no bytes
changed, verify the existing gate hashes and call `decide` directly. Generic
`decide` handles only `ready_for_review`; never use it for acceptance or release
candidates.

`amend` first creates only
`doc/architecture-amendments/<CR-ID>.md` under role
`architecture_amendment`, plus proposed ADR files when needed. It does not edit
the accepted baseline or ADRs. On a later explicit `approve`, apply only the
reviewed proposal while keeping that proposal byte-identical, then re-run
`record-output` with the amendment role, every
proposed/changed ADR role, and canonical `architecture` before generic
`decide`. The state command rejects canonical promotion without the prior
reviewed amendment candidate.

## Ownership and Default Paths

This skill may create or modify only:

- architecture baseline: `doc/architecture-baseline.md`;
- architecture decisions: `doc/adr/NNNN-short-title.md`;
- reviewed amendment proposal: `doc/architecture-amendments/<CR-ID>.md`.

Register the baseline under fixed state role `architecture`; register a
proposed ADR under a bounded active role such as `adr-0001`, and an amendment
proposal as `architecture_amendment`.

Honor explicit user paths, then indexed canonical paths, then exact defaults.
Update the canonical artifact rather than creating a competing source of truth.

## Operations

| Operation | Required before execution | Reads | Creates or modifies | End state |
|---|---|---|---|---|
| `full` | Explicit request; approved PRD and roadmap; confirmed `full` pointer profile | Canonical requirement registry/drivers, roadmap summary/dependencies, constitution and relevant existing decisions | Full baseline and proposed ADRs | `ready_for_review`; stop |
| `lite` | Same approval gate; sizing result recorded; confirmed `lite` pointer profile | Same minimal product sources | One-page baseline; no ADRs | `ready_for_review`; stop |
| `recover` | Explicit request and repository access | Repository evidence plus approved product sources when present | Evidence-labelled baseline | `ready_for_review`; stop |
| `amend` | Explicit challenged decision, CR-ID, and trigger | Accepted baseline, affected ADRs, trigger and necessary context | Architecture amendment proposal and proposed ADRs; accepted truth is unchanged | `ready_for_review`; stop |
| `approve` | Explicit human approval of named reviewed artifacts | Reviewed baseline/ADRs and validation evidence | Approval statuses; supersession links for an approved amendment | `approved`; stop |

Approval records only the decision explicitly approved. It does not begin agent
bootstrap or feature planning in the same turn.

## Context Discipline

- For `full` and `lite`, read the PRD registry before cited requirement text;
  read roadmap summary, dependencies, coverage, and boundaries rather than
  handoff prompts or delivery history.
- For split requirements, select relevant domain files and the cross-cutting
  area from the index; never load all areas speculatively.
- Exclude discovery history, wireframes, feature specs, plans, tasks, and source
  by default. For `amend`, add only the named trigger artifact.
- For `recover`, inspect manifests, build/CI configuration, and directory
  boundaries before a representative source sample. Search before opening large
  files; never scan the repository into context.
- Read [decision altitude](./references/decision-altitude.md) only when a
  candidate's altitude or reversibility is ambiguous, or when a deferred
  decision/spike needs the detailed protocol.
- Cite canonical paths and stable IDs; never copy architecture into the pointer.

## Modes

Use `lite` only with at most eight features, one deployable unit, at most one
datastore, one owning team, and no regulatory, audit, or contractual
architecture constraint.

Otherwise use `full`. If the user explicitly insists on `lite`, comply but
record every failed condition as a risk. A later failure of the sizing test
requires a human-authorized `full` operation that carries the lite decisions
forward.

Keep the Full baseline root below roughly 200 lines and, before the first
feature, normally no more than 12 active ADRs. When growth exceeds either
budget, keep the root as the cross-domain driver/boundary/constraint registry
and move domain-specific decision detail into indexed domain files; never copy
the same decision into both. Resolve only the domain and ADR IDs needed by the
current operation. Lite should remain a one-page baseline.

`lite` compresses artifact count, not guarantees: retain evidence, boundaries,
Plan Constraints, approval, and validation. If a one-way door appears, compare
alternatives and record reversal cost inline even though no separate ADR is
created.

`recover` and `amend` do not require a newly approved roadmap, but use approved
product sources when they exist and report any contradiction without rewriting
either side.

## Decision Altitude

Ask: **would at least two actual roadmap features need to agree?** If yes, the
baseline owns the decision; otherwise the feature plan owns it. A second use of
a previously local library requires a human-authorized amendment.

A **one-way door** reverses through data migration, shipped-feature rewrites, or
external contract breakage; compare alternatives and create an ADR in `full`.
A **two-way door** is a contained refactor; record a concise rationale.

Where evidence is insufficient, do not fill the gap. Record either a deferred
decision with its forcing trigger and option-preserving constraint, or a spike
with one answerable question, time box, blocked feature, and disposable output.

## Conditional Operation Playbooks

After the current request selects an operation, load only its playbook:

- `full` or `lite`: [baseline playbook](./references/baseline-operations.md);
- `recover`: the recovery section in that same playbook;
- `amend` or amendment `approve`: [amendment playbook](./references/architecture-amendment-operation.md).

An ordinary baseline/ADR `approve` uses the approval/hash contract in this file
and does not load an execution playbook. Never load both playbooks speculatively.

## Validation

Before presenting output, verify:

- every decision passes the altitude test and cites an approved requirement,
  principle, repository fact, or external constraint;
- one-way decisions compare alternatives and have proposed ADRs in `full`;
  deferred decisions and spikes contain their required trigger/evidence fields;
- Plan Constraints are testable; product behavior, feature-internal design,
  tasks, code shapes, and unjustified version pins are absent;
- `recover` claims are `Verified` or `Inferred`, and amendments leave accepted
  decisions in force until approval;
- only current outputs become `Ready for Review`; nothing becomes `Approved`,
  `Accepted`, or `Superseded` without explicit human authorization.

Report mode, sizing result, paths, created versus modified files, decisions,
deferred items, spikes, contradictions, validation results, proposed pointer
transition, and allowed next human commands. Stop without invoking them.
