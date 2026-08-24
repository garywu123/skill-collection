---
name: feature-map
description: Create or revise a concise MVP Feature Map with feature outcomes, dependencies, shared technical direction, and a small architecture sketch. Use when the user wants to define, split, or revise MVP Features, their dependencies, shared technical choices, or cross-feature architecture. Do not create milestones, post-MVP roadmap rows, or per-feature implementation plans.
---

# Feature Map

Turn a Product Brief into a small build map. This is the only default document
for MVP scope, shared technology, and cross-feature architecture.

## Output

Create or update `docs/feature-map.md` from
[the template](assets/feature-map.template.md), unless the project already has
one clear canonical map.

Keep the whole map under 60 lines. Keep each feature independently useful and
small enough to plan in one feature document. Use stable IDs such as `F01`. Put
only MVP features in the main table; mention later ideas in one short section
when needed. If the table passes about eight rows the MVP is too large: cut
scope instead of lengthening the table.

Use only these statuses:

- `planned`: delivery has not started;
- `in_progress`: delivery is actively underway;
- `blocked`: a named, concrete condition prevents further progress; and
- `verified`: every planned scenario passes with no blocker remaining.

Do not use `blocked` for ordinary unfinished work. Do not add milestones or use
`later` as a status; keep optional post-MVP ideas in `## Later` without delivery
status.

The technical direction should name only choices needed to begin work:

- application shape and major boundaries;
- language, framework, datastore, and test tools;
- request or data flow; and
- shared constraints that every feature must follow.

Prefer repository conventions for an existing codebase. Do not add class
designs, exhaustive infrastructure, speculative scaling, approval metadata, or
separate architecture documents. Add a small Mermaid diagram only when prose
would be less clear.

## Workflow

1. Read repository guidance, the Product Brief, existing map, manifests, and a
   representative repository structure.
2. If product direction is missing or too unclear to map without inventing MVP
   scope, report the missing decision and stop. Do not create or revise the
   Product Brief as part of this Skill.
3. Identify the smallest coherent MVP feature set and its dependency order.
4. Choose the simplest technical direction that supports those features.
5. Write or revise the map, then run the consistency check.

If one row contains several independently useful outcomes, split it before
planning. Ask the user only when the split changes the intended MVP.

## Consistency Check

Before finishing, re-read the brief and any Storyboard or Feature Plan whose row
changed. Keep feature outcomes, dependencies, shared technology, and
architecture only here, and product meaning only in the brief. Fix stale IDs,
names, status, and paths in this map. If a changed row invalidates visible states
or planned behavior, report the affected Storyboard or Plan for revision instead
of redesigning it here.

Report features added, removed, or changed; technical choices; consistency
edits; unresolved decisions; and validation performed.
