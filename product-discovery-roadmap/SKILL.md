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
- Perform one operation at a time. At every review or approval boundary, report
  the allowed next human commands and stop.
- Use a fresh conversation, fork, or worker for this operation. Reconstruct
  truth from the pointer/index and owning artifacts; do not rely on another
  Skill body, an old pointer, or excerpts inherited across a gate.
- Never invoke another lifecycle skill, Spec Kit command, planning command, or
  implementation workflow.
- Never write code, architecture, feature plans, tasks, wireframes, acceptance
  results, release status, or agent instructions.

When present, read `.specify/flow-state.yaml` first. Use it only to verify the
active scope, current revision, gates, and canonical paths; it does not contain
product truth or grant permission. Query the artifact index next through the
deterministic `resolve` command by ID or path. Never load the complete
`.specify/artifact-index.yaml` into semantic context; full agreement belongs to
the deterministic `validate --check-paths` operation. If state,
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
the candidate artifact, validate the edited file. For a split canonical root,
recompute every member hash after all edits, replace its complete
`## Approved Bundle` table, and verify the table before re-recording the same
role/path at `ready_for_review`; never update only changed-member rows. Use the
revision returned by `record-output` for generic `decide` with the explicit
human actor, date, and decision evidence; it writes an indexed receipt. If no bytes
changed, verify both the existing gate hash and, for a split root, every bundle
member before calling `decide` directly. Generic `decide` handles only
`ready_for_review`; never use it for acceptance or release candidates. An
approval may not start a different operation.

For a change request, `amend` first creates only
`doc/product-amendments/<CR-ID>.md` under role `product_amendment`; approved
canonical product files remain unchanged. On a later explicit
`approve-amendment`, keep the reviewed proposal byte-identical, apply only its
reviewed changes to canonical product files, record approval evidence in those
canonical files/pointer, rebuild and verify every affected split root's complete
bundle table, then re-run `record-output` with `product_amendment` plus every
affected canonical role/path before generic `decide` with actor, date, and
decision evidence. The state command rejects
canonical promotion without that prior reviewed amendment candidate.

## Ownership and Default Paths

This skill owns product semantics in:

- discovery notes: `doc/product-discovery-notes.md`;
- product requirements: `doc/general-product-requirement.md`;
- feature roadmap: `doc/feature-roadmap.md`;
- reviewed amendment proposal: `doc/product-amendments/<CR-ID>.md`.

Register these under fixed state roles `discovery`, `requirements`, and
`roadmap`; register a proposal as `product_amendment`.

Canonical product roots declare exactly one machine-readable field:
`**Artifact bundle**: single` or `**Artifact bundle**: split`. A `single` root
has no `## Approved Bundle` section. A `split` root has that exact heading and a
complete `Path`/`SHA-256` table containing every owned external member exactly
once, excluding the root itself and source artifacts. Member detail files never
repeat the field or table. Registry paths and bundle paths must be identical as
sets. Compute hashes only after member bytes are final, and validate existence,
uniqueness, and current content hashes before every review, approval, or
amendment promotion.

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
- When the roadmap is split, read its root control rows first and only the
  referenced domain-detail files needed by the current operation.
- Keep each opened semantic slice at or below 8 KiB and the initial target
  payload at or below 24 KiB. If complete coverage requires more, process
  stable-ID/domain batches in fresh worker contexts and merge only citations,
  decisions, and a coverage ledger. Never approve or claim complete coverage
  while a required batch or resolver result is truncated.
- Do not copy summaries into the pointer. Store product truth once and reference
  it by path and stable ID.

A `full` or `lite` profile changes document depth, not product guarantees.
`lite` still keeps staged approvals, stable IDs, explicit non-goals, coverage,
dependencies, and independent acceptance; prefer shorter single-file artifacts.

Both roadmap root forms record `Feature count`, `Deployable count`, and `Owning
team count` as positive integers, `Datastore count` as a non-negative integer,
and `Regulatory/audit/contractual constraint` as exactly `yes`, `no`, or
`unknown`.
`Sizing evidence` contains only stable source anchors. Select `lite` only when
feature count is at most 8, deployable count is exactly 1, datastore count is at
most 1, owning team count is exactly 1, and the constraint value is `no`; any
unknown or failed condition requires `full`.

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
  demonstration per feature, and deterministic sizing fields matching the
  Full/Lite criteria with anchor-only `Sizing evidence`;
- for a PRD, require `Product UI structure applicability` to be exactly
  `required` or `not_applicable`; the latter cites one approved `PR-###` whose
  wording explicitly rules out a global shell, navigation, and shared
  cross-feature UI pattern, without changing any feature's `UI Surface`;
- preserve existing downstream links and never rewrite acceptance or release
  evidence when amending; leave canonical product truth untouched in the
  proposal operation;
- verify the `Artifact bundle` value and, for every split root, exact registry
  coverage plus every current member hash;
- set only the current artifact to `Ready for Review`, never `Approved`, unless
  the current request explicitly records that approval.

Report paths, created versus modified files, unresolved decisions, validation
results, the proposed pointer transition, and allowed next human commands. Stop
without invoking them.
