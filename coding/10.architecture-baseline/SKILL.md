---
name: architecture-baseline
description: "Use only when the current user explicitly authorizes architecture-baseline work: create a full or lite cross-feature baseline, recover the architecture an existing repository demonstrates, resolve one approved technical spike, amend a challenged decision, or approve reviewed baseline/ADR artifacts. Do not select this skill merely because roadmap.yaml shows an architecture stage or another phase completed."
---

# Architecture Baseline

Own technical decisions that multiple features must share. Record evidence and
trade-offs without deciding feature-internal design.

## Lifecycle Contract

- Require the current user request to authorize one named operation. A recorded
  stage, a recommended next action, or a completed prerequisite is not
  authorization.
- One named lifecycle authorization may span turns. A context that reaches a
  human decision point, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any human decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from canonical state; a fork or worker does not grant
  new authorization.
- Never invoke another lifecycle skill, Spec Kit command, planning workflow, or
  implementation workflow.
- Never write production code, product requirements, roadmap semantics, feature
  specifications, wireframes, plans, tasks, tests, or agent guidance.

Read `roadmap.yaml` at the repository root first to learn the current stage,
profile, and canonical document paths. It holds no architecture truth and grants
no permission. If it, an approved artifact, and the current request disagree,
stop and report.

## Recording state

After writing an artifact, update `roadmap.yaml` in the same turn. Record only;
never gate, approve, or set a function to `accepted`.

| Operation | `roadmap.yaml` effect |
|---|---|
| `full`, `lite`, `recover` | Set `docs.architecture` |
| `amend` | None; a proposal is not canonical truth |
| `resolve-spike` | None; a spike closes an investigation, not a decision |

Require the current request to identify a CR-ID or SPK-ID; never allocate or
guess one. `full` and `lite` follow the mode the current request names; see
**Modes** below.

`approve` records the human's approval fields — actor, date, and evidence —
inside the reviewed artifact itself, and changes nothing else.

`amend` creates only `doc/architecture-amendments/<CR-ID>.md`, plus proposed ADR
files when needed; accepted truth stays unchanged. A later explicit `approve`
keeps that proposal byte-identical and applies only its reviewed changes.

## Ownership and Default Paths

This skill may create or modify only:

- architecture baseline: `doc/architecture-baseline.md`;
- split architecture detail: `doc/architecture/<domain-key>.md`;
- architecture decisions: `doc/adr/NNNN-short-title.md`;
- spike result: `doc/architecture/spikes/<SPK-ID>.md`;
- reviewed amendment proposal: `doc/architecture-amendments/<CR-ID>.md`.

Record the baseline in `roadmap.yaml` as `docs.architecture`. ADRs, amendment
proposals, and spike results are not `docs` roles; the baseline's own registry
routes to them.

The baseline root declares `**Artifact bundle**: single` or `split`. A split root
lists every domain-detail and ADR member path in its registry exactly once. No
hash table is maintained — Git detects member drift.

Honor explicit user paths, then canonical paths recorded in `roadmap.yaml`, then
exact defaults.
Update the canonical artifact rather than creating a competing source of truth.

## Operations

| Operation | Required before execution | Creates or modifies | Stops at |
|---|---|---|---|
| `full` | Approved PRD and roadmap; the request names `full` | Full baseline and proposed ADRs | Awaiting review |
| `lite` | Same approval prerequisite; the request names `lite` | One-page baseline; no ADRs | Awaiting review |
| `recover` | Repository access | Evidence-labelled baseline | Awaiting review |
| `resolve-spike` | Approved unchanged baseline holds one question, time box, and blocked owner | One investigation result; architecture unchanged | Awaiting review |
| `amend` | Explicit challenged decision, CR-ID, and trigger | Amendment proposal and proposed ADRs; accepted truth unchanged | Awaiting review |
| `approve` | Explicit human approval of named reviewed artifacts | Approval statuses; supersession links | Approved |

`recover` is the operation for adopting an existing codebase: it documents the
architecture the repository demonstrates, labelling each claim `Verified` or
`Inferred`, and never promotes an accident into an intended constraint.

Every operation stops at its end state. Approval records only the decision
explicitly given; it does not begin agent bootstrap or feature planning.

## Context Discipline

- For `full`/`lite`, read the PRD registry before cited requirement text, and
  roadmap summary, dependencies, coverage, and boundaries — not handoff prompts
  or delivery history. For split requirements, select only the relevant domain
  files plus the cross-cutting area.
- Exclude discovery history, wireframes, feature specs, plans, tasks, and source
  by default. For `amend`, add only the named trigger artifact.
- For `recover`, inspect manifests, build/CI configuration, and directory
  boundaries before a representative source sample. Search before opening large
  files; never scan the repository into context.
- Keep each opened slice at or below 8 KiB and the initial target payload at or
  below 24 KiB. Beyond that, batch by stable ID in fresh workers and merge only
  citations, decisions, and a coverage ledger
  (`| Batch | Stable IDs / paths | Result | Evidence |`). Never claim
  completeness while a required batch or resolver result is truncated.
- `Decision Altitude` below is the runtime rule; `references/decision-altitude.md`
  is maintainership background and is not loaded alongside a playbook.
- Cite canonical paths and stable IDs; never copy architecture into
  `roadmap.yaml`.

## Modes

The current request names the mode. Cross-check it against the roadmap's
`Profile sizing` recommendation and `roadmap.yaml`'s `profile` marker: if the
request asks for `lite` where the roadmap's sizing evidence says `full`, report
the mismatch and ask, rather than proceeding or silently upgrading. If a Lite
project later outgrows it, a `full` operation carries the Lite decisions
forward.

`lite` compresses artifact count, not guarantees: retain evidence, boundaries,
Plan Constraints, approval, and validation. If a one-way door appears, compare
alternatives and record reversal cost inline even though no separate ADR exists.
Lite stays a one-page baseline.

Keep the Full root below roughly 200 lines and, before the first feature,
normally at most 12 active ADRs. Past either budget, keep the root as the
cross-domain driver/boundary/constraint registry and move domain-specific
detail into routed domain files. The root owns routing and cross-domain rules;
a domain member owns its decision and constraint text; an ADR owns rationale and
history. Never copy normative text between them, and resolve only the domain and
ADR IDs the current operation needs.

`recover` and `amend` do not require a newly approved roadmap, but use approved
product sources when they exist and report contradictions without rewriting
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

Load only the playbook for the selected operation, never several:

- `full`, `lite`, or `recover`: [baseline playbook](./references/baseline-operations.md);
- `resolve-spike`: [spike result playbook](./references/spike-result-operation.md);
- `amend` or amendment `approve`: [amendment playbook](./references/architecture-amendment-operation.md).

An ordinary baseline/ADR `approve` loads no playbook.

## Validation

Nothing validates these mechanically. Before presenting output, check them
yourself:

- every decision passes the altitude test and cites an approved requirement,
  principle, repository fact, or external constraint;
- one-way decisions compare alternatives and have proposed ADRs in `full`;
  deferred decisions and spikes carry their trigger/evidence fields;
- Plan Constraints are testable; product behavior, feature-internal design,
  tasks, code shapes, and unjustified version pins are absent;
- `recover` claims are `Verified` or `Inferred`, and amendments leave accepted
  decisions in force until approval;
- a spike result answers exactly one approved question, preserves raw evidence,
  and routes any architecture consequence to a separate amendment.

Report mode, sizing result, paths, created versus modified files, decisions,
deferred items, spikes, contradictions, validation results, the `roadmap.yaml`
lines you changed, and allowed next human commands. Stop without invoking them.
