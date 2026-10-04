# Coding Skill Collection

一套面向个人、小团队和 AI 主导开发的精简流程。默认维护三类核心文档：产品方向、
MVP Feature Map，以及每个 Feature 的计划与真实测试结果。需要共享技术方向时由
Architecture Design 单独维护架构，需要可复用测试规则时增加 Testing Strategy；有 UI
的 Feature，或拆 Feature 之前的早期产品问题，可以按需增加一份低保真 Storyboard；MVP
大到一张 Feature Map 放不下时，再增加 Functional Specification 和 Roadmap。Feature 规划和交付也支持保持行为不变的
精简；所有编码工作流都先复用现有能力，只增加当前结果所需的最少代码，并保留必要验证。

## 开发流程

```text
Product Brief
  -> Coding Agent Instructions (AGENTS.md)
  -> Code Style (docs/code-style.md)
  -> [scale only: Functional Spec]
  -> Architecture Design (docs/architecture.md)
  -> [optional Testing Strategy (docs/testing.md)]
  -> [scale only: Roadmap +] Feature Map
  -> [optional Feature Storyboard]
  -> Feature Plan
  -> Feature Delivery (auto | guided)
```

`feature-map`、`feature-plan`、`feature-delivery` 可由模型根据用户请求自动选择，也可
显式调用。它们共享一份 `SKILL.md` 正文和 description：Claude Code 用 frontmatter 的
`disable-model-invocation: false`；Codex 用同目录 `agents/openai.yaml` 的
`policy.allow_implicit_invocation: true`。其他生命周期 Skills 与 `cross-agent` 保持
显式调用边界；Copilot 的发现依其客户端支持，不能假定它识别这两个平台专用字段。
自动选择 Skill 不扩大授权：只请求规划时停在规划，要求完成一个 Feature 时可按已授权
结果衔接必要规划和交付；缺失产物本身不授权创建新产品范围。

Product Brief 和 Functional Spec 可以对照用户授权的访谈证据编写或 `review`：区分用户
原话和模型建议、已确认决定和候选、最新决定和被取代的说法；有出处时保留位置或简短
原文，绝不编造 transcript 或出处。争议或高影响的说法回查原文，作者自己的摘要不能单独
证明用户意图；只有用户要求或已授权的 discovery 流程才保存笔记。小项目没有 Spec 时，
用户确认的产品级约束（内存、延迟、容量等）写在 Brief 的 Product Constraints；有 Spec
时归 Spec。Architecture 只把它们转成技术决定或预算分配，Testing Strategy 只定义测量
方法；没人设定的预算是待决问题，不编数字。Spec 仍是可选的，只在一张 Map 无法保持
可读时才建，需求数量或文档长度本身不是理由。

拆 Feature 之前，`feature-storyboard` 可以从 Brief、Spec 章节或明确的产品问题出发，
写 `docs/storyboards/<topic-slug>.html`，不虚构 Feature ID；未确认的行为标为
`candidate`，草图不确认需求。之后对应 Feature 的 Plan 链接同一文件并沿用 `S*`/`T*`
ID。浏览器验证、低保真和不实现产品逻辑的边界不变。

Feature Map 拆独立用户结果；Feature Plan 评估执行规模、依赖、阶段验收、交接与委派。
一个独立结果只有一份 Plan；执行很长只拆 segment，不拆新 Feature；一份 Plan 含多个
独立结果时，Plan 停下并请求修订 Map。小功能默认单阶段串行；大功能在同一份 Plan 中
用紧凑表安排多个执行 segment/session，最后整体回归。Plan 没有固定行数上限，但只写
本 Feature 的内容；开头保持当前执行位置（已完成/下一段、剩余检查、blocker），新
session 不依赖旧对话即可接手。Plan 读取 Testing Strategy，按真实用户、数据、负载和
失败后果推导风险，只问少量会改变设计或验收的问题。Feature Delivery 按计划执行并重新
核实委派边界；只有收益超过背景加载和整合成本的独立任务才开 sub-agent，最多同时三个，
并受环境限制。

