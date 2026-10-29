# 图表转换工具与 Skill：产品构思

状态：历史探索记录。当前产品方向、MVP 1 范围和待确认问题以 [Product Brief](product-brief.md) 为准；本文保留早期想法和研究线索，不是已批准的产品规格或实施计划。

## 背景

Mermaid 适合用文本和 AI 表达流程，但纯文本编辑不够直观。希望在 VS Code 中拥有更像白板的可视化编辑体验，同时保留 Mermaid 的文本编辑和版本管理能力；后续也希望与 Visio 和 Confluence Whiteboard 交换可编辑图形。

## 想解决的问题

- 以用户已 fork 的 Mermaid NG VS Code 插件为基础，探索更像白板的拖拽、连线和图形编辑体验，而不必总是通过文字告诉 AI 如何修改。
- 保持现有 Mermaid 功能，并优先满足 flowchart 和 swimlane chart；后续可能支持更多 Mermaid 图表类型。
- 先保持 Mermaid 具备的功能，不添加便利贴、手绘等只有白板才有的功能。
- 在此基础上，增加与 Visio 和 Confluence Whiteboard 的转换，并支持从 Visio 或 Whiteboard 转回 Mermaid；各方向的顺序尚未确定。
- 转换后的 Visio 和 Whiteboard 图形应能够继续编辑，而不只是静态图片。
- 让 Skill 根据流程结构设计清晰、易读的 flowchart，包括布局、分支排列、间距、颜色和层次。

## 初步产品方向

VS Code 工具是主要工作界面，基于现有插件增强可视化编辑体验，并保留 Mermaid 编辑能力。泳道使用 Mermaid 的泳道元素。工具负责读取和生成结构，例如节点、文字、形状、连线、箭头和分支标签，并报告不能转换的内容。Skill 负责根据用途设计流程图的视觉表达，以及指导转换后的检查。用户也可以在 Visio 或 Confluence Whiteboard 中继续修改。

三种格式之间的转换可以经过中间表示，不一定需要为每一对格式分别实现转换器。这是待验证的实现思路，不是已定架构。Flowchart 和 swimlane chart 是优先范围；其他 Mermaid 图表类型的增强顺序待确认，不意味着移除插件已有功能。

## 转换与保真

希望保留流程的含义和可编辑性，例如节点、标签、连接方向和分支条件。Visio 和 Whiteboard 可以保存手动布局，而 Mermaid 通常不表达精确坐标：只依靠 Mermaid 往返时，位置、线条路径和视觉样式不一定能还原。

可以探索在 Mermaid 之外保存坐标等布局信息，并在 VS Code、Visio 和 Whiteboard 之间共享，以保留人工调整、减少 AI 重排的工作。具体保存形式、坐标转换和保真程度尚待验证；这不意味着三种格式可以原样共享同一坐标系。对不支持或有歧义的元素，应让用户知道，而不是静默丢弃。

## 现有工具与证据

- [本地 Mermaid NG fork](../../tools/mermaid-visual-editor/README.md)：现有插件说明称支持画布与 Mermaid 文本同步、写回文件、拖拽和多种图表。用户认为整体功能不错；白板式自由布局和保存效果尚需实测。
- [Mermaid 泳道图文档](https://mermaid.js.org/syntax/swimlanes.html)：原生 `swimlane-beta` 从 Mermaid 11.16.0 开始，语法仍可能变化。本地 fork 的说明称内置 Mermaid 11.15.0；需要验证版本和编辑器支持，不能假设现有版本支持该语法。
- [md2visio](https://github.com/Megre/md2visio)：开源的 Mermaid 到 Visio 转换工具，使用本机 Visio；可评估是否复用。
- [Mermaid2Visio](https://mermaid2visio.com/help)：提供 Mermaid 和 Visio 的转换；Visio 到 Mermaid 以流程图为主，在线服务处理公司内容前需要确认使用许可和数据边界。
- [draw.io Mermaid 文档](https://www.drawio.com/blog/mermaid-diagrams)：可将 Mermaid 转为可编辑图形，但图形布局改动不会作为 Mermaid 坐标写回。
- 已通过当前 Atlassian MCP 读取过 Whiteboard 的 SVG，看到形状、文字和连接器的起终点；MCP 的说明提供白板更新操作，其白板格式指南用分区矩形和标签构造泳道。2026-10-28 在个人 space 创建了泳道模板测试白板，读回图形和连接器；导出的图片中两条泳道的背景遮住了节点。尚未验证手动编辑或可靠转换。[Confluence REST API v2 白板文档](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/)目前未列出白板内部元素的读写接口。

以上现有工具的能力来自产品说明或一次读取验证，尚未验证实际转换质量，也不能证明市场上不存在其他完整方案。

## 早期待确认问题

1. 哪个转换工作流程优先：Mermaid 与 Visio 往返，还是 Mermaid 与 Confluence Whiteboard 往返？Visio 和 Whiteboard 是否也需要直接转换？
2. 当多个版本都被修改时，如何决定以哪一份为准？手动触发转换是否足够，还是希望自动同步？
3. 共享的布局信息如何保存，以及关闭重开和不同工具往返后需要保留到什么程度？
4. 除布局外，往返时哪些内容必须保留，例如颜色、形状、连接路径和分组？
5. 主要使用场景是个人本地工作，还是需要与团队共享和协作？对本地运行、公司数据和第三方服务有什么限制？
6. Skill 的视觉风格应更接近 Visio 的正式业务流程图，还是 Whiteboard 的协作草图？是否有现成示例可参考？

## 早期候选验证

- 用真实 flowchart 和 swimlane chart 检查本地插件：验证 Mermaid 版本、泳道语法和可视化编辑支持，检查文本同步、自由布局以及关闭重开后的效果。
- 用同一张图验证 Mermaid → Visio → Mermaid：检查可编辑性、节点、连接方向、标签和转换损失。
- 在明确授权的测试白板中验证 Mermaid → Whiteboard → Mermaid：检查节点和泳道是否可编辑、泳道归属、连接关系和读取结果。
- 根据验证结果决定哪些现有工具可复用，以及需要开发哪些工具和 Skill。