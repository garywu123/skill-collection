# Skill Collection

A human-controlled, spec-driven software-development workflow for coding agents.
The collection emphasizes domain discovery, narrow context, explicit gates, and
evidence over long autonomous chains.

## Start with a worked example

| Guide | Example | Choose it when |
|---|---|---|
| [Spec Driven Flow — Full](spec-driven-flow.md) | Warehouse management system | Multiple domains, deployables, teams, integrations, or material architecture/risk constraints |
| [Spec Driven Flow — Lite](spec-driven-flow-lite.md) | LAN file-transfer CLI | At most eight features, one deployable, at most one datastore, one team, and no regulatory/contractual architecture constraint |

These guides are training, review, and evaluation examples. Do not load either
whole guide into a normal coding turn. Runtime context should contain only the
active Skill, at most one operation reference and only the selected output
variant's minimal template set, the workflow pointer, a small index result, and
bounded targeted artifact/code/evidence slices.

## Operator instructions

- [SPEC Driven Overview](00_instructions/spec-driven-overview.md): understand the roles, order, and boundaries of the whole collection.
- [WMS SPEC Drive Instruction](00_instructions/wms-spec-drive-instruction.md): start an enterprise WMS and deliver one feature at a time.
- [WMS Change Playbook](00_instructions/wms-change-playbook.md): add, change, fix, or migrate an existing WMS repository without losing approved history.
- [Flow State Command Reference](00_instructions/flow-state-command-reference.md): when to use every `flow_state.py` command and its prerequisites.

## Operating model

```text
Human selects one operation
  -> one Skill reads the smallest authoritative context
  -> it writes only its owned output
  -> a deterministic command records paths/hash/candidate state
  -> it reports and stops
  -> human reviews and selects or rejects the next operation
```

- A workflow arrow means prerequisite order, never automatic invocation.
- One named lifecycle authorization may span turns. A context that creates or
  resolves a human gate, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any gate decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from pointer/index and canonical artifacts; a fork or
  worker does not grant new authorization. `guided-tdd-pairing` may keep one
  interactive implementation loop, but it stops before a lifecycle review or
  gate. A fresh worker is only a memory/coverage boundary inside the already
  authorized operation; it cannot select another Skill, stage, gate, or work
  item.
- All eight Skills disable implicit invocation and require explicit
  `$skill-name` authorization. Pointer state and a recommended command do not
  grant permission.
- Skills never invoke other lifecycle Skills or Spec Kit. An authorized Skill
  may call `flow-state/scripts/flow_state.py` for a mechanical state/index
  update; that is a deterministic tool call, not semantic orchestration. Every
  Skill names that one entry point explicitly — deployed skills reach it as
  `<their-skill-dir>/../flow-state/scripts/flow_state.py` — so no Skill has to
  load another Skill to find it.
- An explicit `$skill-name <operation>` request may mechanically `start` only
  that named stage after prerequisites pass. It cannot use the pointer to infer
  or start the recommended next operation.
- `.specify/flow-state.yaml` stores only the active work item, gate, canonical
  paths, small ID/evidence lists, blockers, and human-required next commands.
- `.specify/artifact-index.yaml` is generated from paths, hashes, and stable IDs.
  Its generated `.specify/artifact-index.sha256` sidecar makes manual index edits
  fail closed.
  Use `flow-state resolve`; never open the complete index in semantic model
  context. Full agreement belongs to deterministic `validate --check-paths`.
  `resolve` returns up to 12 occurrences per matched artifact, with a 20-artifact/
  16-KiB output cap, and should be narrowed by ID/path when truncated. Run full
  repository/index agreement only as an explicit validation operation.
- Generic approvals and dedicated feature/release decisions require actor,
  date, and evidence and create content-hashed `.specify/decisions/*.yaml`
  receipts. Dedicated receipts additionally bind reviewed and resulting
  artifact hashes; release results chain to authorization and the external
  execution receipt. The index keeps those decisions discoverable after the
  bounded pointer changes work item.
- Canonical discovery, PRD, roadmap, architecture, and product-UI roots declare
  `single` or `split`; every split root lists a complete member Path/SHA-256
  bundle, and candidate recording or approval rejects stale members. The
  `sync-bundle` command computes and writes that table, so no Skill ever
  transcribes a digest; `record-output --check-only` pre-flights a complex
  transition without writing state or consuming a revision.
- PRD, roadmap, architecture, UI, verification, and acceptance meaning remains
  in the owning artifacts. Never copy their summaries into the pointer.
- Roadmap owns durable product outcomes, horizons, dependencies, and release
  boundaries. It does not duplicate mutable delivery status; pointer plus
  verification/acceptance/release artifacts provide that history.
- Full/Lite confirmation reads structured feature/deployable/datastore/team and
  constraint fields; Lite thresholds and the roadmap's unique F-ID count are
  checked by the state script rather than inferred from prose.
- A pointer is a single-writer worktree/session cursor. Parallel features use
  separate worktrees/cursors or an external tracker; a portfolio view is
  generated from durable evidence, not copied into the roadmap.
- Keep an opened semantic/code/evidence slice at or below 8 KiB and the initial
  target payload for one operation at or below 24 KiB. Larger exhaustive reviews
  use stable-ID/path batches in fresh workers and retain only citations, findings,
  and a coverage ledger; truncation or an uncovered batch prevents a complete or
  passing claim.

