# Coding Skill Collection

一套由人类逐步授权、以 domain + feature 为统一产品模型、以证据完成验收的开发流程。

## 场景指南

| 场景 | 指南 |
|---|---|
| 新建简化库存软件 | [10-small-inventory-new-project.md](00_instructions/10-small-inventory-new-project.md) |
| 新建复杂 WMS | [20-complex-wms-new-project.md](00_instructions/20-complex-wms-new-project.md) |
| Feature 太宽，需要重评 Roadmap | [30-roadmap-reassessment.md](00_instructions/30-roadmap-reassessment.md) |
| 小库存系统演进为 WMS | [40-inventory-to-wms-evolution.md](00_instructions/40-inventory-to-wms-evolution.md) |
| Change Request | [50-change-request.md](00_instructions/50-change-request.md) |
| 已有仓库接入流程 | [60-existing-repository-adoption.md](00_instructions/60-existing-repository-adoption.md) |

指南中的箭头只表示先后依赖，不授权 AI 自动调用下一项 Skill。每次由人类明确授权一个 operation；该 Skill 写自己的产物、更新自己改变的 `roadmap.yaml` 字段、报告并停止。

## 统一模型

- 所有项目的 Feature Roadmap 都使用 `domain + feature`。Domain 是业务知识/职责边界；feature 是可独立验收的结果。小项目中两者可能一一对应，但不合并字段。
- Product Roadmap 的 `draft-roadmap` 自动选择 `lite/full` 与 `single/split`，并在分配 F-ID 前拆开 domain-sized 候选项。
- Architecture 的 `create` 和 `recover` 自动选择 Lite/Full；显式 `lite` 或 `full` 只用于有理由的 override。
- Feature 交付默认走 compact：`implementation-plan.md + checklist.md`。项目很大并不自动要求 Spec Kit。
- 只有 cohesive feature 仍存在无法安全压缩的行为模型时，才建议 detailed/Spec Kit 例外。
- 如果 planning 时发现目标本身像 domain，`feature-implementation-plan` 不写文件；它输出 Roadmap Reassessment Handoff，由人类另行调用 Product amendment。

## Capability map

| Skill | Operations / owned output |
|---|---|
| [`05.product-discovery-roadmap`](05.product-discovery-roadmap/SKILL.md) | `discover`, PRD/Roadmap draft and approval, `assess-roadmap`, `amend` |
| [`10.architecture-baseline`](10.architecture-baseline/SKILL.md) | `create`, `assess`, `recover`, explicit `lite/full`, spikes and amendments |
| [`20.project-map`](20.project-map/SKILL.md) | `init`, `refresh`, `audit` for `roadmap.yaml`, `AGENTS.md`, adapters |
| [`30.feature-implementation-plan`](30.feature-implementation-plan/SKILL.md) | `assess`, `plan`, `audit` for one approved feature |
| [`40.ui-wireframe-spec`](40.ui-wireframe-spec/SKILL.md) | Product UI structure or one feature's wireframes |
| [`50.ui-prototype`](50.ui-prototype/SKILL.md) | Executable fake-data UI prototype for one product and selected features |
| [`spec-sync`](spec-sync/SKILL.md) | `pre-implement`, `post-implement`, `change-request` |
| [`guided-tdd-pairing`](guided-tdd-pairing/SKILL.md) | Optional user-controlled RED/GREEN pairing |
| [`skill-authoring`](skill-authoring/SKILL.md) | Create, review, update, or simplify a reusable Skill |

## Feature lifecycle

```text
approved roadmap feature
  -> feature-implementation-plan (assess first)
       -> reassess: stop, hand off to product roadmap amendment
       -> compact: implementation-plan.md + checklist.md
       -> detailed exception: human explicitly starts the detailed workflow
  -> [feature UI when UI Surface requires it]
  -> [optional executable fake-data UI prototype]
  -> spec-sync pre-implement
  -> TDD implementation
  -> deterministic and risk-specific checks
  -> spec-sync post-implement (write evidence; status verifying)
  -> fresh conversation verifies checklist
  -> human marks accepted and checks the roadmap feature complete
```

`implementation-plan.md` owns component/class/type design, key functions, vertical slices, dependencies, and planned tests. `checklist.md` owns acceptance gates and actual evidence. Product meaning stays in PRD/Roadmap; cross-feature technical rules stay in Architecture.

## Repository structure

```text
coding/
├── 00_instructions/               # six scenario guides
├── 05.product-discovery-roadmap/  # discovery, PRD, domain-aware roadmap
├── 10.architecture-baseline/      # adaptive Lite/Full baseline and ADRs
├── 20.project-map/                # roadmap.yaml and AGENTS.md routing
├── 40.ui-wireframe-spec/          # product and feature UI artifacts
├── 50.ui-prototype/               # executable fake-data UI prototype
├── 30.feature-implementation-plan/ # compact plan/checklist templates
├── spec-sync/                     # alignment, evidence, change routing
├── guided-tdd-pairing/            # optional interactive implementation
└── _obsolete/                     # retired workflow machinery
```

Tests, lint, build, schema validation, migration rehearsal, security review, and CI remain deterministic commands or project policy, not extra lifecycle Skills.
