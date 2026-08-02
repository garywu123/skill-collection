---
name: architecture-baseline
description: "Use only when the current user explicitly authorizes architecture-baseline work: create a full or lite cross-feature baseline, recover demonstrated architecture, resolve one approved technical spike, amend a challenged decision, or approve reviewed baseline/ADR artifacts. Do not select this skill merely because a workflow pointer recommends it or another phase completed."
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
- Use a fresh conversation, fork, or worker for this operation. Reconstruct
  truth from the pointer/index and owning artifacts; do not rely on another
  Skill body, an old pointer, or excerpts inherited across a gate.
- Never invoke another lifecycle skill, Spec Kit command, planning workflow, or
  implementation workflow.
- Never write production code, product requirements, roadmap semantics,
  feature specifications, wireframes, plans, tasks, tests, or agent guidance.

When present, read `.specify/flow-state.yaml` first. Use it only to verify the
active scope, current revision, profile, gates, and canonical paths; it does not
contain architecture truth or grant permission. Query the artifact index next
through the deterministic `resolve` command by ID or path. Never load the
complete `.specify/artifact-index.yaml` into semantic context; full agreement
belongs to the deterministic `validate --check-paths` operation. If state,
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
| `resolve-spike` | `spike` | the explicitly authorized `SPK-ID` | `spike_result` |

These mappings do not grant authority. Run `start` only when the current user
explicitly names that operation and its prerequisites pass; never infer it from
the pointer or a recommendation. For `amend` or `resolve-spike`, require the
current request to identify the CR-ID or SPK-ID; never allocate or guess one. Read the expected revision
immediately before each state-changing command and use the revision returned by
the preceding command; never hard-code or calculate it.

Before `full` or `lite`, require `pointer.project.profile_status` to be
`confirmed` and `pointer.project.profile` to equal the requested mode. A
`full` or `lite` request does not authorize `confirm-profile`. On a provisional
or mismatched profile, stop and report the separate human authorization needed.

`approve` never runs `start`. Require a pending `ready_for_review` gate for the
named roles and paths. If recording approval fields or supersession evidence
changes any candidate artifact, validate the edited files. For a split root,
then recompute every member hash, replace its complete `## Approved Bundle`
table, and verify the table before running `record-output` again for the
complete approval set. Never refresh only changed-member rows. Use the revision
returned by that command for generic `decide` with explicit human actor, date,
and decision evidence; it writes an indexed receipt. If no bytes changed, verify
the existing gate hashes and every split-bundle member before calling `decide`
directly. Generic `decide` handles only `ready_for_review`; never use it for
acceptance or release candidates.

`amend` first creates only
`doc/architecture-amendments/<CR-ID>.md` under role
`architecture_amendment`, plus proposed ADR files when needed. It does not edit
the accepted baseline or ADRs. On a later explicit `approve`, apply only the
reviewed proposal while keeping that proposal byte-identical. When the root is
split, recompute and validate its complete bundle. Then re-run `record-output`
with the amendment role, every proposed/changed ADR role, and canonical
`architecture` before generic `decide` with actor, date, and decision evidence.
The state command rejects canonical
promotion without the prior reviewed amendment candidate.

## Ownership and Default Paths

This skill may create or modify only:

- architecture baseline: `doc/architecture-baseline.md`;
- split architecture detail: `doc/architecture/<domain-key>.md`;
- architecture decisions: `doc/adr/NNNN-short-title.md`;
- spike result: `doc/architecture/spikes/<SPK-ID>.md`;
- reviewed amendment proposal: `doc/architecture-amendments/<CR-ID>.md`.

Register the baseline under fixed state role `architecture`; register a
proposed ADR under a bounded active role such as `adr-0001`, and an amendment
proposal as `architecture_amendment`. Register a spike result only as active
role `spike_result`; it is not part of the canonical architecture bundle.

