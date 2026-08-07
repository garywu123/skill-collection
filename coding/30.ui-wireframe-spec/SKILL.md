---
name: ui-wireframe-spec
description: Create or revise low-fidelity product UI structure or feature wireframes from approved requirements and a clarified feature. Use only when the current user explicitly requests this semantic design work; never infer authorization from a roadmap UI Surface value, a recorded stage in roadmap.yaml, or another skill.
---

# UI Wireframe Spec

Produce reviewable layout intent without making visual-style or implementation
decisions. This is a human-authorized design operation, not an automatic bridge
between lifecycle phases.

## Authority and boundaries

- Require explicit authorization in the current user request. Infer `product`
  or `feature` only when the request itself makes the scope unambiguous; never
  infer authorization from repository state.
- One named lifecycle authorization may span turns. A context that reaches a
  human decision point, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any human decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from canonical state; a fork or worker does not grant
  new authorization.
- Never invoke another lifecycle skill, run a later phase, approve an artifact,
  or advance another phase.
- Never write code, tasks, product requirements, roadmap entries, architecture,
  component-library choices, colors, typography, spacing, or animation.
- Treat an approved roadmap `UI Surface` value as a prerequisite and scope
  signal, not as an invocation trigger.

Read `roadmap.yaml` at the repository root first to learn the current stage and
canonical document paths. Stop when it, an approved artifact, and the current
request conflict; do not repair shared state by guessing.

Keep each opened slice at or below 8 KiB and the initial target payload at or
below 24 KiB. Beyond that, batch by stable ID in fresh workers and merge only
screen ownership, citations, decisions, and a coverage ledger
(`| Batch | Stable IDs / paths | Result | Evidence |`). Never claim a complete
product map while a required domain or resolver result is truncated.

## Recording state

After writing an artifact, update `roadmap.yaml` in the same turn. Record only;
never gate, approve, or set a function to `accepted`.

| Scope | `roadmap.yaml` effect |
|---|---|
| `product` | Set `docs.ui` |
| CR-scoped `product` revision | None beyond `docs.ui` if the path changed |
| `feature` | None; wireframes are routed by the function's spec, not by a `docs` role |

Act only when the request explicitly names `product` or `feature`, the scope is
unambiguous, and prerequisites pass. Require an explicit CR-ID or feature ID;
never allocate or guess either. This skill never approves its own output: a
later explicit human approval supplies actor, date, and evidence inside the
reviewed artifact.

## Source contract

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

Every canonical UI root declares `**Artifact bundle**: single` or `split`. A
split product-UI root lists every domain-detail file in its registry exactly
once. No hash table is maintained — Git detects member drift.

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

## Validation

Nothing validates these mechanically. Before reporting, check them yourself:

- each screen and diagram satisfies the fidelity contract;
- every applicable acceptance scenario is reachable through represented screens
  and states;
- states, destructive-action safeguards, controls, branch conditions, and
  terminology trace to approved sources or are marked unresolved;
- no styling, component, framework, or invented product decision appears;
- feature output references its owning feature, roadmap entry, and either the
  approved UI structure or the approved product-UI N/A rationale.

Run repository-provided deterministic validators when available. For a CR-scoped
revision, verify the root registry still names every member that exists.

Report mode, artifact path, screen count, deliberately omitted screens,
unresolved gaps, deviations, validation results, and the next recommended human
action. Stop; do not invoke product design, planning, or any other phase.
