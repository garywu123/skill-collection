# WMS 工作流使用示例

生命周期 Skill 由人点名调用，下面每条指令都以 `/skill-name` 开头。新项目使用
`DockFlow WMS`，核心 UI Feature 是 `F02 入库收货`；既有项目使用 `StockPilot`；
规模化项目使用 `FleetDock`。

## 使用约定

- 一次只推进当前请求明确覆盖的结果，不要用一句话要求实现整个 WMS。
- 某份产物存在或缺失，都不会自动授权创建或修改相邻产物。
- 一条指令需要多个 Skill 时，按顺序分别点名；AI 不自行选择下一个 Skill。
- `auto` 与 `guided` 是 Delivery 的两种协作方式，按当前意图选择其一即可。

## 场景一：从零开始 DockFlow WMS

### 1. 探索产品方向

```text
/product-brief 我想从零设计 DockFlow WMS。先探索产品目的、主要用户、核心流程和最小 MVP，
每轮最多问三个真正影响方向的问题。只讨论和总结，不要创建文件、拆 Feature 或实现。
```

预期：Product Brief 的 `explore`；输出对话总结和问题；停止于对话，不写 Brief。

### 2. 保存探索 checkpoint

```text
/product-brief 请把已确认的 DockFlow WMS 产品方向保存为 checkpoint。只写确定事实；会影响产品
目的、用户、核心流程或 MVP 边界的未决事项放到 Open Questions。不要猜测或创建 Map。
```

预期：Product Brief 的 `write`；输出 `docs/product-brief.md`；停止于 Brief。

### 3. 恢复探索

```text
/product-brief 请读取现有 DockFlow WMS Product Brief，继续和我探索其中尚未解决的产品方向。
先总结已确认内容，再问下一批高价值问题；这次只对话，不要更新任何文件。
```

预期：Product Brief 的 `explore`；读取现有 Brief 作为上下文；停止于对话，不写文件。

### 4. 定稿 Product Brief

```text
/product-brief 请根据已确认的答案更新并定稿 DockFlow WMS Product Brief，保持简短，明确 MVP
内外边界。只处理 Brief，报告仍未解决的方向问题，不要自动创建 Feature Map。
```

预期：Product Brief 的 `write`；更新 `docs/product-brief.md`；停止于定稿结果。

### 5. 生成 agent 指令文件

```text
/coding-agent-instructions DockFlow WMS 的 Product Brief 已定稿。请生成权威的
`AGENTS.md`。只写路由、优先级、已验证命令、边界和工作规则；仓库里还没有 manifest，
不要编造命令。不要复制产品内容、不要写 code style、不要创建 Feature Map。
```

预期：Coding Agent Instructions 的 `write`；输出 `AGENTS.md`，链接
`docs/product-brief.md`；未验证的命令段被删除并报告；`docs/code-style.md` 尚不存在，
因此省略该路由并报告应运行 `code-style`；停止于指令文件。

### 6. 写 code style 契约

```text
/code-style 为 DockFlow WMS 写 `docs/code-style.md`。后端 C#、前端 TypeScript、报表
查询 SQL。工具已强制的规则只路由不复述；重点写模块组织、文件与函数结构、注释要解释
意图、公共 API 文档，以及关键步骤和算法需要解释到什么程度。写完补上 `AGENTS.md` 的
路由行。
```

预期：Code Style 的 `define`（原 `write` 请求同义）；先就语言集合向你确认一次，再输出
`docs/code-style.md`——每种确认语言一节，外加跨语言的模块组织、结构、注释、文档四节；
组件依赖方向只链接 Architecture Design；最后把 `AGENTS.md` 的 code-style 路由补上，
其余内容不动；停止于该文件与那一行路由。

### 7. 记录共享架构

```text
/architecture-design 基于已定稿的 DockFlow WMS Brief 写 Architecture Design：手持端与
后台的边界、ASN 和库存数据所有权、关键契约、部署假设。只记录当前 MVP 需要的决定，
没有来源的性能预算列为待决，不要创建 Feature Map。
```

预期：Architecture Design 的 `write`；输出 `docs/architecture.md`；未定预算出现在
Open Decisions；停止于设计。

