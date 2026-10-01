# Coding Skill Collection

一套面向个人、小团队和 AI 主导开发的精简流程。默认维护三类核心文档：产品方向、
MVP Feature Map，以及每个 Feature 的计划与真实测试结果。有 UI 的 Feature 可以按需
增加一份低保真 Storyboard；MVP 大到一张 Feature Map 放不下时，再增加 Functional
Specification、Roadmap 和 General Design。Feature 规划和交付也支持保持行为不变的
精简；所有编码工作流都先复用现有能力，只增加当前结果所需的最少代码，并保留必要验证。

## 开发流程

```text
Product Brief
  -> Coding Agent Instructions (AGENTS.md)
  -> Code Style (docs/code-style.md)
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

`cross-agent`（Orch）让当前会话像 PM 一样理解任务、安排阶段并汇报实时进度，适用于
设计、带总体设计的 Roadmap、重构计划与执行，以及指定 Features。Skill 自带的 CLI
（Python 3.11+）每个 run 仍只处理一个阶段和一个 artifact，启动 Claude Code 或 Codex
Producer 与只读 Reviewer。用户一次授权多个阶段时，Orch 在前一阶段通过后自动继续，
每个阶段使用新 session；用户要求人工批准时等待回复。只请求规划不会自动授权执行。
`next --stream` 提供活动、可获得的模型/context/sub-agent 信息和心跳；未知数据明确标注。
Reviewer 执行失败后，用户明确授权恢复时可用 `retry-review` 保留 Producer 与审阅预算；
Producer 报告的 blocker 可通过 `answer` 传递用户的恢复决定，校验失败仍不可绕过。
在对话中显式请求 `cross-agent initiate` 时，Orch 根据项目说明和已有构建、测试定义选择命令，
通过 CLI 的 `init` 创建当前项目根目录的 `.cross-agent/config.toml`，保存 Producer/Reviewer
的模型和 effort，并检测已安装 Codex CLI 与 npm 最新发布版本；已有设置保留并报告差异。
默认不读取用户目录或父目录配置。初始化不自动升级 CLI、不执行项目测试或启动 worker；
无法检测版本时明确报告未知，缺少配置本身不触发初始化。

变更只向下传播：Brief -> Spec -> Design -> Roadmap -> Map -> Plan -> 代码。交付发现
上游文档有误时，Delivery 停下报告，由人先改上游，再改 Map 行，再改 Plan。同一用户
结果的修复、扩展或重新验证复用原 Feature ID 和 Plan；独立的新结果才增加新 Feature。
共享 Design 变化由 Feature Map 找出受影响行、失效旧证据，再由 Feature Plan 修订需要
重新验证的任务。除本 README 的流程图外，不需要独立的 workflow、discovery、PRD、
checklist、spec sync 或审批文档。唯一例外是 `cross-agent` 追加的
`docs/review-backlog.md`：它是人拥有的非权威待办，agent 只在用户明确要求审阅
backlog 或点名条目时才读取；条目先由用户提升到当前请求或对应的 Feature Map 与
Plan，才成为实现范围。Git 保存历史；文档只保存当前事实。

## 使用示例

参见 [WMS 工作流示例](examples/wms-workflows.md)。

跨模型编排的初始化、配置和完整案例，参见 [Cross-agent 使用教程](_doc/cross-agent-guide.md)。

## Skills

| Skill | 作用 | 默认产物 |
|---|---|---|
| [`product-brief`](10.product-brief/SKILL.md) | 探索或记录产品目的、用户、核心流程和 MVP 边界 | 探索时仅对话；定稿时写 `docs/product-brief.md` |
| [`coding-agent-instructions`](15.coding-agent-instructions/SKILL.md) | 为含代码的仓库创建、审计或持续校准 `AGENTS.md`；纯非代码仓库交由所属集合的同类 Skill | 根 `AGENTS.md`；只有真实局部差异时才增加 nested `AGENTS.md` |
| [`code-style`](16.code-style/SKILL.md) | 确认项目实际使用的语言，写出模块边界、结构、注释意图、文档和关键算法说明的规范，并回写 `AGENTS.md` 路由 | `docs/code-style.md` 及 `AGENTS.md` 中的一行路由 |
| [`functional-spec`](17.functional-spec/SKILL.md) | 仅当 MVP 需要多张 Feature Map 时，列出编号的可观察需求 | `docs/functional-spec.md` |
| [`feature-map`](20.feature-map/SKILL.md) | 选择合适规模的 MVP 交付结构：小项目维护一张含共享设计的 Map，大项目拆为 Roadmap、子 Map 和 General Design | `docs/feature-map.md`，或 `docs/feature-maps/` 与 `docs/design/` |
| [`feature-storyboard`](25.feature-storyboard/SKILL.md) | 按需展示一个 UI Feature 的关键状态和交互 | `docs/storyboards/<feature-id>-<slug>.html` |
| [`feature-plan`](30.feature-plan/SKILL.md) | 创建、修订或重开单个 Feature 的实现与验证计划 | `docs/features/<feature-id>-<slug>.md` |
| [`feature-delivery`](40.feature-delivery/SKILL.md) | 自动实现、精简或指导用户实现一个已规划 Feature，并记录真实测试结果 | 更新代码、Feature Plan 和 Feature Map 状态 |
| [`cross-agent`](cross-agent/SKILL.md) | `initiate` 初始化 repo 独立配置、模型/effort 和 Codex CLI 版本检测；PM 式 Orch 编排已授权的设计、规划、执行或多 Feature 阶段，实时汇报 worker 状态；每阶段独立 Producer/Reviewer run，限定审阅次数并裁决 findings | 项目根目录 `.cross-agent/config.toml`；任务产出各阶段 artifact 与对话进度，非阻塞遗留项追加到 `docs/review-backlog.md` |
| [`skill-authoring`](skill-authoring/SKILL.md) | 创建或精简本仓库中的 Skill | 目标 Skill 及本能力表 |
| [`skill-deployment`](skill-deployment/SKILL.md) | 将本仓库明确配置的 Skill 同步到 Copilot、Claude Code 和 Codex | 目标目录更新及受管清单 |
| [`markdown-reflow`](markdown-reflow/SKILL.md) | 用确定性脚本合并被硬换行拆散的 Markdown 段落,保留空行分段、标题、列表、引用、表格和代码块 | 按需修改指定的 `.md` 文件 |

## 文档边界

| 文档 | 只保存 | 不保存 |
|---|---|---|
| Product Brief | 产品目的、用户、核心流程、MVP 边界 | 需求编号、架构、流程 |
| Coding Agent Instructions | 路由、优先级、已验证命令、边界、工作与报告规则；基于权威证据持续校准 | 产品内容、技术方向、代码风格规则、一次性任务状态、工具专用适配层 |
| `docs/code-style.md` | 仓库所有语言的代码风格规则，每种语言一节，外加模块边界、结构、注释、文档等跨语言规范；工具已强制的规则只路由不复述 | 产品或流程内容、工具配置本身 |
| Functional Spec | 编号的可观察需求、排除项、未决决策 | 状态、追溯表、架构、交付顺序 |
| General Design | 多张子 Map 共享的系统或栈上下文、职责、契约、数据所有权、质量约束、不变量和示例；仅在需要大量独立指导时按栈拆分 | 需求原文、顺序、状态、测试、穷举依赖 |
| Roadmap | 子 Map 的顺序、分配的 FS ID、依赖和路径；文件存在后才使用链接 | 需求原文、设计、交付状态 |
| Feature Map | Feature 结果、引用的 FS ID、依赖、状态；单 Map 项目还包含技术方向和架构 | 需求原文、实现细节 |
| Feature Storyboard | 一个 UI Feature 的可见状态和转换 | 实现设计、测试、状态 |
| Feature Plan | 该 Feature 的实现步骤、测试设计和真实结果 | 上游内容的复制 |
| Review Backlog | `cross-agent` 裁决后未进入本次修订的非阻塞遗留项及其理由 | 未告知用户的当前 blocker、prompt、transcript、token 日志、快照、需求或计划内容 |

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