For parallel Full delivery, do not merge feature-branch pointer files. Keep one
integration owner for project canonical state, keep each worktree cursor local,
merge durable specs/verification/acceptance artifacts, then rebuild/validate the
index in the integration worktree. The human selects the next active item from
those artifacts or the external tracker. This collection deliberately does not
reconstruct or merge concurrent cursor history; multi-team portfolio status
requires that external tracker/adapter.

## Capability map

| Skill | Explicit operation and owned output | Maximum result before stopping |
|---|---|---|
| [`flow-state`](flow-state/SKILL.md) | Initialize/query/validate pointer and generated index; record deterministic transitions | Candidate state or an explicitly human-decided state; never another Skill |
| [`product-discovery-roadmap`](product-discovery-roadmap/SKILL.md) | `discover`, staged PRD/roadmap drafting and approval, `amend` | One reviewed/approved product artifact operation |
| [`architecture-baseline`](architecture-baseline/SKILL.md) | `full`, `lite`, `recover`, `resolve-spike`, `amend`, `approve` | Reviewed/approved baseline, ADR, or bounded spike result |
| [`bootstrap-agent-guidance`](bootstrap-agent-guidance/SKILL.md) | `create`, `refresh`, `audit` for concise `AGENTS.md` and requested thin adapters | `ready_for_review`; audit is read-only |
| [`ui-wireframe-spec`](ui-wireframe-spec/SKILL.md) | `product` UI structure or one `feature` wireframe | `ready_for_review`; never planning or code |
| [`spec-sync`](spec-sync/SKILL.md) | `pre-implement`, `post-implement`, `change-request` for one feature or explicitly typed implementation item | Feature `ready_for_acceptance`; other kinds `ready_for_review`; blocked; or a proposed route |
| [`guided-tdd-pairing`](guided-tdd-pairing/SKILL.md) | One user-controlled RED/GREEN pairing step | Lifecycle state unchanged |
| [`delivery-gates`](delivery-gates/SKILL.md) | Independent acceptance/readiness review; durable feature decision, release authorization, and release result | Candidate gate, then only the human's explicit recorded result |

Spec Kit remains the feature-local horizontal workflow: specify, clarify,
plan, checklist, tasks, analyze, and implement. It does not replace product,
cross-feature architecture, vertical alignment, or independent acceptance.

Tests, coverage policy, formatting, lint, build, schema validation, and CI are
deterministic commands, hooks, or pipelines—not additional explanatory Skills.
Code and security review are selected by change risk and produce evidence for
the independent gate.

## Lifecycle at a glance

```text
Discovery -> PRD -> Roadmap -> confirm Full/Lite
                     |              |
                     |              +-> Architecture
                     +-----------------> Agent guidance
                     +-----------------> [Product UI]

approved applicable sources
  -> for one work item:
       Spec Kit specify/clarify -> [Feature UI] -> plan/tasks/analyze
       -> spec-sync pre -> implementation -> deterministic/risk checks
       -> spec-sync post -> delivery-gates acceptance -> human accept/reject
  -> delivery-gates readiness -> human authorizes reviewed release
  -> separately authorized release tooling -> human records terminal result
```

This is a partial order, not one mandatory chain. Agent guidance requires the
approved PRD and roadmap and includes architecture only when architecture is
approved; Product UI likewise starts from approved product/roadmap truth. The
recommended low-rework order is architecture before guidance, but neither
guidance nor Product UI is authority for the other.

Brackets are conditional, not optional guesses. `UI Surface: none` skips UI
artifacts with a reason; applicable safety, validation, acceptance, and release
evidence never disappear in Lite.

Follow-ups remain outside the current feature unless explicitly routed:

- behavior defect -> typed `bug` work item with regression evidence and the
  same pre/post human review contract (feature acceptance is not implied);
- implementation debt -> `doc/tech-debt/TD-###-short-title.md` with impact,
  owner, repayment trigger, and repayment evidence;
- future product idea -> roadmap `Candidate` via a human-authorized product amendment;
- cross-feature technical debt -> independent debt/trigger evidence, then a
  human-authorized architecture amendment before baseline/ADR changes;
- uncertain cross-feature technical question -> approved `SPK-###`, then a
  time-boxed `spike_result`; any architecture consequence still uses a CR/amendment.

## Repository structure

```text
skill-collection/
├── README.md
├── spec-driven-flow.md
├── spec-driven-flow-lite.md
├── flow-state/                   # pointer/index Skill + deterministic script
├── product-discovery-roadmap/    # discovery, PRD, roadmap templates
├── architecture-baseline/        # Full/Lite baseline and ADR templates
├── bootstrap-agent-guidance/     # guidance templates and validator
├── ui-wireframe-spec/            # product/feature UI templates and fidelity rules
├── spec-sync/                    # vertical alignment and change-routing references
├── guided-tdd-pairing/           # optional learning/pairing mode
├── delivery-gates/               # acceptance/release review templates
└── scripts/                      # collection deployment helpers
```

Each Skill keeps its always-needed contract in `SKILL.md`; templates,
references, and scripts are loaded only when their trigger condition applies.
