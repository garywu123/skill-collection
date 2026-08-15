# 模式三：把流程接到已有仓库上（WMS 示例）

已经有一个跑着的 WMS 仓库：可能是人手写的，可能是另一套 AI 流程做的，也可能两者
都有。现在要把这套 Skill 接上去，并把对应的文档补齐。

## 0. 最容易犯的错

**把「代码现在这么做」直接写成「产品应该这么做」。**

代码里的每一个行为都有两种可能：它是当初有意的决定，或者它是某次赶工留下的意外。
AI 读代码分不出这两者，而一旦写进 PRD，意外就变成了承诺，再也没人敢改。

所以本模式全程只做一件事：**把「已验证存在」和「已批准应当」严格分开。**
每一条重建出来的陈述必须带标签：

| 标签 | 含义 | 处理 |
|---|---|---|
| `已批准` | 有人明确确认这是想要的行为 | 写进 PRD |
| `已验证` | 代码/测试/CI 确实如此，但没人确认它是否应该如此 | 写进现状记录，**不写进 PRD** |
| `遗留参考` | 旧文档或注释里的说法，未经代码验证 | 只作线索 |
| `未知` | 读不出意图 | 列进待确认清单 |
| `冲突` | 代码、文档、你的说法互相矛盾 | 停下来问你 |

`未知` 不写进任何 canonical 文档。`冲突` 必须报告，不能由 AI 挑一个。

## 1. 接入顺序

顺序和全新项目不同：先盘点，再重建，最后才谈以后要做什么。

下面每一行单独发送；上一行报告并停止后，先审阅证据，再发送下一行。

| # | 必须调用 | 你可以这样说 | 产物 / 地图回写 |
|---|---|---|---|
| 1 | `$project-map audit` | `使用 $project-map audit，只读盘点当前 WMS 仓库的目录、manifest、CI、测试、可运行命令、领域边界和缺失文档；不要写文件。` | 只读报告；地图不存在或不变 |
| 2 | `$project-map init` | `使用 $project-map init，为现有 WMS 建立 roadmap.yaml 和骨架 AGENTS.md；只写已验证的命令、路径和边界，不把代码行为写成产品规则。` | map/AGENTS；`stage: discovery` |
| 3 | `$product-discovery-roadmap discover` | `使用 $product-discovery-roadmap discover，把仓库证据和我的业务说明分成已批准、已验证、遗留参考、未知、冲突；写 notes、回写 docs.discovery 后停止。` | discovery；`docs.discovery` |
| 4 | `$product-discovery-roadmap discover` | `继续使用 $product-discovery-roadmap discover。我对未决项的裁决如下：<逐条列出>；只更新 discovery 分类，不起草 PRD。` | 更新 discovery；地图不变 |
| 5 | `$product-discovery-roadmap approve-discovery` | `使用 $product-discovery-roadmap approve-discovery；我 <姓名> 于 <日期> 批准已裁决的 discovery 进入 PRD，依据是本消息；只记录批准。` | discovery 批准字段 |
| 6 | `$product-discovery-roadmap draft-prd` | `使用 $product-discovery-roadmap draft-prd，只把已批准的期望行为写入 canonical PRD；已验证但未确认的行为只进待确认附录；回写 docs.prd 和 stage: prd。` | PRD；`docs.prd`、`stage: prd` |
| 7 | `$product-discovery-roadmap approve-prd` | `使用 $product-discovery-roadmap approve-prd；我 <姓名> 于 <日期> 批准当前 PRD，依据是本消息；只记录批准。` | PRD 批准字段 |
| 8 | `$product-discovery-roadmap draft-roadmap` | `使用 $product-discovery-roadmap draft-roadmap，把已观察实现登记为 as-built，把新能力登记为 planned；回写 docs.roadmap、functions 和 stage: roadmap。` | roadmap；mixed function states |
| 9 | `$product-discovery-roadmap approve-roadmap` | `使用 $product-discovery-roadmap approve-roadmap；我 <姓名> 于 <日期> 批准当前能力边界和计划顺序，依据是本消息；只记录批准。` | roadmap 批准字段 |
| 10 | `$architecture-baseline recover` | `使用 $architecture-baseline recover，从 manifest、CI、目录和代表性代码恢复现有架构；每项标 Verified 或 Inferred，不把历史包袱包装成约束；回写 docs.architecture 和 stage: architecture。` | baseline/ADR；`docs.architecture` |
| 11 | `$architecture-baseline approve` | `使用 $architecture-baseline approve；我 <姓名> 于 <日期> 批准当前 recovered baseline 中明确列出的 intended constraints，并保留历史包袱标签；依据是本消息。` | 架构批准字段 |
| 12 | `$project-map refresh` | `使用 $project-map refresh，按 roadmap.yaml 路由和已验证仓库命令刷新 AGENTS.md；不要复制 PRD、function 清单或 architecture 正文。` | 完整但精简的 AGENTS |

