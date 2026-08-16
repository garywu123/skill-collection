# Spec Driven Flow Lite：landrop 完整示例

本文用一个小型局域网文件传输 CLI `landrop` 演示 Lite 流程。
[Full 流程](spec-driven-flow.md)面向大型项目；Lite 只减少文档深度、拆分数量和执行轮次，
不减少需求批准、架构约束、纵向对齐、测试、独立验收或发布门禁。

这是一份仅用于 training/evaluation、给人类看的操作样例，不是 runtime contract。
运行时 agent **不要加载整篇本文**；它先读
`.specify/flow-state.yaml`，再用 `flow-state resolve` 查询生成的 index；模型不整份加载
`.specify/artifact-index.yaml`，完整一致性由确定性的 `validate --check-paths` 检查。
再读取当前明确授权的一个 `SKILL.md`、
该 operation 选择的至多一份完整 reference 和 selected output variant 的最小 template set，
最后按 ID 读取当前步骤所需的 bounded 工件/代码/证据切片。

## 1. 控制原则

- 人类是唯一的生命周期编排者。Skill 可以报告下一条建议命令，但不能调用下一个 Skill。
- 八个 Skill 均关闭 implicit invocation；必须用 `$skill-name` 显式选择。
- 图中的 `A → B` 只表示 B 的前置条件是 A，**不是** A 自动调用 B。
- Pointer 只存当前工作项、revision、gate、路径、证据和下一条允许命令；领域真相留在拥有它的工件中。
- 每次只授权一个 operation。Skill 写完自己的工件、登记候选状态后必须停下。
- `ready_for_review`、`ready_for_acceptance`、`ready_for_release` 都只是候选状态。Generic
  `decide` 只处理 `ready_for_review`，且必须带 `--decided-by`、`--decision-date`、
  `--decision-evidence`；它生成 `.specify/decisions/...yaml` durable receipt 并自动登记
  index。Acceptance、release authorization 和 release result 必须使用各自的人类授权
  operation；它们同样生成内容哈希回执，并额外绑定 owning artifact 的 pre/post hash。
- tests、coverage、lint、build、CI 等确定性检查由脚本、hook 或 CI 执行；Skill 只引用真实结果。
- 每个 lifecycle operation 使用 fresh conversation/fork/worker，从 pointer/index 重建状态；
  不把上一 Skill 或旧 artifact excerpts 带过 gate。只有同一 implementation 内的
  `guided-tdd-pairing` 可以连续互动，且进入 review 前必须结束。Fresh worker 只是同一
  已授权 operation 的 memory/coverage boundary，不能选择另一个 Skill/stage/gate/work item。
- 单个 semantic/code/evidence slice 不超过 8 KiB，一个 operation 的 initial target payload
  不超过 24 KiB；更大审查按 stable ID/path 在 fresh workers 分批。有 truncated/uncovered
  batch 就不能声称完整或通过。

本例的三种调用表面彼此独立：`$skill-name <operation>` 是人类授权的语义操作；
`python .../flow_state.py ...` 是机械状态/哈希/index 记录器；`/speckit.*` 是项目外部安装的
Spec Kit 命令，实际名称、参数和模板必须以项目固定且验证过的版本为准。若希望 Agent
解释状态，可另发 `$flow-state status；只报告当前 gate、revision 与允许的人类动作`。

下文表格每一行和 code block 的每个“当前消息”之间都隐含
`STOP / NEW USER MESSAGE / FRESH CONTEXT`；连续排版不是 command chaining。后文写
“更新 pointer/index”时，若命令会重建 index，也同时更新 `.specify/artifact-index.sha256`。

八个 Skill 的分工如下：

| Skill | 本例职责 | 不做什么 |
|---|---|---|
| `flow-state` | 维护 pointer/index 和 gate | 不保存领域摘要，不调用 Skill |
| `product-discovery-roadmap` | discovery、PRD、roadmap 及其批准 | 不决定架构或交付状态 |
| `architecture-baseline` | 跨 feature 的 Lite 架构基线 | 不写 feature 内部设计 |
| `bootstrap-agent-guidance` | 生成精简 `AGENTS.md` | 不复制 PRD、roadmap、架构全文 |
| `ui-wireframe-spec` | 只为确实存在的 UI 画结构/线框 | 不做视觉风格或代码 |
| `spec-sync` | pre/post 纵向对齐和变更路由 | 不修工件，不做验收 |
| `guided-tdd-pairing` | 可选的人类主写代码配对模式 | 不推进生命周期 |
| `delivery-gates` | 独立 gate review，并持久记录人类明确决定/结果 | 不修代码、不自行决定、不发布 |

## 2. 状态初始化与 provisional sizing

landrop 的初始意图是：两台局域网机器用一个口头传输码发送文件，支持续传和完整性校验。
在 roadmap 尚未批准时，feature 数量未知，因此只能做 **provisional** 判断：预计一个二进制、
无数据库、单人维护、无监管约束，可能不超过八个 feature。

```text
# 当前消息 1：人类只授权初始化
python <flow-state-dir>/scripts/flow_state.py --root . init --project-id LANDROP --profile lite
# Agent 报告并停止

# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---

# 当前消息 2：人类明确请求状态
python <flow-state-dir>/scripts/flow_state.py --root . status
# Agent 报告实际 revision 并停止

# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---

# 当前消息 3：人类明确选择 project discovery
python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind project --work-id LANDROP --stage discovery
# Agent 报告返回的 revision 并停止；不得自动运行 discovery Skill
```

