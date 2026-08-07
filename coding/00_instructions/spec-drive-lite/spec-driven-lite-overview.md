# SPEC Driven Lite 总览

这是本集合的入口说明。它解释各能力的职责、选择顺序和边界；它不是 WMS 业务规范，
也不是可以自动连续执行的脚本。

## 控制模型

把「想做什么」「为何可行」「如何实现」「是否真的完成」分别存放在拥有该事实的工件
里。AI 每次只做一个你明确要求的操作；每个审阅点由你决定是否继续。

```text
你口述一个操作
→ 一个 Skill 读取最小必要上下文
→ 只写自己拥有的工件
→ 顺手更新 roadmap.yaml 里对应的那一行
→ Skill 报告并停止
→ 你审阅，然后口述下一个操作
```

**状态转换是你口述的，不是脚本执行的。** `roadmap.yaml` 只负责*记录*现在在哪里，
它不拦截、不批准、不决定下一步。流程图里的箭头是前置关系，不是自动调用链。

整个状态只有一个文件：仓库根目录的 `roadmap.yaml`。它存路径和状态，不存需求、
不存设计理由、不存历史——那三样分别归它指向的文档和 git 管。
字段规格见 [roadmap 规格](../../20.project-map/references/roadmap-spec.md)。

Project Map 拥有它的 schema、初始化、整体 refresh 和 audit；当前被你授权的 Skill
只回写本次工作直接改变的 `docs` 路径或 function entry。每个操作在最终报告前核对一次，
没有事实变化就不制造状态 diff，也不推进无关条目。

## 每条消息怎么说

正常操作使用同一个句式：

```text
使用 $<skill-name> 执行 <operation + target>；
本次只处理 <scope>；完成后回写本次实际改变的 roadmap.yaml 条目，报告并停止。
```

批准也调用拥有该工件的 Skill，并明确 actor、date 和 evidence，例如：

```text
使用 $product-discovery-roadmap approve-prd；
我 Gary Wu 于 2026-08-07 批准当前 PRD，依据是本消息；只记录批准并停止。
```

Spec Kit 和普通实现不是本集合的 Skill，指南会明确标成“Spec Kit”或“无需 Skill”。
checklist 验证同样无需 Skill，但必须开新对话，并由你明确作出 accepted 或 changes requested
决定。下面三份模式指南给出了每一步可以直接改写使用的完整话术。

## 能力地图

| 编号 | 类别 | Skill / 工具 | 何时使用 | 主要产物 |
|---|---|---|---|---|
| `00` | 操作说明 | `00_instructions` | 先理解三种模式和 WMS 示例 | 人类阅读文档 |
| `05` | 产品定义层 | `product-discovery-roadmap` | 业务尚不清晰，或产品/roadmap 变化 | discovery、PRD、roadmap、产品修订 |
| `10` | 架构治理层 | `architecture-baseline` | 需要跨 function 的技术边界、ADR、spike | architecture baseline、ADR、架构修订 |
| `20` | 项目地图层 | `project-map` | 建立或刷新项目路由、状态与文件夹记录 | `roadmap.yaml`、`AGENTS.md`、薄适配器 |
| `30` | 产品/交互设计层 | `ui-wireframe-spec` | 有全局导航、共享 UI 或 function UI 时 | UI structure、wireframes |
| `40` | 规格与计划层 | Spec Kit（外部） | 要交付一个具体 function | spec、plan、tasks |
| `50` | 实施一致性层 | `spec-sync` | 实施前检查对齐、实施后记录证据、路由变更请求 | pre-review、证据、CR 提案 |
| `60` | 实施协作层 | `guided-tdd-pairing` | 你想自己主写代码、小步 TDD 时 | 一次 RED/GREEN 协作 |

`20` 和 `50` 不拥有产品阶段：`20` 记录地图和状态，`50` 检查纵向对齐。两者都不改
产品需求、架构或代码，也都不能批准任何东西。

交付门禁没有独立的 Skill。它是每个 function 自己的 `checklist.md`，在写 spec 的
同时写出来，**在一个新对话里**核对。写代码的上下文不给自己的作业打勾。

## 三种模式

| 模式 | 什么时候用 | 文档 |
|---|---|---|
| 一 | 全新项目，从业务访谈开始 | [新项目](wms-new-project.md) |
| 二 | 项目在跑，要改一个已有 function | [变更请求](wms-change-request.md) |
| 三 | 已有仓库，此前没用过这套流程 | [已有仓库接入](wms-existing-repo.md) |

三份文档都用同一个 WMS 作例子，可以对照着读。
[新项目](wms-new-project.md)第 4 节给了一个项目大致会有哪些文件。

## 如何选择入口

- 不知道项目现在在哪里：读仓库根目录的 `roadmap.yaml`。
- 还不清楚产品要做什么：`$product-discovery-roadmap discover`。
- 已批准产品，要开始某个能力：进入该 function 的 Spec Kit specification。
- 不确定一项请求会影响产品、架构还是单个 function：`$spec-sync change-request CR-XXXX`。
- 已有实现证据，要判断能否交付：**开一个新对话**，核对该 function 的 `checklist.md`。
- 仓库还没有 `roadmap.yaml`：`$project-map init`。

## 关于 `_obsolete/`

`flow-state` 与 `delivery-gates` 两个 Skill 已停用，连同旧的 `spec-driven-flow.md`
一起移到 `coding/_obsolete/`。它们描述的是一套用 `flow_state.py` 强制状态转换、
用 SHA-256 绑定审批的流程。停用的原因是：单人项目里，那套机制在防范一个不存在的
威胁（多写者篡改已批准事实），而它的成本是实打实的——两个 Skill、5500 行 Python
与测试、1080 行示例文档，外加每个 SKILL.md 约六分之一的篇幅用在 revision 和哈希
协议上，而不是用在正事上。

git 承担历史与漂移检测，`roadmap.yaml` 承担状态记录，checklist 承担交付标准，
新对话承担独立性。什么时候发现这四样确实不够，再从 `_obsolete/` 里把需要的那一件
拿回来——按遇到的具体失败来取，不要预先全套装上。
