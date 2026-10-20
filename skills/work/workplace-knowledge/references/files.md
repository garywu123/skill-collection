# Files Reference

Use when an answer returned files, pages, or issues. Show them in one table
(name, system, location, link) and ask whether to do nothing, index them, or
download Microsoft 365 files. Never download by default.

## Index

1. Ask for the index path. If the working repository defines where source
   links belong, such as a topic `sources.md`, follow that convention.
2. If summaries are missing, ask Copilot in the same conversation to describe
   each item in two or three sentences.
3. Write one entry per item. Update an existing entry with the same link
   instead of adding a duplicate. Confluence pages and Jira issues are
   indexed as links only.

```markdown
## <title>

- Link: <url>
- System: <SharePoint | OneDrive | Confluence | Jira>
- Location: <site, library, space, or project>
- Summary (<source>, <YYYY-MM-DD>): <two or three sentences>
- Found by: "<question>"
```

## Download

1. Ask for the destination folder; pass it as an absolute path.
2. Before downloading a file that lives in a SharePoint library, warn that the
   local copy becomes a personal duplicate and the library copy stays
   authoritative.
3. Call `copilot_download`. Report each result: `downloaded`, `exists`,
   `skipped` (folders), or `failed`. Never set `overwrite` without the user's
   confirmation. Report a policy block as blocked; do not work around it.
