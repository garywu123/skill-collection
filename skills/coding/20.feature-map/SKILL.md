---
name: feature-map
description: Create or revise a concise MVP Feature Map with feature outcomes, dependencies, shared technical direction, and a small architecture sketch; at scale, a Roadmap of child maps with shared General Designs. Invoke explicitly, by name, to define, split, or revise MVP Features, their dependencies, shared technical choices, or cross-feature architecture. Do not create per-feature implementation plans or requirements.
disable-model-invocation: true
---

# Feature Map

Turn a Product Brief into a small build map. This is the only default document
for MVP scope, shared technology, and cross-feature architecture.

The map owns reassessing MVP outcomes, dependencies, and shared technical
boundaries only. It never edits implementation. Keep direction minimal: a
shared abstraction needs current MVP behavior, a repository convention, an
external boundary, or an observed constraint; otherwise omit or defer it
without adding decision metadata.

## Output

Create or update `docs/feature-map.md` from
[the template](assets/feature-map.template.md), unless the project already has
one clear canonical map.

Keep the whole map under 60 lines. Keep each feature independently useful and
small enough to plan in one feature document. Use stable IDs such as `F01` that
are unique across every child map and never reuse or renumber them. Put only
MVP features in the main table; mention later ideas in one short section when
needed. If the table passes about eight rows the MVP is too large: cut scope,
or, when a Functional Specification exists, split into the scale layout below.

When a `docs/functional-spec.md` exists, add a `Requirements` column listing
the `FS-*` IDs each row delivers. Assign every active requirement to an
existing Map row or a future Roadmap row. A requirement may appear on several
Map rows; it is delivered only when at least one Map row cites it and every
citing Map row is `verified`. Do not copy requirement wording into either
document.

### Scale layout

Use this layout only when one map cannot hold the MVP within eight rows and a
Functional Specification exists:

| Document | Path | Holds |
|---|---|---|
| Roadmap | `docs/feature-maps/00.roadmap.md` | One row per child map: ID, outcome, assigned requirement IDs, dependencies, and path |
| Child Feature Map | `docs/feature-maps/<NN>.<slug>.md` | The template table for one delivery stage; link the designs it uses |
| General Design | `docs/design/<stack>-general-design.md` | The Technical Direction, Architecture, and Shared Constraints that several child maps share |

Slice child maps by user outcome or delivery stage, not by subsystem; one child
map may span frontend, backend, and computation. Write one General Design per
independently buildable stack, such as a backend Host and a browser App, and
keep it under 200 lines of ownership, contracts, invariants, and worked
examples. A General Design holds no requirements, delivery order, status, or
tests. Child maps keep only stage-specific direction and link the rest. The
Roadmap carries no delivery status. For a future child map, show its planned
path as code; turn it into a link only after that file exists. Write a child
map only when preparing its stage; do not create empty maps in advance.

Treat lifecycle changes by outcome:

- Reopen the existing Feature ID when correcting, extending, or revalidating
  the same independently useful user outcome. Do not create `v2` rows.
- Add a new globally unique Feature ID when the request introduces a separate
  independently useful outcome, even when it uses an existing component.
- When changing shared technical direction or a General Design, identify every
  affected row and Plan. When recorded evidence no longer proves the changed
  design or behavior, reset affected Plan results to `not run`. Move a
  `verified` Plan and Map row to `planned`; otherwise preserve `planned`,
  `in_progress`, or `blocked` only while it remains truthful, and keep both
  statuses synchronized. Report the Plan for `feature-plan` to revise, but do
  not rewrite its outcome, steps, or tests in this Skill.

Use only these statuses:

- `planned`: delivery has not started;
- `in_progress`: delivery is actively underway;
- `blocked`: a named, concrete condition prevents further progress; and
- `verified`: every planned scenario passes with no blocker remaining.

Initialize each new feature row as `planned`.

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

1. Read repository guidance, the Product Brief, the Functional Specification
   when present, existing maps and designs, manifests, and a representative
   repository structure.
2. If product direction is missing or too unclear to map without inventing MVP
   scope, report the missing decision and stop. Do not create or revise the
   Product Brief or Functional Specification as part of this Skill.
3. Identify the smallest coherent MVP feature set and its dependency order.
   Preserve existing IDs; choose the next unused project-wide ID for a new
   outcome.
4. Choose the simplest technical direction that supports those features. Keep
   a shared abstraction only when current MVP behavior, repository convention,
   an external boundary, or an observed constraint requires it; otherwise omit
   or defer it.
5. Write or revise the map, then run the consistency check.

If one row contains several independently useful outcomes, split it before
planning. Ask the user only when the split changes the intended MVP.

## Consistency Check

Before finishing, re-read the brief, every active `FS-*` requirement, the
Roadmap, all Feature Maps, and any Storyboard or Feature Plan whose row or
linked design changed. Report every active requirement assigned to neither a
Map nor future Roadmap row and every retired or missing ID still cited. An ID
assigned only to the Roadmap is not delivered. Keep feature outcomes,
dependencies, shared technology, and architecture only here or in the
linked General Design, product meaning only in the brief, and requirements only
in the specification. Fix stale IDs, names, and paths in maps and designs. Copy
a matching Feature Plan's explicit status to the Map row only when that Plan's
recorded results and blockers still support the current sources; otherwise
report the conflict. Never infer delivery progress from code or repository
state. If a changed row or design invalidates visible states or planned
behavior, reset the affected Map row and Plan evidence as described above, then
report the Storyboard or Plan for revision instead of redesigning it here.

## Completion

Report features added, removed, or changed; technical choices; consistency
edits; unresolved decisions; and validation performed.
