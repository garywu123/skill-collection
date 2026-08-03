---
name: architecture-baseline
description: "Use only when the current user explicitly authorizes architecture-baseline work: create a full or lite cross-feature baseline, recover demonstrated architecture, resolve one approved technical spike, amend a challenged decision, or approve reviewed baseline/ADR artifacts. Do not select this skill merely because a workflow pointer recommends it or another phase completed."
---

# Architecture Baseline

Own technical decisions that multiple features must share. Record evidence and
trade-offs without deciding feature-internal design.

## Lifecycle Contract

- Require the current user request to authorize one named operation. Pointer
  readiness, a recommended next action, or a completed prerequisite is not
  authorization.
- One named lifecycle authorization may span turns. A context that creates or
  resolves a human gate, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any gate decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from canonical state; a fork or worker does not grant
  new authorization.
- Never invoke another lifecycle skill, Spec Kit command, planning workflow, or
  implementation workflow.
- Never write production code, product requirements, roadmap semantics, feature
  specifications, wireframes, plans, tasks, tests, or agent guidance.

Read `.specify/flow-state.yaml` first to verify active scope, revision, profile,
gates, and canonical paths; it holds no architecture truth and grants no
permission. Query the index only through `resolve --id` or `resolve --path`. If
state, the resolved slice, and an approved artifact disagree, stop and report.

## Deterministic state command

```text
python <this-skill-dir>/../flow-state/scripts/flow_state.py --root . <operation> [options]
```

`flow-state/` deploys as this directory's sibling. Use `--help` for options;
never hand-edit state, index, or bundle tables. Use `<revision-from-status>`
for the first write in a context, then the revision each command returns; on
`stale revision` stop and report the conflict rather than retrying.

```text
start --expect-revision <revision-from-status> \
  --kind project --work-id <project-id> --stage architecture

sync-bundle --artifact doc/architecture-baseline.md \
  --member <domain-or-adr-path> [--member ...] --role architecture

record-output --expect-revision <revision-returned-by-start> \
  --stage architecture --artifact architecture=doc/architecture-baseline.md \
  --next "architecture-baseline approve"

decide --expect-revision <revision-returned-by-record-output> \
  --decision approved --decided-by <actor> --decision-date YYYY-MM-DD \
  --decision-evidence <statement-or-reference>
```

`sync-bundle` computes and writes every member hash; never type a SHA-256 by
hand. Add `--check-only` to `record-output` to validate a complex transition
before writing. Substitute the authorized CR-ID or SPK-ID and its stage for
`amend` and `resolve-spike`.

| Operation | `kind` | `work-id` | `stage` |
|---|---|---|---|
| `full`, `lite`, `recover` | `project` | `pointer.project.id` | `architecture` |
| `amend` | `change_request` | the authorized `CR-ID` | `architecture` |
| `resolve-spike` | `spike` | the authorized `SPK-ID` | `spike_result` |

Require the current request to identify a CR-ID or SPK-ID; never allocate or
guess one. Before `full` or `lite`, require `profile_status: confirmed` and a
`profile` equal to the requested mode; that request never authorizes
`confirm-profile`.

`approve` never runs `start`. Record the human's approval fields in the reviewed
artifact, re-run `sync-bundle` for a split root, `record-output` the complete
approval set, then `decide` with actor, date, and evidence. If no bytes changed,
call `decide` directly. Generic `decide` resolves only `ready_for_review`.

`amend` creates only `doc/architecture-amendments/<CR-ID>.md` under role
`architecture_amendment`, plus proposed ADR files when needed; accepted truth
stays unchanged. A later explicit `approve` applies only the reviewed proposal,
keeps that proposal byte-identical, and re-records the amendment role, every
proposed ADR role, and canonical `architecture` before `decide`.

## Ownership and Default Paths

This skill may create or modify only:

- architecture baseline: `doc/architecture-baseline.md`;
- split architecture detail: `doc/architecture/<domain-key>.md`;
- architecture decisions: `doc/adr/NNNN-short-title.md`;
- spike result: `doc/architecture/spikes/<SPK-ID>.md`;
- reviewed amendment proposal: `doc/architecture-amendments/<CR-ID>.md`.

Register the baseline under fixed role `architecture`, a proposed ADR under a
bounded role such as `adr-0001`, an amendment as `architecture_amendment`, and a
spike result only as `spike_result` (never part of the canonical bundle).

The baseline root declares `**Artifact bundle**: single` or `split`. A split root
also owns a `## Approved Bundle` table covering every domain-detail and ADR
member exactly once; `sync-bundle` writes it.

Honor explicit user paths, then indexed canonical paths, then exact defaults.
Update the canonical artifact rather than creating a competing source of truth.

## Operations

| Operation | Required before execution | Creates or modifies | End state |
|---|---|---|---|
| `full` | Approved PRD and roadmap; confirmed `full` profile | Full baseline and proposed ADRs | `ready_for_review` |
| `lite` | Same approval gate; confirmed `lite` profile | One-page baseline; no ADRs | `ready_for_review` |
| `recover` | Repository access | Evidence-labelled baseline | `ready_for_review` |
| `resolve-spike` | Approved unchanged baseline holds one question, time box, and blocked owner | One investigation result; architecture unchanged | `ready_for_review` |
| `amend` | Explicit challenged decision, CR-ID, and trigger | Amendment proposal and proposed ADRs; accepted truth unchanged | `ready_for_review` |
| `approve` | Explicit human approval of named reviewed artifacts | Approval statuses; supersession links | `approved` |

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
- Cite canonical paths and stable IDs; never copy architecture into the pointer.

## Modes

The confirmed pointer profile selects the mode. This skill never re-derives
sizing: `confirm-profile` owns those thresholds and rejects an ineligible
`lite`. If a confirmed Lite project later outgrows it, a human-authorized `full`
operation carries the Lite decisions forward.

`lite` compresses artifact count, not guarantees: retain evidence, boundaries,
Plan Constraints, approval, and validation. If a one-way door appears, compare
alternatives and record reversal cost inline even though no separate ADR exists.
Lite stays a one-page baseline.

Keep the Full root below roughly 200 lines and, before the first feature,
normally at most 12 active ADRs. Past either budget, keep the root as the
cross-domain driver/boundary/constraint registry and move domain-specific
detail into indexed domain files. The root owns routing and cross-domain rules;
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

The state command fails closed on stage/role/status validity, bundle coverage,
and hash freshness; read its error instead of pre-checking those rules. Before
presenting output, verify the judgments it cannot make:

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
deferred items, spikes, contradictions, validation results, the proposed pointer
transition, and allowed next human commands. Stop without invoking them.
