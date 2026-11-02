# 图表转换 Functional Specification

**产品方向：** [图表转换 Product Brief](product-brief.md)

本文只列产品必须做到的可观察行为，不记录状态。交付状态记在引用需求 ID 的 Feature Map 行里，技术设计在 Architecture Design 里，交付顺序在 Roadmap 里。每条有效需求都要分配到某个 Map 行或未来的 Roadmap 行；只有 `verified` 的 Map 行才算交付。

## 功能区域

| 区域 | 前缀 |
|---|---|
| 所有区域共同遵守的约定 | `FS-COM` |
| Mermaid 编辑器 | `FS-EDT` |
| Confluence 双向工作流 | `FS-CNF` |
| Visio 导出 | `FS-VIS` |

## FS-COM 共同约定

- **FS-COM-001 资料留在原位置。** 编辑、发布、取回都以现有 Work Hub / Active 项目文件夹里的文件为准，不要求把资料迁到别处。Mermaid 既可以内嵌在 Markdown 笔记的 fenced code block 里，也可以是单独的 Mermaid 文件，两种都是有效输入。证据：操作前后文件仍在原路径。
- **FS-COM-002 文本仍可被 AI 读写。** 保存或取回后的 Markdown 和 Mermaid 仍是普通文本，用文本编辑器或 AI 打开能直接读到、改到图的内容。证据：不经编辑器，直接打开保存后的文件能看到 Mermaid 源码。

## FS-EDT Mermaid 编辑器

主用户打开一份内嵌 swimlane 图的会议笔记，先让编辑器自动排成横向，再把几个节点拖到更顺眼的位置，保存后关掉。第二天重新打开，节点还在昨天拖好的位置；笔记仍在原文件夹，AI 照样能读里面的 Mermaid。

- **FS-EDT-001 支持最新版 Mermaid。** Mermaid NG 用当前已发布的最新版 Mermaid 渲染图，已有的编辑能力在新版本上继续工作。证据：用只有新版本才支持的语法写的图能正常渲染。
- **FS-EDT-002 Swimlane diagrams.** Open, render, edit and save native Mermaid swimlane diagrams. Moving a node within its lane changes geometry only; dropping it into another lane changes its logical responsibility and placement, with lane membership saved in the Mermaid text. Evidence: after a cross-lane move, the text assigns the node to the destination lane and reopening preserves that membership.
- **FS-EDT-003 保留已有能力。** 升级后，已有的普通 flowchart 编辑能力和其他现有能力继续可用。证据：升级前能编辑的 flowchart 升级后仍能打开、编辑、保存。
- **FS-EDT-004 Text and visual editing.** Both modes edit the same diagram. Visual changes to logic, including cross-lane moves under FS-EDT-002, update the Mermaid text; geometry-only moves follow FS-EDT-007. Evidence: the text reflects a visual change to lane membership, while a move within the lane preserves the logic.
- **FS-EDT-005 可重复的升级脚本。** Mermaid 发布新版后，主用户运行同一个升级脚本，就能让 Mermaid NG 用上该版本；之后每次新版发布都能再用这个脚本。证据：运行脚本后编辑器使用的 Mermaid 版本变为新版本，且 FS-EDT-003 仍成立。
- **FS-EDT-006 自动排版和方向选择。** 主用户可以让编辑器自动排版，并选择横向或纵向。证据：同一张图分别选横向和纵向，得到对应方向的布局。
- **FS-EDT-007 Preserve manual node positions.** Manual adjustments override automatic placement and survive saving and reopening in Mermaid NG. After text edits by the author or AI, nodes with the same ID and unchanged parent retain their saved positions; label edits preserve identity. New nodes are automatically placed around existing pinned nodes. Deleted IDs lose their saved positions; a renamed ID is a new node. A parent change may reposition the node to keep it inside its new lane. Boundary: this applies in NG; exact edge-waypoint retention and identical layouts in other renderers are not promised. Evidence: in both a flowchart and a swimlane diagram, manually position nodes, save, let AI add a node and edit an existing label, then reopen: existing nodes with unchanged IDs and parents remain in place and the new node is automatically placed.

## FS-CNF Confluence 双向工作流

主用户把一份含 Mermaid 和图片的项目笔记发布到 Confluence Cloud。同事不懂 Mermaid，直接在页面里的 Whiteboard 上加了一个步骤。主用户把修改取回，先检查重建出来的 Mermaid 和文字，确认无误后接受，本地笔记随之更新；页面里一个没见过的 macro 在检查时被单独标了出来，而不是被当成已还原的内容。

