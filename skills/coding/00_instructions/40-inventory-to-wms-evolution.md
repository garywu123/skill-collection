# Example 4：从简化库存软件演进为 WMS

## 变化

原系统只有 `inventory-movement` domain 的 Add/Remove Stock。现在加入收货、上架、库位、批次/序列号、分配、拣选、装运和 ERP 集成。这不是把原 Feature Plan 写长，而是产品范围与跨 feature 架构一起升级。

## 顺序

| Step | 人类调用 | 主要判断与产物 |
|---|---|---|
| 1 | `$spec-sync change-request CR-0100` | 判定最高影响层为 Product；只生成 routing proposal |
| 2 | `$product-discovery-roadmap amend CR-0100` | 提出新/继承 requirements、domains、features、dependency 和 profile/bundle 变化 |
| 3 | `approve-amendment CR-0100` | 应用 approved edit set；Roadmap 从 Lite/Single 演进为 Full/Split（若 sizing evidence 满足） |
| 4 | `$architecture-baseline assess` | 只读指出 Lite baseline 已不能覆盖多 domain、外部合同或一致性决策 |
| 5 | `$architecture-baseline amend CR-0100`，再 `approve` | 提出并批准 Full baseline、domain details、必要 ADR |
| 6 | `$project-map refresh` | 记录 `profile: full`、新 domain/feature 路由和状态；不重写业务内容 |
| 7 | 对第一条新 feature 调用 `$feature-implementation-plan plan F0XX` | 先 assess，再 compact 或输出 reassessment handoff |

## 保留与重做

- 保留 stable PR/F IDs；行为改变的已批准 requirement 使用 successor ID。
- 已接受 feature 若行为改变，默认 reset 为 `planned`、移除 `verified`、清空旧 checklist 结果；只有需要独立部署/支持/追踪时才建立 successor feature。
- 旧 Lite architecture 决策可以被 Full baseline 承接，不从零重写。
- 只为本次要实施的 feature 创建 implementation packet；不要批量生成未来 feature plans。

项目可以随证据从 Lite 平滑演进到 Full，不要求第一天预判最终规模，也不需要把所有 Skills “用 Full 模式重跑一遍”。
