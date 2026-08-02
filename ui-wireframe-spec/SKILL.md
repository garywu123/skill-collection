---
name: ui-wireframe-spec
description: Create or revise low-fidelity product UI structure or feature wireframes from approved requirements and a clarified feature. Use only when the current user explicitly requests this semantic design work; never infer authorization from a roadmap UI Surface value, lifecycle pointer, or another skill.
---

# UI Wireframe Spec

Produce reviewable layout intent without making visual-style or implementation
decisions. This is a human-authorized design operation, not an automatic bridge
between lifecycle phases.

## Authority and boundaries

- Require explicit authorization in the current user request. Infer `product`
  or `feature` only when the request itself makes the scope unambiguous; never
  infer authorization from repository state.
- Use a fresh conversation, fork, or worker for this operation. Reconstruct
  truth from the pointer/index and owning artifacts; do not rely on another
  Skill body, an old pointer, or excerpts inherited across a gate.
- Never invoke another lifecycle skill, run a later phase, approve an artifact,
  or advance another phase.
- Never write code, tasks, product requirements, roadmap entries, architecture,
  component-library choices, colors, typography, spacing, or animation.
- Treat an approved roadmap `UI Surface` value as a prerequisite and scope
  signal, not as an invocation trigger.

Map an already-authorized design operation to deterministic `start` exactly as
follows:

| Operation and scope | `kind` | `work-id` | `stage` |
|---|---|---|---|
| project-scope `product` | `project` | `pointer.project.id` | `product_ui` |
| CR-scoped `product` revision | `change_request` | the explicitly authorized `CR-ID` | `product_ui` |
| `feature` | `feature` | the explicitly authorized roadmap feature ID | `feature_ui` |

These mappings do not grant authority. Run `start` only when the current user
explicitly requests `product` or `feature`, the scope selects exactly one table
row, and prerequisites pass; never infer it from repository state. Require an
explicit CR-ID for a CR-scoped revision and an explicit feature ID for feature
mode; never allocate or guess either. Read the expected revision immediately
before each state-changing command and use the revision returned by the
preceding command; never hard-code or calculate it. The request does not
authorize product planning or any later phase.

## State and source contract

When present, read `.specify/flow-state.yaml` first. Use it only to verify the
active scope, current revision, approvals, and canonical paths. Query the
artifact index next through the deterministic `resolve` command by ID or path.
Never load the complete `.specify/artifact-index.yaml` into semantic context;
full agreement belongs to deterministic `validate --check-paths`. Stop
when state, the resolved index slice, and an approved artifact conflict; do not
repair shared state by guessing.

Keep each opened semantic slice at or below 8 KiB and the initial target payload
at or below 24 KiB. If product/domain coverage requires more, use stable-ID
batches in fresh worker contexts and merge only screen ownership, citations,
decisions, and a coverage ledger. Never claim a complete product map while a
required domain or resolver result is truncated.

| Mode | Required before execution | Read | Creates or modifies |
|---|---|---|---|
| `product` | Explicit request; approved product requirements and roadmap; product has a UI | Applicable product experience constraints and roadmap feature outcomes/UI Surface values | Canonical `doc/ui-structure.md` or user-specified equivalent |
| `feature` | Explicit request; one feature spec exists and is clarified; roadmap UI Surface is not `none`; product UI structure is approved **or** global product UI is explicitly `not applicable` | One roadmap entry, applicable requirement IDs, the feature spec/clarifications, and product UI structure when applicable | Canonical `specs/NNN-feature/wireframes.md` or user-specified equivalent |

In feature mode, a roadmap `UI Surface: none` routes away from wireframing: do
not start `feature_ui`. If `UI Surface` is missing or ambiguous, stop and report
the missing decision. If the product has shared navigation, shell, or UI
patterns but no approved UI structure, report that prerequisite; do not invoke
product mode automatically. A CLI, embedded surface, or isolated terminal view
may instead cite approved product field `Product UI structure applicability:
not_applicable` and its `Product UI applicability evidence` PR anchor stating
that no global shell/navigation/shared pattern exists. That rationale may
replace the product UI structure prerequisite, but it never overrides
`UI Surface: none` or grants feature-mode authority. Never infer the rationale
from code. Update an existing canonical output rather than creating a competing
copy.

Register product output under fixed state role `ui_structure` and feature
output under active role `wireframes`.

