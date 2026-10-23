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
  file. Search in English, the language the pages are written in. Judge each
  candidate by its `space`: prefer the space that owns the product or project,
  skip personal spaces, and skip a short stub or a page that only says it was
  moved. Exporting an unrelated page costs a slower upload and a weaker answer.
  When two versions of the same page compete, such as an underscore-prefixed
  copy and the original, export both: page text never enters your context, and
  Copilot can compare them.
- Jira: write exact JQL, such as
  `project = AET2 AND text ~ "LIT2" ORDER BY updated DESC`. A board or filter
  link is not JQL. Derive one from the project key in the link, such as
  `project = AET AND statusCategory != Done ORDER BY updated DESC`, and state
  the JQL you used in the brief so the user can correct it.
- Keep `--max-issues` at 10 or fewer unless the user asked for a full list. A
  board query that returns everything open is the usual cause of a slow run
  and an oversized context.
- Because the cap truncates, choose the sort for the question. `ORDER BY
  updated DESC` favors recent churn and will silently drop older backlog items.
  For a topical question add a filter instead, such as `text ~ "report"` or a
  component or label, and say in the brief which open items the cap excluded.
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

The summary carries no Jira `status`, assignee, or other field, even though the
exported file does. When the brief needs such a field as a record rather than
as Copilot's synthesis, confirm those few issues with `getJiraIssue`; otherwise
label it as synthesis.

## Atlassian direct

When the route needs exact records without Copilot, read them with the
Atlassian MCP tools `getJiraIssue`, `searchJiraIssuesUsingJql`, or
`getConfluenceContent` (`detail: "summary"` first). Use these only for a few
named records: each full issue or page carries its whole description, comments,
and formatting into your context. For more than about five issues, or for any
board or backlog, export instead and read only the JSON summary. If those tools
report an authentication error, export the records with the script and read
only the needed section. Do not call tools that create, edit, comment on, or
transition issues or pages.
