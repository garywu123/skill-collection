---
name: feature-map
description: Create the right-sized MVP delivery structure - one concise Feature Map, or at scale a Roadmap of child Feature Maps - holding Feature outcomes, requirement assignments, dependencies, and statuses linked to the project's Architecture Design. Use when the user asks to define, split, or revise MVP Features, delivery stages, or dependencies. Do not author architecture or shared technical direction (use architecture-design), per-feature implementation plans, or requirements.
disable-model-invocation: false
---

# Feature Map

Turn a Product Brief into a small build map. This is the only default document
for MVP Feature outcomes, their dependencies and sequence, and delivery status.

The map owns reassessing MVP outcomes and dependencies only. Shared technical
direction and cross-feature architecture belong to the project's Architecture
Design, owned by `architecture-design`; the map links it. The map never edits
implementation.

## Output

For a single-map project, create or update `docs/feature-map.md` from
[the template](assets/feature-map.template.md), unless the project already has
one clear canonical map. For a scale project, create the Roadmap and current
child map described below.

Keep the map concise and each Feature one independently useful outcome.
Execution segments and subagent choices belong in that Feature's Plan; a long
implementation alone does not justify another Map row. Use stable IDs such as
`F01` that are unique across every child map and never reuse or renumber them.
Put only MVP features in the main table; mention later ideas in one short
section when needed.

About 60 lines or eight rows is a readability signal, not a gate: past it,
first remove repeated upstream content and cut optional scope. Use the scale
layout below only when the remaining MVP still cannot be read clearly as one
map, for example because several delivery stages with distinct requirement
areas and dependencies no longer fit one coherent table. Row or line count
alone never justifies a larger document hierarchy.

When scale is clear but `docs/functional-spec.md` is absent, report why one map
would lose useful boundaries, recommend that the user
explicitly invoke `functional-spec`, and stop without creating the
specification, Roadmap, or child maps. Do not ask the user to choose a
document shape when the evidence is clear. Ask only when cutting MVP scope
versus adopting the scale layout would change the intended product boundary.

When a `docs/functional-spec.md` exists, add a `Requirements` column listing
the `FS-*` IDs each row delivers. Assign every active requirement to an
existing Map row or a future Roadmap row. A requirement may appear on several
Map rows; it is delivered only when at least one Map row cites it and every
citing Map row is `verified`. Do not copy requirement wording into either
document.

### Scale layout

Use this layout only when one map cannot hold the MVP readably, as described
above, and a Functional Specification exists:

| Document | Path | Holds |
|---|---|---|
| Roadmap | `docs/feature-maps/00.roadmap.md` | One row per child map: ID, outcome, assigned requirement IDs, dependencies, and path |
| Child Feature Map | `docs/feature-maps/<NN>.<slug>.md` | The template table for one delivery stage; link the Architecture Design sections it uses |

Slice child maps by user outcome or delivery stage, not by subsystem; one child
map may span frontend, backend, and computation. The Roadmap carries no
delivery status. For a future child map, show its planned path as code; turn it
into a link only after that file exists. Write a child map only when preparing
its stage; do not create empty maps in advance.

Shared contracts must be decided in the Architecture Design before planning
dependent child maps, but keep delivery vertical. A DTO, schema, shared type,
route, dependency registration, or other internal artifact is not a Feature or
Roadmap item by itself; the earliest user-visible Feature implements only the
minimum of a durable cross-feature contract that it needs. Add a dependency
between Map rows only when one independently useful outcome must exist before
another; do not use `Depends on` to schedule internal files or layers. A foundation stage is
valid only when it provides a separately verifiable enabling capability used by
several later stages.

Treat lifecycle changes by outcome:

- Reopen the existing Feature ID when correcting, extending, or revalidating
  the same independently useful user outcome. Do not create `v2` rows.
- Add a new globally unique Feature ID when the request introduces a separate
  independently useful outcome, even when it uses an existing component.
- When a linked Architecture Design or another upstream source changed,
  identify every affected row and Plan. When recorded evidence no longer
  proves the changed design or behavior, reset affected Plan results to
  `not run`. Move a
  `verified` Plan and Map row to `planned`; otherwise preserve `planned`,
  `in_progress`, or `blocked` only while it remains truthful, and keep both
  statuses synchronized. Report the Plan for `feature-plan` to revise, but do
  not rewrite its outcome, steps, or tests in this Skill.

Use only these statuses:

- `planned`: delivery has not started;
- `in_progress`: delivery is actively underway;
- `blocked`: a named, concrete condition prevents further progress; and
- `verified`: every planned scenario and selected independent gate passes with
  no blocker remaining.

Initialize each new feature row as `planned`.

Do not use `blocked` for ordinary unfinished work. Do not add milestones or use
`later` as a status; keep optional post-MVP ideas in `## Later` without delivery
status.

### Architecture Link

Link the project's Architecture Design from the map; do not write technical
direction, architecture, or shared technical constraints in a map. Without a
design, a map may still record outcomes and dependencies. When a dependency or
sequence decision requires a shared technical choice that no design records,
report it for `architecture-design` instead of inventing it.

An existing map that still holds `Technical Direction`, `Architecture`, or
`Shared Constraints` sections, or links a General Design, keeps that content
unchanged until `architecture-design` migrates it. Do not expand it; report the
pending migration.

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
4. Decide whether that set fits one map. Use the scale layout only when the
   required outcomes and dependencies cannot remain clear in one map; stop as
   described above when the required Functional Specification is absent.
5. Link the Architecture Design and report any missing shared technical
   decision as described above.
6. Write or revise the map, then run the consistency check.

If one row contains several independently useful outcomes, split it before
planning; this includes a scoped replanning request from `feature-plan` or an
authorized Orchestrator. Keep the original ID and its still-valid evidence for
the outcome its Plan already covers, give each other outcome a new ID, and
report the Plan for `feature-plan` to narrow. Ask the user only when the split
changes the intended MVP.

## Consistency Check

Before finishing, re-read the brief, every active `FS-*` requirement, the
Roadmap, all Feature Maps, and any Storyboard or Feature Plan whose row or
linked design changed. Report every active requirement assigned to neither a
Map nor future Roadmap row and every retired or missing ID still cited. An ID
assigned only to the Roadmap is not delivered. Keep feature outcomes and
dependencies only here, architecture only in the Architecture Design, product
meaning only in the brief, and requirements only in the specification. Fix
stale IDs, names, paths, and design links in maps. Copy
a matching Feature Plan's explicit status to the Map row only when that Plan's
recorded results and blockers still support the current sources; otherwise
report the conflict. Never infer delivery progress from code or repository
state. If a changed row or design invalidates visible states or planned
behavior, reset the affected Map row and Plan evidence as described above, then
report the Storyboard or Plan for revision instead of redesigning it here.

## Completion

Report features added, removed, or changed; consistency edits; missing
architecture decisions or pending migrations; unresolved decisions; and
validation performed.
