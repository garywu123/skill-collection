---
name: workplace-knowledge
description: Answer workplace knowledge questions across Microsoft 365 (mail, meetings, Teams, SharePoint, OneDrive, people, through the m365-copilot-web MCP server) and Atlassian Jira and Confluence (through a read-only export script, with the Atlassian Rovo MCP server optional). By default Microsoft 365 Copilot does the synthesis with Atlassian sources attached, and the agent returns a short cited brief. Can index or download returned files or have Copilot generate Word, PowerPoint, or Excel documents. Use for questions such as what a product is, project or ticket status, what was decided in meetings or email, or where a file or page lives. Do not use to create or edit Jira issues or Confluence pages, export exact mail, or publish to SharePoint.
---

# Workplace Knowledge

Microsoft 365 Copilot is the main reasoner: it reads Microsoft 365 content and
receives Jira and Confluence sources as an attached export file, because the
two systems cannot search each other. This agent routes, assembles context, and
condenses the result into a cited brief. Do not read Office files, mail,
chats, or exported page text yourself to stand in for Copilot.

## Run in a sub-agent

Unless you are already a sub-agent, run this procedure in one sub-agent with
the user's question, any stated source order, and this Skill's name, and ask
it for only the brief. Retrieval payloads are far larger than the answer, and
keeping them out of the main conversation is the point. If no sub-agent tool
is available, say so and keep to the context budget.

## Language

Write every system-facing string in English: the Copilot prompt, Confluence
search terms, and JQL. Write only the final brief in the user's language.
English answers are shorter, faster, and cheaper to carry than translated ones.

## Context budget

- Never read an export file, an attachment, or an offloaded tool result whole.
  Read its summary, or project only the fields you need.
- Retrieve at list level first: keys, titles, status, owner, dates. Fetch full
  text only for the few items the answer actually names.
- Make one Copilot call per question. Ask a second only for a user follow-up.
- Load a reference file on the step that needs it, not in advance.

## Route

An explicit user instruction wins: a named source, a restriction, or an order
such as "Confluence first, then meetings". Otherwise route each part of the
question; split a question that mixes types.

| Part of the question | Path |
|---|---|
| Meetings, mail, chats, decisions, customer communication, files | Copilot only |
| What a product or system is, specifications, designs | Copilot with Confluence attached |
| Ticket status, releases, assignments | Copilot with Jira attached |
| Exact Jira fields or Confluence page text only | Atlassian direct, no Copilot |
| A Word, PowerPoint, or Excel document | Copilot, per [documents](references/documents.md) |

A board, backlog, or any list of more than about five issues goes through the
export script, never through a direct Atlassian search. Full issue payloads
are the main cause of oversized context.

## Procedure

1. Load [Microsoft 365](references/m365.md) before the first Copilot call
   and [Atlassian](references/atlassian.md) before the first Atlassian call.
2. Find Atlassian sources with the export script's `--search` for Confluence
   and an exact JQL for Jira; Rovo `search` is optional. Skip discovery when
   the user already gave a page id, issue key, board, or link.
3. Export them with the script into one file. Read only its JSON summary.
4. Ask Copilot with the synthesis prompt, attaching the file, and carry
   identifiers into the prompt: issue keys, page titles, projects, people,
   sites, and dates.
5. For "Atlassian direct", read the records with Atlassian tools instead.

## Deliver

Condense Copilot's answer into a brief; never copy it whole.

- Lead with the answer in a few bullets or a short table, each fact labeled
  `[Confluence]`, `[Jira]`, or `[M365]`. Copilot and Rovo output is synthesis;
  Jira fields and page text are records.
- Cite original Confluence and Jira links from the export summary, not the
  uploaded copy. Prefer live pages over exports or copies, and date copies.
- Report conflicts with both sources and dates instead of merging them.
- Downgrade any claim Copilot makes about the inside of a diagram, image, or
  scanned file. Copilot can locate such a file and quote text around it, but it
  cannot read shape labels or arrows, and it will still assert them confidently.
  Look for the same fact in mail, chat, or a page; report it as confirmed only
  with that corroboration, and otherwise mark it unverified and offer to index
  or download the file.
- End with sources (title, system, date, link), the Copilot conversation
  link for the full answer, and what was not searched and why.

If results include files, ask whether to do nothing, index them, or download
Microsoft 365 files; never download by default. Load
[files](references/files.md) only after the user chooses index or download.

## Failures and boundaries

- On an Atlassian MCP authentication error, continue with the export script,
  which has its own token, and tell the user that MCP sign-in has expired.
- If a source stays unavailable, answer from the rest and name the gap.
- Atlassian access is read-only. Microsoft 365 changes are limited to
  uploading exported context or user-approved files, documents the user asked
  for, and approved downloads; local index files are the only other writes.
  Never send mail, post messages, change calendars, publish, or delete files.

Stop after the brief, plus any file action or document review the user chose.
