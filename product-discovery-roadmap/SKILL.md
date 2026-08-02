---
name: product-discovery-roadmap
description: "Use only when the current user request explicitly authorizes one product operation: explore, approve discovery, draft or approve a PRD/roadmap, propose an amendment, or approve a reviewed amendment. Do not select this skill merely because a pointer recommends it or a prior phase is complete."
---

# Product Discovery Roadmap

Turn uncertain product intent into reviewed discovery evidence, an approved
product requirements document, and an approved feature roadmap. Keep product
decisions independent of architecture and implementation.

## Lifecycle Contract

- Require the current user request to authorize one named operation. A pointer,
  recommended next action, completed prerequisite, or prior approval is not
  authorization.
- Perform one operation at a time. At every review or approval boundary, report
  the allowed next human commands and stop.
- Never invoke another lifecycle skill, Spec Kit command, planning command, or
  implementation workflow.
- Never write code, architecture, feature plans, tasks, wireframes, acceptance
  results, release status, or agent instructions.

When present, read `.specify/flow-state.yaml` first. Use it only to verify the
active scope, current revision, gates, and canonical paths; it does not contain
product truth or grant permission. Query the artifact index next through the
deterministic `resolve` command by ID or path. Open
`.specify/artifact-index.yaml` in full only when it is clearly small. If state,
the resolved index slice, and an approved artifact disagree, stop and report
the conflict.

Do not hand-edit shared state or index YAML. After validating an output, use the
repository's deterministic state/index command when one is configured;
otherwise report the proposed state transition for the human to record.

Map an already-authorized non-approval operation to deterministic `start`
exactly as follows:

| Operation | `kind` | `work-id` | `stage` |
|---|---|---|---|
| `discover` | `project` | `pointer.project.id` | `discovery` |
| `draft-prd` | `project` | `pointer.project.id` | `prd` |
| `draft-roadmap` | `project` | `pointer.project.id` | `roadmap` |
| `amend` | `change_request` | the explicitly authorized `CR-ID` | `change_request` |

These mappings do not grant authority. Run `start` only when the current user
explicitly names that operation and its prerequisites pass; never infer it from
the pointer or a recommendation. For `amend`, require the current request to
identify the CR-ID; never allocate or guess one. Read the expected revision
immediately before each state-changing command and use the revision returned by
the preceding command; never hard-code or calculate it.

An `approve-*` operation never runs `start`. Require a pending
`ready_for_review` gate for the named role and path. If approval fields change
the candidate artifact, validate the edited file, then run `record-output`
again with the same role, path, and active stage at `ready_for_review` so the
gate stores the reviewed hash. Use the revision returned by that command for
the generic `decide`. If no bytes changed, verify the existing gate hash and
call `decide` directly. Generic `decide` handles only `ready_for_review`; never
use it for acceptance or release candidates. An approval may not start a
different operation.

For a change request, `amend` first creates only
`doc/product-amendments/<CR-ID>.md` under role `product_amendment`; approved
canonical product files remain unchanged. On a later explicit
`approve-amendment`, keep the reviewed proposal byte-identical, apply only its
reviewed changes to canonical product files, record approval evidence in those
canonical files/pointer, then re-run
`record-output` with `product_amendment` plus every affected canonical role/path
before generic `decide`. The state command rejects canonical promotion without
that prior reviewed amendment candidate.

## Ownership and Default Paths

This skill owns product semantics in:

- discovery notes: `doc/product-discovery-notes.md`;
- product requirements: `doc/general-product-requirement.md`;
- feature roadmap: `doc/feature-roadmap.md`;
- reviewed amendment proposal: `doc/product-amendments/<CR-ID>.md`.

Register these under fixed state roles `discovery`, `requirements`, and
`roadmap`; register a proposal as `product_amendment`.

Honor explicit user paths, then indexed canonical paths, then exact defaults.
If several plausible sources remain, ask the user to choose. Update a canonical
artifact instead of creating a competing source of truth.

