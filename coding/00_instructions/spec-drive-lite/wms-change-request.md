# 模式二：修改已有的 Feature（WMS 示例）

项目已经在跑，某个 function 已经交付，现在你想改它。本文回答：这需要重走一遍
discovery 吗？答案是通常不需要——但你必须先回答另一个问题。

## 1. 唯一要先回答的问题

> 这次变更动到的**最高一层已批准事实**是什么？

不是「要改哪个文件」，是「要改哪一层承诺」。判错这一层，后面全部返工。

```text
$spec-sync change-request CR-0021
```

它读你的请求和现有文档，输出一份**提案**：最高影响层、受影响 ID、哪些下游证据会
失效、每一项的拥有者、建议的下一条人工授权。它不改 PRD、roadmap、架构、代码或
`roadmap.yaml`，也不会替你启动后续 Skill。

**Discovery 只在业务问题本身还不清楚时才需要。** 对一个已上线 function 的修改，
你通常已经知道要什么了，缺的是「这个要求撞到哪一层」。那是 change-request 的工作，
不是 discovery 的工作。只有期望的业务事实仍不清楚时才重开 discovery，例如用户问题、
规则目的、责任边界或成功标准尚未形成共识；这既可能发生在新领域，也可能发生在已有领域。

## 2. 路由表

| 请求 | WMS 示例 | 路由 | 最终验证 |
|---|---|---|---|
| 新业务能力 | 新增波次拣货 | product/roadmap 修订 → 新 function | checklist 验收 |
| 业务规则变化 | 允许超收，或允许部分收货 | product 修订；必要时架构修订 → function | checklist 验收 |
| 已接受 function 的行为改动 | F001 收货改为支持部分收货 | 见第 3 节 | checklist 重新验收 |
| 未交付 function 的内部调整 | 实现前改收货页面字段 | 直接重写 spec，刷新 plan/tasks/UI | 正常 pre/post 流程 |
| 缺陷 | 重复扫描导致库存加两次 | `bug` 工作项 + 复现与回归测试 | post-implement + 人工确认 |
| 不改变外部行为的改善 | 查询索引、重构、日志 | `maintenance` 工作项 | post-implement + 人工确认 |
| 数据模型或迁移 | 库存台账表拆分 | `migration` 工作项 + dry run/回退/恢复 | post-implement + 发布证据 |
| 权限或安全 | 仅主管可撤销收货 | `security` 工作项 + threat/abuse case | post-implement + 安全证据 |
| 跨域技术边界 | 库存改为事件驱动 | 架构修订 + ADR → 受影响的各工作项 | 每项独立验证 |

「看起来很小」不是跳过上层修订的依据。判断依据只有一个：外部承诺变了没有。

## 3. 改一个已接受的 function：两种做法

已接受的 function 带着一条 `verified` 记录，那条记录是对**当时那份 spec** 的验收。
改了 spec 而不动状态，那条记录就变成假的。这是唯一必须处理的问题。

### 做法 A：就地修改（默认）

适用于新行为**取代**旧行为。

1. 修改 `specs/F001-receiving/spec.md`。
2. 根据新 spec 重建 `checklist.md` 的受影响条目，并清空旧 boxes、Evidence、Decision、
   reviewer 和 date。
3. 在 `roadmap.yaml` 里把 F001 的 `status` 退回 `specified`，**删掉 `verified` 字段**。
4. 重走一遍：pre-implement → 实施 → post-implement → 开新对话验收。

旧版本的 spec、checklist 和证据都在 git 里。`git log specs/F001-receiving/spec.md`
就是你的历史记录，不需要另建一个 function 编号来保存它。

### 做法 B：后继 function

适用于新旧能力需要被独立部署、支持、验收、迁移或长期追踪。它们可能长期并存，也可能
只在迁移期并行。

这时候它们本来就是两个 function，不是一个 function 的两个版本：

```yaml
  - id: F001
    name: 整单收货
    status: accepted
    verified: 2026-08-14 by Gary Wu
    notes: 部分收货由 F008 承担
  - id: F008
    name: 部分收货
    status: specified
    spec: specs/F008-partial-receiving/spec.md
    checklist: specs/F008-partial-receiving/checklist.md
    notes: 扩展 F001 的收货流程，F001 行为不变
```

默认选 A。只有两个能力需要独立生命周期或独立追踪时才选 B；不要仅仅为了保存历史
创建新编号，因为 Git 已经保存旧 spec、checklist 和证据。

## 4. 完整示例：F001 收货 → 支持部分收货

假设旧的整单收货不再需要，属于做法 A。

| 顺序 | 你口述的操作 | 产物 | `roadmap.yaml` 变化 |
|---|---|---|---|
| 1 | `$spec-sync change-request CR-0021` | `doc/change-requests/CR-0021-部分收货.md` | 无 |
| 2 | 你审阅提案，确认最高影响层是**产品规则** | 无 | 无 |
| 3 | `$product-discovery-roadmap amend CR-0021` | PRD 候选修订 | 无 |
| 4 | 你口述批准 | 更新 `doc/general-product-requirement.md` | 无 |
| 5 | 判断库存状态机是否改变；若改变则 `$architecture-baseline amend CR-0021` | `doc/architecture-amendments/CR-0021.md` / 新 ADR | 无 |
| 6 | Spec Kit 重写 F001 spec 与 checklist | `spec.md`、`checklist.md` | `status: specified`，删 `verified` |
| 7 | `$spec-sync pre-implement F001 feature` | `pre-implementation-review.md` | 无 |
| 8 | 实施 | 代码、测试、迁移 | `status: implementing` |
| 9 | `$spec-sync post-implement F001 feature` | 证据写进 checklist | `status: verifying` |
| 10 | **开新对话**核对 checklist | 勾选、填 Decision | `status: accepted` + 新 `verified` |

第 3 步不是 discovery。它只改动 PRD 里被这次变更影响的那几条规则，不重开业务访谈。

## 5. 缺陷与维护

### Bug

先写下可复现步骤、实际结果、期望结果、受影响版本、回归测试。然后：

```text
建立 BUG-### spec 与 checklist
→ $spec-sync pre-implement BUG-### bug
→ 你口述批准
→ 修复与回归测试
→ $spec-sync post-implement BUG-### bug
→ 开新对话核对 checklist
```

Bug 不能顺手改变产品规则。如果诊断下来发现是规则本身要改，停下来回到第 1 节走 CR。

### Maintenance

记录边界、兼容性、回退方式和验证方法，走同样的 pre/post 流程。
如果这项「维护」改变了用户可观察到的行为，它就不是维护，重新分类。

## 6. 变更完成前的检查

- 已经确定最高影响层，而不是只读了目标代码；
- 已接受 function 的 `verified` 和旧 checklist 结果没有留在已经变化的行为上；
- 每个受影响的下游 spec、plan、测试、证据都重新验证过；
- 测试、CI、迁移、回退、安全、运维证据按风险给足；
- checklist 是在新对话里核对的。
