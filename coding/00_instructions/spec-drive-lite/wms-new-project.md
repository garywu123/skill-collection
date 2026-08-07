# 模式一：全新项目（WMS 示例）

从零开始一个企业级 WMS。本文说明每一步用哪个 Skill、产出什么文件、`roadmap.yaml`
如何随之变化，以及项目最终大致有哪些文件。

每一行都是一次独立的人类授权。AI 完成当前这一步、更新 `roadmap.yaml` 后必须停下；
由你审阅并口述下一步。**状态转换靠你口述，不靠脚本。**

## 0. 开始前的判断

WMS 通常有多个领域、库存一致性约束、外部集成、权限与审计，`profile` 记 `full`。
这个字段只是意图标记，它不强制任何东西——它提醒你别把这个项目当小工具处理。

先确定首个可交付能力（例如 `F001 收货入库`），不要一开始铺开所有领域。

## 1. 建立已批准事实

| 顺序 | 你口述的操作 | 产物 | `roadmap.yaml` 变化 | 你在下一步前要确认 |
|---|---|---|---|---|
| 1 | `$project-map init` | `roadmap.yaml`、骨架 `AGENTS.md` | 创建文件；`stage: discovery` | 项目 ID 正确，`docs` 只列真实存在的文件 |
| 2 | `$product-discovery-roadmap discover` | `doc/product-discovery-notes.md` | `docs.discovery` 指向该文件 | 审阅未决问题、假设、范围；够不够写 PRD |
| 3 | 你口述批准，并说「进入 PRD 阶段」 | 无 | `stage: prd` | 未决的业务选择不能默认为已决定 |
| 4 | `$product-discovery-roadmap draft-prd` | `doc/general-product-requirement.md` | `docs.prd` | 逐条审库存不变量、审计、权限、失败行为 |
| 5 | 你口述批准，并说「进入 roadmap 阶段」 | 无 | `stage: roadmap` | PRD 描述的是「要什么」，没替你决定技术实现 |
| 6 | `$product-discovery-roadmap draft-roadmap` | `doc/feature-roadmap.md` | `docs.roadmap`；`functions[]` 全部写入，状态 `planned` | 每个 function 都能独立验收演示 |
| 7 | `$architecture-baseline full` | `doc/architecture-baseline.md`、`doc/adr/` | `docs.architecture`；`stage: architecture` | 不可违反的技术约束、待解决的 spike |
| 8 | `$project-map refresh` | 填好的 `AGENTS.md` | 无（只校对路径） | 它引用事实，不复制整份 WMS 文档 |
| 9 | `$ui-wireframe-spec product`（有共享 UI 时） | `doc/ui-structure.md` | `docs.ui` | 没有共享 UI 时，PRD 里要有明确的 N/A 理由 |

第 8 步放在架构之后是有原因的：`AGENTS.md` 的路由表要指向已经存在的文件。第 1 步的
骨架版本只够 AI 认路，不是最终版本。

早期 roadmap 的一个合理形态：`F001 收货` → `F002 上架` → `F003 库存查询与调整`
→ `F004 库存预留与分配` → `F005 拣货` → `F006 发运`。以批准后的 roadmap 为准。

## 2. `roadmap.yaml` 的演进

刚 `init` 完：

```yaml
project: WMS
profile: full
stage: discovery
docs: {}
functions: []
```

roadmap 批准后（第 6 步）：

```yaml
project: WMS
profile: full
stage: architecture
docs:
  discovery: doc/product-discovery-notes.md
  prd: doc/general-product-requirement.md
  roadmap: doc/feature-roadmap.md
functions:
  - id: F001
    name: 收货入库
    status: planned
  - id: F002
    name: 上架
    status: planned
  - id: F003
    name: 库存查询与调整
    status: planned
```

F001 交付后：

```yaml
project: WMS
profile: full
stage: implementation
docs:
  discovery: doc/product-discovery-notes.md
  prd: doc/general-product-requirement.md
  roadmap: doc/feature-roadmap.md
  architecture: doc/architecture-baseline.md
  ui: doc/ui-structure.md
functions:
  - id: F001
    name: 收货入库
    status: accepted
    spec: specs/F001-receiving/spec.md
    checklist: specs/F001-receiving/checklist.md
    verified: 2026-08-14 by Gary Wu
  - id: F002
    name: 上架
    status: implementing
    spec: specs/F002-putaway/spec.md
    checklist: specs/F002-putaway/checklist.md
  - id: F003
    name: 库存查询与调整
    status: planned
```

