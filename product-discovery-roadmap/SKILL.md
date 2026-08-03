---
name: product-discovery-roadmap
description: "Use only when the current user request explicitly authorizes one product operation: discover, approve discovery, draft or approve a PRD/roadmap, propose an amendment, or approve a reviewed amendment. Do not select this skill merely because a pointer recommends it or a prior phase is complete."
---

# Product Discovery Roadmap

Turn uncertain product intent into reviewed discovery evidence, an approved
product requirements document, and an approved feature roadmap. Keep product
decisions independent of architecture and implementation.

## Lifecycle Contract

- Require the current user request to authorize one named operation. A pointer,
  recommended next action, completed prerequisite, or prior approval is not
  authorization.
- One named lifecycle authorization may span turns. A context that creates or
  resolves a human gate, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any gate decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from canonical state; a fork or worker does not grant
  new authorization.
- Never invoke another lifecycle skill, Spec Kit command, planning command, or
  implementation workflow.
- Never write code, architecture, feature plans, tasks, wireframes, acceptance
  results, release status, or agent instructions.

Read `.specify/flow-state.yaml` first to verify active scope, revision, gates,
and canonical paths; it holds no product truth and grants no permission. Query
the index only through `resolve --id` or `resolve --path`. If state, the
resolved slice, and an approved artifact disagree, stop and report the conflict.

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
  --kind project --work-id <project-id> --stage prd

sync-bundle --artifact doc/general-product-requirement.md \
  --member <domain-path> [--member ...] --role requirements

record-output --expect-revision <revision-returned-by-start> \
  --stage prd --artifact requirements=doc/general-product-requirement.md \
  --next "product-discovery-roadmap approve-prd"

decide --expect-revision <revision-returned-by-record-output> \
  --decision approved --decided-by <actor> --decision-date YYYY-MM-DD \
  --decision-evidence <statement-or-reference>
```

`sync-bundle` computes and writes every member hash; never type a SHA-256 by
hand. Add `--check-only` to `record-output` to validate a complex transition
before writing.

| Operation | `kind` | `work-id` | `stage` |
|---|---|---|---|
| `discover` | `project` | `pointer.project.id` | `discovery` |
| `draft-prd` | `project` | `pointer.project.id` | `prd` |
| `draft-roadmap` | `project` | `pointer.project.id` | `roadmap` |
| `amend` | `change_request` | the authorized `CR-ID` | `change_request` |

Require the current request to identify a CR-ID; never allocate or guess one.

An `approve-*` operation never runs `start`. Record the human's approval fields
in the reviewed artifact, re-run `sync-bundle` for a split root, `record-output`
the same role/path, then `decide` with actor, date, and evidence. If no bytes
changed, call `decide` directly. Generic `decide` resolves only
`ready_for_review`, and an approval may not start a different operation.

`amend` creates only `doc/product-amendments/<CR-ID>.md` under role
`product_amendment`; canonical product files stay unchanged. A later explicit
`approve-amendment` keeps that proposal byte-identical, applies only its
reviewed changes to canonical files, then re-records `product_amendment` plus
every affected canonical role before `decide`.

## Ownership and Default Paths

This skill owns product semantics in:

- discovery notes: `doc/product-discovery-notes.md`;
- product requirements: `doc/general-product-requirement.md`;
- feature roadmap: `doc/feature-roadmap.md`;
- reviewed amendment proposal: `doc/product-amendments/<CR-ID>.md`.

Register these under fixed roles `discovery`, `requirements`, and `roadmap`;
register a proposal as `product_amendment`.

Each canonical root declares `**Artifact bundle**: single` or `split`. A split
root also owns a `## Approved Bundle` table covering every owned member exactly
once; `sync-bundle` writes it. Discovery is always single.

Honor explicit user paths, then indexed canonical paths, then exact defaults.
If several plausible sources remain, ask the user to choose. Update a canonical
artifact instead of creating a competing source of truth.

## Operations

| Operation | Required before execution | Creates or modifies | End state |
|---|---|---|---|
| `discover` | Explicit product-discovery request | Discovery notes | `in_progress`, or `ready_for_review` once the discovery frontier is bounded |
| `approve-discovery` | Explicit human approval of the reviewed notes | Approval fields in discovery notes | `Approved for PRD`; pointer `approved` |
| `draft-prd` | Discovery notes approved for PRD | Product requirements | `ready_for_review` |
| `approve-prd` | Explicit human approval of the reviewed PRD | PRD status and approval evidence | `approved` |
| `draft-roadmap` | PRD approved | Feature roadmap | `ready_for_review` |
| `approve-roadmap` | Explicit human approval of roadmap boundaries and order | Roadmap status and approval evidence | `approved` |
| `amend` | Explicit product change, CR-ID, and affected canonical artifact | Amendment proposal; canonical truth unchanged | `ready_for_review` |
| `approve-amendment` | Explicit approval of one reviewed amendment and its complete edit set | Applied reviewed edits and approval evidence | Affected canonical roles `approved` |

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
- Do not copy summaries into the pointer. Store product truth once and reference
  it by path and stable ID.

A `full` or `lite` profile changes document depth, not product guarantees.
`lite` still keeps staged approvals, stable IDs, explicit non-goals, coverage,
dependencies, and independent acceptance; prefer shorter single-file artifacts.

## Roadmap sizing fields

`draft-roadmap` must write these fields, because `confirm-profile` later
validates them and cannot infer them from prose. Both root forms record
`Feature count`, `Deployable count`, and `Owning team count` as positive
integers, `Datastore count` as a non-negative integer, and
`Regulatory/audit/contractual constraint` as exactly `yes`, `no`, or `unknown`.
`Sizing evidence` contains only stable source anchors.

Record `Profile sizing: lite` only when feature count is at most 8, deployable
count is exactly 1, datastore count is at most 1, owning team count is exactly
1, and the constraint value is `no`. Any unknown or failed condition requires
`full`.

## Conditional Operation Playbooks

Load exactly one playbook after the current request selects its operation:

- `discover`: [discovery playbook](./references/discovery-operation.md);
- `draft-prd` or `draft-roadmap`: [product artifact playbook](./references/product-artifact-operations.md);
- `amend` or `approve-amendment`: [amendment playbook](./references/product-amendment-operation.md).

Approving discovery, a PRD, or a roadmap loads no drafting playbook.

## Validation

The state command fails closed on stage/role/status validity, bundle coverage,
and hash freshness; read its error instead of pre-checking those rules. Before
presenting an artifact, verify the judgments it cannot make:

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
results, the proposed pointer transition, and allowed next human commands. Stop
without invoking them.
