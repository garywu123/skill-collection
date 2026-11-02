# 图表转换 Product Brief

## Purpose

主用户日常用 Markdown 和 AI 处理工作资料，复杂流程很难只靠文字描述给 AI。这个产品让流程图既能用文本写、也能可视化编辑，并能在本地 Markdown、Confluence 和 Visio 之间转换，同时保住内容含义和手动排好的布局。

## Users

- **主用户**：在现有的 Work Hub / Active 项目文件夹里，用偏 Obsidian 格式的 Markdown 管理产品线、项目、演示、会议、邮件和流程图，主要和 AI 一起处理纯文本。需要可视化编辑复杂流程，并把结果分享出去、再把别人的修改拿回来。
- **同事**：可能不懂 Mermaid。需要拿到能直接看、直接改的图，而不是 Mermaid 源码。

## Core Flows

1. **可视化编辑流程图**：主用户打开一份内嵌 Mermaid 的 Markdown 笔记或单独的 Mermaid 文件，在 Mermaid NG 编辑器里用文本或可视化方式修改，包括 swimlane 图。可以先让工具自动排版并选横向或纵向，再手动调整；保存后手动调整的布局不丢，文件仍留在原文件夹，AI 仍能读写文本。
2. **升级 Mermaid 版本**：Mermaid 发布新版后，主用户运行一个升级脚本，让 Mermaid NG 用上新版本。这个脚本可以反复使用。
3. **发布到 Confluence**：主用户把一份本地 Markdown（含 Mermaid 和图片）发布到 Confluence，得到对应的页面：文字和图片保留，Mermaid 图变成由可编辑形状和连线组成的 Whiteboard，并留在文档中原来的位置，包括嵌在页面或子页面里的情况。
4. **把 Confluence 的修改拿回本地**：页面或 Whiteboard 在 Confluence 上被修改后，主用户把改动取回，更新本地 Markdown 和 Mermaid。重建可以利用原生结构、PDF 或截图加 AI 理解，由主用户检查后接受。
5. **导出到 Visio**：主用户把 Mermaid 图导出成 Visio 文件，得到可编辑的形状和连线。

## MVP Boundary

**In（阶段 1：Mermaid 编辑器）：** 让 Mermaid NG 支持最新版 Mermaid 和原生 swimlane 图，保留已有的普通 flowchart 编辑能力；提供可重复执行的升级脚本；提供自动排版（可选横向或纵向），同时允许手动调整并持久保留。对应流程 1 和 2。

**Later：**

- **阶段 2：Confluence 双向工作流**：对应流程 3 和 4。转换优先级：文字内容和 Whiteboard 最重要，图片也重要；格式尽量贴近 Markdown，以 Obsidian 格式为标准、要能顺利解析；没有对应物的纯装饰细节（如 icon）可以丢掉。
- **阶段 3：Visio**：对应流程 5，排在最后。
- **Jira 每日待办**：在三个阶段之后再考虑。

**Out：**

- 完全自动、无损的双向往返转换。
- 把资料迁出现有的 Work Hub / Active 文件夹。
- 为假设需求预先搭建的通用框架或基础设施。

## Product Constraints

- **内容位置**：资料始终留在现有的 Work Hub / Active 项目文件夹里，Mermaid 可以内嵌在 Markdown 中，也可以是单独文件。来源：用户在本次讨论中的回答，来源未定位。
- **Confluence 环境**：阶段 2 面向 Confluence Cloud，通过 Atlassian 官方 MCP 访问。来源：用户回答"Confluence Cloud，使用 Atlassian 官方 MCP"。
- **布局**：自动排版之外，手动调整的布局必须保留。来源：用户回答"必须保留我手动调整的布局"。

## Open Questions

- Confluence 页面里嵌入的 Jira 卡片和以前没见过的 macro，拿回本地时怎么处理：保留成链接或占位，还是还原内容？这一步需要 LLM 参与，还是只用 MCP 返回的原始内容？（处理嵌入的 Jira 引用不等于做 Jira 任务自动化。）
- 从 Confluence 取回修改，是主用户手动触发，还是需要自动同步？
- Obsidian 的扩展语法（如 callout、wikilink、embed）要覆盖哪些？
- 阶段 3 是否也需要把 Visio 图转回 Mermaid，还是只做导出？