| 阶段/命令 | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `flow-state init` | 当前消息明确要求初始化；仓库无冲突 pointer | 现有 pointer/index（若有） | 创建 `.specify/flow-state.yaml`、派生 `.specify/artifact-index.yaml` 与 `.specify/artifact-index.sha256` | `not_started`，profile 为 provisional，initial `start_discovery` gate pending | 报告 pointer；停。人类可另行请求 `status` |
| `flow-state status/validate` | 人类要求状态/检查 | pointer/index；可选 canonical paths | 无 | 状态不前进 | 报告缺失/冲突后停 |
| `flow-state start ... --stage discovery` | 当前消息明确选择 discovery，并满足 initial `start_discovery` gate；使用刚读取的实际 revision | pointer | 只改 pointer | `in_progress`，profile 仍 provisional | 报告返回 revision 后停；人类再明确调用 discovery Skill |
| `flow-state rebuild-index` | noncanonical indexed artifact 绕过 `record-output`/决定命令发生 out-of-band 变化；pointer integrity 仍通过；approved canonical hash 未漂移 | pointer integrity、受索引目录与 stable IDs | 重建 `.specify/artifact-index.yaml` 与 `.specify/artifact-index.sha256` | 状态不前进 | 随后执行 `validate --check-paths`；approved canonical 漂移必须走 amendment |

后续每个有状态命令都先读取 pointer；一个上下文里的第一次写入用
`<revision-from-status>`，同一已授权 operation 内的后续写命令使用前一条命令返回的
revision，绝不猜测或计算。遇到 `stale revision` 必须停止并报告冲突，不得刷新重试。
当前消息已经授权的生命周期 operation 可运行 `record-output` 登记自己的候选输出；这不是 artifact approval。
只有后续当前消息明确批准/拒绝时，才能运行决定命令：

```text
... record-output --expect-revision <revision-from-status> --stage <stage> --artifact <key>=<path> --next "<human command>"
... validate --check-paths
```

两个机械辅助命令让 hash 与重试都不进入模型上下文：`record-output ... --check-only`
完整校验一次 transition 但不写状态、不消耗 revision；`sync-bundle --artifact
<split-root> --member <path> ... --role <role>` 计算并写入该 root 的完整
`## Approved Bundle` 表，因此模型永远不需要手写 SHA-256。

`record-output` 和决定命令会自动保持 index 及其 SHA-256 sidecar；只有非 canonical indexed artifact 绕过
这些命令发生变化时才单独运行 `rebuild-index`。不得用它重新基线化 approved canonical。

```text
python <flow-state-dir>/scripts/flow_state.py --root . decide --expect-revision <revision-from-status> --decision approved --decided-by <human-name-or-role> --decision-date YYYY-MM-DD --decision-evidence <exact-current-user-statement-or-reference>
```

该 generic 命令只把当前 `ready_for_review` gate 决定为 `approved`/`rejected`，不会
启动下一阶段，也不能产生 `accepted`、`release_authorized` 或 `released`。后三类状态
分别只能来自 `record-feature-decision`、`authorize-release` 和 `record-release-result`，
并校验相应 artifact role/hash 与证据。Generic 与这三个专用 command 都会更新
pointer/index 并生成 `.specify/decisions/...yaml` 内容哈希回执；专用回执还绑定 artifact
的 pre/post hash，release result 再链接 authorization 与外部 execution receipt。报告
receipt path/hash 后停止。

人类直接请求 `$skill-name <operation>` 时，该请求也授权此 Skill 在前置条件通过后，
按该 Skill 的 operation-to-stage 表机械 `start` 精确映射的 stage（例如 `lite → architecture`、
`create → agent_guidance`、`pre-implement → pre_implement`），并不要求 operation/stage 同名。
若同一 kind/work/stage 已是 `in_progress`，重复 start 是不增加 revision 的幂等 no-op；任何
不同 stage 仍拒绝。Approval operation 不 start，只更新 owning artifact 并解决当前 gate。

## 3. Discovery → PRD → Roadmap

产品探索得到几个会改变边界的问题：接收端是否也安装 CLI、如何发现对端、是否强制加密、
同名文件如何处理、目录传输是否进入 MVP。两轮问答足够，但仍分阶段批准。

