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
| 未交付 function 的内部调整 | 实现前改收货页面字段 | 更新 Roadmap behavior source；Detailed route 再刷新 spec/plan/tasks/UI | 正常 pre/post 流程 |
| 缺陷 | 重复扫描导致库存加两次 | `bug` 工作项 + 复现与回归测试 | post-implement + 人工确认 |
| 不改变外部行为的改善 | 查询索引、重构、日志 | `maintenance` 工作项 | post-implement + 人工确认 |
| 数据模型或迁移 | 库存台账表拆分 | `migration` 工作项 + dry run/回退/恢复 | post-implement + 发布证据 |
| 权限或安全 | 仅主管可撤销收货 | `security` 工作项 + threat/abuse case | post-implement + 安全证据 |
| 跨域技术边界 | 库存改为事件驱动 | 架构修订 + ADR → 受影响的各工作项 | 每项独立验证 |

「看起来很小」不是跳过上层修订的依据。判断依据只有一个：外部承诺变了没有。

## 3. 改一个已接受的 function：两种做法

已接受的 function 带着一条 `verified` 记录，那条记录是对**当时 behavior source** 的验收。
改了 Roadmap entry 或 optional spec 而不动状态，那条记录就变成假的。这是唯一必须处理的问题。

### 做法 A：就地修改（默认）

适用于新行为**取代**旧行为。

1. 修改 Roadmap feature entry；Detailed route 同时修改 optional `spec.md`。
2. 根据新 behavior source 重建 `checklist.md` 的受影响条目，并清空旧 boxes、Evidence、Decision、
   reviewer 和 date。
3. 在 `roadmap.yaml` 里把 F001 的 `status` 退回 `planned`，**删掉 `verified` 字段**。
4. 重走一遍：pre-implement → 实施 → post-implement → 开新对话验收。

旧版本的 Roadmap、optional spec、checklist 和证据都在 git 里，不需要另建一个 function
编号来保存它。

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
    status: planned
    spec: specs/F008-partial-receiving/spec.md
    checklist: specs/F008-partial-receiving/checklist.md
    notes: 扩展 F001 的收货流程，F001 行为不变
