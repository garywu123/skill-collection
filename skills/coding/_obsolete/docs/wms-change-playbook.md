# WMS Change Playbook

本手册用于已有 WMS 仓库。它的目标是先判断变更影响了哪一层已批准事实，再只重做必要的
下游工作。不要从“改代码”开始。

## 1. 所有变更的入口

对任何不确定的请求，先明确请求：

```text
$spec-sync change-request CR-XXXX
```

它会产生一个**提案**，列出最高影响层、受影响 ID、会失效的下游证据、拥有者和建议的下一条
人工授权。它不会修改 PRD、roadmap、架构、代码或状态，也不会替你启动后续 Skill。

## 2. 选择正确的工作类型

| 请求 | 示例 | 路由 | 最终验证 |
|---|---|---|---|
| 新业务能力 | 新增波次拣货 | product/roadmap amendment → 新 successor Feature | Feature acceptance |
| 业务规则变化 | 允许超收，或部分收货 | product amendment；必要时 architecture amendment；新 successor Feature | Feature acceptance |
| 已接受功能的改动 | F001 收货改为部分收货 | 创建说明 supersession 的新 Feature；保留 F001 历史 | 新 Feature acceptance |
| 未交付 Feature 的内部调整 | 实现前变更收货页面字段 | 重新授权 specification/clarify，刷新受影响 plan/tasks/UI | pre/post review 后验收 |
| 缺陷 | 重复扫描导致库存加两次 | `bug` work item，复现与回归测试 | post-implementation + generic human review |
| 不改变外部行为的改善 | 查询索引、重构、日志 | `maintenance` work item | post-implementation + generic human review |
| 数据模型或数据迁移 | 库存台账表拆分 | `migration` work item；dry run、回退、恢复 | post-implementation + release evidence |
| 权限/安全修复 | 仅主管可撤销收货 | `security` work item；threat/abuse case | post-implementation + applicable security evidence |
| 跨域技术边界变化 | 库存改为事件驱动 | architecture amendment 和 ADR；再创建受影响 work item | 每个 work item 独立验证 |

## 3. 新增 Feature 的路径

以“新增波次拣货”为例：

```text
change-request CR-0012
→ 产品/roadmap amendment（若新增业务承诺或依赖）
→ architecture amendment（若改变库存预留、任务分配或共享约束）
→ 人工批准每个 amendment
→ 建立 successor Feature，例如 F007
→ Spec Kit specify/clarify/plan/tasks
→ spec-sync pre-implement
→ 人工批准
→ 实现与测试
→ spec-sync post-implement
→ independent acceptance
→ 人工 Accepted
```

只有当 CR 证明它只是一个未交付 Feature 的内部调整时，才可以跳过产品或架构 amendment。
“看起来很小”不是跳过依据。

## 4. 修改已接受 Feature 的路径

已接受 Feature 是历史证据，不能原地改写其 spec、acceptance 或决定。假设 `F001 收货` 已接受，
现在要支持部分收货：

1. 建立 `CR-0021`，由 `spec-sync change-request` 确定最高影响层。
2. 如业务承诺改变，先用 `$product-discovery-roadmap amend CR-0021` 写候选提案；人工审阅、批准后才更新 canonical PRD/roadmap。
3. 如库存状态机、并发、集成或共享约束改变，再用 `$architecture-baseline amend CR-0021`；人工批准后才更新 baseline/ADR。
4. roadmap 创建后继 Feature，例如 `F008 部分收货（supersedes F001）`。
5. F008 走完整的 feature loop：spec → plan/tasks → pre-review → 实现 → post-review → acceptance → Accepted。

这保证未来仍能回答：“旧 F001 在当时批准了什么；新规则从哪个 Feature 和 release 开始生效。”

## 5. 缺陷和维护路径

### Bug

先记录可复现步骤、实际结果、期望结果、受影响版本和回归测试。然后：

```text
创建 BUG-### spec
→ plan/tasks
→ $spec-sync pre-implement BUG-### bug
→ 人工批准
→ 修复与回归测试
→ $spec-sync post-implement BUG-### bug
→ generic decide approved/rejected
```

Bug 不使用 `accept-feature`，也不能借此悄悄改变产品规则；若诊断发现规则本身要改，回到 CR。

### Maintenance

记录边界、兼容性、回退方式和验证。使用 `maintenance`，执行同样的 pre/post 对齐和 generic review。
如果维护工作改变用户可观察行为，它就不是 maintenance，应重新走 CR 分类。

## 6. 变更完成前的检查

- 已确定最高影响层，而非只阅读目标代码；
- 已接受 Feature 的历史没有被覆盖；
- 每个受影响的下游 spec、plan、test、verification 和 acceptance 都已重新验证；
- 测试、CI、迁移、回退、安全和运维证据按风险提供；
- 只有人工显式决定才能改变 gate、接受 Feature 或授权 release。