### 8. 按需建立 Testing Strategy

```text
/testing-strategy 为 DockFlow WMS 写测试策略：测试项目和已验证命令、单元与集成边界、
收货数量的业务不变量、fixture 来源和规模、资源测量方法。没有已验证命令就不写命令。
```

预期：Testing Strategy 的 `write`；输出 `docs/testing.md`，链接需求和架构而不复制；
停止于策略，不写测试代码。

### 9. 创建 MVP Feature Map

```text
/feature-map 基于已定稿的 DockFlow WMS Brief 创建最小 MVP Feature Map，链接现有
Architecture Design。包含 F02 入库收货：操作员扫描 ASN 并确认实收数量。只保留 MVP；
不要创建 Plan 或代码。
```

预期：Feature Map；输出 `docs/feature-map.md`，链接 `docs/architecture.md`，不写技术
方向；新行从 `planned` 开始；停止于地图。

### 10. 按需创建 F02 Storyboard

```text
/feature-storyboard 为 F02 创建低保真手持设备 HTML Storyboard，展示扫描 ASN、确认实收数量和无效 ASN。
使用代表性假数据，所有状态静态可见且不用 JavaScript。不要创建 Plan 或实现代码。
```

预期：Feature Storyboard；输出 `docs/storyboards/F02-*.html` 和首次使用时的共享
CSS；报告 `S*`、`T*` 和 rendering checks。浏览器不可用时才报告未验证风险并停止。

### 11. 创建 F02 Feature Plan

```text
/feature-plan 为 F02 创建可执行 Feature Plan。读取 Map、代码约定和 Storyboard，引用相关 S*、T*；
先设计 happy path，再设计相关 failure path 和验证命令。不要实现或创建额外任务清单。
```

预期：Feature Plan；输出 `docs/features/F02-*.md`，结果为 `not run`；停止于计划。

### 12. 选择一种 Delivery 方式

自动实现：

```text
/feature-delivery 按现有 F02 Plan 自动完成入库收货，只实现该 Feature。先写和运行聚焦测试，再做最小
实现；运行计划验证和相关回归，把真实结果写回 Plan 并同步 Map。不要实现其他 Feature。
```

预期：Delivery `auto`；修改测试、代码、Plan 和 Map。全部通过且无 blocker 才
`verified`；仍可继续的未完成工作保持 `in_progress`，只有具体条件阻止继续才 `blocked`。

如果希望自己写核心实现，则改用：

```text
/feature-delivery 用 guided 方式带我完成 F02。我写核心实现；你负责测试和 fixture，每次告诉我下一个
文件、symbol 或 signature 及所需行为，等我完成再检查。不要改我的文件或推进其他 Feature。
```

预期：Delivery `guided`；等待时保持 `in_progress`。具体条件阻止继续时才
`blocked`；最终由真实结果决定是否 `verified`。

## 场景二：F02 开发中突然变更

现在 F02 还要记录破损数量并选择隔离库位。先更新设计和计划，再另行授权实现。
本例主动把文档调整和实现拆成两次请求，以明确授权边界；这不是流程强制的审批关卡。

### 1. 只协调文档变化

```text
/feature-map F02 入库收货的需求变了：确认收货时必须记录破损数量，破损数量大于零时
还要选择隔离库位。只更新 F02 的 Feature Map 行，报告受影响的 Storyboard 和 Plan。
```

```text
/feature-storyboard 按更新后的 F02 Map 行修订 Storyboard，补充破损数量和隔离库位状态。
```

```text
/feature-plan 按更新后的 F02 Map 行和 Storyboard 修订 Feature Plan，引用新的 S* 与 T*。
保留不受影响且仍有效的测试结果，受影响的结果改为 not run。不授权实现。
```

预期：三次点名，各自输出一份协调后的文档；停止于代码修改之前。

状态应按已有证据处理：

- 如果变化使原来的 `verified` 证据失效，Plan 与 Map 回到 `planned`。
- 如果 Feature 已在开发且仍可继续，保持 `in_progress`。
- 只有受影响的结果回到 `not run`；预期行为没有变化的真实结果可以保留。
- 这个变化仍属于原有 MVP 收货方向，因此通常不改 Product Brief；只有产品方向、
  用户、核心流程或 MVP 边界变化时，才显式要求更新 Brief。
