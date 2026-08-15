# Example 3：Planning 发现 Feature 太宽

## 输入

已批准 Roadmap 中有一行：

```text
F020 | Putaway Management | putaway | Complete all putaway work ...
```

它同时包含策略选择、任务生成、移动执行、异常处置和确认。每部分可独立交付，拥有不同 state transition 和 acceptance path。

## 正确流程

| Step | 调用 | 结果 |
|---|---|---|
| 1 | `$feature-implementation-plan plan F020` | Skill 先 assess，判定 `reassess` |
| 2 | 自动停止 | 不创建 plan/checklist，不编辑 Roadmap/map，不分配新 F-ID |
| 3 | 输出 `Roadmap Reassessment Handoff` | 用临时标签列出候选 outcomes、PR/AC 分配、依赖、共同约束和 open decisions |
| 4 | 人类给 CR-ID 并调用 `$product-discovery-roadmap amend CR-0042 ...` | 只创建 amendment proposal；canonical roadmap 不变 |
| 5 | 人类 review 后调用 `approve-amendment CR-0042` | Roadmap 分配正式 F-ID，并同步受影响控制行 |
| 6 | 对一个新 feature 重新调用 `$feature-implementation-plan plan F0XX` | 若 cohesive，创建 compact packet |

handoff 的临时拆分可能是：

- Candidate A — Determine Putaway Destination
- Candidate B — Release Putaway Tasks
- Candidate C — Execute Inventory Move
- Candidate D — Handle Putaway Exception

这些不是 canonical feature IDs。只有 Product Roadmap owner 可以在 approved amendment 中形成 F-ID。

## 为什么不直接切到 Spec Kit

F020 的问题是产品边界太宽，不是缺少更多实现文档。给一个 domain-sized feature 写更大的 spec/plan 会掩盖独立验收、排期和依赖。先修 Roadmap；只有拆分后某个 cohesive feature 仍有复杂协议、状态机或合规追踪模型时，才考虑 detailed exception。
