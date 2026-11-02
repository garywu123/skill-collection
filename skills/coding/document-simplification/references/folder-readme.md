# Folder README

A folder README tells the reader what the folder is for and which file to
open. It is short; most fit in under 200 words.

Shape:

1. One or two sentences on what the folder holds and, when it matters, the
   reading order.
2. A list or table of files, one line each, saying what question the file
   answers.

Good:

```markdown
# Mars

How to read the base reports for the Mars site. Read the common report page
first, then the Mars page with the same name.

- `source-mapping.md` - Mars Order Types, operations and states.
- `order-history.md` - Mars Order shape, pickup and drop columns.
- `alarm-history.md` - Mars alarm labels and sources.
```

Leave out version provenance, source-authority rules, validation history,
ownership tables, and instructions for agents. Those belong in `AGENTS.md`,
its routed guidance, or the environment record. A top-level README for a large
folder may add a short "how to use" paragraph, not a policy section.
