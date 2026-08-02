# Spec Driven Flow（Full）：WMS 完整示例

这是一份**人类可读的使用样本**：用仓库管理系统（WMS）演示怎样组合本仓库的
八个 Skill、Spec Kit 和确定性工程检查。它仅用于 training/evaluation，不是运行时
contract，也不应被整个塞进一次编码会话。

实际执行时，Agent 只读取：

1. `.specify/flow-state.yaml`；
2. 通过 `flow-state resolve` 找到的 index 小切片（只有可证明很小时才打开整个 index）；
3. 当前操作明确需要的少量章节、代码和证据。

大型项目使用 Full，小项目使用
[Lite 示例](spec-driven-flow-lite.md)。两者的质量保证、人工闸门和独立验收相同；
Full 只增加分析深度、拆分文档和风险证据，不增加自动化权限。

## 1. 不可破坏的执行规则

- 人类是生命周期主控。每个 lifecycle operation 都必须由当前消息明确选择。
- 八个 Skill 均关闭 implicit invocation；示例使用 `$skill-name` 显式选择。
- 下文箭头只表示**前置条件**，不表示自动调用。一个阶段完成后，Agent 报告并停止。
- Skill 不调用 Skill，也不调用 Spec Kit。它只能调用已配置的确定性脚本，记录本次
  已获授权操作产生的路径、哈希和候选状态。
- `next.recommended` 是导航，不是授权；`auto_invoke` 永远为 `false`。
- `ready_for_review`、`ready_for_acceptance`、`ready_for_release` 都是候选状态。
  Generic `decide` 只把 `ready_for_review` 明确决定为 `approved`/`rejected`；
  feature acceptance、release authorization 与 release result 分别由其专用的
  人类授权 operation 持久化，不能借 generic `decide` 越级产生。
- Pointer 只存工作项、阶段、闸门、路径、ID、证据指针和 blocker；产品、架构、
  UI 或验收语义只存在其 owning artifact 中。
- 任何缺失证据都标为 `missing`、`not_run` 或有理由的
  `not_applicable`，不得由 Agent 补写“看起来应该通过”的结论。

统一的单步节奏是：

```text
人类选择一个操作
  -> Agent 读取最小上下文并只执行该操作
  -> 输出候选 artifact
  -> 确定性脚本登记状态与 index
  -> Agent 报告并停止
  -> 人类审阅、批准/拒绝，或选择另一个操作
```

## 2. 能力边界

| 能力 | 负责什么 | 拥有的主要输出 | 不负责什么 |
|---|---|---|---|
| [`flow-state`](flow-state/SKILL.md) | 小型 pointer、派生 index、revision-safe 状态转换 | `.specify/flow-state.yaml`、`.specify/artifact-index.yaml` | 领域真相、编排 Skill |
| [`product-discovery-roadmap`](product-discovery-roadmap/SKILL.md) | Discovery、PRD、Roadmap 及产品变更 | `doc/*discovery*`、`doc/*requirements*`、`doc/*roadmap*` | 架构、spec、实现、验收 |
| [`architecture-baseline`](architecture-baseline/SKILL.md) | 跨 feature 决策、边界、ADR | `doc/architecture-baseline.md`、`doc/adr/` | 单 feature 设计与代码 |
| [`bootstrap-agent-guidance`](bootstrap-agent-guidance/SKILL.md) | 把已批准真相编译为简洁路由规则 | `AGENTS.md`，必要时薄适配器 | 复制或覆盖领域文档 |
| [`ui-wireframe-spec`](ui-wireframe-spec/SKILL.md) | Product UI 结构、Feature 低保真 wireframe | `doc/ui-structure.md`、`specs/.../wireframes.md` | 视觉风格、组件与实现 |
| Spec Kit | 一个工作项内的 specify、clarify、plan、tasks 与实现组织 | `spec.md`、`plan.md`、`tasks.md` 等 | 产品/跨 feature 真相 |
| [`spec-sync`](spec-sync/SKILL.md) | 单一 feature/typed implementation item 纵向对齐、实现证据、变更路由 | `pre-implementation-review.md`、`verification.md`、可选 CR | 代码审查、接受或发布 |
| [`guided-tdd-pairing`](guided-tdd-pairing/SKILL.md) | 用户自己写实现时的小步 TDD 协作 | 用户明确分配的测试/代码 | 生命周期推进 |
| [`delivery-gates`](delivery-gates/SKILL.md) | 独立 acceptance/release review，并持久记录人类明确决定/授权/结果 | `acceptance.md`、release readiness | 修代码、自行决定、部署 |

测试、coverage policy、lint/build、CI 和格式转换是确定性命令、hook 或 pipeline；
它们产生证据，不应包装成充满解释文字的新 Skill。Code review 与 security review
按变更风险选用独立 reviewer，也不是生命周期的自动下一步。

## 3. State、Index 与工作项类型

下文用：

```text
python flow-state/scripts/flow_state.py --root . <operation> [options]
```

命令不熟悉时先运行对应的 `--help`。所有写操作都带
`--expect-revision N`，过期 revision 必须停止，不能覆盖。

### 3.1 初始化与状态操作卡