| Operation | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `$product-discovery-roadmap discover` | 人类授权探索 | pointer/index、已有产品证据 | `doc/product-discovery-notes.md` | `ready_for_review` | 列出未决问题，停 |
| `$product-discovery-roadmap approve-discovery；actor/date/evidence 如当前消息` | 人类已审阅并明确批准 notes；当前消息提供 actor/date/evidence | discovery notes | notes 批准字段；以同 role/path re-record 新 hash，再执行带三项 provenance 的 generic `decide`；生成 `.specify/decisions/...yaml` 并更新 pointer/index | 工件 `Approved for PRD`；pointer `approved` | 报告 receipt path/hash 后停；不自动起草 PRD |
| `$product-discovery-roadmap draft-prd` | discovery 已批准 | 已批准 notes | `doc/general-product-requirement.md` | `ready_for_review` | 等人类审阅 |
| `$product-discovery-roadmap approve-prd；actor/date/evidence 如当前消息` | 人类明确批准 PRD；当前消息提供 actor/date/evidence | PRD；必要时回看 cited notes | PRD 状态/批准证据；同 role/path re-record 新 hash，再执行带三项 provenance 的 generic `decide`；生成 indexed durable receipt | `approved` | 报告 receipt path/hash 后停；不自动建 roadmap |
| `$product-discovery-roadmap draft-roadmap` | PRD 已批准 | PRD registry 和必要正文 | `doc/feature-roadmap.md` | `ready_for_review` | 等人类审阅 |
| `$product-discovery-roadmap approve-roadmap；actor/date/evidence 如当前消息` | 人类明确批准范围、依赖、顺序与 Lite sizing；当前消息提供 actor/date/evidence | roadmap、PRD coverage registry | roadmap 状态/批准证据；同 role/path re-record 新 hash，再执行带三项 provenance 的 generic `decide`；生成 indexed durable receipt | `approved` | 报告 receipt path/hash 后停；不自动做架构 |

精简 PRD 使用 append-only ID，例如：

- `PR-001`：发送方生成可口头转述的传输码。
- `PR-002`：接收方凭传输码接收单个文件。
- `PR-003`：中断后从已确认分块续传。
- `PR-004`：完成后校验内容；不一致时明确失败。
- `PR-100`：内容不得明文经过网络。
- `PR-101`：不得静默覆盖同名目标。
- `PR-102`：产品没有共享/global shell、导航或跨 feature UI pattern；终端内局部视图
  由 owning feature 自己定义。它是 approved product-UI N/A rationale，不代表 feature
  `UI Surface: none`。

因此批准后的 PRD 同时写入 `Product UI structure applicability: not_applicable` 和
`Product UI applicability evidence: PR-102`；UI Skill 不需要靠仓库代码猜测这个结论。

批准后的 roadmap 是五个可独立验收的能力：

| Feature | Product Domain | Outcome | UI Surface | Depends on |
|---|---|---|---|---|
| `F001` 单文件传输 | transfer | 两台机器可靠传一个文件 | `none` | — |
| `F002` 完整性与冲突 | transfer | 校验内容且不静默覆盖 | `none` | F001 |
| `F003` 断点续传 | transfer | 网络中断后不重传已确认分块 | `none` | F001 |
| `F004` 终端进度视图 | experience | 显示进度、速率和 ETA | `new screens` | F001 |
| `F005` 目录传输 | transfer | 一次发送目录 | `none` | F002 |

Roadmap 不复制 mutable delivery status；当前状态在 pointer，历史 verification、acceptance
和 release 记录按 feature ID 从 index 定位。

Roadmap 使用机器可检查字段：`Profile sizing: lite`、`Feature count: 5`、
`Deployable count: 1`、`Datastore count: 0`、`Owning team count: 1`、
`Regulatory/audit/contractual constraint: no`；`Sizing evidence` 只保存这些判断的稳定来源
anchor。五项全过，且脚本会复核 root 中恰有 5 个唯一 F-ID。roadmap gate 已解决且没有其他 pending
gate 后，由人类显式记录确认；不要手改 YAML：

```text
python <flow-state-dir>/scripts/flow_state.py --root . confirm-profile --expect-revision <revision-from-status> --profile lite
```

若 roadmap **批准前**任一项失败或未知，应先在 roadmap 写入 `Profile sizing: full` 与
完整 evidence，批准后再确认 `--profile full`。若已经批准/确认 Lite 后才发现条件失败，
必须由人类另行授权 product amendment，把 reviewed sizing/evidence 更新到 `full` 并重新
批准；只有随后 `confirm-profile --profile full` 才会通过。未受影响的产品真相继续复用。

## 4. Lite 架构基线

```text
$architecture-baseline lite
```

| Operation | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `$architecture-baseline lite` | 人类授权；PRD/roadmap 已批准；sizing 已确认 | requirement drivers、roadmap 摘要/依赖、constitution | 一页 `doc/architecture-baseline.md`；不建 ADR | `ready_for_review` | 报告 decisions、risks、Plan Constraints 后停 |
| `$architecture-baseline approve；actor/date/evidence 如当前消息` | 人类明确批准该 baseline；当前消息提供 actor/date/evidence | reviewed baseline/validation | baseline 批准状态；如字节改变则同 role/path re-record 新 hash，再执行带三项 provenance 的 generic `decide`；生成 `.specify/decisions/...yaml` 并更新 pointer/index | `approved` | 报告 receipt path/hash 后停；不自动 bootstrap |

本例只固定跨 feature 决策：单一静态二进制、TLS/PSK、分块协议、sidecar 续传状态、原子落盘；
并生成 `AC-001...` Plan Constraints。feature 内部函数、包和任务留给各自 plan。

## 5. Agent guidance 与 UI 路由

这是推荐排版顺序而非依赖链：approved PRD/Roadmap 已允许 guidance 与 UI 路由；本例先批准
architecture 只是为了让首版 `AGENTS.md` 一次指向已批准约束。两个 operation 互不授权。

