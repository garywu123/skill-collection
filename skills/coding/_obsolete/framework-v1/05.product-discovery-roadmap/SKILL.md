---
name: product-discovery-roadmap
description: "Use only when the current user request explicitly authorizes one product operation: discover, approve discovery, draft or approve a PRD/roadmap, assess an existing roadmap, propose an amendment, or approve a reviewed amendment. Do not select this skill merely because roadmap.yaml shows a matching stage or a prior phase is complete."
---

# Product Discovery Roadmap

Turn uncertain product intent into reviewed discovery evidence, an approved
product requirements document, and an approved feature roadmap. Keep product
decisions independent of architecture and implementation.

Every artifact stores current product truth at its own altitude. Conversation
history and superseded wording live in Git, not in downstream summaries.

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
| `draft-roadmap` | Set `docs.roadmap` and selected `profile`; add domain-aware functions as `planned`, and evidence-backed existing implementations as `as-built` during brownfield adoption |
| `assess-roadmap` | None; assessment is read-only |
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
- discovery-maintained domain knowledge: `doc/domain/<topic>.md`;
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
| `assess-roadmap` | Existing roadmap | Read-only profile, bundle, domain, and feature-cohesion findings | Assessment reported |
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
- Discovery notes summarize the current understanding; they do not preserve
  interview rounds, question transcripts, rejected alternatives, or a decision
  history. Put substantial reusable vocabulary and process facts in linked
  `doc/domain/` files rather than expanding the notes.
- PRDs and roadmaps never contain decision logs. A PRD does not retain a
  discovery-to-requirement coverage table. A roadmap records requirement
  ownership only from feature to requirement and never repeats the inverse
  mapping.
- Discovery, PRD, and roadmap artifacts do not prescribe or hand off a
  downstream specification workflow. Delivery work links back to the approved
  roadmap when it begins.

A `full` or `lite` profile changes scale, splitting, and necessary domain depth,
not the semantic model or the rule against duplication. Every roadmap is
organized as domains containing independently acceptable features. In a small
project one domain may contain one feature, but the two remain distinct fields.
Both profiles retain staged approvals, stable IDs, feature-to-requirement
ownership, dependencies, and observable acceptance.

## Roadmap sizing fields

`draft-roadmap` records `Feature count`, `Deployable count`, and
`Owning team count` as positive integers, `Datastore count` as a non-negative
integer, and `Regulatory/audit/contractual constraint` as exactly `yes`, `no`,
or `unknown`. `Sizing evidence` contains only stable source anchors.

Select `Profile sizing: lite` only when feature count is at most 8,
deployable count is exactly 1, datastore count is at most 1, owning team count
is exactly 1, and the constraint value is `no`. Any unknown or failed condition
means `full`.

Write the evidence-backed result into the roadmap and record the same profile in
`roadmap.yaml`. A user may explicitly override it only with a rationale recorded
in `Sizing evidence`. `draft-roadmap` also selects `single` or `split`
automatically from the artifact rules. No initial mode decision is required.

Before assigning feature IDs, test each candidate for one independently
acceptable outcome. Split domain-sized candidates into cohesive features during
drafting. During `assess-roadmap`, report over-broad features and a proposed
temporary-label split, but do not edit approved artifacts. Route any approved
roadmap change through `amend <CR-ID>` and `approve-amendment`.

## Conditional Operation Playbooks

Load exactly one playbook after the current request selects its operation:

- `discover`: [discovery playbook](./references/discovery-operation.md);
- `draft-prd`, `draft-roadmap`, or `assess-roadmap`: [product artifact playbook](./references/product-artifact-operations.md);
- `amend` or `approve-amendment`: [amendment playbook](./references/product-amendment-operation.md).

Approving discovery, a PRD, or a roadmap loads no drafting playbook.

## Validation

For a roadmap, run the deterministic ownership and dependency validator against
the canonical PRD file(s) and roadmap:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/Test-ProductArtifacts.ps1 `
  -RequirementsPath doc/general-product-requirement.md `
  -RoadmapPath doc/feature-roadmap.md
```

For a split PRD, pass all requirement-member paths to `-RequirementsPath`.
Before presenting any artifact, also check:

- prerequisites and cited approval evidence hold;
- stable IDs are unique and references resolve;
- no product statement prescribes architecture or implementation;
- for a roadmap: every requirement has exactly one primary owner, every
  `Also Bound By` reference resolves, dependencies resolve without cycles,
  delivery boundaries and UI values are valid, every feature has a stable
  domain key and one cohesive outcome, each feature has observable
  acceptance, and sizing fields match the criteria above with anchor-only
  `Sizing evidence`; perform this check without writing a reverse coverage table;
- for a PRD, `Product UI structure applicability` is exactly `required` or
  `not_applicable`; the latter cites one approved `PR-###` whose wording rules
  out a global shell, navigation, and shared cross-feature UI pattern, without
  changing any feature's `UI Surface`;
- amendments preserve downstream links, never rewrite acceptance or release
  evidence, and leave canonical product truth untouched in the proposal step.

Report paths, created versus modified files, unresolved decisions, validation
results, the `roadmap.yaml` lines you changed, and allowed next human commands.
Stop without invoking them.