| 操作/明确命令 | 执行前 | 最小读取 | 创建 | 修改 | 最大结束状态 | 人类停止点/下一步 |
|---|---|---|---|---|---|---|
| `init --project-id WMS --profile full` | 人类明确要求初始化；pointer 不存在 | 无 | pointer、index | 无 | profile 为 `provisional` | 查看 `status`，再明确选择 discovery |
| `start --expect-revision 0 --kind project --work-id WMS --stage discovery` | 人类选择 project discovery | pointer | 无 | pointer | `in_progress` | 明确调用 discovery Skill |
| `status` / `validate --check-paths` | 状态或校验请求 | pointer；validate 时检查路径 | 无 | 无 | 不变 | 修正冲突，或选择一个允许操作 |
| `record-output --expect-revision N --stage <stage> --artifact key=path --next "<prompt>"` | 当前 Skill 已获授权且输出已验证 | pointer、输出路径 | 无 | pointer；自动重建 index | 候选状态、pending gate | Skill 报告并停止，等人类审阅 |
| `block --expect-revision N --artifact key=path --blocker "<fact>"` | 当前已授权操作发现确定 blocker，且没有 pending gate | pointer、blocker 证据 | 无 | pointer/index；登记 blocker artifact | `blocked` | 报告解除 blocker 所需的人类动作并停 |
| `decide --expect-revision N --decision approved\|rejected` | 当前 gate 为 `ready_for_review`，且当前消息明确批准或拒绝 | pointer、候选 artifact/证据及 gate hashes | 无 | pointer | `approved` 或 `rejected` | 人类另起命令选择后续操作；不得用于 acceptance/release |
| `record-feature-decision ...` | 当前消息给出明确决定、actor/date/evidence；acceptance hash 未变；`Accepted` 还要求 review status 为 `ready`/`conditional` 且无 unresolved blocker | pointer、acceptance | 无 | 脚本只替换四个决定字段；pointer/index | `accepted` 或 `rejected` | 不改 review findings；停 |
| `authorize-release ...` | readiness review status 为 `ready`/`conditional`、无 unresolved blocker；当前消息明确授权固定 scope | pointer、readiness hash | 无 | 脚本只替换四个授权字段；pointer/index | `release_authorized` | 不运行 release tooling；停 |
| `record-release-result ... --execution-evidence <receipt.yaml>` | 外部 tooling 已另行授权并终止；结构化 receipt 匹配 ID/result；当前消息确认 | pointer、authorized readiness、receipt | 无 | 脚本 hash receipt 并只替换四个执行字段；pointer/index | `released` 或 `rejected` | 只有 succeeded 且有 artifact SHA 可 released；停 |
| `confirm-profile --expect-revision N --profile full` | Roadmap 已批准且其 `Profile sizing: full` / concrete `Sizing evidence` 已复核 | pointer、Roadmap sizing 字段 | 无 | pointer | profile `confirmed` | 再选择 architecture mode |
| `rebuild-index` | 非 canonical indexed artifact 已变化；approved canonical hash 未漂移 | pointer integrity、受索引目录元数据 | index（若不存在） | index | 状态不变 | 可执行 validate/resolve；canonical 漂移必须走 amendment |
| `resolve --id F001` | 需要定位一个稳定 ID | pointer integrity、派生 index structure、命中 artifact | 无 | 无 | 状态不变 | 只打开返回的 compact path/line/heading |

`record-output` 通常由当前已获授权的 Skill 机械执行；它没有选择下一个 Skill 的
权限。`decide` 只有在当前人类消息明确表达决定时才能运行。
状态机只允许 generic `decide` 处理 `ready_for_review`。`accepted` 必须来自
`record-feature-decision`，`release_authorized` 必须来自 `authorize-release`，
`released` 必须来自 `record-release-result`；各专用 operation 还要校验对应 role、
artifact hash 与证据。
人类直接请求 `$skill-name <operation>` 时，该请求也允许此 Skill 在前置条件通过后，
机械执行该 operation 对应的 `start`；无需人类再输入一条重复命令，但绝不能借此
start 推荐的下一 operation。Approval operation 不 start，而是更新 owning artifact 后
解决当前 pending gate。

### 3.2 Pointer 样例

下面是 F001 已完成纵向证据登记、等待独立验收时的状态。它没有复制任何领域摘要：

```yaml
schema_version: 1
revision: 24
project:
  id: WMS
  profile: full
  profile_status: confirmed
active_work:
  kind: feature
  id: F001
  stage: post_implement
  status: ready_for_acceptance
human_gate:
  name: approve_post_implement
  status: pending
  owner: human
  artifact_roles:
    - verification
  artifact_hashes:
    verification: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
canonical:
  discovery: doc/wms-discovery-notes.md
  requirements: doc/wms-product-requirements.md
  roadmap: doc/wms-feature-roadmap.md
  architecture: doc/architecture-baseline.md
  agent_guidance: AGENTS.md
  ui_structure: doc/ui-structure.md
  artifact_index: .specify/artifact-index.yaml
canonical_status:
  discovery: approved
  requirements: approved
  roadmap: approved
  architecture: approved
  agent_guidance: approved
  ui_structure: approved
canonical_hashes:
  discovery: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  requirements: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  roadmap: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
  architecture: dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
  agent_guidance: eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
  ui_structure: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
active_artifacts:
  - role: plan
    path: specs/001-receiving/plan.md
    status: approved
    sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
  - role: pre_implementation
    path: specs/001-receiving/pre-implementation-review.md
    status: approved
    sha256: dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
  - role: requirements_checklist
    path: specs/001-receiving/checklists/requirements.md
    status: approved
    sha256: eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
  - role: spec
    path: specs/001-receiving/spec.md
    status: approved
    sha256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  - role: tasks
    path: specs/001-receiving/tasks.md
    status: approved
    sha256: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
  - role: verification
    path: specs/001-receiving/verification.md
    status: ready_for_acceptance
    sha256: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  - role: wireframes
    path: specs/001-receiving/wireframes.md
    status: approved
    sha256: '1111111111111111111111111111111111111111111111111111111111111111'
context_ids:
  - F001
  - PR-001
  - PR-100
next:
  allowed:
    - command: $delivery-gates accept-feature F001
      requires_human: true
  recommended: $delivery-gates accept-feature F001
  auto_invoke: false
evidence:
  - path: specs/001-receiving/verification.md
    sha256: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
blockers: []
last_transition:
  revision: 23
  stage: post_implement
  status: ready_for_acceptance
  operation: record-output
```

