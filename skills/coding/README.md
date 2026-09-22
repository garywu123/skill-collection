# Coding Skill Collection

一套面向个人、小团队和 AI 主导开发的精简流程。默认维护三类核心文档：产品方向、
MVP Feature Map，以及每个 Feature 的计划与真实测试结果。有 UI 的 Feature 可以按需
增加一份低保真 Storyboard；MVP 大到一张 Feature Map 放不下时，再增加 Functional
Specification、Roadmap 和 General Design。Feature 规划和交付也支持保持行为不变的
精简；所有编码工作流都先复用现有能力，只增加当前结果所需的最少代码，并保留必要验证。

## 开发流程

```text
Product Brief
  -> Agent Instructions (AGENTS.md + docs/code-style.md + CLAUDE.md + Copilot)
  -> [scale only: Functional Spec -> Roadmap + General Design]
  -> Feature Map
  -> [optional Feature Storyboard]
  -> Feature Plan
  -> Feature Delivery (auto | guided)
```

生命周期 Skill 只由人显式点名调用（Claude Code 中为 `/skill-name`），不由 AI 根据
对话自动选择；`SKILL.md` 用 `disable-model-invocation: true` 声明这一点。Copilot 和
Codex 目前没有等价开关，只能依赖 description 中的 "Invoke explicitly, by name"。
一个已有或缺失的产物本身不授权相邻 Skill；一条指令明确覆盖多个结果时，才依次调用
多个 Skill。

变更只向下传播：Brief -> Spec -> Design -> Roadmap -> Map -> Plan -> 代码。交付发现
上游文档有误时，Delivery 停下报告，由人先改上游，再改 Map 行，再改 Plan。同一用户
结果的修复、扩展或重新验证复用原 Feature ID 和 Plan；独立的新结果才增加新 Feature。
共享 Design 变化由 Feature Map 找出受影响行、失效旧证据，再由 Feature Plan 修订需要
重新验证的任务。除本 README 的流程图外，不需要独立的 workflow、discovery、PRD、
checklist、spec sync 或审批文档。Git 保存历史；文档只保存当前事实。

## 使用示例

参见 [WMS 工作流示例](examples/wms-workflows.md)。

## Skills

| Skill | 作用 | 默认产物 |
|---|---|---|
| [`product-brief`](10.product-brief/SKILL.md) | 探索或记录产品目的、用户、核心流程和 MVP 边界 | 探索时仅对话；定稿时写 `docs/product-brief.md` |
| [`agent-instructions`](15.agent-instructions/SKILL.md) | 为软件、文档、分析、演示、运维和混合仓库生成或审计项目 agent 指令 | 三份根指令文件；软件项目另有 `docs/code-style.md`；按需增加 scoped instructions |
| [`functional-spec`](17.functional-spec/SKILL.md) | 仅当 MVP 需要多张 Feature Map 时，列出编号的可观察需求 | `docs/functional-spec.md` |
| [`feature-map`](20.feature-map/SKILL.md) | 确定 MVP Features、依赖、技术方向和整体架构；规模大时拆为 Roadmap、子 Map 和 General Design | `docs/feature-map.md`，或 `docs/feature-maps/` 与 `docs/design/` |
| [`feature-storyboard`](25.feature-storyboard/SKILL.md) | 按需展示一个 UI Feature 的关键状态和交互 | `docs/storyboards/<feature-id>-<slug>.html` |
| [`feature-plan`](30.feature-plan/SKILL.md) | 创建、修订或重开单个 Feature 的实现与验证计划 | `docs/features/<feature-id>-<slug>.md` |
| [`feature-delivery`](40.feature-delivery/SKILL.md) | 自动实现、精简或指导用户实现一个已规划 Feature，并记录真实测试结果 | 更新代码、Feature Plan 和 Feature Map 状态 |
| [`skill-authoring`](skill-authoring/SKILL.md) | 创建或精简本仓库中的 Skill | 目标 Skill 及本能力表 |
| [`skill-deployment`](skill-deployment/SKILL.md) | 将本仓库明确配置的 Skill 同步到 Copilot、Claude Code 和 Codex | 目标目录更新及受管清单 |
| [`markdown-reflow`](markdown-reflow/SKILL.md) | 用确定性脚本合并被硬换行拆散的 Markdown 段落,保留空行分段、标题、列表、引用、表格和代码块 | 按需修改指定的 `.md` 文件 |

## 文档边界

| 文档 | 只保存 | 不保存 |
|---|---|---|
| Product Brief | 产品目的、用户、核心流程、MVP 边界 | 需求编号、架构、流程 |
| Agent Instructions | 路由、优先级、已验证命令、沟通与工作规则；`AGENTS.md` 唯一权威，适配层不复制通用规则 | 产品内容、技术方向、代码风格规则 |
| `docs/code-style.md` | 仓库所有语言的代码风格规则，每种语言一节，工具已强制的规则只路由不复述 | 产品或流程内容 |
| Functional Spec | 编号的可观察需求、排除项、未决决策 | 状态、追溯表、架构、交付顺序 |
| General Design | 多张子 Map 共享的职责、契约、不变量和示例，每个可独立构建的栈一份 | 需求、顺序、状态、测试 |
| Roadmap | 子 Map 的顺序、分配的 FS ID、依赖和路径；文件存在后才使用链接 | 需求原文、设计、交付状态 |
| Feature Map | Feature 结果、引用的 FS ID、依赖、状态；单 Map 项目还包含技术方向和架构 | 需求原文、实现细节 |
| Feature Storyboard | 一个 UI Feature 的可见状态和转换 | 实现设计、测试、状态 |
| Feature Plan | 该 Feature 的实现步骤、测试设计和真实结果 | 上游内容的复制 |

下游文档链接上游文档，不复制上游内容。用户指定的既有 domain knowledge 只是可选
输入，不由任何 Skill 创建或维护。

## Feature 状态

- `planned`：尚未开始实现。
- `in_progress`：已经开始，当前仍可继续推进；测试失败或 guided mode 等待用户实现
  时仍使用此状态。
- `blocked`：存在一个具体条件，使当前无法继续。
- `verified`：所有计划场景已实际通过且没有 blocker。

状态只写在 Feature Plan 和 Feature Map 行。已 `verified` 的 Feature 在当前需求或设计
使原证据失效时回到 `planned`，受影响结果回到 `not run`；开始重新交付后再进入
`in_progress`。一个 FS 需求必须分配到 Map 或未来 Roadmap 行；只有至少一行 Map 引用
它、且所有引用它的 Map 行都 `verified` 时才视为交付。Spec 本身不打勾。每个 Skill
在创建或修改文档后，都必须扫描项目中的相关文档，检查冲突、重复、过期名称、路径和
状态。机械问题在同一轮修正；只有
会改变产品行为、UI 交互、技术方向或职责边界的语义决定才询问用户。各项能力的详细
契约以对应 `SKILL.md` 为准；本文件只维护公开能力和文档边界。
