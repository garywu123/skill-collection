# 图表转换 Architecture Design

**Scope:** 图表转换跨区域的组件边界、数据归属、外部契约和技术选择。目前没有 Feature Map 引用本文。

**Sources:** [图表转换 Product Brief](product-brief.md)，[图表转换 Functional Specification](functional-spec.md)

标“建议”的是未经产品确认的技术建议。Spec 的未决项本文不替它决定。

## System Context

- **本地资料**：Work Hub / Active 里的 Markdown 和 Mermaid 文件，是 source of truth（FS-COM-001、FS-COM-002）。
- **Mermaid NG**：扩展现有 VS Code fork，不另做编辑器。
- **上游 Mermaid**：[swimlane-beta 从 v11.16.0 引入](https://mermaid.ai/open-source/syntax/swimlanes.html)，语法可能变化；[v12](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4012.0.0) 是 breaking release。
- **现有 AI assistant + 官方 Atlassian MCP**：建议作 Confluence 流程的按需宿主和 LLM 来源。
- **Confluence Cloud**：只经官方 MCP 访问。**Visio**：只作导出目标。

## Components

| Component | Owns | Does not own |
|---|---|---|
| Mermaid NG 编辑器 | 文本和可视化编辑、swimlane、自动排版和方向、手动几何、现有能力（FS-EDT-002 到 FS-EDT-007） | 新 layout 算法；外部转换 |
| 打包的 Mermaid + 升级脚本 | 固定版本副本、替换脚本、升级后兼容性检查（FS-EDT-001、FS-EDT-005） | 未来 major 版本免维护 |
| 渲染几何 | NG 实际渲染出的节点、文字、泳道、连线和坐标 | 流程逻辑；通用 schema |
| Confluence 转换 | 发布映射、取回候选、损失报告、检查后写回（FS-CNF-*） | 常驻 service、数据库、自动同步、独立 LLM 账号、新的必需 UI |
| Visio 导出 | 把渲染几何写成可编辑形状和连线（FS-VIS-001） | 现在的实现；反向转换 |

## Technology

- **Runtime:** 编辑器沿用 fork 的 VS Code extension 和 webview。Confluence 转换由 assistant 会话调用确定性脚本和 MCP tool；载体（例如本仓库一个 Skill 加脚本）是建议。
- **Layout:** 复用 Mermaid 自带 engine，不写新算法。[v12 打包 ELK](https://mermaid.ai/open-source/config/layouts.html)，普通 flowchart 默认 ELK，Dagre 仍可用；这不代表其他图类型。swimlane-beta 支持 TB/TD/BT/LR/RL，layout 单独验证。
- **方向:** 写成 Mermaid 文本的标准方向关键字（FS-EDT-006）。
- **打包（建议）:** fork 目前把 Mermaid 11.15.0 inline 在 webview HTML，也不识别 swimlane-beta。改成独立 vendored 文件并记录版本，升级脚本只换这一处再跑兼容性检查；major 升级仍可能要人工维护。
- **Deployment:** 全在主用户本机按需运行，取回由主用户触发（FS-CNF-004）。

## Contracts And Data Ownership

### 图和几何

- **Logic owner: Mermaid text.** Nodes, edges, labels, lanes, direction and parent membership belong here. A swimlane parent is its Mermaid subgraph membership, with no custom parent syntax. NG writes a cross-lane drop back to that membership and adjusts placement; a same-lane move changes geometry only (FS-EDT-002, FS-EDT-004).
- **Geometry owner: NG association data.** Saved coordinates override automatic placement in NG (FS-EDT-007). A sidecar alone cannot provide dragging, attached/rerouted edges, restoration or export integration. The layout loader is a candidate integration point; whether the existing engine can place new nodes around pinned ones remains unverified. Applying coordinates after a full layout alone does not establish that capability. Exact edge-waypoint retention is not promised.
- **Identity:** use Mermaid node IDs. **Diagram key (suggested):** add a short `%%` comment ID when association data is first needed; Markdown block order is unstable.
- **Storage (suggested):** one association file beside the source, keyed by diagram and node ID, with the parent ID at save time as geometry context for comparison with current text. Coordinates stay outside the body. Missing or unmatched geometry falls back to automatic placement for affected nodes without blocking opening or changing text; it does not discard valid positions for other nodes.
- **Source-edit reconciliation:** NG matches node ID and Mermaid parent to retain saved positions under FS-EDT-007. Label changes keep identity; new or renamed IDs receive automatic placement around pinned nodes, deleted IDs lose saved coordinates, and parent changes allow placement inside the new lane. Parent membership is read from text, not independently owned by the sidecar.
- **渲染几何**是派生数据，供 Whiteboard 和 Visio 使用，让导出和屏幕一致，不回写为逻辑。

### Confluence 复合文档

- **Binding (suggested storage):** page ID in note frontmatter; Whiteboard IDs and local image relative-path → page/attachment ID mappings in the existing source association file, owned by Confluence conversion. Distinct image paths stay distinct on retrieval. Store each page's and Whiteboard's last published or explicitly resolved remote revision/change marker and its outcome with its binding where MCP supports it, reusing existing association metadata; no sync database.
- **Update gate:** conversion compares the page and each Whiteboard separately with their recorded markers before updating an existing target (FS-CNF-001). A change requires retrieval and explicit resolution through FS-CNF-005. Markers advance after successful publication, accepted retrieval, or a reviewed explicit "Keep local and publish" decision tied to that target's reviewed revision. The last choice authorizes replacing only that revision without writing its candidate locally. Recheck current markers before updating: a newer remote change requires another retrieval/review. Inspection, decline, postponement and cancellation do not advance markers or authorize replacement. No unchecked overwrite bypass or automatic merge; unavailable change detection remains an unresolved MCP capability.
- **Shape identity:** retrieval preserves known Mermaid IDs for this product's published shapes (FS-CNF-004). Suggested mechanism: store Whiteboard shape ID → Mermaid node ID per diagram in the existing association entry at publication, reuse it on retrieval, and allocate IDs only for genuinely new shapes. Stable shape IDs through MCP remain unverified (Open Decision 3); failed matching must not silently treat every existing shape as new. Whether remote moves replace NG geometry stays with the Spec's unresolved decision.
- **确定性**：标题、段落、列表、表格、链接、本地图片、可访问的 card 引用，在 Obsidian Markdown 和 MCP 页面格式间确定性转换（FS-CNF-003）；可读到原生形状和连线的 Whiteboard 先确定性映射回 Mermaid。
- **语义重建**：外来 Whiteboard 结构不够（FS-CNF-006），或只有图片、PDF 时，assistant 按需用 LLM 出 Mermaid 候选并标出不确定处。
- **写回**：接受前不写原文件，可用 VS Code diff 展示（FS-CNF-005）；三类损失（FS-CNF-007）只在检查时报告，不落盘。

### MCP 契约和证据边界

- **MCP 是 tool 接口**，返回形式和后端处理取决于具体 tool，不能一概认定是原始 REST/ADF 或 AI 摘要。[Rovo search 解释自然语言意图，fetch 读取指定内容](https://support.atlassian.com/atlassian-ai-gateway/docs/use-rovo-search-and-fetch-in-the-atlassian-remote-mcp-server/)。转换输入只用指定内容读取（如 `getConfluenceContent`），search 只用来定位。
- **[官方目录](https://developer.atlassian.com/cloud/rovo-mcp/guides/supported-tools/)声明**：`getConfluenceContent` 读页面、Whiteboard 和 embed；`resolveConfluenceContentMacros` 返回支持的 macro HTML；`createConfluenceContent`、`updateConfluenceContent` 写页面和 Whiteboard；attachment 上传返回 curl 命令，下载返回 URL 或本地命令；`getJiraIssue` 按 key 读 issue；`getContentFormatGuide` 给出格式说明。这只证明能力被声明，不证明转换质量，可用性取决于 tenant 和 scope。
- **REST 不等于 MCP schema**：[REST v2 页面 body](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/) 有 storage、atlas_doc_format、view，不代表 MCP 返回同样格式；不静默改走另一套认证的 REST。
- **嵌入的 Jira 项**：[inlineCard](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/inlineCard/) 带 URL 和引用数据，默认确定性保留为 key、标题和原 URL 的链接，不需要 LLM。主用户要求展开且有权限时，才用现有 Jira tool 读字段；展开策略是 Spec 未决项。
- **没见过的 macro**：先拿可读数据，包括文字、链接内容、支持的 HTML、渲染图或 PDF。有数据时 LLM 帮忙理解，出带不确定标记的候选。拿不到的数据 LLM 补不回来，就保留已有文字或链接并说明损失，不编造核心内容；纯装饰可丢。不做穷举字典，不承诺任意 macro。
- **LLM（建议）**：由现有 assistant 按需提供，不打包常驻模型 service、不另开账号、不设固定阈值、不指定 provider；确定性代码能做的不交给 LLM。

### Visio 边界

- 只读渲染几何。文件格式和生成方式到 Visio 阶段再定。

## Quality Constraints

| Subject | Conditions | Property or budget | Source | Verification |
|---|---|---|---|---|
| 性能、保真度、准确率 | 所有区域 | `open decision`：无人设预算 | [Spec 未决项](functional-spec.md#排除项和未决事项) | 尚无 Testing Strategy |
| Mermaid 升级 | 每次运行升级脚本后 | 现有 flowchart 和 swimlane 样例能打开、编辑、保存 | FS-EDT-003、FS-EDT-005 | 脚本的兼容性检查 |

## Invariants

- Mermaid text owns diagram logic; association data holds geometry, identity mappings and remote markers with explicit resolution outcomes. Invalid geometry falls back to automatic placement only for affected nodes; missing identity or remote-change evidence cannot bypass the Confluence contracts.
- 主用户接受前，取回不改本地文件。
- 拿不到的核心内容只标缺失，不生成替代正文。
- 只用主用户授权的官方 MCP；文件里不放 credential。

## Open Decisions

1. **Manual-layout feasibility (Mermaid NG):** on the target version, establish FS-EDT-007 for both flowchart and swimlane-beta: after manual positioning, an AI label edit and node addition preserve unchanged-ID/parent positions while new nodes are automatically placed around them. Also establish deletion/ID-rename handling, cross-lane membership writeback and placement, attached/rerouted edges, reopening, and agreement between rendered/exported geometry and the screen. This evidence determines layout-loader integration and association storage; check that `%%` diagram IDs do not affect Obsidian rendering. No feasibility result is established yet.
2. **v12 兼容性（Mermaid NG）**：现有编辑和拖拽在 v12 副本上能否工作；证据是现有样例能打开、编辑、保存。结果决定目标版本和脚本检查范围。
3. **Tenant MCP capabilities (Confluence; failures go to product):** use `getContentFormatGuide` and a real composite page with text, tables, images, a Jira card, an unfamiliar macro and an embedded Whiteboard to establish read/write formats, editable shapes/connectors and embedding, native structure retrieval, and rendered-image/PDF access. Separately establish usable page and Whiteboard revision/change markers and stable shape IDs across publication, colleague edits and retrieval. This evidence determines update gating and identity mapping; none is tenant-verified. Missing capabilities leave the corresponding FS-CNF-001/002/004 contract unresolved before implementation; do not substitute unchecked publishing, fresh IDs, REST authentication or images.
4. **LLM 参与范围（产品）**：上面的确定性和 LLM 分工是技术建议；Jira 和陌生 macro 的处理方式仍按 Spec 未决项由产品确认。