没有 Feature 的有界技术问题（可行性、性能、选型）用 `feature-plan` 的 standalone
validation 写 `docs/plans/<topic>.md`，不需要 Brief、Map 或虚构的 Feature ID；
`feature-delivery` 执行它。执行状态（`completed`/`incomplete` 等）与结论
（`supported`/`not supported`/`inconclusive`）分开：否定结论也算完成实验，证据缺失则是
`incomplete`；实验不验证任何 Feature。

`cross-agent`（Orch）让当前会话像 PM 一样理解任务、安排阶段并汇报实时进度，适用于
设计、带总体设计的 Roadmap、重构计划与执行，以及指定 Features。Skill 自带的 CLI
（Python 3.11+）每个 run 仍只处理一个阶段和一个 artifact，启动 Claude Code 或 Codex
Producer 与只读 Reviewer。用户一次授权多个阶段时，Orch 在前一阶段通过后自动继续，
每个阶段使用新 session；用户要求人工批准时等待回复。只请求规划不会自动授权执行。
`next --stream` 显示阶段 Skill 正文注入成功（路径/hash/加载方式）、worker 就绪后的阶段
开始、活动、可获得的模型/context/sub-agent 信息和心跳；未知数据明确标注。CLI 对
Producer 的 timeout/明确瞬态连接错误每 run 自动恢复一次，优先 resume 原 session；
失效 session 或超过 context 阈值才替换，并保留历史。默认单次调用仍为 30 分钟硬上限。
失败的执行可在修复原因后用 `retry-producer` 明确重试；`retry-review` 保留 Producer 与
审阅预算，blocker 通过 `answer` 传递用户决定，schema 和只读校验失败不可绕过。
执行阶段的 `checkpoint` 保存真实验收证据与未完成工作，下一次 `next` 新开 Producer
session；仍为同一个 run，原始 baseline、findings 和 review 预算保留，不提前送审。
每 run 最多八个 checkpoint；全部完成后才整体检查并交给 Reviewer。
只有用户请求或项目规则明确授权 commit 时，Orch 才在每个完成的有界 section（一次设计、
规划、审阅或交付 run，或 Plan segment 的 checkpoint）结束、worker 停止后提交本地 commit：
只按路径提交该 section 的变更，不碰用户其他暂存、未跟踪文件和私有配置；message 写真实
结果（checkpoint 未独立审阅、`independently-passed`、`completed-by-orchestrator`、失败
等），commit 不代表验证通过；默认不 amend、push、reset 或空 commit。失败 section 可保留
恢复 commit，但停止依赖工作、不回滚也不关闭 run；可用的一次自动恢复照常进行，commit
既不消耗也不补充任何预算。commit 不改变 run 的原始 baseline、findings 和预算，最终评审
仍覆盖已提交的 segment。checkpoint 先于 commit 保存，所以执行阶段的 `start --request`
要求每个后续 Producer 先用 `git log -1 --format=%h` 读取当前 revision；新 run 的请求直接
写明 revision。worker 永不 commit；直接调用的
Feature Delivery 只有获得明确授权时才按 segment commit。Skill 本身不构成 commit 授权。
每次评审都附带该 revision 固定的确定性测试变更摘要：测试、fixture/mock、runner/配置路径
与原始 hunk，支持框架的 skip/过滤标记，以及检查退出码；计数只来自 `test_reports`
配置的新鲜 JUnit XML，其余为未知。未检测到变化不代表测试充分。
CLI 自动保存 `.cross-agent/history/<run-id>.csv`：每次 Producer/Reviewer 调用一行，
包括 Feature/主题、round、segment/session、模型/effort、UTC 起止时间、耗时、状态和
可获得的 token 用量；`start --item` 可让同一功能跨阶段使用相同分组。
`history` 命令汇总到 `.cross-agent/history.csv`，`close` 后仍保留。未知用量留空，
部分用量明确标注；统计范围是父 worker 调用，不包含当前 Orch，不能保证覆盖子 agent。
用户把失败的 Delivery 转回规划时，`park` 暂存旧 run 并保留历史；同一 Plan 独立审阅
通过后，`resume-delivery` 新开 Producer，保留原 Delivery baseline 和剩余预算。
在对话中显式请求 `cross-agent initiate` 时，Orch 根据项目说明和已有构建、测试定义选择命令，
通过 CLI 的 `init` 创建当前项目根目录的 `.cross-agent/config.toml`，保存 Producer/Reviewer
的模型和 effort，并检测已安装 Codex CLI 与 npm 最新发布版本；已有设置保留并报告差异。
新配置从 `cross-agent/assets/config.example.toml` 初始化；Python 不提供运行默认值。
后续调用只读取项目配置，运行控制参数、完整的 `provider:model:effort`、所选 CLI 的绝对路径
和当前项目的三个字段必须齐全，缺项报错；空命令或目录列表必须明确写成 `[]`。
可选的 `[stages.<阶段>]` 可用同样完整格式为该阶段设置 `producer` / `reviewer`；每个角色
依次取 run 覆盖、阶段角色、默认角色，`status` 与 run 事件显示最终选择和来源，无效选择
在启动 worker 前失败。run 保存启动时的角色和 Skill 路径，之后改配置不影响已打开的 run。
`general` 只有在 `[stages.general]` 明确配置 `skill` 时才注入该 Skill。
默认不读取用户目录或父目录配置。可用单层 `config_file` 入口共享 workspace 配置，各项目命令保持分区；启动、恢复和版本检测使用配置中的同一 CLI 选择，路径缺失或失效时不回退 PATH。初始化不自动升级 CLI、不执行项目测试或启动 worker；
无法检测版本时明确报告未知，缺少配置本身不触发初始化。