`.specify/artifact-index.yaml` 是可重建的路径、哈希与稳定 ID 列表。它不是人工
维护的目录，也不存总结。大型 index 不应完整加载；优先使用
`resolve --id PR-001` 或 `resolve --id F001`。
`active_artifacts` 只保留当前 work item，硬上限为 24；context IDs、evidence、
blockers 与 next actions 也有小型上限，超出时应把细节留在 owning artifact，pointer
只保留路径。

### 3.3 不同工作项使用不同 spec

| `kind` | 需要的最小规范/证据 | 仍然不能省略 |
|---|---|---|
| `project` | PRD、Roadmap、architecture/guidance 基线 | 人工批准与来源追踪 |
| `feature` | 用户场景、acceptance、plan/tasks | pre/post sync、独立 acceptance |
| `bug` | 可复现步骤、期望/实际、regression test | 影响范围、验证与显式 human review |
| `maintenance` | 变更边界、兼容性与回退 | 测试、审查、证据 |
| `spike` | 一个可回答问题、timebox、discardable output | 结论证据；不能把 spike 当生产实现 |
| `migration` | 数据不变量、dry run、rollback/recovery | 安全、兼容与发布闸门 |
| `security` | threat/abuse case、修复边界、验证方法 | 独立 security evidence |
| `change_request` | 原始请求、最高影响层、受影响 ID | 人工路由，不自动修改真相 |
| `release` | 明确 scope、artifact provenance、gate evidence | 人工 release 决定与实际执行授权 |

Full 不意味着所有工作项都写同样长的 spec；它意味着按风险选对 spec 类型，同时
保留同样的可追溯性、验证和人类闸门。
本仓库的专用 `accept-feature` / `record-feature-decision` 只接受 `kind: feature`；
`bug`/`maintenance`/`migration`/`security` 使用 `$spec-sync pre-implement <ID> <kind>`
与对应 post operation，最后通过 generic `ready_for_review -> approved/rejected`；
`spike` 只产出 time-boxed evidence 并回到 owning feature/architecture decision。
不要为了复用命令把其他类型伪装成 feature；若组织要求独立的非 feature acceptance
语义，再新增窄而明确的 gate operation。

对 `bug`/`maintenance`/`migration`/`security`，调用 `pre-implement` 前仍必须完成与
该 work item 同 ID、同 kind 的两个人工 gate：先在 `specify` stage 登记并批准 role
`spec`；再在 `plan` stage 登记并一起批准 roles `plan`、`requirements_checklist`、
`tasks`。只有这四个 role 的记录 hash 仍匹配且状态均为 `approved`，才可由人类另行
选择 `$spec-sync pre-implement <ID> <kind>`。非 feature 只是最后不走 feature
acceptance，并不省略 spec/plan/tasks/checklist。

## 4. WMS 总路径

WMS 示例假设：手持设备收货/上架/拣货、经理桌面处理例外、ERP 集成、离线操作和
库存审计会影响多个 feature，因此使用 Full。

```text
人类选 discover -> Discovery 候选 -> 人类批准
人类选 draft-prd -> PRD 候选 -> 人类批准
人类选 draft-roadmap -> Roadmap 候选 -> 人类批准并确认 Full
人类选 architecture full -> Baseline/ADR 候选 -> 人类批准
人类选 guidance create -> AGENTS 候选 -> 人类批准
人类选 UI product -> UI structure 候选 -> 人类批准
对每个 feature：
  人类 start -> specify -> clarify -> [feature wireframe] -> plan
  -> checklist -> tasks -> analyze -> pre-sync review -> 人类批准 -> exact implementation start -> implementation
  -> deterministic/risk gates -> post-sync -> independent acceptance
最后：release readiness review -> authorize-release -> 人类另行授权实际 release automation
  -> record-release-result -> released
```

每个 `->` 都只是“左侧经人工确认后，右侧才允许被人类选择”。

## 5. Product Discovery、PRD 与 Roadmap

WMS 使用自定义 canonical paths：

- `doc/wms-discovery-notes.md`
- `doc/wms-product-requirements.md`
- `doc/wms-feature-roadmap.md`