## Operations

| Operation | Required before execution | Reads | Creates or modifies | End state |
|---|---|---|---|---|
| `discover` | Explicit product-discovery request | Existing notes and only relevant product sources | Discovery notes | `in_progress`, or `ready_for_review` when the discovery frontier is bounded; then stop |
| `approve-discovery` | Explicit human approval of the reviewed notes | Discovery notes | Approval fields in discovery notes | Artifact `Approved for PRD`; pointer `approved`; stop |
| `draft-prd` | Discovery notes approved for PRD | Approved notes | Product requirements | `ready_for_review`; stop |
| `approve-prd` | Explicit human approval of the reviewed PRD | PRD and cited notes as needed | PRD status and approval evidence | `approved`; stop |
| `draft-roadmap` | PRD approved | Approved PRD | Feature roadmap | `ready_for_review`; stop |
| `approve-roadmap` | Explicit human approval of roadmap boundaries and order | Roadmap and PRD coverage registry | Roadmap status and approval evidence | `approved`; stop |
| `amend` | Explicit product change, CR-ID, and affected canonical artifact | Only affected approved product artifacts and cited evidence | Product amendment proposal; canonical truth is unchanged | `ready_for_review`; stop |
| `approve-amendment` | Explicit approval of one reviewed amendment and its complete edit set | Amendment/hash and only named canonical artifacts | Apply reviewed edits and record approval evidence | Affected canonical roles `approved`; stop |

Approval operations record only the approval the user explicitly gave. They do
not begin the next operation in the same turn.

## Context Discipline

- Read the smallest authoritative slice that can answer the current operation.
- During discovery, do not load architecture, feature plans, tasks, or source
  code unless the user explicitly supplies them as product evidence.
- For `draft-prd`, use approved discovery notes; do not reread unrelated
  repository files.
- For `draft-roadmap`, use the approved PRD and its requirement registry. Consult
  discovery history only when an approved requirement cites unresolved
  rationale.
- When the PRD is split, read its index first and only the domain-area files
  needed by the current operation. Always include the single cross-cutting area
  when it constrains those domains.
- Do not copy summaries into the pointer. Store product truth once and reference
  it by path and stable ID.

A `full` or `lite` profile changes document depth, not product guarantees.
`lite` still keeps staged approvals, stable IDs, explicit non-goals, coverage,
dependencies, and independent acceptance; prefer shorter single-file artifacts.

## Conditional Operation Playbooks

Load exactly one playbook after the current request selects its operation:

- `discover`: [discovery playbook](./references/discovery-operation.md);
- `draft-prd` or `draft-roadmap`: [product artifact playbook](./references/product-artifact-operations.md);
- `amend` or `approve-amendment`: [amendment playbook](./references/product-amendment-operation.md).

Approval of discovery, PRD, or roadmap uses the approval/hash contract already
in this file and does not load a drafting playbook. Never load all playbooks in
one operation.

## Validation

Before presenting an artifact:

- verify prerequisites and cited approval evidence;
- ensure stable IDs are unique and references resolve;
- ensure no product statement prescribes architecture or implementation;
- for a roadmap, verify complete requirement coverage, single primary ownership,
  acyclic dependencies, explicit MVP/deferred boundaries, allowed horizon/UI
  values, one stable product domain per feature, an independent acceptance
  demonstration per feature, and concrete `Profile sizing`/`Sizing evidence`
  fields matching the Full/Lite criteria;
- preserve existing downstream links and never rewrite acceptance or release
  evidence when amending; leave canonical product truth untouched in the
  proposal operation;
- set only the current artifact to `Ready for Review`, never `Approved`, unless
  the current request explicitly records that approval.

Report paths, created versus modified files, unresolved decisions, validation
results, the proposed pointer transition, and allowed next human commands. Stop
without invoking them.
