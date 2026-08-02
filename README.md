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
active Skill, the workflow pointer, a small index result, and the targeted
artifact/code/evidence slices.

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
- All eight Skills disable implicit invocation and require explicit
  `$skill-name` authorization. Pointer state and a recommended command do not
  grant permission.
- Skills never invoke other lifecycle Skills or Spec Kit. An authorized Skill
  may call `flow-state/scripts/flow_state.py` for a mechanical state/index
  update; that is a deterministic tool call, not semantic orchestration.
- An explicit `$skill-name <operation>` request may mechanically `start` only
  that named stage after prerequisites pass. It cannot use the pointer to infer
  or start the recommended next operation.
- `.specify/flow-state.yaml` stores only the active work item, gate, canonical
  paths, small ID/evidence lists, blockers, and human-required next commands.
- `.specify/artifact-index.yaml` is generated from paths, hashes, and stable IDs.
  Use `flow-state resolve` rather than opening a large index in model context;
  it returns compact anchors with a 20-result/24-KiB cap and should be narrowed
  by ID/path when truncated. Run full index verification only as an explicit
  validation operation.
- PRD, roadmap, architecture, UI, verification, and acceptance meaning remains
  in the owning artifacts. Never copy their summaries into the pointer.
- Roadmap owns durable product outcomes, horizons, dependencies, and release
  boundaries. It does not duplicate mutable delivery status; pointer plus
  verification/acceptance/release artifacts provide that history.
- A pointer is a single-writer worktree/session cursor. Parallel features use
  separate worktrees/cursors or an external tracker; a portfolio view is
  generated from durable evidence, not copied into the roadmap.

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
| [`architecture-baseline`](architecture-baseline/SKILL.md) | `full`, `lite`, `recover`, `amend`, `approve` | Reviewed or explicitly approved baseline/ADR |
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
  -> Architecture -> Agent guidance -> [Product UI]
  -> for one work item:
       Spec Kit specify/clarify -> [Feature UI] -> plan/tasks/analyze
       -> spec-sync pre -> implementation -> deterministic/risk checks
       -> spec-sync post -> delivery-gates acceptance -> human accept/reject
  -> delivery-gates readiness -> human authorizes reviewed release
  -> separately authorized release tooling -> human records terminal result
```

Brackets are conditional, not optional guesses. `UI Surface: none` skips UI
artifacts with a reason; applicable safety, validation, acceptance, and release
evidence never disappear in Lite.

Follow-ups remain outside the current feature unless explicitly routed:

- behavior defect -> typed `bug` work item with regression evidence and the
  same pre/post human review contract (feature acceptance is not implied);
- implementation debt -> `doc/tech-debt/TD-###-short-title.md` with impact,
  owner, repayment trigger, and repayment evidence;
- future product idea -> roadmap `Candidate` via a human-authorized product amendment;
- cross-feature technical debt -> architecture deferred decision or proposed ADR;
- uncertain technical question -> time-boxed `spike` evidence owned by the
  affected feature plan or architecture decision; never production output.

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