| Operation | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `$bootstrap-agent-guidance create` | 人类授权；PRD、roadmap、baseline 已批准 | pointer/index、批准工件、可验证的 manifest/CI 命令 | 根 `AGENTS.md`；仅当当前请求点名 consumer/adapter 时才创建对应薄 adapter | `ready_for_review` | 校验并停；未知命令只报告为 omitted |
| `$flow-state decide --expect-revision <revision-from-status> --decision approved --decided-by <human-name-or-role> --decision-date YYYY-MM-DD --decision-evidence <exact-current-user-statement-or-reference>`（guidance） | 人类审阅并明确批准 | 当前 guidance gate/revision、guidance hash/validation、当前人类决定 | `.specify/decisions/...yaml` durable receipt；更新 pointer/index | `approved` | 报告 receipt path/hash 后停；不自动选择 feature |
| `$ui-wireframe-spec product` | 产品有全局 UI 且人类授权 | 产品 experience constraints、roadmap UI inventory | `doc/ui-structure.md` | `ready_for_review` | landrop 不满足前置，故不运行 |

landrop 是 CLI，没有导航与全局 shell，所以产品级 UI 被**正确跳过**，不是 gate 被省略。
F001 的 approved Roadmap `UI Surface: none` entry 本身就是持久 UI N/A 来源，不新增
artifact 或 state role，也不运行 feature wireframe；若有人要求运行，Skill 应报告前置不满足并停。
F004 的 `UI Surface: new screens` 则引用 approved `PR-102` 作为“无需 product UI structure”
的全局 N/A prerequisite；这不能替代 F004 自己的 feature wireframe。

## 6. F001：一个完整 Lite feature

人类先选中 committed feature：

```text
python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind feature --work-id F001 --stage specify
```

| 阶段/命令 | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `/speckit.specify F001 Single File Transfer；只覆盖 Roadmap F001` | 人类授权；F001 committed | pointer/index；F001 roadmap entry、owned `PR-###` | `specs/001-single-file-transfer/spec.md` | draft/review candidate | 不吸收 F002+；停 |
| `/speckit.clarify 001-single-file-transfer` | spec 已存在 | spec 的高影响歧义、必要 owned PR anchors | 更新 spec/clarifications | clarified | 未决行为会阻塞 plan；停 |
| UI route for F001 | spec 已批准；approved Roadmap 中 F001 `UI Surface: none` | approved F001 roadmap entry | 无；Roadmap entry 本身是持久 N/A，不新增 artifact/role | unchanged | 报告 N/A 来源并停；不得调用 wireframe Skill |
| `python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind feature --work-id F001 --stage plan` | spec 已批准；wireframe 已批准或 approved Roadmap N/A；baseline 已批准；人类选择 plan | pointer/current revision | pointer stage | `in_progress` | 报告 revision 并停；不自动执行 plan |
| `/speckit.plan 001-single-file-transfer` | spec 已批准；feature wireframe 已批准，或 approved Roadmap 的 `UI Surface: none` 是持久 N/A；baseline 已批准 | approved spec、适用 `AC-###`、approved wireframe 或 Roadmap N/A entry、必要 repo evidence | `specs/001-single-file-transfer/plan.md` | review candidate | 跨-feature 冲突先停；否则报告 plan 并停 |
| `/speckit.checklist 001-single-file-transfer requirements` | spec 已批准且可审查 | approved spec、clarifications、acceptance scenarios | `specs/001-single-file-transfer/checklists/requirements.md`（固定 role `requirements_checklist`） | checklist evidence | 报告 blocker 并停；不自动运行 tasks |
| `/speckit.tasks 001-single-file-transfer` | spec/plan 已由人类 review；requirements checklist 无 blocker | reviewed spec、reviewed plan、`requirements_checklist` | `specs/001-single-file-transfer/tasks.md` | ordered tasks | 报告任务边界并停；不自动运行 analyze |
| `/speckit.analyze 001-single-file-transfer` | spec/plan/tasks 齐全 | exact `spec.md`、`plan.md`、`tasks.md` 与 applicable constitution rules | 默认只输出 findings | `pass` 或 `blocked` | 不修纵向 truth；报告 findings 并停 |
| `$spec-sync pre-implement F001 feature` | approved spec/plan/tasks 齐全；requirements checklist nonblocking；wireframe approved 或 approved Roadmap N/A | pointer/index；F001 entry；相关 roadmap/PR/AC/UI sections；spec/plan/tasks/checklist | `specs/001-single-file-transfer/pre-implementation-review.md`，Pass 时以 role `pre_implementation` 登记 | Blocking 时 `blocked`；Pass 时 `ready_for_review` | Blocking 就停；Pass 后 `record-output` 并停等 generic `decide` |
| `python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind feature --work-id F001 --stage implementation` | role `pre_implementation` 已由 generic `decide` 批准；人类另行选择实现 | pointer/current revision | pointer stage | `in_progress` | 报告 exact stage/revision 并停；不自动实现 |
| `/speckit.implement 001-single-file-transfer` | exact implementation start 已完成；人类授权 | 当前 tasks、最小 spec/plan、相关代码 | 代码、测试、task evidence | implementation candidate | 每个 bounded batch 报告并停；不宣称交付 |
| “收敛 F001 implementation；只处理 tasks/checks 已指出的 scope drift” | 实现 task 已完成；人类授权处理剩余漂移 | 当前 diff、tasks、checks | 只修当前 scope 内漂移并补齐证据 | converged candidate | 进入证据门禁前停 |

