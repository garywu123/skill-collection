---
name: markdown-reflow
description: Un-wrap Markdown paragraphs that were hard-wrapped onto multiple short lines, joining each paragraph back into a single line while preserving blank-line paragraph breaks, headings, lists, blockquotes, tables, and code fences. Use when the user asks to reflow, un-wrap, or clean up line breaks an AI or editor inserted inside Markdown paragraphs. Do not use for prose rewriting, reformatting list/table/blockquote content, or any content change beyond whitespace and line joins.
---

# Markdown Reflow

Collapse unintentional hard-wrapped lines inside Markdown paragraphs back into
one line per paragraph, using a deterministic script instead of a model
rewrite. This keeps the operation free, repeatable, and incapable of changing
wording.

## Why this is safe without a model

A Markdown paragraph is a run of non-blank lines; a blank line is what starts a
new paragraph. Per CommonMark, a single line break inside a paragraph already
renders as a plain space, so joining wrapped lines back into one line does not
change how the paragraph renders. The one exception — an intentional hard line
break, marked by two or more trailing spaces or a trailing backslash — is
detected and preserved as its own line. Because the boundary rule (blank line)
and the exception (hard-break marker) are both syntactic, a script can apply
them exactly; no judgment call about "should this be one paragraph or two" is
needed.

## Scope

This Skill only touches plain paragraph text. It leaves the following
untouched, matched by line pattern, not by content:

- blank lines (paragraph boundaries);
- ATX headings (`#` … `######`) and setext heading underlines;
- list items (`-`, `*`, `+`, or `1.`/`1)` markers) and their continuation
  lines;
- blockquote lines (`>`);
- table rows (lines starting with `|`);
- thematic breaks (`---`, `***`, `___`);
- fenced code blocks (` ``` ` or `~~~`), including their contents.

List items, blockquotes, and table cells are left as-is in this version even
if they contain hard-wrapped text; reflow those manually or extend the script
if that becomes a recurring need.

This Skill has no automatic trigger. It runs only when explicitly invoked; it
does not hook into file save or edit events.

## Procedure

1. Confirm the target file(s) or folder from the user's request. If
   unspecified and ambiguous, ask rather than guessing a wide glob.
2. Preview the change:

   ```powershell
   powershell -ExecutionPolicy Bypass -File skills/coding/markdown-reflow/scripts/Unwrap-Markdown.ps1 -Path <file-or-folder> -Preview
   ```

3. Review the reported diff. Files with no paragraph-level hard wraps are
   reported as unchanged.
4. Re-run the same command without `-Preview` to write the change once the
   preview looks correct.
5. Report which files changed and remind the user that list items,
   blockquotes, and table cells were intentionally left untouched.

## Validation

Re-run the script with `-Preview` after writing; it must report no further
changes. Spot-check one changed file to confirm paragraph wording is
unchanged and blank-line paragraph breaks are intact.