- Plan 的 `## Decisions` 记录一行变更原因和影响，开头的当前执行位置指向需要重跑的
  场景；组织要求变更单时只链接它，不另建 CR 文档。

如果已在 `cross-agent` 中授权完成 F02，Orch 可以按同样的上游优先顺序协调这三次修订，
只为实质的产品选择询问你。

### 2. 确认后再实现变化

```text
/feature-delivery F02 的 Map、Storyboard 和 Plan 变化已经确认。现在请按修订后的 Plan 自动实现破损
数量与隔离库位流程，只修改 F02 所需代码和测试。重新运行受影响场景及相关回归，
记录真实结果并同步 Plan 和 Map 状态。
```

预期：只选择 Feature Delivery；输出代码、测试和实际结果。具体条件阻止继续时记录
blocker，并把 Plan 与 Map 都设为 `blocked`；否则以验证证据决定 `in_progress` 或
`verified`。

在 `cross-agent` 中执行这一步时，Reviewer 还会收到该 revision 的测试变更摘要：
被删除或改写的 F02 测试、新的 skip 或过滤参数、fixture 变化和检查的计数来源。摘要
只是检测信号；没有检测到变化时，Reviewer 仍要对照修订后的 Plan 判断破损数量和隔离
库位场景是否真正被测试和断言。

## 场景三：让既有 StockPilot 项目采用这套 Skills

假设 `StockPilot` 是一个使用 .NET 8 和 React 的库存与收货系统，仓库中已有代码，
但还没有这套流程的规范文档。

### 1. 建立当前的 Product Brief 与 Feature Map

```text
/product-brief 请让既有 StockPilot 项目采用当前 coding workflow。读取仓库 guidance、
现有产品文档、manifest，以及有代表性的收货代码和测试；不要穷举整个仓库。根据明确的
产品意图创建或 reconcile 当前 Product Brief。代码只是当前行为的证据，不是期望行为的
唯一真相。资料不足时停下询问，不要猜测。
```

```text
/architecture-design 根据 StockPilot 现有代码和配置写 Architecture Design，保留已有的
.NET 8、React 边界和数据所有权。代码是现状证据；无法判断是否有意为之的选择列为待决。
```

```text
/feature-map 基于 StockPilot 的 Brief 创建 MVP Feature Map，链接 Architecture Design。
Map 只包含当前尚待交付的 MVP，不要重建历史功能清单；新 row 从 planned
开始，只有 matching Plan 的 status、results 和 blockers 一致时才能同步其他状态。
不要为历史功能批量创建 Storyboard 或 Feature Plan。
```

预期：三次点名。资料充分时输出或协调 `docs/product-brief.md`、`docs/architecture.md`
与 `docs/feature-map.md`；不足时停止于具体问题。

### 2. 只为下一项工作准备 F02

```text
/feature-storyboard StockPilot 下一项工作是 Feature Map 中的 F02 入库收货：扫描 ASN
并确认实收数量。为它创建低保真手持设备 Storyboard。
```

```text
/feature-plan 为 StockPilot 的 F02 创建引用 Storyboard S*、T* 的 Feature Plan。检查现有
.NET 8 API、React UI 和代表性测试来制定最小改动；不要实现，也不要给其他历史 Feature
补建 Plan。如果出现会改变可见行为的实质冲突，停下询问，不要创建不可靠的 Plan。
```

预期：两次点名。没有实质可见冲突时输出 F02 HTML 与 Plan；若有冲突，停止于决策点
且不创建不可靠的 Plan；始终停止于实现前。

### 3. 按现有工程约定交付

```text
/feature-delivery 请按 StockPilot 的 F02 Feature Plan 自动交付该 Feature，沿用现有 .NET 8、React、
测试和目录约定。只实现 F02，运行聚焦测试和必要回归，把真实结果写回 Plan 并同步
Feature Map；不要因为发现其他旧代码问题而扩大范围。
```

