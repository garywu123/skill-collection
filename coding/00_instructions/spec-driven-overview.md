# SPEC Driven Overview

这是本集合的入口说明。它解释各能力的职责、选择顺序和边界；它不是 WMS 业务规范、
命令参考或可以自动连续执行的脚本。

## 它解决的问题

SPEC Driven Flow 把“想做什么”“为何可行”“如何实现”“是否真的完成”分别存放在拥有
该事实的工件中。AI 每次只做一个明确授权的操作；人类在每个审阅点决定是否继续。

```text
人类选择一个 operation
→ 一个 Skill 读取最小必要上下文
→ 只写自己拥有的工件
→ flow-state 脚本登记路径、哈希和候选 gate
→ Skill 报告并停止
→ 人类审阅并明确选择下一项 operation
```

流程箭头是前置关系，不是自动调用链。`next.recommended` 只是导航，不授予 AI 权限。

## 能力地图

| 编号 | 类别 | Skill / 工具 | 何时使用 | 主要产物 |
|---|---|---|---|---|
| `00` | 操作说明 | `00_instructions` | 先理解流程、WMS 示例、变更和命令 | 人类阅读文档 |
| `05` | 流程控制层 | `flow-state` + `flow_state.py` | 初始化、查询、记录候选状态、审批、索引 | pointer、index、receipt |
| `10` | 产品定义层 | `product-discovery-roadmap` | 业务尚不清晰，或产品/roadmap 发生变化 | discovery、PRD、roadmap、product amendment |
| `20` | 架构治理层 | `architecture-baseline` | 需要跨 Feature 的技术边界、ADR、spike 或架构变更 | architecture baseline、ADR、architecture amendment |
| `30` | Agent 工作规则层 | `bootstrap-agent-guidance` | 已有批准事实后，为 Agent 建立/刷新项目路由规则 | `AGENTS.md` 与薄适配器 |
| `35` | 产品/交互设计层 | `ui-wireframe-spec` | 有全局导航、共享 UI 或 Feature UI 时 | UI structure、wireframes |
| `40` | Feature 规格与计划层 | Spec Kit（外部） | 要交付一个具体 Feature 或实施工作项 | spec、plan、tasks、checklist |
| `50` | 实施一致性层 | `spec-sync` | 实施前检查对齐、实施后记录证据、或路由 Change Request | pre-review、verification、CR proposal |
| `60` | 实施协作层 | `guided-tdd-pairing` | 用户希望自己主写代码并进行小步 TDD 时 | 一次 RED/GREEN 协作 |
| `70` | 独立质量与交付层 | `delivery-gates` | 独立验收 Feature，审查、授权和记录 release | acceptance、release readiness、decision receipt |

`05`、`50` 和 `70` 不是产品阶段的拥有者：它们分别记录流程、检查纵向对齐、独立判断
交付质量。它们不改产品需求、架构或代码。

## 新项目的高层路径

```text
05 初始化状态
→ 10 Discovery → PRD → Roadmap
→ 确认 Full/Lite
→ 20 Architecture（适用时）
→ 30 Agent guidance 和 35 Product UI（适用时）
→ 对每个 Feature：40 → 50 pre → 实施 → 50 post → 70 acceptance
→ 70 release readiness → 人工授权 → 外部发布工具 → 记录结果
```

产品与 roadmap 是 Feature 开始前的来源；Architecture 通常应在首个高风险 Feature 前完成。
UI、TDD、架构深度和发布检查按适用性选择，不是无理由跳过。

## 已有项目的高层路径

先区分请求类型，随后只使用需要的路径：

| 变更 | 首选路径 |
|---|---|
| 新能力、业务规则或 roadmap 边界 | `spec-sync change-request` → product amendment → successor Feature |
| 跨 Feature 技术边界 | `spec-sync change-request` → architecture amendment → 受影响 work item |
| 行为缺陷 | `bug` work item + regression evidence |
| 不改变外部行为的改善 | `maintenance` work item |
| 数据变更 | `migration` work item + dry run/rollback/recovery |
| 权限或安全修复 | `security` work item + threat/abuse evidence |

已接受 Feature 的 spec、acceptance 和决定是历史证据，不能原地改写。行为变化创建说明
supersession 的后继 Feature，并重新验证和验收。

## 如何选择入口

- 不知道项目现在在哪里：`$flow-state status`。
- 还不清楚产品要做什么：`$product-discovery-roadmap discover`。
- 已批准产品，需要开始某个能力：进入该 Feature 的 Spec Kit specification。
- 不确定一项请求会影响产品、架构还是 Feature：`$spec-sync change-request CR-XXXX`。
- 已有实现证据，需要独立判断能否交付：`$delivery-gates accept-feature FXXX`。

详见 [WMS SPEC Drive Instruction](wms-spec-drive-instruction.md)、
[WMS Change Playbook](wms-change-playbook.md) 和
[Flow State Command Reference](flow-state-command-reference.md)。