Lite 保留明确的状态 checkpoint，只是工件更短：clarify 后以 role `spec`
`record-output` 并由人类 generic `decide`；plan/checklist/tasks/analyze 后登记 `plan`、
`requirements_checklist`、`tasks` 的精确路径并再次等待 generic `decide`；pre-sync Pass
后以 role `pre_implementation` 登记 `pre-implementation-review.md`，得到
`ready_for_review` 并再次等待 generic `decide`。只有该 review 已批准，且人类另起操作
运行上表 exact `start ... --stage implementation` 后，才允许明确执行
`/speckit.implement 001-single-file-transfer`。Spec Kit 命令本身不推断或批准共享状态。
这里每个 generic `decide` 都使用第 2 节的完整 actor/date/evidence 参数，并在更新
pointer/index 时生成 `.specify/decisions/...yaml` receipt；每次报告 receipt path/hash 后停止。

如果用户希望自己写核心逻辑，可在已授权 implement 范围内显式进入
`$guided-tdd-pairing`：agent 写一个失败测试，用户写最小实现，跑 focused test 后停；它不更新 pointer。

确定性证据由真实命令产生，例如 `go test ./...`、项目定义的 coverage policy、lint/build 和 CI。
review 按风险选择：F001 涉及 TLS/传输码，应有独立 code review 与针对密钥、重放、路径输入的 security review；
纯文案改动不必套同一组检查。`not_run` 不能伪装成 `pass`。

| 阶段/命令 | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `$spec-sync post-implement F001 feature` | approved、hash-matching `pre_implementation` 仍属于 F001；converged；tasks/checks/evidence 已命名 | 当前 feature、相关代码/test anchors、CI/review evidence | `specs/001-single-file-transfer/verification.md`，以 role `verification` 登记 | `ready_for_acceptance` | 不改 roadmap、不验收 |
| `$delivery-gates accept-feature F001` | 人类授权；active F001 为 `ready_for_acceptance`；approved spec/scenarios 与 verification hash 可定位；必须由独立 reviewer 执行，不得是本次 implementation agent | approved scenarios、diff、verification、适用 gates | `acceptance.md`，以 role `acceptance` 登记 | 候选 `ready`/`conditional`/`not_ready`；pointer 仍 `ready_for_acceptance` | 等人类决定 |
| `$delivery-gates record-feature-decision F001 Accepted；decider/date/evidence 如当前消息` | 人类审阅 acceptance 并明确批准；review status 为 `ready`/`conditional` 且无 unresolved blocker | 当前 revision/gate、acceptance artifact/hash 与 blocker | 只替换四个决定字段；生成绑定 artifact pre/post hash 的 indexed、content-hashed receipt；更新 pointer/index | `accepted` | 报告 receipt path/hash；不自动选择 F002 |
| `$bootstrap-agent-guidance refresh；只更新已验证的 Go build/test 路由` | F001 已 terminal `accepted`，无 pending gate；人类另行授权 project refresh；真实 `go build`/`go test` 已可验证 | pointer/index、现有 guidance、manifest 与精确命令证据 | 仅 stale `AGENTS.md` guidance | `ready_for_review` | validator 后停；不能在 F001 implementation 中途切换 project cursor |
| `$flow-state decide ... --decision approved --decided-by ... --decision-date ... --decision-evidence ...`（仅在执行 refresh 后） | 人类已审阅 refreshed guidance；当前 gate/hash 匹配 | pointer、AGENTS hash、validator evidence、当前人类决定 | indexed decision receipt；pointer/index/sidecar | `approved` | 报告 receipt 后停；未解决就不能 start F004 |

Lite 不削减 feature truth：spec 中每个 `SC-###` 都必须在 acceptance 的
`Scenario Evidence` 中恰好出现一次，Tests / deterministic verification 始终为
`required`。其他 gate 可以有证据地 `not_applicable`，但不能因项目小而省略判断。

## 7. F004：仅增加真正需要的 UI 工件

F004 必须先成为 active work，并完整解决 spec gate；不能从已接受的 F001 直接跳到
`feature_ui`：

```text
# 当前消息：人类选择 F004 specify；执行后停止
python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind feature --work-id F004 --stage specify

# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---

# 后续两个当前消息分别选择，且每条完成后停止
/speckit.specify F004 Progress View；只覆盖 Roadmap F004

# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
/speckit.clarify 004-progress-view

# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---

# clarify bundle 完成后机械登记 candidate；使用上一条状态命令返回的 revision
python <flow-state-dir>/scripts/flow_state.py --root . record-output --expect-revision <revision-from-status> --stage specify --artifact spec=specs/004-progress-view/spec.md --next "review F004 spec"
# Agent validate、报告并停止

# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---

# 后续当前消息明确批准时才解决 spec gate；生成持久 decision receipt 后停止
python <flow-state-dir>/scripts/flow_state.py --root . decide --expect-revision <revision-from-status> --decision approved --decided-by <human-name-or-role> --decision-date YYYY-MM-DD --decision-evidence <exact-current-user-statement-or-reference>
```

只有 role `spec` 已 approved 且 hash 仍匹配后，roadmap 的 `new screens` 才允许人类
显式授权下表 operation；`$ui-wireframe-spec feature` 会为这次已授权操作机械执行
`start --kind feature --work-id F004 --stage feature_ui`，登记 candidate 后停止：

