# Example 6：已有仓库接入新流程

## 目标

代码库从未使用这套 spec-driven Skills。接入时先记录“现在实际是什么”，不要把现有代码自动宣称为“产品应该是什么”，也不要为整个历史系统一次性补齐所有 feature plans。

## 顺序、模式与产物

| Step | 人类调用 | AI 行为 | 产物 |
|---|---|---|---|
| 1 | `$project-map init`（已有 map 则 `audit`） | 检查 README、manifests、CI、test commands；profile 暂不猜 | `roadmap.yaml`, routing-only `AGENTS.md` |
| 2 | `$product-discovery-roadmap discover` | 从人类目标与批准 evidence 建 desired product understanding；legacy/code 标为 reference | discovery notes |
| 3 | `draft-prd`、审批 | 区分 desired requirements 与 observed behavior | approved PRD |
| 4 | `draft-roadmap`、审批 | 自动 domain+feature、profile、single/split；已识别实现可记录 `as-built`，不是 `accepted` | approved roadmap + map entries |
| 5 | `$architecture-baseline recover` | 从 manifests、boundaries、representative code 自动选 Lite/Full；每项标 `Verified`/`Inferred` | evidence-labelled baseline |
| 6 | 人类 approve architecture，随后 `$project-map refresh` | 将 approved docs、verified commands、domain/status 路由写入 map/guidance | refreshed map |
| 7 | 要改某个 as-built feature 时，先把它转为 `planned` 并调用 `$feature-implementation-plan plan F0XX` | 只为触碰的 feature 建 compact packet，或要求 Roadmap reassessment | plan + checklist 或 handoff |
| 8 | `spec-sync pre-implement`、TDD、post、fresh verify | 建立新的可追溯 evidence | `verifying`，然后人类 `accepted` |

## Adoption 审计重点

- Roadmap 是否每个 feature 都有 stable domain key，是否存在把整个 subsystem 当成一个 feature 的旧条目。
- Roadmap 的 profile/bundle 是否与真实 feature/domain/team/deployable 证据匹配。
- Architecture 是否只写跨 feature 约束，feature-local classes 是否错误地塞进 baseline。
- `roadmap.yaml` 路径是否存在，`as-built` 是否被误写成 `accepted`。
- 现有 spec/plan/checklist 是否仍与 approved sources 对齐；不对齐时不复用旧 evidence。

接入完成的标准不是“所有文件都补齐”，而是 canonical product/architecture/map 已建立，且下一条要改的 feature 可以安全进入 assess → plan → TDD → evidence 流程。