一次用户消息只选择下表一行。

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$product-discovery-roadmap discover WMS；写入 doc/wms-discovery-notes.md` | project/discovery 已 start | pointer/index；已有 notes；用户给出的产品证据 | notes（首次） | notes 的访谈轮次、决定与 frontier | `Ready for Review` | 报告未决问题并停；人类审阅 |
| `$product-discovery-roadmap approve-discovery；我批准 D-001..D-008` | notes 已 review；当前消息是明确批准 | pointer/index；notes 的决定、假设和 frontier | 无 | notes approval evidence；随后同 role/path `record-output` 刷新 hash，再 generic `decide` | `Approved for PRD` / pointer `approved` | 停；人类另行选择 draft-prd |
| `$product-discovery-roadmap draft-prd；输出 doc/wms-product-requirements.md` | Discovery 已批准 | pointer/index；approved notes | PRD（首次） | PRD（续写时） | `Ready for Review` | 停；人类按 PR ID 审阅 |
| `$product-discovery-roadmap approve-prd；我批准 PR-001..PR-118 与 non-goals` | PRD Ready for Review | pointer/index；PRD；仅在引用时看 notes | 无 | PRD status/批准证据；同 role/path re-record 新 hash，再 generic `decide` | `approved` | 停；人类另行选择 draft-roadmap |
| `$product-discovery-roadmap draft-roadmap；输出 doc/wms-feature-roadmap.md` | PRD 已批准 | pointer/index；PRD registry 与相关 requirement sections | Roadmap root/domain files（首次） | Roadmap（续写时） | `Ready for Review` | 停；人类检查 coverage、domain、依赖、horizon、UI Surface 与 profile sizing evidence |
| `$product-discovery-roadmap approve-roadmap；批准 F001..F012 的边界、顺序与 Profile sizing: full` | Roadmap Ready for Review | pointer/index；Roadmap；PRD coverage registry | 无 | Roadmap status/批准证据；同 role/path re-record 新 hash，再 generic `decide` | `approved` | 停；人类运行 confirm-profile |

这个示例可形成：

- `F001 Receiving`：owns `PR-001..PR-012`，`Product Domain: inbound`，`UI Surface: new screens`；
- `F002 Put-away`：依赖 F001；
- `F003 Inventory ledger`：为后续拣货提供库存真相；
- `F004 Picking`：依赖库存与位置；
- 其余 capability 继续用稳定 ID 分解，而不是塞入一个“大 WMS feature”。

Roadmap 的 `Profile sizing: full`，并用 `Sizing evidence` 记录 12 个 feature、多个
deployable/datastore/team 以及审计/集成约束。若 roadmap 超过约 12 个 feature 或 300 行，
root 只保留 domain registry、dependency/order、horizon/release boundary、coverage 与 sizing；
feature 详情按 domain 拆分，运行时只 resolve 当前 F-ID 的 domain 文件。

Roadmap 保存持久的产品承诺、边界、依赖与 acceptance 定义；pointer 保存当前
work/stage/gate。Roadmap 不保存可变 delivery checkbox 或状态；历史 verification、
acceptance 与 release 记录通过 feature ID 在 index 中解析，避免两份状态漂移。

Roadmap 批准后，人类复核 Full/Lite sizing，并运行：

```text
python flow-state/scripts/flow_state.py --root . confirm-profile --expect-revision N --profile full
```

## 6. Architecture、Agent Guidance 与 Product UI

### 6.1 Full architecture

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$architecture-baseline full；为 WMS 建立跨 feature baseline` | PRD/Roadmap 已批准；Full 已确认 | pointer/index；PRD registry/technical drivers；Roadmap summary/dependencies；constitution；相关 accepted ADR | baseline、必要的 proposed ADR | 已存在的 review-state baseline | `ready_for_review` | 报告 alternatives、deferred decisions、spikes 后停 |
| `$architecture-baseline approve；我批准 baseline 和 ADR-0001..0004` | 指定 artifacts 已 review；明确人类批准 | pointer/index；reviewed baseline/ADR；validation evidence | 无 | status/approval evidence；任何字节变化后以完整同 role/path set re-record 新 hash，再 generic `decide` | `approved` | 停；人类另行选择 guidance |

Discovery history、所有 feature specs、tasks 和源码默认都不读。WMS 的跨 feature
离线同步、库存一致性、ERP 边界、audit 与认证策略属于 baseline；某个收货页面内的
类、函数和局部库属于 F001 plan。

### 6.2 Agent guidance

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$bootstrap-agent-guidance create；只生成根 AGENTS.md` | PRD/Roadmap/architecture 已批准 | pointer/index；这些 artifacts 的 routing/constraints；现有 guidance；manifest、CI/test config 与代表文件用于验证命令 | `AGENTS.md` | 存在时仅更新已过时 guidance | `ready_for_review` | validator 后停；人类审阅再用 flow-state decide |

`AGENTS.md` 应指向 PRD、Roadmap、baseline 和 active spec，不复制它们。示例不
要求 `CLAUDE.md` 或 Copilot adapter；只有这些 consumer 真正在用时，人类才显式
要求薄适配器。

### 6.3 Product UI structure

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$ui-wireframe-spec product；为 WMS 手持端与经理端生成 doc/ui-structure.md` | PRD/Roadmap 已批准；产品确有 UI | pointer/index；product experience constraints；Roadmap 的 feature outcome/domain/dependency/UI Surface | `doc/ui-structure.md` | canonical 文件已存在时更新 | `ready_for_review` | 只画 L0 + global shell；停等人类批准 |

