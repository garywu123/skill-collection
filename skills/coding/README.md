# Coding Skill Collection

一套面向个人、小团队和 AI 主导开发的精简流程。默认维护三类核心文档：产品方向、
MVP Feature Map，以及每个 Feature 的计划与真实测试结果。需要共享技术方向时由
Architecture Design 单独维护架构，需要可复用测试规则时增加 Testing Strategy；有 UI
的 Feature，或拆 Feature 之前的早期产品问题，可以按需增加一份低保真 Storyboard；用户
要求时可以增加 Functional Specification，MVP 大到一张 Feature Map 放不下时再增加 Spec 和 Roadmap。Feature 规划和交付也支持保持行为不变的
精简；所有编码工作流都先复用现有能力，只增加当前结果所需的最少代码，并保留必要验证。

## 开发流程

```text
Product Brief
  -> Coding Agent Instructions (AGENTS.md)
  -> Code Style (docs/code-style.md)
  -> [optional: Functional Spec]
  -> Architecture Design (docs/architecture.md)
  -> [optional Testing Strategy (docs/testing.md)]
  -> [scale only: Roadmap +] Feature Map
  -> [optional Feature Storyboard]
  -> Feature Plan
  -> Feature Delivery (auto | guided)
```

`feature-map`、`feature-plan`、`feature-delivery`、`cross-agent` 可由模型根据用户请求自动选择，也可
显式调用。它们共享一份 `SKILL.md` 正文和 description：Claude Code 用 frontmatter 的
`disable-model-invocation: false`；Codex 用同目录 `agents/openai.yaml` 的
`policy.allow_implicit_invocation: true`。其他生命周期 Skills 保持
显式调用边界；Copilot 的发现依其客户端支持，不能假定它识别这两个平台专用字段。
自动选择 Skill 不扩大授权：只请求规划时停在规划，要求完成一个 Feature 时可按已授权
结果衔接必要规划和交付；缺失产物本身不授权创建新产品范围。小范围直接修改或普通一次评审
不必启动 Cross-agent；仅在协调与独立评审的收益值得 worker 和上下文成本时自动选择它。

Product Brief 和 Functional Spec 可以对照用户授权的访谈证据编写或 `review`：区分用户
原话和模型建议、已确认决定和候选、最新决定和被取代的说法；有出处时保留位置或简短
原文，绝不编造 transcript 或出处。争议或高影响的说法回查原文，作者自己的摘要不能单独
证明用户意图；只有用户要求或已授权的 discovery 流程才保存笔记。小项目没有 Spec 时，
用户确认的产品级约束（内存、延迟、容量等）写在 Brief 的 Product Constraints；有 Spec
时归 Spec。Architecture 只把它们转成技术决定或预算分配，Testing Strategy 只定义测量
方法；没人设定的预算是待决问题，不编数字。Spec 仍是可选的：用户要求时任何规模都可以建，
否则只在一张 Map 无法保持可读时才建，需求数量或文档长度本身不是理由。

Brief 访谈从一个真实任务问起（谁、带什么输入、做什么、要什么结果），只问会改变方向的
问题；改动产品含义前先用几句话向用户复述并等确认。Spec 的契约仍是编号需求，可用简短的
具体故事、流程图和输入输出示例解释，但它们不新增需求也没有自己的 ID；格式由用户或项目
选 Markdown 或 HTML，既有路径和 ID 不悄悄迁移，也不维护另一种格式的副本。字数目标按
英文词：Brief 400–700（超过 800 先删），Spec 1,500–2,500（超过 3,000 先删）；它们是写作
目标而不是关卡，字数从不触发拆分，其他语言不换算。`Test-DocBudget.ps1` 只数 Markdown，
不能代表 HTML 的读者文字。

拆 Feature 之前，`feature-storyboard` 可以从 Brief、Spec 章节或明确的产品问题出发，
写 `docs/storyboards/<topic-slug>.html`，不虚构 Feature ID；未确认的行为标为
`candidate`，草图不确认需求。之后对应 Feature 的 Plan 链接同一文件并沿用 `S*`/`T*`
ID。浏览器验证、低保真和不实现产品逻辑的边界不变。

