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

| 顺序 | 你口述的操作 | 产物 | 关键约束 |
|---|---|---|---|
| 1 | `$project-map audit` | 只读盘点报告 | 不写任何文件。产出：目录结构、可运行命令、测试覆盖、明显的领域边界、缺失文档清单 |
| 2 | `$project-map init` | `roadmap.yaml`、基于**已验证**证据的 `AGENTS.md` | 只写代码里能证实的东西：命令、路径、目录约定。不写业务规则 |
| 3 | `$product-discovery-roadmap discover` | `doc/product-discovery-notes.md` | 输入是代码证据 + 你的口述，不是纯代码推断。逐条打标签 |
| 4 | 你逐条裁决 `未知` 和 `冲突` | 更新 discovery | 这一步没有捷径，也不能让 AI 代劳 |
| 5 | `$product-discovery-roadmap draft-prd` | `doc/general-product-requirement.md` | **只写 `已批准` 的条目**。`已验证` 但未确认的进「现状待确认」附录 |
| 6 | `$product-discovery-roadmap draft-roadmap` | `doc/feature-roadmap.md` | 同时含已有能力和计划能力，见第 2 节 |
| 7 | `$architecture-baseline recover` | `doc/architecture-baseline.md`、`doc/adr/` | 记录**现有**边界，并标出哪些是有意约束、哪些是历史包袱 |
| 8 | `$project-map refresh` | 完整 `AGENTS.md` | 现在才有真实的路由目标 |

第 2 步和第 8 步都写 `AGENTS.md`，是故意的。第 2 步那份只让 AI 认得路（命令、目录、
禁区），第 8 步那份才带业务路由。中间那几步 AI 需要能在仓库里干活。

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

`as-built` 的意思是：仓库里存在可识别的实现，但这套流程尚未建立完整 spec、业务
符合性或验收结论。测试或运行证据可以写进现状记录，但状态本身不保证“能跑”。
它不是失败状态，是一个诚实的起点。

## 3. 不要回头补全所有 spec

这是本模式最重要的一条实践建议。

一个跑了两年的 WMS 可能有三十个 function。把它们全部补上 spec、checklist 和验收，
是几个月的工作，产出的文档没人读，而且写完就开始过期。

**改到哪个，才补哪个。** 下次你要动 F002 上架时，它自然要走一遍
[模式二](wms-change-request.md)：那时候补 spec 和 checklist 是顺手的，而且写出来
的东西马上就被用到。

```text
as-built  --（下次要改它时）-->  specified  -->  implementing  -->  verifying  -->  accepted
```

主动补 spec 只有两种情况值得：这个 function 出过事故要重建理解，或者它是新人和 AI
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
├── specs/                          + 一开始是空的，改到哪个建哪个
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
