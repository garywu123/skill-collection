---
name: product-discovery-roadmap
description: "Use only when the current user request explicitly authorizes one product operation: discover, approve discovery, draft or approve a PRD/roadmap, propose an amendment, or approve a reviewed amendment. Do not select this skill merely because roadmap.yaml shows a matching stage or a prior phase is complete."
---

# Product Discovery Roadmap

Turn uncertain product intent into reviewed discovery evidence, an approved
product requirements document, and an approved feature roadmap. Keep product
decisions independent of architecture and implementation.

## Lifecycle Contract

- Require the current user request to authorize one named operation. A recorded
  stage, recommended next action, completed prerequisite, or prior approval is
  not authorization.
- One named lifecycle authorization may span turns. A context that reaches a
  human decision point, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any human decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from canonical state; a fork or worker does not grant
  new authorization.
- Never invoke another lifecycle skill, Spec Kit command, planning command, or
  implementation workflow.
- Never write code, architecture, feature plans, tasks, wireframes, acceptance
  results, release status, or agent instructions.

Read `roadmap.yaml` at the repository root first to learn the current stage and
canonical document paths. It holds no product truth and grants no permission. If
it, an approved artifact, and the current request disagree, stop and report the
conflict.

## Recording state

After writing an artifact, update `roadmap.yaml` in the same turn. Record only;
never gate, approve, or set a function to `accepted`.

| Operation | `roadmap.yaml` effect |
|---|---|
| `discover` | Set `docs.discovery` |
| `draft-prd` | Set `docs.prd` |
| `draft-roadmap` | Set `docs.roadmap`; add new functions as `planned`, and evidence-backed existing implementations as `as-built` during brownfield adoption |
| `amend` | None; a proposal is not canonical truth |

Advance `stage` only when the current request asked to advance it. Leave
`as-built` entries alone unless the request names one.

An `approve-*` operation records the human's approval fields — actor, date, and
evidence — inside the reviewed artifact itself, and changes nothing else. An
approval never starts the next operation.

`amend` creates only `doc/product-amendments/<CR-ID>.md`; canonical product
files stay unchanged. A later explicit `approve-amendment` keeps that proposal
byte-identical and applies only its reviewed changes to the canonical files.
Require the current request to identify a CR-ID; never allocate or guess one.

## Ownership and Default Paths

This skill owns product semantics in:

- discovery notes: `doc/product-discovery-notes.md`;
- product requirements: `doc/general-product-requirement.md`;
- feature roadmap: `doc/feature-roadmap.md`;
- reviewed amendment proposal: `doc/product-amendments/<CR-ID>.md`.

Record these in `roadmap.yaml` under `docs.discovery`, `docs.prd`, and
`docs.roadmap`. An amendment proposal is not a `docs` role; leave it out.

Each canonical root declares `**Artifact bundle**: single` or `split`. A split
root lists every member path in its own registry exactly once. No hash table is
maintained — Git detects member drift. Discovery is always single.

Honor explicit user paths, then canonical paths recorded in `roadmap.yaml`, then
exact defaults.
If several plausible sources remain, ask the user to choose. Update a canonical
artifact instead of creating a competing source of truth.

## Operations

| Operation | Required before execution | Creates or modifies | Stops at |
|---|---|---|---|
| `discover` | Explicit product-discovery request | Discovery notes | Draft, or awaiting review once the discovery frontier is bounded |
| `approve-discovery` | Explicit human approval of the reviewed notes | Approval fields in discovery notes | `Approved for PRD` |
| `draft-prd` | Discovery notes approved for PRD | Product requirements | Awaiting review |
| `approve-prd` | Explicit human approval of the reviewed PRD | PRD status and approval evidence | Approved |
| `draft-roadmap` | PRD approved | Feature roadmap | Awaiting review |
| `approve-roadmap` | Explicit human approval of roadmap boundaries and order | Roadmap status and approval evidence | Approved |
| `amend` | Explicit product change, CR-ID, and affected canonical artifact | Amendment proposal; canonical truth unchanged | Awaiting review |
| `approve-amendment` | Explicit approval of one reviewed amendment and its complete edit set | Applied reviewed edits and approval evidence | Approved |

Every operation stops at its end state. Approval records only the approval the
user explicitly gave and does not begin the next operation.

## Context Discipline

- Read the smallest authoritative slice that answers the current operation.
- During discovery, do not load architecture, feature plans, tasks, or source
  code unless the user supplies them as product evidence.
- For `draft-prd`, use approved discovery notes; do not reread unrelated files.
- For `draft-roadmap`, use the approved PRD and its requirement registry.
  Consult discovery history only when an approved requirement cites unresolved
  rationale.
- For a split PRD, read its index first and only the domain-area files this
  operation needs, always including the cross-cutting area when it constrains
  them. For a split roadmap, read the root control rows first.
- Keep each opened slice at or below 8 KiB and the initial target payload at or
  below 24 KiB. Beyond that, batch by stable ID/domain in fresh workers and
  merge only citations, decisions, and a coverage ledger
  (`| Batch | Stable IDs / paths | Result | Evidence |`). Never approve or claim
  complete coverage while a required batch or resolver result is truncated.
- Do not copy summaries into `roadmap.yaml`. Store product truth once and
  reference it by path and stable ID.

A `full` or `lite` profile changes document depth, not product guarantees.
`lite` still keeps staged approvals, stable IDs, explicit non-goals, coverage,
dependencies, and independent acceptance; prefer shorter single-file artifacts.

## Roadmap sizing fields

`draft-roadmap` records `Feature count`, `Deployable count`, and
`Owning team count` as positive integers, `Datastore count` as a non-negative
integer, and `Regulatory/audit/contractual constraint` as exactly `yes`, `no`,
or `unknown`. `Sizing evidence` contains only stable source anchors.

Recommend `Profile sizing: lite` only when feature count is at most 8,
deployable count is exactly 1, datastore count is at most 1, owning team count
is exactly 1, and the constraint value is `no`. Any unknown or failed condition
means `full`.

The recommendation is written into the roadmap for the human to accept or
override; `roadmap.yaml`'s `profile` field is an intent marker that enforces
nothing. Report a mismatch between the two instead of silently correcting it.

## Conditional Operation Playbooks

Load exactly one playbook after the current request selects its operation:

- `discover`: [discovery playbook](./references/discovery-operation.md);
- `draft-prd` or `draft-roadmap`: [product artifact playbook](./references/product-artifact-operations.md);
- `amend` or `approve-amendment`: [amendment playbook](./references/product-amendment-operation.md).

Approving discovery, a PRD, or a roadmap loads no drafting playbook.

## Validation

Nothing validates these mechanically. Before presenting an artifact, check them
yourself:

- prerequisites and cited approval evidence hold;
- stable IDs are unique and references resolve;
- no product statement prescribes architecture or implementation;
- for a roadmap: complete requirement coverage, single primary ownership,
  acyclic dependencies, explicit MVP/deferred boundaries, allowed horizon/UI
  values, one stable product domain per feature, an independent acceptance
  demonstration per feature, and sizing fields matching the criteria above with
  anchor-only `Sizing evidence`;
- for a PRD, `Product UI structure applicability` is exactly `required` or
  `not_applicable`; the latter cites one approved `PR-###` whose wording rules
  out a global shell, navigation, and shared cross-feature UI pattern, without
  changing any feature's `UI Surface`;
- amendments preserve downstream links, never rewrite acceptance or release
  evidence, and leave canonical product truth untouched in the proposal step.

Report paths, created versus modified files, unresolved decisions, validation
results, the `roadmap.yaml` lines you changed, and allowed next human commands.
Stop without invoking them.