大型 Roadmap 不应一次读入：先画 global shell，再由人类每轮选择一个 domain。
Product mode 不画 F001 具体 screen。

## 7. F001 Receiving 的单 Feature 交付

先由人类选择工作项：

```text
python flow-state/scripts/flow_state.py --root . start --expect-revision N --kind feature --work-id F001 --stage specify
```

### 7.1 Spec Kit：水平一致性

这些是人类逐个选择的外部命令，不是任何 Skill 自动触发的 pipeline。

| 命令/明确输入 | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `/speckit.specify F001 Receiving；只覆盖 Roadmap F001` | F001 Committed；active work=F001 | pointer；`resolve --id F001`；F001 owns/applicable PR sections | `specs/001-receiving/spec.md` | 无 | feature spec draft | 停；人类审阅并选择 clarify |
| `/speckit.clarify 001-receiving` | spec 存在 | active spec；其中 unresolved sections；必要的 owning PR anchors | clarify record/section（按项目模板） | spec 的 clarification | clarified spec | 停；人类决定是否需要 feature UI |
| `/speckit.plan 001-receiving` | spec 已批准；feature wireframe 已批准，或 approved Roadmap 的 `UI Surface: none` 是持久 N/A；baseline 已批准 | approved spec；适用 AC/ADR；approved wireframe 或 Roadmap N/A entry；AGENTS 中已验证约束 | `plan.md`；必要时 research/data-model/contracts | 仅这些 feature-local artifacts | reviewable plan | 停；人类审阅 |
| `/speckit.checklist 001-receiving requirements` | spec 已批准且可审查 | approved spec、clarifications 与 acceptance scenarios | `checklists/requirements.md`（固定 role `requirements_checklist`） | 无 | checklist evidence | 停；人类处理缺口，不自动运行 tasks |
| `/speckit.tasks 001-receiving` | spec/plan 已 review；requirements checklist 无 blocker | reviewed spec、reviewed plan、`requirements_checklist` | `tasks.md` | 无 | ordered tasks | 停；人类审阅任务边界，不自动运行 analyze |
| `/speckit.analyze 001-receiving` | spec/plan/tasks 都存在 | exact `spec.md`、`plan.md`、`tasks.md` 与 applicable constitution rules | response/report | 无 | findings only | 停；有 blocker 时由人类选择返回哪个 owner |

Spec Kit 的 analyze 检查 feature 内部横向一致性；它不代替跨层
`spec-sync pre-implement`。

Spec Kit 本身不拥有共享状态；本例在 bundle 边界机械登记：

| Bundle checkpoint | 机械状态动作 | 候选态与人工停止点 |
|---|---|---|
| clarify 完成 | `record-output ... --stage specify --artifact spec=specs/001-receiving/spec.md` | `ready_for_review`；人类批准后才可选 UI/plan |
| 人类选择 plan | `python flow-state/scripts/flow_state.py --root . start --expect-revision N --kind feature --work-id F001 --stage plan` | `in_progress`；只授权 plan bundle |
| analyze 无 blocker | `record-output` 登记 `plan`、`requirements_checklist`、`tasks` 与各自精确路径 | `ready_for_review`；generic `decide` 批准后才可选 pre-sync |
| pre-sync Pass | `record-output ... --stage pre_implement --artifact pre_implementation=specs/001-receiving/pre-implementation-review.md` | `ready_for_review`；停等人类 generic `decide` |
| 人类批准 pre-sync review | `python flow-state/scripts/flow_state.py --root . decide --expect-revision N --decision approved` | `approved`；只批准 role `pre_implementation`，然后停 |
| 人类另行选择 implement | `python flow-state/scripts/flow_state.py --root . start --expect-revision N --kind feature --work-id F001 --stage implementation` | `in_progress`；只授权实现范围，然后再明确运行 `/speckit.implement 001-receiving` |

Feature wireframe 的 `start`、role `wireframes` 和 candidate 由当前已获授权的
`$ui-wireframe-spec feature` 按共享契约登记；它在 `ready_for_review` 停止。只有后续
当前消息明确批准/拒绝时，才由 `flow-state decide` 解决该 gate，UI Skill 自己不记录
人工决定。

### 7.2 Feature wireframe

F001 为 `new screens`，因此在人类明确选择后执行：

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$ui-wireframe-spec feature；为 F001/001-receiving 生成 wireframes.md` | spec 已批准且 clarified；F001 UI Surface 非 none；UI structure 已批准（无全局 UI 的产品可改用已批准 N/A rationale） | pointer/index；F001 entry；适用 PR IDs；approved spec/clarifications；适用的 UI structure/N/A 来源 | `specs/001-receiving/wireframes.md` | canonical 文件存在时更新 | `ready_for_review` | 画必要 L1/L2、分支才画 L3；停等人类批准 |

若 approved Roadmap 的 `UI Surface: none`，该 entry 本身就是持久 N/A 来源；不新增
wireframe artifact 或 state role。Skill 不得从 `none` 自动改成 UI，也不得自动运行
product mode。

### 7.3 Pre-implement vertical review

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$spec-sync pre-implement F001 feature` | approved spec/plan/tasks 存在；wireframe 已批准或 approved Roadmap N/A；Roadmap dependencies 已 accepted，或 approved Roadmap 明确记录 parallel scope/owner/risk | pointer/index；F001 entry；仅被引用的 PR、AC/ADR、UI sections；spec/plan/tasks；`requirements_checklist` | `specs/001-receiving/pre-implementation-review.md` | 既有同名 review；Pass 时以 role `pre_implementation` 登记 | Blocking 时 `blocked`；Pass 时 `ready_for_review` | 报 Blocking/Advisory/Skipped；Blocking 就停，Pass 则 `record-output` 后停等 generic `decide` |