| Operation | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `$ui-wireframe-spec feature；为 F004/004-progress-view 生成 wireframes.md` | 人类授权；F004 role `spec` 已批准、hash-matching 且 clarified；UI Surface 非 none；approved Roadmap/产品已记录“无 global shell/navigation” | pointer/index；F004 entry、适用 PR、spec/clarifications、approved product-UI N/A rationale | `specs/004-progress-view/wireframes.md`（role `wireframes`；UI Structure 字段引用 N/A 来源） | `ready_for_review` | 报告 screen/control/state coverage 后停 |
| `$flow-state decide ... --decision approved --decided-by ... --decision-date ... --decision-evidence ...` | 人类已审阅 wireframes/validation；当前 gate 是 `ready_for_review` | pointer、wireframes hash、validation、当前人类决定 | pointer/index；生成 `.specify/decisions/...yaml` durable receipt，语义 wireframe 不扩写 | `approved` | 报告 receipt path/hash 后停；再由人类授权 plan |

它只需一个终端 L1 skeleton，但该 L1 必须配套完整 L2 control table 与
loading/transferring/reconnecting/verifying/success/failure/cancelled state table；没有产品
L0 导航，也没有无分支的 L3 图。后续每一步仍由人类分别输入 exact target：

```text
python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind feature --work-id F004 --stage plan
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
/speckit.plan 004-progress-view
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
/speckit.checklist 004-progress-view requirements
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
/speckit.tasks 004-progress-view
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
/speckit.analyze 004-progress-view
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
python <flow-state-dir>/scripts/flow_state.py --root . record-output --expect-revision <revision-from-status> --stage plan --artifact plan=specs/004-progress-view/plan.md --artifact requirements_checklist=specs/004-progress-view/checklists/requirements.md --artifact tasks=specs/004-progress-view/tasks.md --next "review F004 plan bundle"
# 报告 ready_for_review 与返回 revision 后停止
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
python <flow-state-dir>/scripts/flow_state.py --root . decide --expect-revision <revision-from-status> --decision approved --decided-by <human-name-or-role> --decision-date YYYY-MM-DD --decision-evidence <exact-current-user-statement-or-reference>
# 报告自动登记到 index 的 .specify/decisions/...yaml receipt path/hash 后停止
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
$spec-sync pre-implement F004 feature
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
python <flow-state-dir>/scripts/flow_state.py --root . decide --expect-revision <revision-from-status> --decision approved --decided-by <human-name-or-role> --decision-date YYYY-MM-DD --decision-evidence <exact-current-user-statement-or-reference>
# 报告自动登记到 index 的 .specify/decisions/...yaml receipt path/hash 后停止
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind feature --work-id F004 --stage implementation
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
/speckit.implement 004-progress-view
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
“收敛 F004 implementation；只处理 tasks/checks 已指出的 scope drift”
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
“运行 AGENTS.md 的 F004 targeted tests 和 full relevant tests”
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
“执行项目 coverage policy，并运行 lint/build/CI，记录命令、revision 与 evidence path”
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
“独立 code review F004 diff”
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
“按风险执行 F004 security review，或记录有证据的 N/A reason”
# --- STOP / NEW USER MESSAGE / FRESH CONTEXT ---
$spec-sync post-implement F004 feature
```

F004 plan 使用 approved spec、approved wireframes、approved baseline 与适用 `AC-###`；
checklist、tasks、analyze 的分离 stop、fixed role `requirements_checklist` 和 exact-read 规则与
F001 相同。`$spec-sync pre-implement F004 feature` 另外要求 F001 已 `accepted`，或
approved Roadmap（必要时经 product amendment）明确记录 parallel scope、owner 与风险处置；Pass 时创建
`specs/004-progress-view/pre-implementation-review.md`，以 role `pre_implementation`
`record-output` 到 `ready_for_review`，再等上面列出的 generic `decide`。实现收敛后必须先运行
项目已验证的 F004 targeted/full relevant tests、coverage policy、lint/build/CI，并完成适用的
独立 code/security review；只有这些 checks/reviews 都有命名 evidence 且 blocker 已处理，
才可执行 `$spec-sync post-implement F004 feature`。Post-sync 创建
`specs/004-progress-view/verification.md`，最大状态仍是 `ready_for_acceptance`，随后才是另行
授权的 `$delivery-gates accept-feature F004`，且 reviewer 必须独立于本次 implementation
agent。只有人类审阅该 acceptance、review status 为 `ready`/`conditional`、无 unresolved
blocker，并在当前消息提供 decider/date/evidence 时，才可另行执行
`$delivery-gates record-feature-decision F004 Accepted`；否则不得进入 `accepted`。

## 8. 变更、债务与未来想法

“希望支持跨子网中继”先进入 `$spec-sync change-request CR-0002`，而不是直接改代码。

