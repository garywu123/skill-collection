# Example 5：Change Request

## 场景

已接受的 `F001 Add Stock` 原来只记录 SKU 与数量。新 request 要求同时记录 batch number，并在重复 batch 时合并数量。

## 路由

| Step | 人类调用 | 产物/停止点 |
|---|---|---|
| 1 | `$spec-sync change-request CR-0007` | `doc/change-requests/CR-0007.md` 或等价响应；列最高影响层、affected IDs、stale evidence、每一步 owner |
| 2 | 若 business rule 改变：`$product-discovery-roadmap amend CR-0007` | reviewed product amendment proposal；不改 canonical files |
| 3 | `approve-amendment CR-0007` | approved PRD/Roadmap 更新；F001 reset 为 `planned`，旧 evidence 清除 |
| 4 | 若 shared data/identity rule 改变：`$architecture-baseline amend CR-0007` | architecture proposal，必要时 superseding ADR |
| 5 | `$feature-implementation-plan audit F001` 或 `plan F001` | 重做 component design、slices、test mapping 和 checklist |
| 6 | `$spec-sync pre-implement F001 feature` | alignment Pass/Blocked，停止等待实现授权 |
| 7 | TDD、`post-implement`、fresh verification | 新 evidence；人类重新接受 |

如果只是未交付 feature 的内部实现替换，且 Roadmap behavior 与 Architecture 都不变，可以从 implementation-plan audit 开始。若 feature boundary 变宽，先走 Product amendment；Planning Skill 不能静默扩大 scope。

Change Request 文件只保存原 request、impact 与 pending route，不复制修改后的正式 requirement、architecture decision 或 implementation plan。
