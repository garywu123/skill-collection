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
/agent-instructions DockFlow WMS 的 Product Brief 已定稿。请生成项目的 agent 指令
文件：权威的 `AGENTS.md`、`docs/code-style.md`，加上 `CLAUDE.md` 和
`.github/copilot-instructions.md` 两个薄适配层。只写路由、优先级、已验证命令和工作
规则；仓库里还没有 manifest，不要编造命令。不要复制产品内容或创建 Feature Map。
```

预期：Agent Instructions 的 `write`；输出三份指令文件和 `docs/code-style.md`，
`AGENTS.md` 链接 `docs/product-brief.md` 与 `docs/code-style.md` 并预留其他路由；
未验证的命令段被删除并报告；停止于指令文件。

### 6. 创建 MVP Feature Map

```text
/feature-map 基于已定稿的 DockFlow WMS Brief 创建最小 MVP Feature Map 和共享技术方向。包含
F02 入库收货：操作员扫描 ASN 并确认实收数量。只保留 MVP；不要创建 Plan 或代码。
```

预期：Feature Map；输出 `docs/feature-map.md`，新行从 `planned` 开始；停止于地图。

### 7. 按需创建 F02 Storyboard

```text
/feature-storyboard 为 F02 创建低保真手持设备 HTML Storyboard，展示扫描 ASN、确认实收数量和无效 ASN。
使用代表性假数据，所有状态静态可见且不用 JavaScript。不要创建 Plan 或实现代码。
```

预期：Feature Storyboard；输出 `docs/storyboards/F02-*.html` 和首次使用时的共享
CSS；报告 `S*`、`T*` 和 rendering checks。浏览器不可用时才报告未验证风险并停止。

### 8. 创建 F02 Feature Plan

```text
/feature-plan 为 F02 创建可执行 Feature Plan。读取 Map、代码约定和 Storyboard，引用相关 S*、T*；
先设计 happy path，再设计相关 failure path 和验证命令。不要实现或创建额外任务清单。
```

预期：Feature Plan；输出 `docs/features/F02-*.md`，结果为 `not run`；停止于计划。

### 9. 选择一种 Delivery 方式

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

### 2. 确认后再实现变化

```text
/feature-delivery F02 的 Map、Storyboard 和 Plan 变化已经确认。现在请按修订后的 Plan 自动实现破损
数量与隔离库位流程，只修改 F02 所需代码和测试。重新运行受影响场景及相关回归，
记录真实结果并同步 Plan 和 Map 状态。
```

预期：只选择 Feature Delivery；输出代码、测试和实际结果。具体条件阻止继续时记录
blocker，并把 Plan 与 Map 都设为 `blocked`；否则以验证证据决定 `in_progress` 或
`verified`。

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
/feature-map 基于 StockPilot 的 Brief 创建 MVP Feature Map，保留项目已有的 .NET 8、
React 约定。Map 只包含当前尚待交付的 MVP，不要重建历史功能清单；新 row 从 planned
开始，只有 matching Plan 的 status、results 和 blockers 一致时才能同步其他状态。
不要为历史功能批量创建 Storyboard 或 Feature Plan。
```

预期：两次点名。资料充分时输出或协调 `docs/product-brief.md` 与
`docs/feature-map.md`；不足时停止于具体问题。

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
MVP 明显超过八个 Feature，且涉及项目文件、地图编辑、车辆配置和运行观察多个领域。

### 1. 先写 Functional Specification

```text
/functional-spec FleetDock 的 Product Brief 已定稿，MVP 至少需要四张 Feature Map。
请先探索功能领域和需求措辞，每轮最多三个问题；确认后写 docs/functional-spec.md，
只列编号的可观察需求、排除项和未决决策，不写状态、架构或交付顺序。
```

预期：Functional Spec 先 `explore` 再 `write`；输出带 `FS-*` 编号的需求清单；停止于
Spec，不创建 Roadmap 或 Map。

### 2. 建立 Roadmap、General Design 和第一张子 Map

```text
/feature-map 基于 FleetDock 的 Brief 和 Functional Spec 建立规模化布局：
docs/feature-maps/00.roadmap.md 列出各阶段子 Map 的顺序、分配的 FS ID 和依赖；
docs/design/backend-general-design.md 与 docs/design/web-general-design.md 保存多张
子 Map 共享的职责、契约和不变量；只写第一阶段的子 Map 01.foundation.md，每行填
Requirements 列引用的 FS ID。后续阶段的子 Map 留到准备交付时再写。
```

预期：Feature Map 按 scale layout 输出 Roadmap、两份 General Design 和一张子 Map；
Roadmap 不保存交付状态，尚未创建的子 Map 只显示代码形式的预定路径；子 Map 只保留
阶段特有的技术方向，其余链接 General Design；停止于地图。

### 3. 之后的流程与单 Map 项目相同

每个子 Map 行按 `/feature-plan` 和 `/feature-delivery` 推进。Delivery 只更新 Plan 和
Map 行；Roadmap 分配不算交付，某个 FS 需求至少被一行 Map 引用、且所有引用它的 Map
行都 `verified` 后才视为交付。交付中发现 Spec
或 Design 有误时，Delivery 停下报告，由人依次 `/functional-spec`、`/feature-map`、
`/feature-plan` 修订后再继续。

## 场景五：重开任务、增加 Feature、修改共享 Design

- 修复或扩展同一个用户结果时，`/feature-plan` 重开原 Plan，复用原 Feature ID；失效
  结果回到 `not run`，Plan 与 Map 回到 `planned`，再由 `/feature-delivery` 实现。
- 出现可独立交付的新用户结果时，先用 `/feature-map` 分配全项目唯一的新 Feature ID，
  再创建新 Plan；不要把它塞进旧 Plan 或创建 `F02-v2`。
- 修改 General Design 时，先用 `/feature-map` 更新设计并列出全部受影响行。旧证据不再
  证明当前设计的行回到 `planned`；随后分别用 `/feature-plan` 协调受影响 Plan，再重新
  Delivery。未受影响且证据仍有效的 Feature 保持原状态。