字段含义与状态规则见
[roadmap 规格](../../20.project-map/references/roadmap-spec.md)。

## 3. 交付一个 Feature（以 F001 收货入库 为例）

每个 function 独立重复这个循环。不能用 F001 的验收替代其他 function 的验收。

| 顺序 | 你口述的操作 | 产物 | `roadmap.yaml` 变化 |
|---|---|---|---|
| 1 | Spec Kit `specify F001` | `spec.md`：用户场景、业务规则、负向场景、`SC-###` 验收场景 | `status: specified`，写入 `spec` 路径 |
| 2 | 同一步：写交付 checklist | `checklist.md`，验收场景逐条成为一个 box | 写入 `checklist` 路径 |
| 3 | Spec Kit `clarify F001` | 澄清写回 spec | 无 |
| 4 | `$ui-wireframe-spec feature F001`（有 UI 时） | `wireframes.md` | 无 |
| 5 | Spec Kit `plan`、`tasks` | `plan.md`、`tasks.md` | 无 |
| 6 | `$spec-sync pre-implement F001 feature` | `pre-implementation-review.md`，Pass 或 Blocked | 无 |
| 7 | 你审阅并口述批准，开始实施 | 代码、自动化测试、迁移证据 | `status: implementing` |
| 8 | `$spec-sync post-implement F001 feature` | 把证据写进 `checklist.md` 的 Evidence 表 | `status: verifying` |
| 9 | **开新对话**，核对 checklist | 勾选、填 Decision 段 | `status: accepted` + `verified` |

第 2 步的时机是关键：checklist 和 spec 一起写，因为这时候你才最清楚验收标准是什么。
交付前才补的 checklist 一定会被写成刚好能通过的样子。

第 9 步必须换对话。写代码的上下文不给自己的作业打勾——这是整套流程里唯一不能省的
独立性要求。

实现后发现的新问题不能悄悄塞回 F001：行为缺陷、技术债、未来想法、跨 function 技术
决策各有各的路径，见[模式二](wms-change-request.md)。

## 4. WMS 项目大致有哪些文件

每个项目不同，但形状类似。以 WMS 为样本：

```text
wms/
├── AGENTS.md                          # project-map 拥有：路由与边界
├── CLAUDE.md                          # 可选薄适配器，指向 AGENTS.md
├── roadmap.yaml                       # project-map 拥有 schema；各操作回写自己改变的条目
├── doc/
│   ├── product-discovery-notes.md     # product-discovery-roadmap
│   ├── general-product-requirement.md # product-discovery-roadmap
│   ├── feature-roadmap.md             # product-discovery-roadmap
│   ├── architecture-baseline.md       # architecture-baseline
│   ├── adr/
│   │   ├── 0001-inventory-consistency.md
│   │   ├── 0002-erp-integration-boundary.md
│   │   └── 0003-concurrency-and-transactions.md
│   ├── ui-structure.md                # ui-wireframe-spec（有共享 UI 时）
│   └── change-requests/
│       └── CR-0001-部分收货.md         # spec-sync
├── specs/
│   ├── F001-receiving/
│   │   ├── spec.md                    # Spec Kit
│   │   ├── plan.md                    # Spec Kit
│   │   ├── tasks.md                   # Spec Kit
│   │   ├── wireframes.md              # ui-wireframe-spec
│   │   ├── pre-implementation-review.md  # spec-sync
│   │   └── checklist.md               # 交付标准与证据
│   ├── F002-putaway/
│   └── F003-inventory/
├── src/
├── tests/
└── migrations/
```

三条规律，比具体目录名更重要：

- **一份事实一个语义拥有者。** 各 Skill 只改自己拥有的工件；`roadmap.yaml` 是例外的
  共享记账文件，Project Map 拥有 schema，各操作只回写自己直接改变的条目。
- **全局的进 `doc/`，单个 function 的进 `specs/F###-slug/`。** 判断标准是这份内容
  是否跨 function。
- **`roadmap.yaml` 只存路径和状态。** 任何需要一段话说明的东西都属于它指向的文件。

## 5. 操作者的三个固定动作

每个阶段结束时只做一件事：

1. 审阅本阶段产物和缺失证据；
2. 明确批准、拒绝，或要求修改；
3. 在下一条消息中口述下一项操作。

AI 报告的「建议下一步」是导航，不是它已经拿到的授权。
