# Coding Skill Collection

Feature 规划和交付也支持保持行为不变的精简；所有编码工作流都先复用现有能力，
只增加当前结果所需的最少代码，并保留必要验证。

一套面向个人、小团队和 AI 主导开发的精简流程。默认维护三类核心文档：产品方向、
MVP Feature Map，以及每个 Feature 的计划与真实测试结果。有 UI 的 Feature 可以按需
增加一份低保真 Storyboard。

## 开发流程

```text
Product Brief
  -> [Agent Instructions: AGENTS.md + CLAUDE.md + Copilot]
  -> Feature Map + Technical Direction
  -> [optional Feature Storyboard]
  -> Feature Plan
  -> Feature Delivery (auto | guided)
```

Agent Instructions 只写路由、优先级、已验证命令和工作规则，因此 Brief 定稿后即可
生成。技术方向仍留在 Feature Map 中，由 `AGENTS.md` 链接。构建命令、目录约定或
Feature Map 发生变化后，可以再次运行它刷新。

这是常见路线，不是自动执行的阶段链。每个 Skill 都可以根据用户的自然语言意图自动
选择，不要求用户点名。一个已有或缺失的产物本身不授权相邻 Skill；只有原始请求同时
覆盖多个可观察结果时，协调器才可以依次选择多个 Skill。

不要求独立的 discovery、PRD、roadmap、architecture baseline、project map、
checklist、spec sync 或审批文档。Git 保存历史；文档只保存当前事实。

## 使用示例

参见 [WMS 工作流示例](examples/wms-workflows.md)。

## Skills

| Skill | 作用 | 默认产物 |
|---|---|---|
| [`product-brief`](10.product-brief/SKILL.md) | 探索或记录产品目的、用户、核心流程和 MVP 边界 | 探索时仅对话；定稿时写 `docs/product-brief.md` |
| [`agent-instructions`](15.agent-instructions/SKILL.md) | 为软件、文档、分析、演示、运维和混合仓库生成或审计项目 agent 指令 | 三份根指令文件；按需增加受控的 scoped instructions |
| [`feature-map`](20.feature-map/SKILL.md) | 确定 MVP Features、依赖、技术方向和整体架构 | `docs/feature-map.md` |
| [`feature-storyboard`](25.feature-storyboard/SKILL.md) | 按需展示一个 UI Feature 的关键状态和交互 | `docs/storyboards/<feature-id>-<slug>.html` |
| [`feature-plan`](30.feature-plan/SKILL.md) | 规划单个 Feature 的新实现或保持行为不变的精简，以及 happy path 和 failure path 验证 | `docs/features/<feature-id>-<slug>.md` |
| [`feature-delivery`](40.feature-delivery/SKILL.md) | 自动实现、精简或指导用户实现一个已规划 Feature，并记录真实测试结果 | 更新代码、Feature Plan 和 Feature Map 状态 |
| [`skill-authoring`](skill-authoring/SKILL.md) | 创建或精简本仓库中的 Skill | 目标 Skill 及本能力表 |
| [`skill-deployment`](skill-deployment/SKILL.md) | 将本仓库明确配置的 Skill 同步到 Copilot、Claude Code 和 Codex | 目标目录更新及受管清单 |
| [`markdown-reflow`](markdown-reflow/SKILL.md) | 用确定性脚本合并被硬换行拆散的 Markdown 段落,保留空行分段、标题、列表、引用、表格和代码块 | 按需修改指定的 `.md` 文件 |

## 文档边界

- Product Brief 只在用户要求创建、定稿或更新时保存产品目的、用户、核心流程和 MVP
  边界。用户指定的既有 domain knowledge 只是可选输入，不由该 Skill 创建或维护。
- Agent Instructions 为软件、文档、分析、演示、运维和混合仓库保存路由、优先级、
  已验证命令、沟通规则和工作规则；可按仓库证据选用 C#、Python、frontend、
  EditorConfig 比较和分支策略参考。除三份根指令文件，以及用户要求或已验证的
  subtree/surface 差异所需的 scoped instructions 外，它不创建代码、项目产物或样式
  配置，也不制定分支策略。`AGENTS.md` 是唯一权威文件，适配层和 scoped instructions
  不得复制通用规则。
- Feature Map 只保存 Feature 结果、依赖、共享技术和整体架构。
- Feature Storyboard 只保存一个 UI Feature 的可见状态和交互转换；它是可选产物，不
  保存实现设计、测试或生命周期状态。
- Feature Plan 只保存该 Feature 的实现步骤、测试设计和真实结果。
- 下游文档链接上游文档，不复制上游内容。

## Feature 状态

- `planned`：尚未开始实现。
- `in_progress`：已经开始，当前仍可继续推进；测试失败或 guided mode 等待用户实现
  时仍使用此状态。
- `blocked`：存在一个具体条件，使当前无法继续。
- `verified`：所有计划场景已实际通过且没有 blocker。

每个 Skill 在创建或修改文档后，都必须扫描项目中的相关文档，检查冲突、重复、过期
名称、路径和状态。机械问题在同一轮修正；只有会改变产品行为、UI 交互、技术方向或
职责边界的语义决定才询问用户。
各项能力的详细契约以对应 `SKILL.md` 为准；本文件只维护公开能力和文档边界。
