# Example 1：简化本地库存软件

## 场景

单机、本地使用，只做两件事：货物入库与货物出库。一个进程、一个本地数据库、一个维护团队，没有审计或外部合同约束。

AI 仍先识别 domain，再定义 feature：`inventory-movement` domain 下有 `F001 Add Stock` 与 `F002 Remove Stock`。小项目里 domain 与 feature 很接近，但 Roadmap 仍保留两个字段。

## 顺序、模式与产物

| Step | 人类调用 | Skill 自动选择 | 主要产物 | 下一步 |
|---|---|---|---|---|
| 1 | `$project-map init` | 不预设 profile | `roadmap.yaml`, `AGENTS.md` | 开始 discovery |
| 2 | `$product-discovery-roadmap discover` | 单文件 discovery | `doc/product-discovery-notes.md` | 人类 review/approve |
| 3 | `draft-prd`、review、`approve-prd` | 单文件 PRD | `doc/general-product-requirement.md` | Draft Roadmap |
| 4 | `draft-roadmap`、review、`approve-roadmap` | `lite + single`；先检查 feature cohesion | `doc/feature-roadmap.md`；map 中新增 domain-aware F001/F002 | 建 Architecture |
| 5 | `$architecture-baseline create`、review、`approve` | Lite | `doc/architecture-baseline.md` | Refresh map |
| 6 | `$project-map refresh` | 记录已存在事实 | 更新 `roadmap.yaml`, `AGENTS.md` | 计划 F001 |
| 7 | `$feature-implementation-plan plan F001` | compact | `specs/F001-add-stock/implementation-plan.md`, `checklist.md` | Pre-implementation review |
| 8 | `$spec-sync pre-implement F001 feature` | compact | `Pass/Blocked` 响应；不新建 review 文件 | 人类授权 TDD |
| 9 | TDD implementation | 每个 slice 做 red/green/refactor | 代码与测试 | Post review |
| 10 | `$spec-sync post-implement F001 feature` | compact | checklist Evidence；状态最多到 `verifying` | 新 conversation 验证 |
| 11 | 人类 fresh-context 验证 | — | checklist Decision、`accepted`、Roadmap 勾选 | 计划 F002 |

每个 approval 都是单独的人类操作；表格不会授权 AI 自动连跑。

## 关键文件内容

```text
roadmap.yaml
doc/
  product-discovery-notes.md
  general-product-requirement.md
  feature-roadmap.md
  architecture-baseline.md
specs/
  F001-add-stock/
    implementation-plan.md
    checklist.md
```

- Roadmap：domain、feature outcome、requirement ownership、acceptance、dependency。
- Architecture Lite：本地持久化边界、事务/错误策略、所有 feature 都必须遵守的短约束；不列 feature 内部 classes。
- Implementation plan：例如 `InventoryItem`/`StockLedger` 或仓库实际采用的模块、关键函数、垂直 slices、slice 依赖、unit/integration 计划。
- Checklist：Roadmap acceptance、适用架构约束、实际测试命令和结果、fresh-context decision。

如果没有 UI，Roadmap 写 `UI Surface: none`，不创建 wireframe。F001 完成后才单独规划 F002；不一次性为所有 feature 生成计划。
