# WMS SPEC Drive Instruction

本文件是企业级 WMS 从零开始时的日常操作说明。它不是自动化脚本：每一行都是一次
独立的人类授权。AI 完成当前操作、登记候选产物后必须停止；由你审阅并选择下一行。

完整的状态、哈希和命令细节见 [Flow State Command Reference](flow-state-command-reference.md)。

## 0. 开始前的决定

使用 `full` profile。企业 WMS 通常有多个领域、仓储/库存一致性约束、外部集成、权限与审计，
不应按 Lite 处理。确定首个可交付能力，例如 `F001 收货入库`；不要一开始同时实现所有领域。

## 1. 建立 WMS 的已批准事实

| 顺序 | 你明确请求的操作 | AI 读取和完成什么 | 产物 | 你在切换前要做什么 |
|---|---|---|---|---|
| 1 | `python flow-state/scripts/flow_state.py --root . init --project-id WMS --profile full` | 初始化项目 cursor 和派生索引 | `.specify/flow-state.yaml`、artifact index | 运行 `status`，确认项目 ID/profile 正确。 |
| 2 | `$product-discovery-roadmap discover` | 访谈并界定业务问题：仓库、货主、收货、上架、库存、分配、拣货、发运、盘点、权限、审计、ERP/WCS 集成 | `doc/wms-discovery-notes.md` | 审阅未决问题、假设和范围；确认是否足以写 PRD。 |
| 3 | `$product-discovery-roadmap approve-discovery` | 只记录你的审批证据 | discovery 审批回执 | 明确认可业务发现结论；未决的业务选择不能默认为已决定。 |
| 4 | `$product-discovery-roadmap draft-prd` | 将已批准发现写成稳定的业务需求、约束、非目标和需求 ID | `doc/wms-product-requirements.md` | 审阅每项业务规则；尤其确认库存不变量、审计、权限和失败行为。 |
| 5 | `$product-discovery-roadmap approve-prd` | 只记录你的 PRD 审批 | PRD 审批回执 | 确认 PRD 描述的是“要什么”，没有替你决定技术实现。 |
| 6 | `$product-discovery-roadmap draft-roadmap` | 将 PRD 拆为可独立验收的 Feature，写依赖、领域和交付顺序 | `doc/wms-feature-roadmap.md` | 审阅边界和顺序；确认每个 Feature 都有独立验收演示。 |
| 7 | `$product-discovery-roadmap approve-roadmap`，随后 `confirm-profile --profile full` | 记录 roadmap 审批并确认 Full sizing | roadmap 审批回执；profile 已确认 | 确认 feature 数、部署单元、数据存储、团队及约束的 sizing evidence。 |
| 8 | `$architecture-baseline full` | 定义跨 Feature 的领域边界、库存一致性、并发、事务、事件、集成、权限、审计和 ADR | `doc/architecture-baseline.md`、`doc/adr/` | 审阅不可违反的技术约束与待解决的 spike；批准基线。 |
| 9 | `$bootstrap-agent-guidance create` | 从已批准 PRD、roadmap、架构生成薄的 AI 路由规则 | `AGENTS.md` | 审阅并批准；它应引用事实，不能复制整份 WMS 文档。 |
| 10 | `$ui-wireframe-spec product`（仅当存在全局导航/共享 UI） | 定义产品级导航、共享页面结构和一致性规则 | `doc/ui-structure.md` | 审阅；如果没有共享 UI，PRD 中必须有明确 N/A 理由。 |

一个合理的早期 roadmap 示例是：`F001 收货` → `F002 上架` → `F003 库存查询与调整`
→ `F004 库存预留与分配` → `F005 拣货` → `F006 发运`。具体顺序以批准后的 roadmap 为准。

## 2. 交付一个 WMS Feature

以下以 `F001 收货入库` 为例。每个 Feature 独立重复此循环；不得用 F001 的验收替代其他
Feature 的验收。

| 顺序 | 你明确请求的操作 | AI 产物/结果 | 你在切换前要确认 |
|---|---|---|---|
| 1 | Spec Kit `specify F001` | `specs/001-receiving/spec.md`：用户场景、业务规则、负向场景、`SC-###` 验收场景 | 需求覆盖收货、重复扫描、数量差异、不可用状态、审计等真实业务结果。 |
| 2 | Spec Kit `clarify F001` | 澄清写回 Feature spec | 所有会影响行为或验收的歧义都有明确决定。 |
| 3 | `$ui-wireframe-spec feature F001`（仅 UI Surface 适用时） | `wireframes.md` | 线框图与 spec 场景一致；无 UI 时记录 `not_applicable` 理由。 |
| 4 | Spec Kit `plan`、`tasks`、`analyze` | `plan.md`、`tasks.md`、checklist | 计划遵守已批准架构，任务包含测试、迁移和运维工作。 |
| 5 | `$spec-sync pre-implement F001 feature` | `pre-implementation-review.md`，Pass 或 Blocked | 若 Pass，仍须单独人工批准该审查；若 Blocked，先修复不一致。 |
| 6 | 实施授权 | 代码、自动化测试、必要的迁移/运维证据 | 只在 pre-implementation artifact 已批准且哈希未变化时开始实现。 |
| 7 | `$spec-sync post-implement F001 feature` | `verification.md`，进入 `ready_for_acceptance` 或 Blocked | 每个需求/场景都有真实实现和测试证据；绿色 build 本身不够。 |
| 8 | `$delivery-gates accept-feature F001` | `acceptance.md`，状态为 ready/conditional/not_ready | 由非实现者审阅；确认场景、测试、CI 和适用风险证据。 |
| 9 | `$delivery-gates record-feature-decision F001 Accepted` | 接受决定和不可变回执 | 只有 acceptance 为 ready/conditional 且无 blocker 时才接受。 |

实现后发现的新问题不能悄悄塞回 F001：行为缺陷走 `bug`，技术债走 `maintenance`，未来想法回到
roadmap，跨 Feature 技术决策走 architecture amendment。

## 3. 发布

当 release scope 内每个 Feature 都有自己的 `Accepted` 回执后：

1. 你请求 `$delivery-gates release REL-YYYY.MM；scope F001,F002,...`。
2. AI 输出 release readiness；你审阅 build provenance、CI、迁移、回滚、可观测性、运维和安全证据。
3. 你请求 `$delivery-gates authorize-release REL-YYYY.MM`；这只记录授权，不发布。
4. 你另行授权项目的 CI/CD 或发布工具实际执行。
5. 工具产出结构化执行 receipt 后，你请求 `$delivery-gates record-release-result ...`。

## 操作者的三个固定动作

每个阶段结束时只做一件事：

1. 审阅本阶段产物和缺失证据；
2. 明确批准、拒绝，或要求修改；
3. 在下一条消息中明确选择下一项操作。

不要把“推荐的下一步”当作 AI 自动获得的授权。