| Operation | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `$spec-sync change-request CR-0002；materialize doc/change-requests/CR-0002.md` | 人类授权；原始请求文本；durable path 已明确 | pointer/index、受影响 IDs、最小 owning artifacts | `doc/change-requests/CR-0002.md` | pointer `ready_for_review` | 列出最高影响层和建议 prompts，不执行 |
| `$flow-state decide --expect-revision <revision-from-status> --decision approved --decided-by <human-name-or-role> --decision-date YYYY-MM-DD --decision-evidence <exact-current-user-statement-or-reference>`（CR-0002 intake） | 人类审阅 materialized CR 并明确批准为路由输入 | pointer、CR/hash、当前人类决定 | `.specify/decisions/...yaml` durable receipt；更新 pointer/index | `approved` | 报告 receipt path/hash 后停；pending gate 未解决时不得进入 owner amend |
| `$product-discovery-roadmap amend CR-0002` | CR intake 已 approved；人类另行授权 product route | CR；受影响的 approved product sections | `doc/product-amendments/CR-0002.md`；candidate 只登记 role `product_amendment`，不改 canonical PRD/Roadmap | `ready_for_review` | 报告 proposal/hash 后停；旧 product truth 仍有效 |
| `$product-discovery-roadmap approve-amendment CR-0002；actor/date/evidence 如当前消息` | 人类明确批准 byte-identical proposal 与完整 named canonical edit set，并提供 actor/date/evidence | proposal/hash；仅受影响 canonical files | 只应用 reviewed canonical edits；在决定前 re-record 同一 `product_amendment` proposal role 和每个 changed canonical role，再执行带三项 provenance 的 generic `decide`，生成 indexed durable receipt | `approved` | proposal 改变或 role set 不完整就停；否则报告 receipt path/hash 后停 |
| `$architecture-baseline amend CR-0002` | CR intake 及必要产品边界已 approved；人类另行授权 architecture route | CR；accepted baseline/ADR；必要的新 product sections | `doc/architecture-amendments/CR-0002.md`（role `architecture_amendment`）与 exact proposed `adr-*` role set；不改 approved baseline/ADR | `ready_for_review` | 报告 exact proposal/ADR set 后停；旧 architecture truth 仍有效 |
| `$architecture-baseline approve CR-0002；actor/date/evidence 如当前消息` | 人类明确批准 byte-identical proposal、exact proposed ADR set 与 named baseline edits，并提供 actor/date/evidence | amendment/hash；exact named proposal/ADR/baseline files | 应用 reviewed canonical edits；在决定前 re-record exact same `architecture_amendment`/`adr-*` set 加 canonical `architecture`，再执行带三项 provenance 的 generic `decide`，生成 indexed durable receipt | `approved` | exact set 不匹配就停；否则报告 receipt path/hash 后停，不自动 refresh guidance |

- 行为缺陷：新建 `BUG-###`，不偷偷扩 F001，也不冒充 feature acceptance。
- 实现债务：记录 `doc/tech-debt/TD-###-short-title.md`、影响、owner、偿还触发点与证据。
- 未来产品想法：先 materialize/批准 CR，再由人类显式选择
  `$product-discovery-roadmap amend <CR-ID>`；只有 reviewed proposal 经上述 exact-set promotion
  才能写入 roadmap `Candidate`，不得直接修改 approved Roadmap，也不进入当前 feature。
- 跨 feature 技术债：先保存独立 debt/trigger evidence 并批准 CR，再由人类显式选择
  `$architecture-baseline amend <CR-ID>`；只有 reviewed proposal 经上述 exact-set promotion
  才能改 approved baseline/ADR 或新增 deferred decision。
- `feature`、`bug`、`maintenance`、`spike`、`migration`、`security`、`change_request`、`release`
  可使用对应 pointer `kind`。专用 acceptance 只处理 `feature`；任何类型都不得伪装成另一类型。

Architecture spike 使用可执行 closure：approved architecture baseline 必须已包含该
`SPK-###` 及其一个问题/timebox/blocked owner，然后人类显式运行
`$architecture-baseline resolve-spike SPK-###`。该已授权 Skill 机械执行 exact
`start --kind spike --work-id SPK-### --stage spike_result`，只读取该 spike definition 与
必要调查证据；time-boxed 调查完成后，以 exact role `spike_result` 和 durable result path
执行 `record-output`，到
`ready_for_review` 就停。后续人类用带 actor/date/evidence 的 generic `decide` 生成 indexed
receipt；它只批准/拒绝 investigation closure。若结论会改变 approved baseline/ADR，必须
另行 materialize/批准 CR 并显式选择 `$architecture-baseline amend <CR-ID>`，不得由 spike
直接应用。

`bug`、`maintenance`、`migration`、`security` 的 typed path 与 feature 使用相同四角色保障。
对同一 `<ID>/<kind>`，人类先 `start ... --stage specify`，创建并以 role `spec`
`record-output`，再用带三项 provenance 的 generic `decide` 生成 indexed receipt；随后另行
`start ... --stage plan`，创建并以精确路径登记 `plan`、`requirements_checklist`、`tasks`，
再次由 generic `decide` 生成 indexed receipt。只有 `spec`、`plan`、
`requirements_checklist`、`tasks` 四个 role 都属于同一 work ID/kind、状态为 `approved`、
hash 仍匹配且 checklist 无 blocker，才可另行授权
`$spec-sync pre-implement <ID> <kind>`；实现后再走 typed post path，并在
`ready_for_review` 由同样带 actor/date/evidence 的 generic decision 结束。

## 9. Release gate

当一个明确 release scope 内的 feature 都有**人类 acceptance decision** 后：