The canonical baseline declares exactly one machine-readable field:
`**Artifact bundle**: single` or `**Artifact bundle**: split`. A `single` root
has no `## Approved Bundle` section. A `split` root has that exact heading and a
complete `Path`/`SHA-256` table containing every owned domain-detail and ADR
member exactly once, excluding the root itself and source artifacts. Member
files never repeat the field or table. Registry paths and bundle paths must be
identical as sets. Compute hashes only after member bytes are final, and verify
existence, uniqueness, and current hashes before every review, approval, or
amendment promotion.

Honor explicit user paths, then indexed canonical paths, then exact defaults.
Update the canonical artifact rather than creating a competing source of truth.

## Operations

| Operation | Required before execution | Reads | Creates or modifies | End state |
|---|---|---|---|---|
| `full` | Explicit request; approved PRD and roadmap; confirmed `full` pointer profile | Canonical requirement registry/drivers, roadmap summary/dependencies, constitution and relevant existing decisions | Full baseline and proposed ADRs | `ready_for_review`; stop |
| `lite` | Same approval gate; sizing result recorded; confirmed `lite` pointer profile | Same minimal product sources | One-page baseline; no ADRs | `ready_for_review`; stop |
| `recover` | Explicit request and repository access | Repository evidence plus approved product sources when present | Evidence-labelled baseline | `ready_for_review`; stop |
| `resolve-spike` | Explicit SPK-ID; approved unchanged baseline contains one question, time box, and blocked owner | Only that spike definition and evidence needed to answer it | One investigation result; canonical architecture unchanged | `ready_for_review`; stop |
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
- Keep each opened semantic slice at or below 8 KiB and the initial target
  payload at or below 24 KiB. If complete coverage requires more, use stable-ID
  batches in fresh worker contexts and merge only citations, decisions, and a
  coverage ledger. Never claim completeness while a required batch or resolver
  result is truncated.
- The concise `Decision Altitude` section below is the runtime rule. The longer
  `references/decision-altitude.md` is maintainership background; do not load it
  in addition to the operation playbook.
- Cite canonical paths and stable IDs; never copy architecture into the pointer.

## Modes

Use `lite` only with at most eight features, one deployable unit, at most one
datastore, one owning team, and no regulatory, audit, or contractual
architecture constraint.

Otherwise use `full`. The state command rejects `lite` profile confirmation
when any condition fails or is unknown; a `lite` architecture request cannot
override that result. Stop and report that the human must separately authorize
`full`. If an already-confirmed Lite project later exceeds a threshold, a
human-authorized `full` operation carries the Lite decisions forward.

Keep the Full baseline root below roughly 200 lines and, before the first
feature, normally no more than 12 active ADRs. When growth exceeds either
budget, keep the root as the cross-domain driver/boundary/constraint registry
and move domain-specific decision detail into indexed domain files. The root
owns routing and cross-domain rules; a domain member owns its decision and
constraint text; an ADR owns rationale and history. Never copy normative text
between them. Resolve only the domain and ADR IDs needed by the current
operation. Lite should remain a one-page baseline.

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
- `resolve-spike`: [spike result playbook](./references/spike-result-operation.md);
- `amend` or amendment `approve`: [amendment playbook](./references/architecture-amendment-operation.md).

An ordinary baseline/ADR `approve` uses the approval/hash contract in this file
and does not load an execution playbook. Never load multiple playbooks speculatively.

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
- a spike result answers exactly one approved question, preserves raw evidence,
  and routes any architecture consequence to a separate amendment;
- the `Artifact bundle` value matches the root form and every split root has
  exact registry coverage plus current hashes for all members;
- only current outputs become `Ready for Review`; nothing becomes `Approved`,
  `Accepted`, or `Superseded` without explicit human authorization.

Report mode, sizing result, paths, created versus modified files, decisions,
deferred items, spikes, contradictions, validation results, proposed pointer
transition, and allowed next human commands. Stop without invoking them.
