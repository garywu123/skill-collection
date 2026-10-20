# Atlassian Reference

Atlassian content reaches Copilot through the `knowledge-export` script, which
finds Confluence pages, filters Jira with JQL, and writes their text into one
file without passing it through the agent. It uses the personal API token, so
it keeps working when the Atlassian Rovo MCP server's sign-in has expired.

## Locate the script

The script is `knowledge-export/export_context.py` in the `atlassian-automation`
repository. Find that repository's path in the workspace's repository registry
(for example `context/repos.md`); otherwise ask the user once. Run it with the
repository's own Python, `<repo>\.venv\Scripts\python.exe`.

## Find

- Confluence: `export_context.py --search '<specific title words>' --limit 8`
  prints candidates (`id`, `title`, `space`, `modified`, `url`) and writes no
  file. Prefer the team space over personal spaces. Skip pages that only say
  they were moved. When two versions of the same page compete, such as an
  underscore-prefixed copy and the original, export both: page text never
  enters your context, and Copilot can compare them.
- Jira: write exact JQL, such as
  `project = AET2 AND text ~ "LIT2" ORDER BY updated DESC`.
- Rovo `search` (Atlassian MCP) is optional, for broad discovery across Jira,
  Confluence, and linked tools when its sign-in works; each call can consume up
  to 10 Rovo credits.

## Export

```powershell
& '<repo>\.venv\Scripts\python.exe' '<repo>\knowledge-export\export_context.py' `
    --page-id <id> <id> --jql '<jql>' --max-issues 10
```

It prints a JSON summary with `file`, `chars`, and per item `system`, `title`,
`modified`, `url`, `chars`, and `truncated`. Attach `file` to Copilot; cite
the item `url` values. Never open the file.

## Atlassian direct

When the route needs exact records without Copilot, read them with the
Atlassian MCP tools `getJiraIssue`, `searchJiraIssuesUsingJql`, or
`getConfluenceContent` (`detail: "summary"` first). If those tools report an
authentication error, export the records with the script and read only the
needed section. Do not call tools that create, edit, comment on, or
transition issues or pages.