```

默认选 A。只有两个能力需要独立生命周期或独立追踪时才选 B；不要仅仅为了保存历史
创建新编号，因为 Git 已经保存旧 spec、checklist 和证据。

## 4. 完整示例：F001 收货 → 支持部分收货

假设旧的整单收货不再需要，属于做法 A。

下面每一行单独发送；上一行报告并停止后，先审阅产物，再决定是否发送下一行。

| # | 必须调用 | 你可以这样说 | 产物 / 地图回写 |
|---|---|---|---|
| 1 | `$spec-sync change-request CR-0021` | `使用 $spec-sync change-request CR-0021。原始请求是“F001 支持部分收货”；判断最高影响层、受影响 IDs 和失效证据，只写路由提案，不修改 canonical 工件或 roadmap.yaml。` | CR 提案；地图不变 |
| 2 | 无；人类选择 | `我审阅了 CR-0021，确认最高影响层是产品规则，并选择提案中的 product amendment 路径；不要执行其他路径。` | 授权下一项；地图不变 |
| 3 | `$product-discovery-roadmap amend CR-0021` | `使用 $product-discovery-roadmap amend CR-0021，只为“部分收货”提出受影响 PRD/roadmap 规则的候选修订；canonical 文件和 roadmap.yaml 暂时不变。` | product amendment；地图不变 |
| 4 | `$product-discovery-roadmap approve-amendment` | `使用 $product-discovery-roadmap approve-amendment CR-0021；我 <姓名> 于 <日期> 批准完整修订集，依据是本消息；应用到 canonical product 文件并停止。` | canonical 产品事实更新；必要时校正 `docs.*` |
| 5 | `$architecture-baseline amend CR-0021`，仅影响共享技术边界时 | `使用 $architecture-baseline amend CR-0021，评估部分收货是否改变库存状态、事务或集成边界；只写架构修订和 proposed ADR，不修改 accepted baseline。` | 架构修订提案；地图不变 |
| 6 | `$architecture-baseline approve`，仅执行第 5 步后 | `使用 $architecture-baseline approve CR-0021；我 <姓名> 于 <日期> 批准列出的 baseline/ADR 变更，依据是本消息；应用完整修订并停止。` | canonical 架构更新；地图路径通常不变 |
| 7 | 无或 Spec Kit | `从修订后的 Roadmap 重新选择 Direct/Detailed route；重建 checklist，清空旧 boxes、Evidence 和 Decision；设为 planned 并删除 verified。Detailed route 同时刷新 spec/plan/tasks。` | behavior source/checklist；`planned`、无 `verified` |
| 8 | `$spec-sync pre-implement F001 feature` | `使用 $spec-sync pre-implement F001 feature，按选定 route 检查修订后的输入；报告后停止。` | Direct: response；Detailed: pre-review |
| 9 | 无；普通实现，或可选 `$guided-tdd-pairing` | `我批准当前 route 的 pre-check。现在只实现部分收货变更及所需测试/迁移，并把 F001 设为 implementing；不要验收。` | 代码/测试/迁移；`implementing` |
| 10 | `$spec-sync post-implement F001 feature` | `使用 $spec-sync post-implement F001 feature，把真实执行证据写进 checklist；不要勾选或作 acceptance decision；无 blocker 时设为 verifying。` | Evidence；`verifying` |
| 11 | 无；必须开新对话 | `独立核对 F001 最新 behavior source、checklist、diff、测试和迁移证据，不修代码。若全部满足，我 <姓名> 于 <日期> 接受 F001；否则记录 changes requested。` | 新 Decision；通过时 `accepted` + 新 `verified` |

第 3 步不是 discovery。它只改动 PRD 里被这次变更影响的那几条规则，不重开业务访谈。

## 5. 缺陷与维护

### Bug

先写下可复现步骤、实际结果、期望结果、受影响版本、回归测试。然后逐条发送：

| 必须调用 | 你可以这样说 |
|---|---|
| Spec Kit | `为 BUG-0042 建立 bug spec 和 checklist，只描述重复扫描导致库存加两次的复现、期望行为、边界和回归证据；登记路径并保持 planned。` |
| `$spec-sync pre-implement BUG-0042 bug` | `使用 $spec-sync pre-implement BUG-0042 bug，确认它没有偷偷改变产品规则；报告后停止。` |
| 无；普通实现 | `我批准 BUG-0042 pre-review。只修复该缺陷并增加先失败后通过的回归测试；设为 implementing，不要扩大行为。` |
| `$spec-sync post-implement BUG-0042 bug` | `使用 $spec-sync post-implement BUG-0042 bug，把复现、修复后结果和回归命令写入 checklist；无 blocker 时设为 verifying。` |
| 无；新对话 | `独立核对 BUG-0042 checklist 和回归证据，不修代码；由我明确 accepted 或 changes requested。` |

Bug 不能顺手改变产品规则。如果诊断下来发现是规则本身要改，停下来回到第 1 节走 CR。

### Maintenance

记录边界、兼容性、回退方式和验证方法，使用同样的消息结构，只把 kind 换成
`maintenance`：建立 work request/spec 与 checklist → `$spec-sync pre-implement <ID> maintenance`
→ 普通实现 → `$spec-sync post-implement <ID> maintenance` → 新对话验证。
如果这项「维护」改变了用户可观察到的行为，它就不是维护，重新分类。

## 6. 变更完成前的检查

- 已经确定最高影响层，而不是只读了目标代码；
- 已接受 function 的 `verified` 和旧 checklist 结果没有留在已经变化的行为上；
- 每个受影响的下游 spec、plan、测试、证据都重新验证过；
- 测试、CI、迁移、回退、安全、运维证据按风险给足；
- checklist 是在新对话里核对的。