第 2 步和第 12 步都写 `AGENTS.md`，是故意的。第 2 步那份只让 AI 认得路（命令、目录、
禁区），第 12 步才补齐稳定的事实路由；具体路径仍由 `roadmap.yaml` 提供。

## 2. 已有 function 记成什么状态

已经上线并且在用的功能，既不是 `planned`，也不能算 `accepted`——它从来没有经过
checklist 验收。诚实的记法是 `as-built`：

```yaml
project: WMS
profile: full
stage: implementation
docs:
  discovery: doc/product-discovery-notes.md
  prd: doc/general-product-requirement.md
  roadmap: doc/feature-roadmap.md
  architecture: doc/architecture-baseline.md
functions:
  - id: F001
    name: 收货入库
    status: as-built
    notes: 代码在 src/receiving/，无 spec，未经本流程验收

  - id: F002
    name: 上架
    status: as-built
    notes: 代码在 src/putaway/，行为与 F001 有耦合，见 adr/0002

  - id: F003
    name: 库存查询与调整
    status: as-built
    notes: 调整权限规则与 PRD 附录 A 冲突，待裁决

  - id: F007
    name: 波次拣货
    status: planned
    notes: 新能力，走完整流程
```

`as-built` 的意思是：仓库里存在可识别的实现，但这套流程尚未建立业务符合性或验收
结论。测试或运行证据可以写进现状记录，但状态本身不保证“能跑”。
它不是失败状态，是一个诚实的起点。

## 3. 不要回头补全所有 delivery artifacts

这是本模式最重要的一条实践建议。

一个跑了两年的 WMS 可能有三十个 function。把它们全部补上 checklist、optional spec 和验收，
是几个月的工作，产出的文档没人读，而且写完就开始过期。

**改到哪个，才补哪个。** 下次你要动 F002 上架时，它自然要走一遍
[模式二](wms-change-request.md)：先把状态改为 `planned`，再判断 approved Roadmap entry
是否足以走 Direct route；只有不足时才补 optional spec/plan/tasks。

```text
as-built  --（下次要改它时）-->  planned  -->  implementing  -->  verifying  -->  accepted
```

主动补 optional spec 只有两种情况值得：这个 function 出过事故要重建理解，或者它是新人和 AI
最常撞上的那一块。除此之外，让 `as-built` 就那么放着。

## 4. 一个已有仓库接入后长什么样

新增的文件（标 `+`）叠在原有结构上，原有代码目录不动：

```text
wms/
├── AGENTS.md                       + project-map
├── roadmap.yaml                    + project-map
├── doc/
│   ├── product-discovery-notes.md      + 含「现状 vs 期望」标签
│   ├── general-product-requirement.md  + 只含已批准条目 + 待确认附录
│   ├── feature-roadmap.md              + 已有能力与计划能力并列
│   ├── architecture-baseline.md        + 记录现状，标出有意约束与历史包袱
│   ├── adr/
│   │   ├── 0001-inventory-consistency.md   + 追认既有决定
│   │   └── 0002-receiving-putaway-coupling.md  + 标为历史包袱
│   └── change-requests/            +
├── specs/                          + 一开始可为空，改到哪个才建 checklist/optional detail
│   └── F007-wave-picking/
├── src/                              原有代码，本次不动
├── tests/                            原有测试，作为「已验证」证据来源
└── ...                               原有其他内容
```

追认既有决定的 ADR 值得单独说一句：它记录的是「我们现在确实是这么做的，以及我们
现在认为这样对不对」。把一个历史包袱明确写成历史包袱，比假装它是设计决定要有用得多。

## 5. 接入完成的判断标准

不是「文档写完了」，是这四条：

- `AGENTS.md` 里每一条命令和路径都在仓库里验证过，没有一条是猜的；
- PRD 里没有任何一条是从代码行为直接翻译过来却没人确认的；
- 所有 `冲突` 都已经由你裁决，没有被 AI 静悄悄选掉一个；
- `roadmap.yaml` 列全了 function，状态诚实——不确定的写 `as-built`，不写 `accepted`。

第四条最容易被违反。把没验收过的东西标成 `accepted`，等于在项目最开始就往状态文件
里写了一句假话，后面每个读它的人和 AI 都会被误导。