Skipped 不是 pass。若 plan 与 `AC-004` 冲突，人类可要求修改 feature plan；若
baseline 本身不再适用，则必须另起 `architecture-baseline amend`，不能由
`spec-sync` 修改。依赖型 feature（例如 Roadmap 中的 F004）必须让每个 prerequisite
已 `accepted`，或 approved Roadmap（必要时经 product amendment）明确记录 parallel scope、owner 与风险处置；仅有计划
或口头假设不能通过 dependency check。

### 7.4 Implementation 与 optional Guided TDD

| 操作/示例 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `/speckit.implement 001-receiving` 或“实现 F001 tasks.md 中 T-001” | role `pre_implementation` 已由 generic `decide` 批准；exact implementation `start` 已完成；实现已由人类授权 | pointer/index；当前 task；最小 spec/plan section；目标代码/测试 | task 所需代码/测试 | 仅当前 feature scope 与任务记录 | implementation complete，未接受 | 每个 bounded batch 报结果；不推进 acceptance |
| `$guided-tdd-pairing；我写 core logic，你写 failing test` | 已授权同一 implementation；用户明确要 pairing | pointer/index；当前 task；一个 behavior；目标代码/测试 | 仅双方约定文件 | 同左 | 一个 red/green/refactor step | Agent 给一个 hint 后停，等用户写代码 |

Guided TDD 是协作方式，不是必经阶段。它不读取整个 Roadmap，不更新 pointer，
也不会因为 focused test 通过就宣称 feature 完成。

### 7.5 确定性检查与风险审查

所有命令必须来自已验证的 `AGENTS.md`/CI 配置，不能在示例里臆造技术栈命令。

| 检查/明确 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| “运行 AGENTS.md 的 F001 targeted tests 和 full relevant tests” | 当前实现 batch 完成 | verified command、目标 tests | test result/log | 无语义 artifact | pass/fail evidence | fail 则人类授权修复 |
| “执行项目 coverage policy，不自行提高/降低阈值” | tests 可运行 | coverage config、changed paths | coverage report | 无 | policy pass/fail/N/A | 保存证据路径 |
| “运行 lint/build；提交 CI 并记录 run ID” | local checks 通过 | manifest、CI config | build/lint/CI evidence | 无 | pass/fail | 不把绿灯当 acceptance |
| “独立 code review F001 diff” | diff 稳定 | F001 spec/constraints、diff、target tests | review findings | 无 | reviewed/not_ready | blocker 返回人工选择的实现任务 |
| “按风险决定并执行 security review” | auth、权限、外部输入、secret、数据或依赖风险适用 | threat/abuse cases、相关 diff/config/tests | security findings/evidence | 无 | pass/fail/N/A with reason | blocker 形成 security/bug work item |

Code review 默认适用于非平凡生产变更。Security review 的深度按风险：扫描器输入、
授权、库存审计、ERP 边界或依赖变化通常适用；纯文案变化可以有理由地标 N/A。

### 7.6 Post-implement 与独立 acceptance

| 操作/明确命令 | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `$spec-sync post-implement F001 feature` | approved、hash-matching `pre_implementation` 仍属于 F001；实现已 converge；tasks/checks 与证据路径齐全 | pointer/index；spec/plan/tasks；命名测试/CI/review 证据；相关 code/test anchors | `specs/001-receiving/verification.md` | 既有 verification；以 role `verification` 机械登记 pointer/index | `ready_for_acceptance` | 不改 Roadmap、不接受；停 |
| `$delivery-gates accept-feature F001` | ready_for_acceptance；独立 reviewer；明确授权 | pointer/index；approved scenarios/constraints/wireframe；diff；verification 与所有适用 gate evidence | `specs/001-receiving/acceptance.md` | 无领域/代码修改；以 role `acceptance` 机械登记候选态 | 仍为 `ready_for_acceptance`，decision ready/conditional/not_ready | 停等人类决定 |
| `$delivery-gates record-feature-decision F001 Accepted；decider/date/evidence 如当前消息` | 人类已审阅 acceptance，并在当前消息明确接受 F001；review status 为 `ready`/`conditional` 且无 unresolved blocker | pointer、acceptance artifact/hash 与 blocker | 无 | 确定性命令只替换四个决定字段并更新 pointer/index | `accepted` | 人类选择下一个 feature 或 release scope |

`delivery-gates` 评估用户可见 scenario 与负面路径，而不是重复确认 build 绿色。
拒绝或 request changes 不会在同一操作里修代码。

## 8. Change Request、Tech Debt 与 Future Work

例：上线前业务提出“一个收货单跨多个 warehouse”，可能同时改变产品边界和
跨 feature tenancy/authorization 决策。

