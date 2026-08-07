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

每行是一条独立消息。把姓名、日期和范围替换为真实值。

| # | 必须调用 | 你可以这样说 | 产物 / 地图回写 |
|---|---|---|---|
| 1 | `$project-map init` | `使用 $project-map init，为 WMS 创建 profile: full 的 roadmap.yaml 和骨架 AGENTS.md；docs 只登记真实存在的文件，完成后报告并停止。` | 创建两文件；`stage: discovery`、`docs: {}` |
| 2 | `$product-discovery-roadmap discover` | `使用 $product-discovery-roadmap discover，围绕 WMS 用户、收货到发运流程、库存不变量、权限、审计和外部集成开展 discovery；写完 notes、回写 docs.discovery，然后停止。` | discovery notes；`docs.discovery` |
| 3 | `$product-discovery-roadmap approve-discovery` | `使用 $product-discovery-roadmap approve-discovery；我 <姓名> 于 <日期> 批准当前 discovery notes 进入 PRD，依据是本消息；只记录批准并停止。` | notes 内批准字段；地图不变 |
| 4 | `$product-discovery-roadmap draft-prd` | `使用 $product-discovery-roadmap draft-prd，从已批准 discovery 起草 WMS PRD；只写产品结果、规则、范围和非目标；回写 docs.prd，并将描述性 stage 记为 prd，然后停止。` | PRD；`docs.prd`、`stage: prd` |
| 5 | `$product-discovery-roadmap approve-prd` | `使用 $product-discovery-roadmap approve-prd；我 <姓名> 于 <日期> 批准当前 PRD，依据是本消息；只记录批准并停止。` | PRD 批准字段；地图不变 |
| 6 | `$product-discovery-roadmap draft-roadmap` | `使用 $product-discovery-roadmap draft-roadmap，从已批准 PRD 建立可独立验收的 WMS functions、依赖和 MVP 边界；回写 docs.roadmap 与 planned entries，将 stage 记为 roadmap，然后停止。` | 产品 roadmap；`docs.roadmap`、`functions[]`、`stage: roadmap` |
| 7 | `$product-discovery-roadmap approve-roadmap` | `使用 $product-discovery-roadmap approve-roadmap；我 <姓名> 于 <日期> 批准当前 function 边界、依赖和顺序，依据是本消息；只记录批准并停止。` | roadmap 批准字段；地图不变 |
| 8 | `$architecture-baseline full` | `使用 $architecture-baseline full，为已批准的 WMS PRD 和 roadmap 建立跨 function 架构约束、ADR、deferred decisions 和 spikes；回写 docs.architecture，将 stage 记为 architecture，然后停止。` | baseline/ADR；`docs.architecture`、`stage: architecture` |
| 9 | `$architecture-baseline approve` | `使用 $architecture-baseline approve；我 <姓名> 于 <日期> 批准当前 architecture baseline 和列出的 ADR，依据是本消息；只记录批准并停止。` | 架构批准字段；地图不变 |
| 10 | `$project-map refresh` | `使用 $project-map refresh，从已批准产品、roadmap、architecture 和仓库证据刷新 AGENTS.md；只保留 roadmap.yaml 路由、项目边界和已验证命令，不复制业务或架构正文。` | 精简 AGENTS；只校对地图 |
| 11 | `$ui-wireframe-spec product`，仅适用时 | `使用 $ui-wireframe-spec product，为 WMS 共享导航、全局 shell 和跨 function UI 模式建立 ui-structure；回写 docs.ui，然后停止。` | UI structure；`docs.ui` |
| 12 | `$ui-wireframe-spec product`，仅适用时 | `使用 $ui-wireframe-spec product；我 <姓名> 于 <日期> 批准当前 product UI structure，依据是本消息；只记录批准字段，不重画或进入 feature UI。` | UI 批准字段；地图不变 |

第 10 步放在架构之后，是为了让骨架 `AGENTS.md` 升级成可靠的路由文件。它不需要复制
具体路径：运行时先读 `roadmap.yaml`，再按 `docs.*` 找到相应事实。

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

roadmap 批准后（第 7 步）：

```yaml
project: WMS
profile: full
stage: roadmap
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

| # | 必须调用 | 你可以这样说 | 产物 / 地图回写 |
|---|---|---|---|
| 1 | Spec Kit `specify` | `执行 Spec Kit specify F001 收货入库；只覆盖 roadmap 中的 F001 和它拥有的 PR IDs，同时创建 spec.md 与交付 checklist；回写 spec/checklist 路径并设为 specified。` | spec/checklist；`specified` |
| 2 | Spec Kit `clarify` | `执行 Spec Kit clarify F001；只解决会改变验收场景、边界或失败行为的问题，把答案写回 spec 后停止。` | 澄清后的 spec；地图不变 |
| 3 | `$ui-wireframe-spec feature F001`，仅适用时 | `使用 $ui-wireframe-spec feature F001，根据已澄清 spec 和 product UI structure 画低保真结构与状态；只写 F001 wireframes，然后停止。` | wireframes；地图不变 |
| 4 | `$ui-wireframe-spec feature F001`，仅适用时 | `使用 $ui-wireframe-spec feature F001；我 <姓名> 于 <日期> 批准当前 F001 wireframes，依据是本消息；只记录批准，不进入 plan。` | UI 批准字段；地图不变 |
| 5 | Spec Kit `plan` | `执行 Spec Kit plan F001；遵守 architecture baseline 和已批准 wireframes，只设计 F001，不吸收后续 functions。` | plan；地图不变 |
| 6 | Spec Kit `tasks` | `执行 Spec Kit tasks F001；把 spec 场景、plan 和所需验证拆成可执行任务，不扩大范围。` | tasks；地图不变 |
| 7 | `$spec-sync pre-implement F001 feature` | `使用 $spec-sync pre-implement F001 feature，检查 spec、plan、tasks、checklist 与上层事实的纵向一致性；只写 pre-review，报告 Pass/Blocked 后停止。` | pre-review；Blocked 时只记 notes |
| 8 | 无；普通实现，或可选 `$guided-tdd-pairing` | `我已审阅并批准 F001 pre-implementation review。现在只实现 F001，运行约定测试，并把 roadmap.yaml 中 F001 设为 implementing、stage 记为 implementation；不要验收。` | 代码/测试；`implementing` |
| 9 | `$spec-sync post-implement F001 feature` | `使用 $spec-sync post-implement F001 feature，把实际命令和结果写入 checklist Evidence；不要勾 acceptance boxes 或填写 Decision；无 blocker 时设为 verifying。` | Evidence；`verifying` |
| 10 | 无；必须开新对话 | `核对 roadmap.yaml 中 F001 指向的 spec、checklist、diff 和测试证据。不要修代码；逐项判断 checklist。若全部满足，我 <姓名> 于 <日期> 明确接受 F001；否则记录 changes requested。` | checklist Decision；通过时 `accepted` + `verified` |

第 1 步同时写 checklist 是关键：这时候你才最清楚验收标准是什么。
交付前才补的 checklist 一定会被写成刚好能通过的样子。

第 10 步必须换对话。写代码的上下文不给自己的作业打勾——这是整套流程里唯一不能省的
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