变更只向下传播：Brief -> Spec -> Architecture/Testing Strategy -> Roadmap -> Map ->
Plan -> 代码。交付发现上游文档有误或中途收到已授权的变更时，Delivery 停下受影响的
工作并报告；由用户，或在已授权目标内由 `cross-agent` Orch 协调，先改上游 owner，再改
所有受影响的中间契约（如 Architecture Design、Testing Strategy），再改 Storyboard 和
Map 行，再改 Plan（记录一行原因和影响），只把失效的结果重置为 `not run`；这些 owner
都对齐之后才能做下游验收。架构、测试策略、命令、项目结构或文档路由变化后，需要由
`coding-agent-instructions` 的 `assess` 给每个相关指令文件一个结果：`updated`（附已验证
证据的机械更新）、`unchanged`（附原因）或 `unresolved`（附原因和需要的决定）；新的语义
规则只上报不写入。这是评估，不是每个 Feature 都改 `AGENTS.md`。Orch 只为实质影响产品行为、已接受约束、权限、成本或用户明确关卡的未决
选择询问用户；任何 agent 都不能为了让测试通过而改写权威输入。同一用户结果的修复、
扩展或重新验证复用原 Feature ID 和 Plan；独立的新结果才增加新 Feature。Architecture Design 变化由 `architecture-design` 报告受影响的行和
Plan，再由 Feature Map 失效旧证据、Feature Plan 修订需要重新验证的任务。除本 README 的流程图外，不需要独立的 workflow、discovery、PRD、
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
| [`product-brief`](10.product-brief/SKILL.md) | 探索、记录或对照授权访谈证据审阅产品目的、用户、核心流程、MVP 边界和已确认的产品级约束 | 探索和审阅时仅对话；定稿时写 `docs/product-brief.md` |
| [`coding-agent-instructions`](15.coding-agent-instructions/SKILL.md) | 为含代码的仓库创建、审计或持续校准 `AGENTS.md`；变化后做 instruction-impact assessment；纯非代码仓库交由所属集合的同类 Skill | 根 `AGENTS.md`；只有真实局部差异时才增加 nested `AGENTS.md`；assessment 结果在报告中 |
| [`code-style`](16.code-style/SKILL.md) | `define` 确认实际语言并写出结构、模块组织、注释意图、文档和关键算法说明的规范；`audit` 报告指定范围的偏差；`apply` 在授权代码范围内按既有规则做保持行为的修改并运行已验证检查 | `docs/code-style.md`、真实局部差异的 `<subproject>/docs/code-style.md`，以及 `AGENTS.md` 中的一行路由 |
| [`functional-spec`](17.functional-spec/SKILL.md) | 仅当 MVP 需要多张 Feature Map 时，列出编号的可观察功能和产品级质量需求；可对照 Brief 和授权访谈证据审阅 | `docs/functional-spec.md` |
| [`architecture-design`](18.architecture-design/SKILL.md) | 探索、编写、审阅唯一的共享架构：组件边界、契约、数据所有权、依赖方向、部署假设和技术质量约束；把 Map 内的技术方向或既有 General Design 迁移过来 | `docs/architecture.md`，或沿用既有 General Design 路径 |
| [`testing-strategy`](19.testing-strategy/SKILL.md) | 编写或审阅可复用的项目测试规则：测试层级、业务不变量、算法 oracle、fixture 规模、资源测量方法、回归和独立测试条件；未定预算记为待决 | `docs/testing.md` |
| [`feature-map`](20.feature-map/SKILL.md) | 选择合适规模的 MVP 交付结构：小项目一张 Map，大项目拆为 Roadmap 和子 Map；只管结果、依赖和状态，链接 Architecture Design | `docs/feature-map.md`，或 `docs/feature-maps/` |
| [`feature-storyboard`](25.feature-storyboard/SKILL.md) | 按需展示一个 UI Feature，或拆 Feature 前一个早期产品问题的关键状态和交互 | `docs/storyboards/<feature-id>-<slug>.html`；早期为 `docs/storyboards/<topic-slug>.html` |
| [`feature-plan`](30.feature-plan/SKILL.md) | 创建、修订或重开单个 Feature 的实现与验证计划（分段、当前执行位置、风险与测试设计）；或为有界技术问题写 standalone validation 计划 | `docs/features/<feature-id>-<slug>.md`；validation 为 `docs/plans/<topic>.md` |
| [`feature-delivery`](40.feature-delivery/SKILL.md) | 自动实现、精简或指导用户实现一个已规划 Feature，增量 TDD 并记录真实测试结果，每个最终结果（含 validation 证据）绑定实际测试的 revision、相关路径和 dirty 内容标识（后续相关变更才使其失效）；选定独立关卡时只报告 readiness；或执行 validation 计划并分别记录执行状态与结论；在 Orch 下不 commit，直接调用且明确授权时按 segment commit | 更新代码、Feature Plan 和 Feature Map 状态；validation 只更新其计划 |
| [`cross-agent`](cross-agent/SKILL.md) | `initiate` 初始化 repo 独立配置、模型/effort（可按阶段设置）和 Codex CLI 版本检测；PM 式 Orch 编排已授权的设计、规划、执行或多 Feature 阶段，实时汇报 worker 状态；每阶段独立 Producer/Reviewer run，限定审阅次数并裁决 findings，每次评审附确定性测试变更摘要，按功能/主题保留调用历史；明确授权时由 Orch 逐 section 提交本地 commit | 项目根目录 `.cross-agent/config.toml`；各阶段 artifact 与对话进度；`.cross-agent/history/` 的时间与用量 CSV，`history` 可汇总；非阻塞遗留项追加到 `docs/review-backlog.md` |
| [`skill-authoring`](skill-authoring/SKILL.md) | 创建或精简本仓库中的 Skill | 目标 Skill 及本能力表 |
| [`skill-deployment`](skill-deployment/SKILL.md) | 将本仓库明确配置的 Skill 同步到 Copilot、Claude Code 和 Codex | 目标目录更新及受管清单 |
| [`markdown-reflow`](markdown-reflow/SKILL.md) | 用确定性脚本合并被硬换行拆散的 Markdown 段落,保留空行分段、标题、列表、引用、表格和代码块 | 按需修改指定的 `.md` 文件 |