预期：Feature Delivery；输出最小代码与测试变更、Plan 结果和 Map 状态。根据
真实进展停止于 `in_progress`、`blocked` 或 `verified`；只有具体条件阻止继续时才使用
`blocked`。

## 场景四：FleetDock 大到一张 Feature Map 放不下

`FleetDock` 是一个含浏览器端调度台和 .NET 后端的车队调度产品。Brief 定稿后，
删掉可选范围后，MVP 仍需要多个交付阶段，涉及项目文件、地图编辑、车辆配置和运行观察
多个需求领域，一张 Map 已无法清楚表达它们的依赖。行数本身不是拆分理由。

### 1. 先写 Functional Specification

```text
/functional-spec FleetDock 的 Product Brief 已定稿，MVP 至少需要四张 Feature Map。
请先探索功能领域和需求措辞，每轮最多三个问题；确认后写 docs/functional-spec.md，
只列编号的可观察需求、排除项和未决决策，不写状态、架构或交付顺序。
```

预期：Functional Spec 先 `explore` 再 `write`；输出带 `FS-*` 编号的需求清单；停止于
Spec，不创建 Roadmap 或 Map。

### 2. 建立 Architecture Design

```text
/architecture-design 基于 FleetDock 的 Brief 和 Functional Spec 写 docs/architecture.md：
多张子 Map 共享的系统上下文、组件职责、跨栈契约、数据所有权和质量约束。只引用 FS ID，
不复制需求，不写交付顺序或状态。
```

预期：Architecture Design 的 `write`；输出一份共享设计，只有某个栈需要大量独立指导时
才拆分；停止于设计。

### 3. 建立 Roadmap 和第一张子 Map

```text
/feature-map 基于 FleetDock 的 Brief、Functional Spec 和 Architecture Design 建立规模化
布局：docs/feature-maps/00.roadmap.md 列出各阶段子 Map 的顺序、分配的 FS ID 和依赖；
只写第一阶段可用流程的子 Map 01.vehicle-configuration.md，每行填 Requirements 列引用的
FS ID。后续阶段的子 Map 留到准备交付时再写。DTO、schema 和注册等内部基础不单独成为
Feature。
```

预期：Feature Map 按 scale layout 输出 Roadmap 和一张子 Map；Roadmap 不保存交付状态，
尚未创建的子 Map 只显示代码形式的预定路径；子 Map 链接 Architecture Design，不写技术
方向；停止于地图。

### 4. 之后的流程与单 Map 项目相同

每个子 Map 行按 `/feature-plan` 和 `/feature-delivery` 推进。Delivery 只更新 Plan 和
Map 行；Roadmap 分配不算交付，某个 FS 需求至少被一行 Map 引用、且所有引用它的 Map
行都 `verified` 后才视为交付。交付中发现 Spec 或 Architecture Design 有误时，Delivery
停下报告，由你或已授权的 `cross-agent` Orch 依次 `/functional-spec` 或
`/architecture-design`、`/feature-map`、`/feature-plan` 修订后再继续。

## 场景五：重开任务、增加 Feature、修改共享架构

- 修复或扩展同一个用户结果时，`/feature-plan` 重开原 Plan，复用原 Feature ID；失效
  结果回到 `not run`，Plan 与 Map 回到 `planned`，再由 `/feature-delivery` 实现。
- 出现可独立交付的新用户结果时，先用 `/feature-map` 分配全项目唯一的新 Feature ID，
  再创建新 Plan；不要把它塞进旧 Plan 或创建 `F02-v2`。
- 修改 Architecture Design 时，先用 `/architecture-design` 更新设计并报告全部受影响行
  和 Plan；再用 `/feature-map` 把旧证据不再证明当前设计的行回到 `planned`，随后分别用
  `/feature-plan` 协调受影响 Plan，再重新 Delivery。未受影响且证据仍有效的 Feature
  保持原状态。
- 一个 Feature 只是执行很长时，`/feature-plan` 在同一份 Plan 中拆 segment；如果 Plan
  发现它其实含多个独立结果，就停下请求 `/feature-map` 拆行，保留原 ID 给已规划的结果。

## 场景六：把 Map 中的架构迁移出去

