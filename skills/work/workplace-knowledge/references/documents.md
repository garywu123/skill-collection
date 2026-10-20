# Documents Reference

Use only when the user asks for a Word, PowerPoint, or Excel document.

1. Use Chat mode with a named session. State the audience, structure, and
   source material in the prompt; attach exported Atlassian context when the
   document depends on Jira or Confluence.
2. Use `timeoutSeconds: 600`. The result appears in `files` with kind
   `generated` and a `savedIn` location. Do not build the document locally.
3. Ask Copilot in the same session to review what it produced: section or
   slide titles, key claims, sources used, and assumptions or gaps.
4. Give the user that review and the link, which opens in Office for the web.
   Mention that Copilot may leave extra intermediate copies in
   `OneDrive\Documents\Copilot\Created`.
5. Ask whether to keep it in OneDrive only, request a revision in the same
   session, or download it to a folder.
