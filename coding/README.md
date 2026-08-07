# Skill Collection

A human-controlled, spec-driven development workflow for coding agents. It
emphasizes domain discovery, narrow context, and evidence over long autonomous
chains.

## Start here

[SPEC Driven Lite 总览](00_instructions/spec-drive-lite/spec-driven-lite-overview.md)
explains the control model and the capability map. Then pick the mode that
matches your situation:

| Mode | Use when | Guide |
|---|---|---|
| New project | Starting from business discovery | [新项目](00_instructions/spec-drive-lite/wms-new-project.md) |
| Change request | Project running, changing an existing function | [变更请求](00_instructions/spec-drive-lite/wms-change-request.md) |
| Existing repository | Adopting the flow into a codebase that never used it | [已有仓库接入](00_instructions/spec-drive-lite/wms-existing-repo.md) |

All three use the same WMS example, so they can be read against each other.
They are operator guides — do not load a whole guide into a normal coding turn.

## Operating model

```text
Human speaks one operation
  -> one Skill reads the smallest authoritative context
  -> it writes only its owned artifacts
  -> it updates that artifact's line in roadmap.yaml
  -> it reports and stops
  -> human reviews and speaks the next operation
```

- **State transitions are spoken, not enforced.** `roadmap.yaml` records where
  the project is; it never gates, approves, or decides what comes next.
- A workflow arrow means prerequisite order, never automatic invocation.
- The human states intent in natural language and explicitly names the
  `$skill-name`. A recommended next step is navigation, not permission.
- Skills never invoke other Skills or Spec Kit.
- One state file per repository: `roadmap.yaml` at the root, holding stage,
  document routes, and one line per function. Requirements, design rationale,
  and history live in the routed documents and in Git — never in that file.
- Project Map owns the `roadmap.yaml` schema, initialization, refresh, and
  audit. Each authorized operation updates only the route or function entry it
  directly changed, then reconciles that entry before its final response.
- `stage` is descriptive project context. It never authorizes a Skill or gates
  an operation.
- Delivery has no gate Skill. Each function carries a `checklist.md` written
  alongside its spec and verified **in a fresh conversation**. The context that
  implemented a function does not tick its own boxes.
- Production release governance is project policy outside this Lite lifecycle.
  Add scoped build, migration, rollback, operations, and execution evidence
  when the repository's risk requires it; function acceptance is not release
  authorization.
- Keep an opened semantic/code/evidence slice at or below 8 KiB and the initial
  payload for one operation at or below 24 KiB. Larger reviews use batches and
  retain only citations, findings, and a coverage ledger; truncation or an
  uncovered batch prevents a passing claim.
- `guided-tdd-pairing` may keep one interactive implementation loop, but it
  stops before any review.

## Capability map

| Skill | Explicit operations and owned output |
|---|---|
| [`05.product-discovery-roadmap`](05.product-discovery-roadmap/SKILL.md) | `discover`, staged PRD/roadmap drafting, `amend` |
| [`10.architecture-baseline`](10.architecture-baseline/SKILL.md) | `full`, `lite`, `recover`, `resolve-spike`, `amend` |
| [`20.project-map`](20.project-map/SKILL.md) | `init`, `refresh`, `audit` for `roadmap.yaml`, `AGENTS.md`, thin adapters |
| [`30.ui-wireframe-spec`](30.ui-wireframe-spec/SKILL.md) | `product` UI structure or one `feature` wireframe |
| [`spec-sync`](spec-sync/SKILL.md) | `pre-implement`, `post-implement`, `change-request` |
| [`guided-tdd-pairing`](guided-tdd-pairing/SKILL.md) | One user-controlled RED/GREEN pairing step |

Spec Kit remains the feature-local horizontal workflow: specify, clarify, plan,
tasks, analyze, implement. It does not replace product definition, cross-function
architecture, or vertical alignment.

Tests, coverage, formatting, lint, build, schema validation, and CI are
deterministic commands, hooks, or pipelines — not additional Skills.

## Lifecycle at a glance

```text
Discovery -> PRD -> Roadmap
                     |
                     +-> Architecture
                     +-> Project map (AGENTS.md)
                     +-> [Product UI]

for one function:
  Spec Kit specify/clarify (+ checklist) -> [Feature UI] -> plan/tasks
  -> spec-sync pre-implement -> implementation -> deterministic/risk checks
  -> spec-sync post-implement -> FRESH CONVERSATION: verify checklist -> accepted
```

A partial order, not one mandatory chain. Brackets are conditional, not optional
guesses: `UI Surface: none` skips UI artifacts with a stated reason.

Follow-ups stay outside the current function unless explicitly routed:

- behavior defect -> `bug` work item with regression evidence;
- implementation debt -> `doc/tech-debt/TD-###-short-title.md` with impact,
  owner, and repayment trigger;
- future product idea -> roadmap candidate via a product amendment;
- cross-function technical question -> a time-boxed spike, then an architecture
  amendment for any consequence.

## Repository structure

```text
skill-collection/
├── scripts/                        # Deploy-Skills.ps1 and deploy paths
└── coding/
    ├── README.md
    ├── 00_instructions/spec-drive-lite/   # overview + the three mode guides
    ├── 05.product-discovery-roadmap/      # discovery, PRD, roadmap templates
    ├── 10.architecture-baseline/          # baseline and ADR templates
    ├── 20.project-map/                    # roadmap.yaml, AGENTS.md, checklist templates
    ├── 30.ui-wireframe-spec/              # product/feature UI templates
    ├── spec-sync/                         # alignment and change-routing references
    ├── guided-tdd-pairing/                # optional learning/pairing mode
    └── _obsolete/                         # retired flow-state and delivery-gates
```

Each Skill keeps its always-needed contract in `SKILL.md`; templates,
references, and scripts load only when their trigger applies.

## `_obsolete/`

`flow-state` and `delivery-gates`, plus the old full/lite flow guides, enforced
state transitions through `flow_state.py` and bound approvals with SHA-256
receipts. They were retired because that machinery defends against multi-writer
tampering, which a single-writer project does not have, while its cost was real:
two whole Skills, 5,500 lines of Python and tests, 1,080 lines of worked
examples, and roughly a sixth of every surviving `SKILL.md` spent on revision
and hash protocol rather than on the work.

Git carries history and drift detection, `roadmap.yaml` carries state, the
per-function checklist carries the delivery bar, and a fresh conversation
carries independence. Take a piece back from `_obsolete/` when a specific
failure calls for it — not in advance.
