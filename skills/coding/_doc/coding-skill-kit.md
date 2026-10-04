# Coding Skill Kit — Getting Started

Audience: solo developers, small teams, and AI-led delivery who want a
lightweight documentation trail (product direction, MVP Feature Map, per-Feature
plan and real test results) without a heavyweight process.

This guide is an onboarding tutorial with one real worked example. The flow
diagram, Skill list, and document-ownership rules live in
[`skills/coding/README.md`](../README.md); this page only shows
what running the kit looks like.

> [!NOTE]
> Upstream lifecycle Skills such as `/product-brief` and
> `/architecture-design` are invoked by you, by name. `feature-map`,
> `feature-plan`, and `feature-delivery` can also be selected from your
> request. Each prompt below names the Skill it runs.

## Real example: standing up "DockFlow WMS"

This walkthrough is taken from this repository's own
[WMS workflow example](../examples/wms-workflows.md), which is
used to validate the kit itself. The prompts are real, not illustrative.

### 1. Explore product direction

```text
/product-brief 我想从零设计 DockFlow WMS。先探索产品目的、主要用户、核心流程和最小
MVP，每轮最多问三个真正影响方向的问题。只讨论和总结，不要创建文件、拆 Feature 或实现。
```

Runs `product-brief` in explore mode: a conversation and a running summary,
nothing written to disk yet.

### 2. Save the confirmed direction

```text
/product-brief 请把已确认的 DockFlow WMS 产品方向保存为 checkpoint。只写确定事实；
会影响产品目的、用户、核心流程或 MVP 边界的未决事项放到 Open Questions。
```

Writes `docs/product-brief.md` and stops. Product-level limits you confirm,
such as a response-time budget, go under its Product Constraints; unset budgets
stay open questions. `/product-brief` can also review a draft against interview
notes you name, separating your confirmed decisions from model suggestions and
superseded statements.

### 3. Generate agent instruction files

```text
/coding-agent-instructions DockFlow WMS 的 Product Brief 已定稿。请生成项目的 agent
指令文件：权威的 `AGENTS.md`。仓库里还没有 manifest，不要编造命令。
```

Produces one authoritative `AGENTS.md`. Code-style rules are not written here;
the next step owns them.

### 4. Write the code-style contract

```text
/code-style 为 DockFlow WMS 写 `docs/code-style.md`。后端是 C#，前端是 TypeScript，
报表查询是 SQL。工具已强制的规则只路由，重点写模块组织、文件结构、注释意图、公共 API
文档，以及关键算法要解释到什么程度。写完把 `AGENTS.md` 的路由补上。
```

Runs `code-style` in `define` mode: asks you to confirm the language set, then
writes `docs/code-style.md` with one section per confirmed language plus the
cross-language module, structure, comment, and documentation rules, and updates
the `AGENTS.md` route to it. Dependency direction between components stays in
the Architecture Design. Later, `audit` reports a named scope's deviations and
`apply` brings an authorized scope into line without changing the rules.

### 5. Record the shared architecture

```text
/architecture-design 基于已定稿的 DockFlow WMS Brief 写 Architecture Design：手持端与
后台的边界、ASN 和库存数据所有权、关键契约、部署假设。只记录当前 MVP 需要的决定，
没有来源的性能预算列为待决，不要创建 Feature Map。
```

Writes `docs/architecture.md`, the single owner of shared technical direction.
A reusable test rule set can follow with `/testing-strategy`, which writes
`docs/testing.md`.

### 6. Create the MVP Feature Map

```text
/feature-map 基于已定稿的 DockFlow WMS Brief 创建最小 MVP Feature Map，链接现有
Architecture Design。包含 F20 入库收货：操作员扫描 ASN 并确认实收数量。只保留 MVP；
不要创建 Plan 或代码。
```

Writes `docs/feature-map.md` with the new Feature row starting at status
`planned` and a link to the Architecture Design. DockFlow fits one map, so no
Functional Specification or Roadmap is created; the example file shows the
scale variant.

### 7. Plan one Feature, then deliver it

```text
/feature-plan 为 F20 创建可执行 Feature Plan。读取 Map、代码约定和 Storyboard，引用
相关 S*、T*；先设计 happy path，再设计相关 failure path 和验证命令。
```

```text
/feature-delivery 按现有 F20 Plan 自动完成入库收货，只实现该 Feature。先写和运行聚焦
测试，再做最小实现；运行计划验证和相关回归，把真实结果写回 Plan 并同步 Map。
```

Status only becomes `verified` when every planned scenario has an actual
passing result, not when the code merely compiles. When you select an
independent review, finishing the code is only readiness; the Feature stays
`in_progress` until that review passes. Delivery updates the Plan and the Map
row only; it never edits an upstream document. The Plan starts with its current
execution position, so a new session can resume without the earlier chat.

A bounded technical question without a Feature, such as whether a library meets
a load target, uses the same pair: `/feature-plan` writes a standalone
validation plan at `docs/plans/<topic>.md`, and `/feature-delivery` runs it and
records whether execution completed separately from the conclusion.

## What to read next

- Full scenarios, including a product too large for one map, onboarding an
  *existing* project, and a mid-flight requirement change:
  [`examples/wms-workflows.md`](../examples/wms-workflows.md)
- Flow, Skill list, and document-ownership rules:
  [`skills/coding/README.md`](../README.md)
- Adding or changing a Skill in this kit:
  [`skill-authoring`](../skill-authoring/SKILL.md)