- **FS-CNF-001 Publish to a page.** Publish local Markdown to its corresponding Confluence Cloud page, preserving text and images. Before updating an existing target, check the page and each associated Whiteboard separately against the remote revisions/change markers last published or explicitly resolved under FS-CNF-005. If either changed, retrieve and review those changes before publishing. An explicit reviewed "Keep local and publish" choice permits replacing only that reviewed remote revision without adopting its candidate locally; any newer remote change blocks publishing and requires another retrieval/review. There is no unchecked overwrite bypass or automatic merge. Evidence: the published page contains the original text and images; a page-only or Whiteboard-only edit blocks republishing until resolved under FS-CNF-005, and a newer edit blocks again.
- **FS-CNF-002 Mermaid 变成可编辑 Whiteboard。** 发布时每张 Mermaid 图变成由可编辑形状和连线组成的 Whiteboard，不是一张图片，并留在文档中原来的位置；Whiteboard 嵌在页面或子页面里时，也保持它与所属文档的关联和位置。证据：在 Confluence 中能单独移动、修改其中的形状和连线，且 Whiteboard 出现在原 Mermaid 所在位置。
- **FS-CNF-003 内容优先，格式尽量贴近。** 转换中，文字内容和 Whiteboard 不能丢，图片也要保留；格式尽量贴近本地 Markdown，以 Obsidian 格式为标准，取回的结果要能被顺利解析。没有对应物的纯装饰细节（如 icon）可以丢掉。证据：一份往返后的笔记，文字、图和图片都在，能被 Obsidian 正常打开解析；只有装饰细节缺失。
- **FS-CNF-004 Author-triggered retrieval.** The author can retrieve page or Whiteboard changes to update local Markdown and Mermaid. For shapes published by this product, retrieval reuses their known Mermaid node IDs; only genuinely new shapes receive new IDs. Evidence: after a colleague edits a label and adds a shape, the retrieved candidate includes both edits, keeps existing node IDs and assigns a new ID only to the new shape.
- **FS-CNF-005 Review before accepting or keeping local.** Present the retrieved candidate for the author's review; update local files only when the author accepts it. Alternatively, after review the author may explicitly choose "Keep local and publish", leaving local files unchanged and authorizing publication over only the reviewed remote revision under FS-CNF-001. Merely inspecting, declining, postponing or cancelling neither changes local files nor authorizes remote replacement. Evidence: inspection and decline leave local files unchanged and publishing blocked; accepting updates local files; the explicit keep-local choice leaves them unchanged and allows replacement of the reviewed remote revision only.
- **FS-CNF-006 外来图也能取回。** 不是由本产品发布的图，例如同事在 Confluence 上新建的 Whiteboard，也能被取回成 Mermaid 候选，由主用户检查。重建可以借助原生结构、PDF 或截图加 AI 理解；不承诺完全自动、无损还原。证据：一张同事新建的 Whiteboard 取回后得到可检查的 Mermaid 候选。
- **FS-CNF-007 区分三类非完整还原。** 取回时，无法完整还原的内容要按三类区别对待，并在检查时让主用户看到：保留下来的文字或链接；内容在、只是格式近似的表现性损失；以及拿不到的核心内容。拿不到的核心内容不能被当成重建成功，也不能用编造的文字补上。边界：不要求能还原任意未知内容。证据：一份含未知 macro 的页面取回后，检查结果能指出哪些属于哪一类，且没有凭空生成的正文。

## FS-VIS Visio 导出

- **FS-VIS-001 导出可编辑的 Visio 图。** 主用户能把一张 Mermaid 图导出为 Visio 文件，文件里是可编辑的形状和连线，节点文字和连接关系与原图一致，不是一张图片。证据：在 Visio 中打开导出的文件，能单独移动、修改形状和连线。

## 排除项和未决事项

- 排除：完全自动、无损的双向往返转换。
- 排除：把资料迁出现有的 Work Hub / Active 文件夹。
- 排除：为假设需求预先搭建的通用框架或基础设施。
- 排除：本文不包含 Jira 每日待办；读取 Confluence 页面里嵌入的 Jira 引用属于 FS-CNF，不等于 Jira 任务自动化。
- 未决：嵌入的 Jira 卡片和没见过的 macro 取回本地时，是保留成链接或占位，还是还原内容；这一步是否需要 LLM，还是只用 MCP 返回的原始内容。在决定前，只有 FS-CNF-007 约束这类内容。
- 未决：除 FS-CNF-004 的手动取回外，是否还需要自动同步，以及同步时机。
- 未决：要覆盖哪些 Obsidian 扩展语法，如 callout、wikilink、embed。
- Unresolved: whether remote Whiteboard shape moves update NG manual geometry on retrieval; node identity retention under FS-CNF-004 does not decide geometry adoption.
- 未决：是否需要把 Visio 图转回 Mermaid，还是只做导出。
- 未决：没有任何负责人设定性能、容量、转换保真度或准确率预算，本文不写数值要求。
