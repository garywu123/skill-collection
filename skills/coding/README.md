# Coding Skill Collection

一套面向个人、小团队和 AI 主导开发的精简流程。默认只维护三类文档：产品方向、
MVP Feature Map，以及每个 Feature 的计划与真实测试结果。

## 开发流程

```text
Product Brief
  -> Feature Map + Technical Direction
  -> Feature Plan
  -> Implement + Test + Record Results
```

不要求独立的 discovery、PRD、roadmap、architecture baseline、project map、
checklist、spec sync 或审批文档。Git 保存历史；文档只保存当前事实。

## Skills

| Skill | 作用 | 默认产物 |
|---|---|---|
| [`product-brief`](10.product-brief/SKILL.md) | 快速确定产品目的、用户、核心流程和 MVP 边界 | `docs/product-brief.md` |
| [`feature-map`](20.feature-map/SKILL.md) | 确定 MVP Features、依赖、技术方向和整体架构 | `docs/feature-map.md` |
| [`feature-plan`](30.feature-plan/SKILL.md) | 规划单个 Feature 的实现、happy path 和 failure path 验证 | `docs/features/<feature-id>-<slug>.md` |
| [`feature-delivery`](40.feature-delivery/SKILL.md) | 实现 Feature、运行测试并将真实结果写回 Feature Plan | 更新代码、Feature Plan 和 Feature Map 状态 |
| [`skill-authoring`](skill-authoring/SKILL.md) | 创建或精简本仓库中的 Skill | 目标 Skill 及本能力表 |

## 文档边界

- Product Brief 只保存产品目的、用户、核心流程和 MVP 边界。
- Feature Map 只保存 Feature 结果、依赖、共享技术和整体架构。
- Feature Plan 只保存该 Feature 的实现步骤、测试设计和真实结果。
- 下游文档链接上游文档，不复制上游内容。

每个 Skill 在创建或修改文档后，都必须扫描项目中的文档，检查冲突、重复、过期名称、
路径和状态。机械问题在同一轮修正；只有需要产品或技术决策时才询问用户。

## 归档

上一版多阶段流程和场景 instructions 保存在
[`_obsolete/framework-v1`](_obsolete/framework-v1/README.md)，仅作为历史参考，
不参与部署。