Every canonical UI root declares exactly one machine-readable field:
`**Artifact bundle**: single` or `**Artifact bundle**: split`. A single root has
no `## Approved Bundle` section. A split product-UI root has that exact heading
and a complete `Path`/`SHA-256` table containing every owned domain-detail file
exactly once, excluding the root and source artifacts. Detail members never
repeat the field or table. Its domain registry and bundle paths must be
identical as sets.

## Fidelity contract

Draw screens, not individual controls:

- L0: product navigation map, in `product` mode only.
- L1: ASCII skeleton for a new screen/route or materially changed layout.
- L2: control and state tables for each L1 screen.
- L3: Mermaid only for a multi-screen flow with a branch.

Record inputs, dropdowns, inline validation, established confirmations, and
loading/empty/error/offline variants in L2 tables unless they materially change
layout or navigation. Keep each L1 skeleton under 25 lines and use the notation
shown in the selected output template. Read
[fidelity rules](references/fidelity-rules.md) only when a candidate is
borderline, a novel confirmation changes layout, or the feature exceeds the
size limits.

## Workflow

### Product mode

1. Extract only experience constraints that affect navigation, global shell,
   device contexts, terminology, or cross-screen behavior.
2. Read the roadmap as an inventory of feature ID, outcome, product domain,
   dependencies, and `UI Surface`; never open every feature specification.
   Derive screens from outcomes, not data entities, and map each screen to its
   owning feature and requirement IDs.
3. Draft one L0 navigation map and one L1 global-shell skeleton. Do not draw
   feature screens.
4. For a bounded product, use the
   [single UI structure template](assets/ui-structure-template.md). For a large
   or concurrently owned product, use the
   [split root template](assets/ui-structure-index-template.md) plus the
   [domain-detail template](assets/ui-structure-domain-template.md).

For a large roadmap spanning multiple product domains, draft the global shell
and one human-selected domain per round. The root owns device/channel contexts,
global experience constraints, shell/navigation, shared patterns, terminology,
and domain routing. A domain member owns only its navigation branch, screen
inventory, domain-only patterns, and open questions. Do not repeat normative
text across those boundaries. Preserve all already reviewed members in the
complete bundle while working one domain at a time; record unresolved domains
and stop for review rather than loading the entire product into one context.

### Feature mode

1. Apply the fidelity contract to every clarified flow and state. Present the
   candidate screen inventory and qualifying reasons before drawing when scope
   is uncertain or exceeds eight L1 screens.
2. For every qualifying screen, produce L1 then L2. Every specified state must
   appear in the state table; every visible control must appear in the control
   table.
3. Add L3 only for qualifying branching flows and name every edge condition.
4. Reuse the approved shell, terminology, and patterns when applicable. If
   product UI is explicitly N/A, record the cited reason and use only approved
   product terminology. Record deviations and unresolved behavioral gaps;
   never invent missing domain behavior.
5. Use [the feature wireframes template](assets/feature-wireframes-template.md).

Ask at most five decision-changing questions per round. Prefer a recommended
answer with its consequence. Do not ask styling questions.

## Validation and state recording

Before writing `ready_for_review`, verify:

- each screen and diagram satisfies the fidelity contract;
- every applicable acceptance scenario is reachable through represented screens
  and states;
- states, destructive-action safeguards, controls, branch conditions, and
  terminology trace to approved sources or are marked unresolved;
- no styling, component, framework, or invented product decision appears;
- feature output references its owning feature, roadmap entry, and either the
  approved UI structure or the approved product-UI N/A rationale.
- every UI root's `Artifact bundle` value matches its form; for a split root,
  finalize all member bytes, compute every current member hash including
  unchanged members, replace the complete bundle table, and verify exact domain
  registry coverage.

Run repository-provided deterministic validators when available. Then use the
shared lifecycle command, when present, to register the output path/hash in the
artifact index and record `ready_for_review` plus a recommended next human
action. Never edit shared YAML directly or record approval. If no command
exists, leave state unchanged and report the proposed record.

A later explicit generic approval supplies actor, date, and evidence to the
state command, which creates an indexed decision receipt. This Skill never
fills that authority or runs the decision itself.

For a CR-scoped revision, recompute and validate the same complete bundle before
re-registering the root. The lifecycle owner must repeat that validation
immediately before later approval; a changed or missing member invalidates the
reviewed root hash.

Report mode, artifact path, screen count, deliberately omitted screens,
unresolved gaps, deviations, validation results, and the next recommended human
action. Stop; do not invoke product design, planning, or any other phase.
