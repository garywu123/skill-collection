# 内容编辑与跨平台转换：Product Brief

## 目的

让用户以本地文本和 AI 辅助编辑内容，并根据需要将内容带到其他平台继续查看、编辑和协作。先解决流程图和泳道图在 Mermaid 与 Confluence Whiteboard 之间的转换；长期再扩展到文档和其他平台。

## 用户

- 主要面向在 VS Code 中使用 Markdown、Mermaid 和 AI 的用户，需要直观编辑图表，并与使用其他工具的人员协作。

## 核心流程

1. 在本地以 Markdown 编写主要内容；复杂主题可以用 HTML 补充表达。图表以 Mermaid 为主要来源。
2. 在已有 Mermaid NG 插件中通过文本和可视化方式编辑图表，保留现有 Mermaid 功能，并逐步让操作更像白板。
3. 将 Mermaid 流程图或泳道图转换为 Confluence Whiteboard 中可继续编辑的图形。发布前确认目标；转换时提示无法保留或有歧义的内容。
4. 按需根据 Whiteboard 的节点、文字和连接关系重建 Mermaid，检查结果后将其作为新的 Mermaid 版本。
5. 使用 Skill 辅助设计清晰的流程图，并检查转换结果。

## MVP 1 边界

**包含：** 以 Mermaid NG fork 为基础，聚焦 flowchart 和 Mermaid 的 swimlane 图；支持 Mermaid 到 Whiteboard 的可编辑转换，以及从 Whiteboard 重建 Mermaid。保持 Mermaid 已有功能；不要求两个平台自动同步或完整往返。

**暂不包含：** 只有 Whiteboard 才有的便利贴、手绘等功能；Visio 转换；Markdown、HTML 与 Confluence 页面或 Word 之间的文档转换；其他 Mermaid 图表类型的新转换能力。

## 后续方向

探索 Visio 图表转换，以及 Markdown、HTML、Confluence 页面和 Word 内容的导入或发布。HTML 是复杂主题的补充，不要求所有 HTML 都由 Markdown 生成。

## 待确认问题

- Whiteboard 无法可靠提供结构时，是否需要在 MVP 1 中支持从 PNG 辅助重建 Mermaid？识别结果如何交给用户确认？
- 哪些形状、标签、泳道归属和布局信息必须保留？是否需要在 Mermaid 之外保存布局信息？
- 产品使用场景和公司数据处理边界是什么？在用户环境中如何可靠地访问 Whiteboard？
- Visio 和文档整合的优先顺序是什么？