旧版 `docs/feature-map.md` 含 `Technical Direction`、`Architecture`、`Shared Constraints`，
或规模化项目已有 `docs/design/*-general-design.md`。

```text
/architecture-design 把 docs/feature-map.md 中的技术方向、架构和共享约束迁移到唯一的
Architecture Design。已有 General Design 就沿用其路径。Map 只把迁出的章节换成链接，
不要改 Feature 行、ID、依赖或状态。
```

预期：Architecture Design 的 `write`；架构只剩一个 owner，Map 保留结果、依赖和状态并
链接设计；纯迁移不改变 Feature 状态或测试结果；停止于设计和链接。迁移前 `/feature-map`
保留旧章节不扩写，并报告待迁移。

## 场景七：没有 Feature 的有界验证

Architecture Design 把“现有 ASN 解析库能否在手持端 2 秒内解析 5,000 行”列为待决的
可行性问题，还没有对应 Feature；2 秒来自产品负责人在 Brief 中写下的约束。

```text
/feature-plan 为 ASN 解析可行性写 standalone validation plan：docs/plans/asn-parse-feasibility.md。
用代表性和最大规模 ASN 样本、现有解析库与手写基准对比，说明步骤、指标、预算和停止条件，
判定标准引用 Brief 的 2 秒约束。不要创建 Feature ID、修改 Map 或实现生产代码。
```

```text
/feature-delivery 执行 docs/plans/asn-parse-feasibility.md，只在计划指定的实验目录写代码，
记录真实证据、执行状态和结论，并报告给 Architecture Design 的所有者。
```

预期：两次点名，不需要 Map 行。证据齐全但超过 2 秒时，状态 `completed`、结论
`not supported`；预算用完或样本缺失时状态 `incomplete`、结论保持 `pending`。两种结果都不
验证任何 Feature，Delivery 也不修改 Architecture Design。

## 场景八：访谈证据、早期 Storyboard、分范围代码风格与指令评估

### 1. 对照访谈证据审阅 Brief

```text
/product-brief 对照 docs/discovery/dockflow-interview.md 审阅 Brief 草稿。区分我的原话和
模型建议、已确认和候选、最新决定和被取代的说法；指出遗漏的已确认需求。只报告，不改文件。
```

预期：Product Brief 的 `review`；每条发现附访谈位置或简短原文，例如我后来把“整托
收货”改成“逐箱扫描”，或模型建议的“离线模式”未被我确认；只报告，不写文件。之后
`write` 只写最新的已确认决定，我确认的“扫描后 1 秒内显示结果”写入 Product
Constraints，未定的内存预算留在 Open Questions。

### 2. 拆 Feature 之前画早期 Storyboard

```text
/feature-storyboard 还没有 Feature Map。根据 Brief 的收货流程回答一个问题：扫描到未知
ASN 时操作员看到什么？用 topic slug，不要编 Feature ID，未确认的行为标 candidate。
```

预期：输出 `docs/storyboards/unknown-asn-scan.html`，`S*`/`T*` 稳定，未确认状态标
`candidate`，不写产品逻辑，报告浏览器检查结果。之后 F02 的 Plan 直接链接这个文件。

### 3. 分范围代码风格：定义、审计、应用

```text
/code-style apply：按已有 docs/code-style.md 和 web/docs/code-style.md，只修改
web/src/receiving/ 的偏差。不要改规则文件或工具配置，保持行为并运行已验证的检查。
```

预期：Code Style 的 `apply`；只改授权范围内的代码，不为迁就旧代码放宽规则，报告修改、
运行的命令和结果。共享规则只在根文件；`web/docs/code-style.md` 只写前端真实差异。

### 4. 变化后的指令评估

```text
/coding-agent-instructions assess：后端测试命令改为 dotnet test backend/DockFlow.sln，
web 新增 Playwright 端到端测试。评估根 AGENTS.md 和 web/AGENTS.md 是否需要更新。
```

预期：每个文件一个结果：已验证的命令变化记为 `updated` 并附证据；无关文件记为
`unchanged` 并说明原因；没有权威来源的新规则（例如“合并前必须跑端到端测试”）记为
`unresolved`，只上报不写入。