| 操作/明确 prompt | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `start ... --kind change_request --work-id CR-0007 --stage change_request` | 人类选择原始 change request | pointer | 无 | pointer | in_progress | 人类明确调用 spec-sync change-request |
| `$spec-sync change-request CR-0007；保留原始请求并 materialize doc/change-requests/CR-0007.md` | 原始请求文本存在；durable CR path 已指定 | pointer/index；受影响 ID 的目标 sections；routing rules | `doc/change-requests/CR-0007.md` | 仅既有 CR 草稿 | pointer `ready_for_review` | 列最高层与建议 prompts 后停；不得直接进入 owner amend |
| `flow-state decide`（CR-0007 intake） | materialized CR 已由人类审阅并明确批准作为路由输入 | pointer、CR artifact/hash | 无 | pointer gate | `approved` | 停；此后人类才可选择 routed owner `amend` |
| `$product-discovery-roadmap amend；只提议 CR-0007 影响的 PR/F IDs` | 人类批准产品路由 | pointer/index；CR；受影响的 approved product sections | `doc/product-amendments/CR-0007.md`，role `product_amendment` | 不改 canonical PRD/Roadmap | `ready_for_review` | 人类审阅 proposal 后另行 `approve-amendment` |
| `$product-discovery-roadmap approve-amendment；应用已审阅 CR-0007 proposal` | 人类明确批准 proposal 与完整 named canonical edit set | proposal/hash；仅受影响 canonical files | 无 | proposal 保持 byte-identical；只改 canonical；re-record 原 proposal role set + all affected canonical roles 后 generic `decide` | `approved` | 未批准或已变更 proposal 不能 promotion；停 |
| `$architecture-baseline amend；评估 CR-0007 对 AC-003/ADR-0002 的影响` | 产品边界已获批准；人类选择 architecture route | pointer/index；accepted baseline/ADR；CR/新 PR 的必要 sections | `doc/architecture-amendments/CR-0007.md` 与 proposed ADR roles | 不改 accepted baseline/ADR | `ready_for_review` | 原 ADR 仍有效；人类另行 approve |
| `$architecture-baseline approve；应用已审阅 CR-0007 architecture proposal` | 人类明确批准 proposal/ADR/baseline edits | amendment/hash、named baseline/ADRs | 无 | amendment proposal 保持 byte-identical；应用 reviewed canonical/ADR edits；re-record exact amendment/ADR set + canonical `architecture` 后 generic `decide` | `approved` | promotion 后停；不自动 refresh guidance |
| `$bootstrap-agent-guidance refresh CR-0007；只刷新被该已批准决策影响的路由` | CR-0007 owning artifacts 已批准且 guidance 确实 stale | pointer/index；changed approved sections；现有 guidance；必要 repo evidence | 无（通常） | 仅 stale guidance | `ready_for_review` | validator 后停 |

Follow-up 不应悄悄变成 F001 scope：

| 发现 | 记录位置/类型 | 后续人类选择 |
|---|---|---|
| 当前行为不符合已批准 spec | `bug` work item + regression evidence | 先完成该 BUG 的 approved `spec`，再完成 approved `plan`/`requirements_checklist`/`tasks`；之后才可 `$spec-sync pre-implement BUG-### bug`，实现后 `post-implement BUG-### bug`，走 generic human review；不冒充 feature acceptance |
| 实现质量问题但不改变用户行为 | `doc/tech-debt/TD-###-short-title.md`：impact、owner、repayment trigger/evidence | 排期 maintenance；说明是否 blocking |
| 新产品想法 | Roadmap `Candidate`，经 product amend | 以后再决定是否 Committed |
| 跨 feature 技术欠债 | 先形成独立 debt/trigger evidence；不得直接改 approved baseline | 人类显式选择 `architecture-baseline amend <CR-ID>`，用 reviewed amendment proposal 新增 deferred decision 或 proposed ADR；promotion 前旧 baseline 继续有效 |
| 不确定技术问题 | `spike`，一个问题与 timebox | 只把证据带回 owning decision |

## 9. Release

先由人类明确 release scope，例如 `REL-2026.09` 包含已接受的 F001–F004。

