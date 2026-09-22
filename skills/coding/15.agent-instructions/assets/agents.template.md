# <Project> Agent Instructions

<One or two sentences: what this project is and who it serves.>

## Documents

| Need | Read |
|---|---|
| Project purpose, audience, and expected outcomes | `<path-if-maintained>` |
| Domain or operating guidance | `<path-if-maintained>` |
| Current task requirements and acceptance criteria | `<path-if-maintained>` |
| Evidence, decisions, or source materials | `<path-if-maintained>` |
| Code style for every language in this repository | `docs/code-style.md` |

Read only the route the current task needs. Do not reconstruct project state
from conversation history. Rename placeholders to match project terminology,
delete rows the project does not keep, and delete this section when no document
route exists.

## Precedence

Resolve conflicts in this order: the current explicit user instruction,
applicable governing, project, and task documents, then repository evidence.
Report a conflict instead of promoting observed behavior into intended
behavior.

## Verified Commands And Checks

- Setup: `<verified command>`
- Produce or run: `<verified command>`
- Focused check: `<verified command>`
- Full check: `<verified command>`

<Keep only commands or checks verified by project configuration, automation, or
an observed successful run. Delete this whole section when none is verified.>

## Conventions

- <A verified project convention: structure, naming, workflow, or tooling.
  Code-style rules belong in `docs/code-style.md`, not here. Delete this
  section when the repository shows none.>

## Communication Style

- Lead with the result, recommendation, or decision in plain, direct language.
- Be concise without omitting facts, risks, verification, assumptions, or explanations needed to act.

## Working rules

1. Make the smallest bounded change that satisfies the current task.
2. Reuse existing artifacts, conventions, and tools before creating or replacing
  them.
3. Validate changed outputs with applicable verified checks.
4. Report only results actually produced or observed.
5. Report unknowns, conflicts, assumptions, and remaining risk.
6. Protect secrets and private or confidential data from commits and disclosure.
