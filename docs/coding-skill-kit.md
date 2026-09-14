# Coding Skill Kit — Getting Started

Audience: solo developers, small teams, and AI-led delivery who want a
lightweight documentation trail (product direction, MVP Feature Map, per-Feature
plan and real test results) without a heavyweight process.

This guide is an onboarding tutorial with one real worked example. The
authoritative Skill list, capability table, and document-ownership rules live
in [`skills/coding/README.md`](../skills/coding/README.md) — read that for the
full picture; this page only shows what running the kit actually looks like.

## The flow

```text
Product Brief
  -> Agent Instructions (AGENTS.md + CLAUDE.md + Copilot)
  -> Feature Map + Technical Direction
  -> [optional Feature Storyboard]
  -> Feature Plan
  -> Feature Delivery (auto | guided)
```

> [!TIP]
> Every step below is plain natural language — you never have to name a
> Skill. The coordinator picks one from what your request clearly asks for.

## Real example: standing up "DockFlow WMS"

This walkthrough is taken directly from this repository's own
[WMS workflow example](../skills/coding/examples/wms-workflows.md), which is
used to validate the kit itself. The prompts are real, not illustrative.

### 1. Explore product direction

```text
我想从零设计 DockFlow WMS。先探索产品目的、主要用户、核心流程和最小 MVP，
每轮最多问三个真正影响方向的问题。只讨论和总结，不要创建文件、拆 Feature 或实现。
```

Runs `product-brief` in explore mode: a conversation and a running summary,
nothing written to disk yet.

### 2. Save the confirmed direction

```text
请把已确认的 DockFlow WMS 产品方向保存为 checkpoint。只写确定事实；会影响产品
目的、用户、核心流程或 MVP 边界的未决事项放到 Open Questions。不要猜测或创建 Map。
```

Writes [`docs/product-brief.md`](../skills/coding/10.product-brief/SKILL.md)
and stops — it does not chain into a Feature Map on its own.

### 3. Generate agent instruction files

```text
DockFlow WMS 的 Product Brief 已定稿。请生成项目的 agent 指令文件：权威的
`AGENTS.md`，加上 `CLAUDE.md` 和 `.github/copilot-instructions.md` 两个薄适配层。
只写路由、优先级、已验证命令和工作规则；仓库里还没有 manifest，不要编造命令。
```

Produces the same three-file pattern this repository itself uses: one
authoritative `AGENTS.md` plus two thin adapters.

### 4. Create the MVP Feature Map

```text
基于已定稿的 DockFlow WMS Brief 创建最小 MVP Feature Map 和共享技术方向。包含
F02 入库收货：操作员扫描 ASN 并确认实收数量。只保留 MVP；不要创建 Plan 或代码。
```

Writes `docs/feature-map.md` with the new Feature row starting at status
`planned`.

### 5. Plan one Feature, then deliver it

```text
为 F02 创建可执行 Feature Plan。读取 Map、代码约定和 Storyboard，引用相关 S*、T*；
先设计 happy path，再设计相关 failure path 和验证命令。
```

```text
按现有 F02 Plan 自动完成入库收货，只实现该 Feature。先写和运行聚焦测试，再做最小
实现；运行计划验证和相关回归，把真实结果写回 Plan 并同步 Map。
```

The first prompt runs `feature-plan`; the second runs `feature-delivery` in
`auto` mode. Status only becomes `verified` when every planned scenario has an
actual passing result — not when the code merely compiles.

## What to read next

- Full scenarios, including onboarding an *existing* project and handling a
  mid-flight requirement change: [`examples/wms-workflows.md`](../skills/coding/examples/wms-workflows.md)
- Capability table and document-ownership rules: [`skills/coding/README.md`](../skills/coding/README.md)
- Adding or changing a Skill in this kit: [`skill-authoring`](../skills/coding/skill-authoring/SKILL.md)