Feature Map 拆独立用户结果；Feature Plan 评估执行规模、依赖、阶段验收、交接与委派。
一个独立结果只有一份 Plan；执行很长只拆 segment，不拆新 Feature；一份 Plan 含多个
独立结果时，Plan 停下并请求修订 Map。小功能默认单阶段串行；大功能在同一份 Plan 中
用紧凑表安排多个执行 segment/session，最后整体回归。Plan 有字数预算（进行中 ≤ 2,500 词，`verified` 后 ≤ 1,500 词，Map ≤ 1,500 词），超出先删重复、
历史和日志，仍超出说明 Feature 太大、应拆 Map；确需更长时在文档顶部写明理由，由 Reviewer 判断；只写
本 Feature 的内容；开头保持当前执行位置（已完成/下一段、剩余检查、blocker），新
session 不依赖旧对话即可接手。Plan 读取 Testing Strategy，按真实用户、数据、负载和
失败后果推导风险，先读取已确认决定，只问会改变设计或验收的未决问题，不为失败用例凑数量。
Testing Strategy 要求各测试层覆盖不同失败，优先复用或加强已有用例；Delivery 只为覆盖缺口
增补测试，仍执行所有必要关卡。Reviewer 的问题应有实际触发条件、后果和最小修复建议，新增
测试应说明现有覆盖漏掉什么；本次改动新增却没有实际触发、消费者或读者的代码、guard、选项、测试或文字记为 `excess`，接受后由 Producer 删除；Orch 裁决证据，不自动接受严重性标签。交接保留当前决定、下一步、
未解决问题和验证出处，不累积每轮叙述，也不丢失独有证据。Feature Delivery 按计划执行并重新
核实委派边界；只有收益超过背景加载和整合成本的独立任务才开 sub-agent，最多同时三个，
并受环境限制。

没有 Feature 的有界技术问题（可行性、性能、选型）用 `feature-plan` 的 standalone
validation 写 `docs/plans/<topic>.md`，不需要 Brief、Map 或虚构的 Feature ID；
`feature-delivery` 执行它。执行状态（`completed`/`incomplete` 等）与结论
（`supported`/`not supported`/`inconclusive`）分开：否定结论也算完成实验，证据缺失则是
`incomplete`；实验不验证任何 Feature。

`cross-agent`（Orch）让当前会话像 PM 一样安排阶段、启动 Claude Code 或 Codex 的
Producer 和只读 Reviewer，并汇报进度；每个 run 只处理一个阶段和一个 artifact，审阅次数有限，
只有明确授权时 Orch 才逐 section 提交本地 commit，worker 永不 commit。CLI 命令、恢复、
checkpoint、配置和历史记录见 [`cross-agent/SKILL.md`](cross-agent/SKILL.md) 和
[使用教程](_doc/cross-agent-guide.md)。