## 文档边界

| 文档 | 只保存 | 不保存 |
|---|---|---|
| Product Brief | 产品目的、用户、核心流程、MVP 边界；没有 Spec 时保存已确认的产品级约束 | 需求编号、架构、流程、访谈记录 |
| Coding Agent Instructions | 路由、优先级、已验证命令、边界、工作与报告规则；基于权威证据持续校准 | 产品内容、技术方向、代码风格规则、一次性任务状态、工具专用适配层、assessment 记录 |
| `docs/code-style.md` | 仓库共享的代码风格规则，每种语言一节，外加模块组织、结构、注释、文档等跨语言规范，并列出 scoped 文件；工具已强制的规则只路由不复述；`<subproject>/docs/code-style.md` 只保存真实局部差异 | 产品或流程内容、架构依赖方向与系统边界、工具配置本身、重复的共享规则 |
| Functional Spec | 编号的可观察功能和产品级质量需求、排除项、未决决策 | 状态、追溯表、架构、交付顺序 |
| Architecture Design | 共享的系统上下文、组件职责、契约、数据所有权、依赖方向、技术选型、部署假设、质量约束（主体、条件、属性或预算、来源、验证引用）和不变量；既有 General Design 即为此文档；仅在需要大量独立指导时按栈拆分 | 需求原文、Feature 列表、顺序、状态、测试用例、代码级风格规则 |
| Testing Strategy | 可复用的测试层级、业务不变量与来源、算法 oracle、fixture 与 mock 限制、发现与 skip 规则、资源测量方法、回归和独立测试条件 | 逐 Feature 用例、测试结果、产品需求或资源预算本身 |
| Roadmap | 子 Map 的顺序、分配的 FS ID、依赖和路径；文件存在后才使用链接 | 需求原文、设计、交付状态 |
| Feature Map | Feature 结果、引用的 FS ID、依赖、状态和 Architecture Design 链接 | 需求原文、技术方向、架构、实现细节 |
| Feature Storyboard | 一个 UI Feature 或早期产品问题的可见状态和转换，未确认行为标为 `candidate` | 已确认需求、虚构 Feature ID、实现设计、测试、状态 |
| Feature Plan | 该 Feature 的当前执行位置、执行阶段、依赖、验收、交接、委派选择、测试设计、选定的独立关卡、关键决定与变更原因，以及真实结果 | 上游内容的复制、transcript 和例行活动日志 |
| Validation Plan | 一个有界问题的假设、输入、oracle、步骤、指标、预算与停止条件、证据、判定标准、执行状态和结论 | Feature ID、Map 状态、所支持决定的正文 |
| Review Backlog | `cross-agent` 裁决后未进入本次修订的非阻塞遗留项及其理由 | 未告知用户的当前 blocker、prompt、transcript、token 日志、快照、需求或计划内容 |