| Operation | Requires | Reads | Creates / modifies | 最大结束状态 | Stop |
|---|---|---|---|---|---|
| `python <flow-state-dir>/scripts/flow_state.py --root . start --expect-revision <revision-from-status> --kind release --work-id REL-0.1.0 --stage release_readiness` | release scope F001,F004 已明确；included features 已 accepted | pointer/current revision | pointer stage | `in_progress` | 报告 revision 并停；再收集 release evidence |
| “为 REL-0.1.0 scope F001,F004 的 fixed revision/diff 生成 build provenance、收集独立 code-review evidence，并运行已验证的 CI/dependency/security/migration/compatibility/rollback/observability/ops/docs gates” | release scope 与 included revisions/diffs 已固定 | build/CI config、included revisions/diffs、适用 runbook 与 risk inputs | reports/run IDs/artifacts，包括用户/运维文档证据 | pass/fail/N/A evidence | 缺证据就停；N/A 必须记录 absent signal 与 scope |
| `$delivery-gates release REL-0.1.0 F001,F004` | 人类明确授权该 scope；feature acceptance/provenance 已知 | acceptance decisions、build provenance、CI、适用 code/dependency/security/migration/compatibility/rollback/observability/ops/docs evidence、known issues | `doc/releases/REL-0.1.0-readiness.md`；ready/conditional 登记 gate，not_ready 用 concrete blockers 执行 `block` | `ready_for_release` 或 `blocked` | 不 tag、不 publish |
| `$delivery-gates authorize-release REL-0.1.0；authorizer/date/evidence 如当前消息` | 人类已审阅 `ready_for_release` artifact；review status 为 `ready`/`conditional` 且无 unresolved blocker；当前消息明确授权固定 scope/revision | pointer/index、readiness artifact/hash、blockers/provenance | 只替换四个授权字段；生成绑定 readiness pre/post hash 的 indexed、content-hashed authorization receipt；更新 pointer/index | `release_authorized` | 报告 receipt path/hash 后停；不运行项目 release automation |
| “我另行授权项目 release automation 发布已处于 release_authorized 的 REL-0.1.0” | pointer 为 `release_authorized`；当前消息另行授权实际副作用 | authorized readiness、build provenance、runbook | tag/package/publish evidence + `doc/releases/REL-0.1.0-result.yaml` structured receipt | success/fail | 报告实际结果/receipt 并停；失败时不标 released |
| `$delivery-gates record-release-result REL-0.1.0 Succeeded；receipt=doc/releases/REL-0.1.0-result.yaml，confirmer/date 如当前消息` | automation 已终止；receipt ID/result/run/time/artifact hash 匹配；人类确认 | pointer、authorized readiness、外部 receipt | 写入外部 receipt path/SHA-256，替换五个执行字段；生成链接 authorization/result hash 的 indexed、content-hashed result receipt；更新 pointer/index | `released` | 报告 release ID 与两个 receipt path/hash |

对本地 CLI，deployment、migration、observability 可有理由地记为 `not_applicable`；构建 provenance、
fixed-diff code review、跨平台测试、依赖/安全、兼容性、回滚、用户/运维文档和已知问题
不能因 Lite 自动消失。

## 10. Runtime context 与文件结果

```text
.specify/
├── decisions/...
├── flow-state.yaml
├── artifact-index.yaml
└── artifact-index.sha256
AGENTS.md
doc/
├── product-discovery-notes.md
├── general-product-requirement.md
├── feature-roadmap.md
├── architecture-baseline.md
└── releases/{REL-0.1.0-readiness.md,REL-0.1.0-result.yaml}
specs/
├── 001-single-file-transfer/{spec,plan,tasks,pre-implementation-review,verification,acceptance}.md + checklists/
└── 004-progress-view/{spec,wireframes,plan,tasks,pre-implementation-review,verification,acceptance}.md + checklists/
```

为了控制大型或长期项目的 context、token 与幻觉风险，即使走 Lite 也要：

1. 每个 lifecycle operation 使用新会话/fork/worker；pointer/index 是重建上下文的导航，
   不是聊天摘要。`guided-tdd-pairing` 只可在同一 implementation 内延续，不能跨 gate。
2. 先按 ID 搜索，再打开命中的 section；不要加载完整 PRD、roadmap、全部 specs 或 source tree。
3. 每个 Skill 只读其 operation 表列出的来源；每次至多选择一个完整 operation reference
   和 selected output variant 的最小 template set，不把前一个 Skill 的内容留作当前权威。
4. 真相只写一次，用路径和稳定 ID 引用；不要把摘要复制进 `AGENTS.md`、pointer 或多个报告。
5. CI 日志只保留失败片段、命令和 artifact link；大 diff 先按 changed paths 分区审阅。
6. `record-output`、generic `decide` 与专用决定命令会自动维护 index；只有 noncanonical
   indexed artifact 绕过这些命令发生 out-of-band 变化后才显式 `rebuild-index`，随后
   `validate --check-paths`；发现 revision 或 canonical path 冲突立即停，approved canonical
   漂移必须走 amendment。
7. 一个 pointer 只服务一个 worktree/session writer；并行 feature 使用独立 cursor 或外部 tracker。
8. 单个 slice ≤ 8 KiB、initial target payload ≤ 24 KiB；超出时按 ID/path 在 fresh workers
   分批并维护 coverage ledger，任何未覆盖或 truncated batch 都阻止完整/通过结论。

Lite 的目标不是“少做步骤”，而是让每一步只携带足够作出当前决定的证据。