变更只向下传播：Brief -> Spec -> Architecture/Testing Strategy -> Roadmap -> Map ->
Plan -> 代码。交付发现上游文档有误或中途收到已授权的变更时，Delivery 停下受影响的
工作并报告；由用户，或在已授权目标内由 `cross-agent` Orch 协调，先改上游 owner，再改
所有受影响的中间契约（如 Architecture Design、Testing Strategy），再改 Storyboard 和
Map 行，再改 Plan（记录一行原因和影响），只把失效的结果重置为 `not run`；这些 owner
都对齐之后才能做下游验收。Plan 的 Sources 已记录用户或 owner 做出的替换决定（如评审中已定的条目）
不算冲突：先规划、实现，交付时再由 Delivery 写进 owner 文档。变化可能影响 AGENTS 里的文档路由、已验证命令或边界时，需要由
`coding-agent-instructions` 的 `assess` 给每个相关指令文件一个结果：`updated`（附已验证
证据的机械更新）、`unchanged`（附原因）或 `unresolved`（附原因和需要的决定）；新的语义
规则只上报不写入。这是评估，不是每个 Feature 都改 `AGENTS.md`。Orch 只为实质影响产品行为、已接受约束、权限、成本或用户明确关卡的未决
选择询问用户；任何 agent 都不能为了让测试通过而改写权威输入。同一用户结果的修复、
扩展或重新验证复用原 Feature ID 和仍存在的 Plan（已 verified 的 Plan 已删除，则重新写一份）；独立的新结果才增加新 Feature。Architecture Design 变化由 `architecture-design` 报告受影响的行和
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
| [`coding-agent-instructions`](15.coding-agent-instructions/SKILL.md) | 为含代码的仓库创建、审计或持续校准 `AGENTS.md`；变化后做 instruction-impact assessment；纯非代码仓库交由所属集合的同类 Skill | 根 `AGENTS.md`；只有真实局部差异时才增加 nested `AGENTS.md`；缺失时复制只读链接检查器 `scripts/Test-DocLinks.ps1` 和字数预算检查器 `scripts/Test-DocBudget.ps1`（不覆盖已有文件，按版本头报告差异），链接检查器首次运行验证后在 `AGENTS.md` 加入它的命令，预算检查器由各文档的 owner Skill 按自己的预算调用；assessment 结果在报告中 |
| [`code-style`](16.code-style/SKILL.md) | `define` 确认实际语言和项目，未被用户或项目文档另行决定的规则直接采用 owner 默认 profile（SQL 三层注释、Python 分段标头、参数换行和具体时间示例、各语言 API 文档格式等），写出结构、模块组织、注释意图、文档和关键算法说明的规范；缺失的 `.editorconfig` 和 `.vscode` 文件先给用户看模板内容、确认后才创建，已有配置只读并报告差异；`audit` 和 `apply` 先跑 formatter，在有界范围内按大小分批（必要时用 subagent），`audit` 只报告，`apply` 做保持行为的修改并运行已验证检查 | `docs/code-style.md`；多项目 workspace 中每个项目一份继承根文件的 `<project>/docs/code-style.md`；缺失时创建的 `.editorconfig` 和 `.vscode/*.json`；`AGENTS.md` 中的路由和一条 Working-rules 规则 |
| [`functional-spec`](17.functional-spec/SKILL.md) | 可选：用户要求时（任何规模）或 MVP 需要多张 Feature Map 时，列出编号的可观察功能和产品级质量需求，用简短故事、流程图和示例解释；可对照 Brief 和授权访谈证据审阅 | `docs/functional-spec.md`，项目选 HTML 时为 `docs/functional-spec.html`；既有 canonical 路径不变 |
| [`architecture-design`](18.architecture-design/SKILL.md) | 探索、编写、审阅共享架构：组件边界、契约、数据所有权、依赖方向、部署假设和技术质量约束；主 design 作索引和跨领域契约，按领域（不按技术）拆分子文档，每份约 2,500 词，超出时先精简再拆分，只写当前状态，每个契约和数值只有一个 owner；接收 delivery 上移的决定；把 Map 内的技术方向或既有 General Design 迁移过来 | `docs/architecture.md`，或沿用既有 General Design 路径 |
| [`testing-strategy`](19.testing-strategy/SKILL.md) | 编写或审阅可复用的项目测试规则：测试层级、业务不变量、算法 oracle、fixture 规模、资源测量方法、回归和独立测试条件；未定预算记为待决 | `docs/testing.md` |
| [`feature-map`](20.feature-map/SKILL.md) | 探讨或写入合适规模的 MVP 交付结构：小项目一张 Map，大项目拆为 Roadmap 和子 Map；只管结果、依赖和状态，链接 Architecture Design | `docs/feature-map.md`，或 `docs/feature-maps/` |
| [`feature-storyboard`](25.feature-storyboard/SKILL.md) | 按需把一个 UI Feature，或拆 Feature 前一个早期产品问题，做成可点击的线框 app 故事（一个文件一个用户故事），套用项目共享的 app shell，展示关键状态和交互，并可切到全状态 overview 检查死路和漏掉的分支 | `docs/storyboards/<feature-id>-<slug>.html`；多个故事时为 `<feature-id>-<n>-<story-slug>.html` 加索引 `<feature-id>-<slug>.html`；早期为 `docs/storyboards/<topic-slug>.html` |
| [`feature-plan`](30.feature-plan/SKILL.md) | 创建、修订或重开单个 Feature 的实现与验证计划（分段、当前执行位置、风险与测试设计）；一个已定规则或精简横跨多个已交付 Feature 时写一份 Change Plan（变更点表、规则只在入口校验一次、owner 测试只测一次）；或为有界技术问题写 standalone validation 计划；Plan 是工作文档，verified 后由 delivery 删除，内容留在 git 历史 | `docs/features/<feature-id>-<slug>.md`；Change Plan 和 validation 为 `docs/plans/<topic>.md` |
| [`feature-delivery`](40.feature-delivery/SKILL.md) | 自动实现、精简或指导用户实现一个已规划 Feature，增量 TDD：编辑时只跑 focused 测试和失败重跑，segment 边界跑 owner 和改动契约的 consumer，最终 tree 只跑一次全量；结果一行绑定 commit（`passed n/n @ sha`），不写 hash、manifest、log 路径或已解决的失败历史；测试在执行前就因环境失败时不重试、不诊断，报告一次后交给能执行的一方；全部场景通过后把 Plan 中的持久决定上移到 AGENTS.md 路由的所属长期文档（默认 Architecture Design；当前规则、一两句、无历史），找不到 owner 时保留 Plan 并报告，verified 时删除 Plan 并把链接指向验证 revision；选定独立关卡时只报告 readiness；或执行 validation 计划并分别记录执行状态与结论；在 Orch 下不 commit，直接调用且明确授权时按 segment commit | 更新代码、Feature Plan 和 Feature Map 状态；validation 只更新其计划 |
| [`cross-agent`](cross-agent/SKILL.md) | `initiate` 初始化 repo 独立配置、模型/effort（可按专家和阶段设置）和 Codex CLI 版本检测；PM 式 Orch 编排已授权的设计、规划、执行或多 Feature 阶段，实时汇报 worker 状态；专家从只读讨论连续进入生产，正式产出默认独立 review（用户可明确跳过），限定审阅次数并裁决 findings，每次评审附确定性测试变更摘要，按功能/主题保留调用历史；明确授权时由 Orch 逐 section 提交本地 commit | 项目根目录 `.cross-agent/config.toml`；各阶段 artifact 与对话进度；`.cross-agent/history/` 的时间与用量 CSV，`history` 可汇总；非阻塞遗留项追加到 `docs/review-backlog.md` |
| [`simplification-review`](simplification-review/SKILL.md) | 对已有仓库做业务驱动的精简评审：先粗读仓库并按行业知识逐轮追问业务规模、精度、信任边界等约束（不限题数，每题附场景和推荐答案），确认后写入 Spec 或 Brief；再写评审计划（模块与跨模块调用链），之后每次只评审一个批次（先跨模块、后模块），批次开始先问专项问题，产出 findings；不改代码，选中的条目交给 `feature-plan` 或 `feature-delivery`；全部条目完成或否决、Change Plan 都交付后收尾，确认决定已进 owner 文档，内容已在 commit 中时删除评审文档 | `docs/reviews/00.review-plan.md` 与每批 `docs/reviews/<NN>.<slug>.md`（收尾时删除）；字数预算由 `scripts/Measure-ReviewDoc.ps1` 检查 |
| [`document-simplification`](document-simplification/SKILL.md) | 显式调用，精简一两份已有文档：先以目标读者身份通读、找出读不通的地方；结构要变时先给用户看大纲，只改表达时直接重写；保留读者需要的事实，已定规则写进其 owner 文档，非阻塞的后续改进按项目已有 backlog 的规则处理，阻塞当前内容的问题写进 owner 的未决问题并问用户；HTML 另查渲染后的可读性和导航；references 给出常见形状和反例（数据分析、文件夹 README、通用反模式），不是模板；新反例只向用户提议，不自动写入 | 按需重写指定的 `.md` 或 `.html` 文件；报告每份的读者、结构、前后字数和移走内容的去向 |
| [`skill-authoring`](skill-authoring/SKILL.md) | 创建或精简本仓库中的 Skill | 目标 Skill 及本能力表 |
| [`skill-deployment`](skill-deployment/SKILL.md) | 将本仓库明确配置的 Skill 同步到 Copilot、Claude Code 和 Codex | 目标目录更新及受管清单 |