下游文档链接上游文档，不复制上游内容。用户指定的既有 domain knowledge 只是可选
输入，不由任何 Skill 创建或维护。

## Feature 状态

- `planned`：尚未开始实现。
- `in_progress`：已经开始，当前仍可继续推进；测试失败或 guided mode 等待用户实现
  时仍使用此状态。
- `blocked`：存在一个具体条件，使当前无法继续。
- `verified`：所有计划场景和选定的独立关卡都已实际通过且没有 blocker。

选定独立审阅或测试关卡时，Producer 完成实现和自测只是该关卡的 readiness，状态保持
`in_progress`；关卡通过后由 Producer 的后续调用或用户授权的仅改状态收尾写入
`verified`，Reviewer 始终只读。`completed-by-orchestrator` 不是独立通过。没有选定关卡
时沿用原完成路径。Validation Plan 不使用这些 Feature 状态：选定关卡时 Producer 照常
记录执行状态和结论，关卡行保持 `not run`，通过后只更新关卡行和当前位置。

状态只写在 Feature Plan 和 Feature Map 行。已 `verified` 的 Feature 在当前需求或设计
使原证据失效时回到 `planned`，受影响结果回到 `not run`；开始重新交付后再进入
`in_progress`。一个 FS 需求必须分配到 Map 或未来 Roadmap 行；只有至少一行 Map 引用
它、且所有引用它的 Map 行都 `verified` 时才视为交付。Spec 本身不打勾。每个 Skill
在创建或修改文档后，都必须扫描项目中的相关文档，检查冲突、重复、过期名称、路径和
状态。机械问题在同一轮修正；只有
会改变产品行为、UI 交互、技术方向或职责边界的语义决定才询问用户。各项能力的详细
契约以对应 `SKILL.md` 为准；本文件只维护公开能力和文档边界。