| 操作/明确命令 | 执行前 | 精确最小读取 | 创建 | 修改 | 最大结束状态 | 停止与下一次人类动作 |
|---|---|---|---|---|---|---|
| `python flow-state/scripts/flow_state.py --root . start --expect-revision N --kind release --work-id REL-2026.09 --stage release_readiness` | scope 已由人类明确；included features 已 accepted | pointer | 无 | pointer | `in_progress` | 收集 release evidence |
| “按风险生成 build provenance，并收集 fixed revision/diff 的 code-review evidence；运行 release CI/dependency/security/migration/compatibility/rollback/ops/docs gates” | release scope 固定 | build/CI configs；included revisions/diffs；适用 runbooks 与 risk inputs | pipeline/review reports、run IDs、artifacts | 无领域 truth | pass/fail/N/A evidence | 缺证据则停；N/A 必须说明 absent signal 与 scope |
| `$delivery-gates release REL-2026.09；scope F001-F004` | 每个 feature 有 human acceptance；evidence 可定位 | pointer/index；acceptance decisions；build provenance、CI、适用 code/dependency/security/migration/compatibility/rollback/observability/ops/docs evidence；已 disposition 的 bug/debt | `doc/releases/REL-2026.09-readiness.md` | 以 role `release_readiness` 机械登记；不改代码、tag、deploy 或 accepted history | `ready_for_release` | ready/conditional/not_ready 后停 |
| `$delivery-gates authorize-release REL-2026.09；authorizer/date/evidence 如当前消息` | 人类已审阅 `ready_for_release` artifact；其 review status 为 `ready`/`conditional` 且无 unresolved blocker；当前消息明确授权该固定 scope/revision | pointer/index；readiness artifact/hash；scope、blocker 与 provenance | 无 | 确定性命令只替换四个授权字段并更新 pointer/index | `release_authorized` | 停；不 tag、不 publish、不调用项目 automation |
| “我另行授权项目 release automation 发布已处于 release_authorized 的 REL-2026.09” | pointer 为 `release_authorized`；当前消息另行授权外部副作用 | authorized readiness、release artifact、runbook | tag/package/deployment record，以及符合 receipt schema 的 `doc/releases/REL-2026.09-result.yaml` | 外部 release state | success/fail | 报告实际结果与 receipt path；失败不标 `released` |
| `$delivery-gates record-release-result REL-2026.09 Succeeded；receipt=doc/releases/REL-2026.09-result.yaml，confirmer/date 如当前消息` | 实际 automation 已终止；receipt 的 ID/result/time/run/artifact hash 匹配；当前消息确认 | pointer、authorized readiness、结构化 receipt | 无 | 确定性命令校验并 hash receipt，只替换四个执行字段并更新 pointer/index | `released` | 报告 release ID 与 receipt path/hash；结束 |

`delivery-gates` 本身永远不 tag、publish 或 deploy。对高风险 WMS，migration、
rollback、observability 与 operator documentation 一般不能随意标 N/A。

## 10. Full 项目的 Context / Token 防线

Full 的风险不是文档数量本身，而是把“可能相关”误当成“必须加载”。实际 coder
应遵循以下规则：

1. **每次只激活一个 work item 和一个 operation。** 在人工 gate 后开启新会话很正常；
   用 pointer 恢复状态，不靠上一会话的长摘要。
2. **先 resolve，再 read。** 先读 pointer，再
   `resolve --id F001`、`resolve --id PR-001`；只打开命中的标题/section。
3. **不预载八个 Skill。** 只有当前请求匹配的 Skill 进入 procedural context；
   它引用的 reference 也只在对应边界条件出现时读取。
4. **不把本流程文档放进运行时。** 它是培训、审查与 eval 样本；运行时 contract 在
   当前 `SKILL.md`、pointer 和 owning artifacts。
5. **按层取样。** 实现一个 task 通常只需要 active task、对应 spec/plan 段、
   适用 AC/PR IDs、目标 code/tests；不需要整份 PRD、Roadmap 和所有 ADR。
6. **长文档先 index。** PRD 超过约 400 行/40 requirements 或并发编辑需要时按
   domain 拆分，但保留一个 ID registry；UI 大域逐轮选择；日志只保存路径/run ID。
7. **确定性工作移出语言上下文。** YAML 转换、hash/index、lint、coverage、CI 与
   schema checks 用 script/hook/pipeline，Agent 只消费结论与失败切片。
8. **隔离审查。** Code/security/acceptance reviewer 读取固定 diff、spec IDs 和
   evidence，不继承实现聊天中的解释，从而降低确认偏差。
9. **冲突即停止。** revision 过期、canonical path 冲突、ID 不一致或证据缺失时，
   不补猜、不继续串阶段。
10. **Pointer 是 worktree cursor，不是项目数据库。** 并行 feature 使用独立
    worktree/cursor 或外部 tracker；不要合并两个 Agent 的 pointer 写入。Portfolio 状态应由
    acceptance/release artifacts 确定性生成，不回填 Roadmap 形成第二份真相。

推荐的 runtime context envelope：

```text
pointer
+ resolve 后的少量 index 结果
+ 当前 Skill
+ 当前 artifact/task
+ 1~2 个上层来源的目标 sections
+ 目标 diff/tests 或证据失败切片
```

如果一次操作要求“加载全部 PRD + 全 Roadmap + 全 baseline + 全 specs + 全源码”，
说明工作项或文档路由仍然过大，应先由人类缩小 scope 或拆分 artifact，而不是增加
上下文窗口。

## 11. 结果目录示意

```text
.specify/
  flow-state.yaml
  artifact-index.yaml
doc/
  wms-discovery-notes.md
  wms-product-requirements.md
  wms-feature-roadmap.md
  architecture-baseline.md
  adr/
  product-amendments/
  architecture-amendments/
  tech-debt/
  ui-structure.md
  change-requests/
  releases/
    REL-2026.09-readiness.md
    REL-2026.09-result.yaml
AGENTS.md
specs/
  001-receiving/
    spec.md
    wireframes.md
    plan.md
    tasks.md
    checklists/
    pre-implementation-review.md
    verification.md
    acceptance.md
```

这个目录表达 ownership，不要求所有 feature 一次生成。任何时刻都应只有当前人类
选中的那一个 operation 在工作；其余内容通过路径与稳定 ID 保持可发现，而不是常驻
Agent 上下文。