## 文档边界

| 文档 | 只保存 | 不保存 |
|---|---|---|
| Product Brief | 产品目的、用户、核心流程、MVP 边界；没有 Spec 时保存已确认的产品级约束 | 需求编号、架构、流程、访谈记录 |
| Coding Agent Instructions | 路由、优先级、已验证命令、边界、工作与报告规则；基于权威证据持续校准 | 产品内容、技术方向、代码风格规则、一次性任务状态、工具专用适配层、assessment 记录 |
| `docs/code-style.md` | 仓库共享的代码风格规则，每种语言一节，外加模块组织、结构、注释、文档等跨语言规范，并列出每个项目文件；工具已强制的规则只路由不复述；多项目 workspace 中每个项目的 `<project>/docs/code-style.md` 以继承根文件开头，只保存本项目的局部规则，没有时写 `Local Rules: None.` | 产品或流程内容、架构依赖方向与系统边界、工具配置本身、重复的共享规则 |
| Functional Spec | 编号的可观察功能和产品级质量需求、解释它们的简短故事和流程图、排除项、未决决策 | 状态、追溯表、架构、交付顺序、实现或测试清单 |
| Architecture Design | 共享的系统上下文、组件职责、契约、数据所有权、依赖方向、技术选型、部署假设、质量约束（主体、条件、属性或预算、来源、验证引用）和不变量；既有 General Design 即为此文档；仅在需要大量独立指导时按栈拆分 | 需求原文、Feature 列表、顺序、状态、测试用例、代码级风格规则 |
| Testing Strategy | 可复用的测试层级、业务不变量与来源、算法 oracle、fixture 与 mock 限制、发现与 skip 规则、资源测量方法、回归和独立测试条件 | 逐 Feature 用例、测试结果、产品需求或资源预算本身 |
| Roadmap | 子 Map 的顺序、分配的 FS ID、依赖和路径；文件存在后才使用链接 | 需求原文、设计、交付状态 |
| Feature Map | Feature 结果、引用的 FS ID、依赖、状态和 Architecture Design 链接 | 需求原文、技术方向、架构、实现细节 |
| Feature Storyboard | 一个 UI Feature 或早期产品问题的可见状态和转换，未确认行为标为 `candidate` | 已确认需求、虚构 Feature ID、实现设计、测试、状态 |
| Feature Plan | 该 Feature 的当前执行位置、执行阶段、依赖、验收、交接、委派选择、测试设计、选定的独立关卡、关键决定与变更原因，以及真实结果 | 上游内容的复制、transcript 和例行活动日志 |
| Validation Plan | 一个有界问题的假设、输入、oracle、步骤、指标、预算与停止条件、证据、判定标准、执行状态和结论 | Feature ID、Map 状态、所支持决定的正文 |
| Simplification Review | 评审计划（批次、范围、当前位置）和每批的问答、findings 清单与条目（场景、建议、必须保持的行为、状态）；计划 ≤ 1,000 词，每批 ≤ 2,000 词，每条 ≤ 150 词；评审收尾时删除 | 命令、测试计数、评审轮次、历史，产品约束本身（归 Spec 或 Brief） |
| Review Backlog | `cross-agent` 裁决后未进入本次修订的非阻塞遗留项及其理由 | 未告知用户的当前 blocker、prompt、transcript、token 日志、快照、需求或计划内容 |

`cross-agent` 在 checkpoint 保持 Plan 的当前位置，并在 Plan -> Delivery、Feature
完成等阶段边界评估 Orch 上下文是否需要压缩。交接只保留当前授权、artifact/run、revision、
未完成工作、关卡和证据出处；worker rotation 不轮换 Orch，不增加定时器或独立 memory 文件。
压缩后先核对 CLI status、当前 revision/diff 和 Plan，再继续原 run 与预算。

`coding-agent-instructions` 提供
[可选 Feature 工作流 profile](15.coding-agent-instructions/assets/feature-workflow.profile.md)。
只有用户为当前项目明确选用后，才把 cross-agent、独立 review、Step 验证、ponytail 与
branch/本地 commit 约定写入 AGENTS；这不启动 Feature，也不授权 push、merge 或历史改写。
项目名和命名差异在项目中确定，模型/effort 留在 cross-agent 配置，具体步骤和结果留在 Plan。

下游文档链接上游文档，不复制上游内容。用户指定的既有 domain knowledge 只是可选
输入，不由任何 Skill 创建；`feature-delivery` 只把 AGENTS.md 路由到它的已定规则写进去。

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
