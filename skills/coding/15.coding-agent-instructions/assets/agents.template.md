# <Project> Agent Instructions

<One or two sentences: what this repository is and who it serves.>

## Precedence

Resolve conflicts in this order: the current explicit user instruction,
applicable governing, project, and task documents, then verified repository
evidence. Report a conflict instead of promoting observed behavior into
intended behavior.

## Documents

| Need | Read |
|---|---|
| Project purpose, audience, and expected outcomes | `<path-if-maintained>` |
| Domain or operating guidance | `<path-if-maintained>` |
| Current task requirements and acceptance criteria | `<path-if-maintained>` |
| Evidence, decisions, or source materials | `<path-if-maintained>` |
| Code style for every language in this repository | `docs/code-style.md` |

Read only the route the current task needs. Rename placeholders to match
project terminology, delete rows the project does not maintain, and delete this
section when no document route exists.

## Verified Commands And Checks

- From `<directory>`, run `<setup command>` before `<condition>`.
- From `<directory>`, run `<focused check>` after changing `<scope>`.
- From `<directory>`, run `<full check>` only when `<condition>`.

Keep only commands verified by project configuration, automation, or an
observed successful run. State the working directory, trigger, and relevant
scope. Delete this section when no command is verified.

## Boundaries

- Do not create, amend, or push commits unless the user explicitly requests it.
  When requested, include only task-scoped changes after applicable verified
  checks.
- Protect secrets and private or confidential data from commits and disclosure.
- <State a verified file, dependency, schema, release, generated-output, or
  authorization boundary and the correct alternative. Delete when none exists.>

## Working Rules

1. Make the smallest bounded change that satisfies the current task.
2. Reuse existing artifacts, conventions, and tools before creating or replacing
   them.
3. Preserve unrelated user changes.
4. Validate changed outputs with applicable verified checks.
5. Report only results actually produced or observed.
6. Report unknowns, conflicts, assumptions, and remaining risk.

## Reporting

- Lead with the result.
- Report what changed, important caveats, and checks actually run.
- State unresolved conflicts, omitted verification, and remaining risk.
