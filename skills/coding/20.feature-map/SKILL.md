---
name: feature-map
description: Create the right-sized MVP delivery structure - one concise Feature Map with shared technical direction, or at scale a Roadmap of child Feature Maps with shared General Designs. Invoke explicitly, by name, to define, split, or revise MVP Features, delivery stages, dependencies, shared technical choices, or cross-feature architecture. Do not create per-feature implementation plans or requirements.
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

For a single-map project, create or update `docs/feature-map.md` from
[the template](assets/feature-map.template.md), unless the project already has
one clear canonical map. For a scale project, create the Roadmap, shared
General Design, and current child map described below.

Keep the whole map under 60 lines. Keep each feature independently useful and
small enough to plan in one feature document. Use stable IDs such as `F01` that
are unique across every child map and never reuse or renumber them. Put only
MVP features in the main table; mention later ideas in one short section when
needed. Use one map when the coherent MVP fits in about eight rows with its
shared direction and architecture. When it does not, first cut optional scope;
if the remaining MVP still needs several delivery stages or maps, use the scale
layout below.

When scale is clear but `docs/functional-spec.md` is absent, report why one map
would lose useful boundaries or exceed these limits, recommend that the user
explicitly invoke `functional-spec`, and stop without creating the
specification, Roadmap, designs, or child maps. Do not ask the user to choose a
document shape when the evidence is clear. Ask only when cutting MVP scope
versus adopting the scale layout would change the intended product boundary.

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
| General Design | `docs/design/<scope>-general-design.md` | The system or stack context, responsibilities, contracts, data ownership, quality constraints, and invariants that several child maps share |

Slice child maps by user outcome or delivery stage, not by subsystem; one child
map may span frontend, backend, and computation. Start with the smallest shared
General Design from [the template](assets/general-design.template.md). Split it
by independently buildable stack only when each stack needs substantial
distinct guidance, and give every cross-stack contract exactly one owner. Keep
each design under 200 lines. A General Design holds no requirement wording,
delivery order, status, or tests. Child maps keep only stage-specific direction
and link the rest. The Roadmap carries no delivery status. For a future child
map, show its planned path as code; turn it into a link only after that file
exists. Write a child map only when preparing its stage; do not create empty
maps in advance.

Decide shared contracts before planning dependent child maps, but keep delivery
vertical. A DTO, schema, shared type, route, dependency registration, or other
internal artifact is not a Feature or Roadmap item by itself. Put the durable
cross-feature contract in the General Design and implement only the minimum
needed by the earliest user-visible Feature. Add a dependency between Map rows
only when one independently useful outcome must exist before another; do not
use `Depends on` to schedule internal files or layers. A foundation stage is
valid only when it provides a separately verifiable enabling capability used by
several later stages.

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
- language, framework, datastore, test tools, and architecture-significant
  dependencies;
- request or data flow and material upstream, downstream, or external systems;
- source-backed performance, security, reliability, or deployment constraints
  that affect the design; and
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
4. Decide whether that set fits one map. Use the scale layout when the required
   outcomes and shared design cannot remain clear within the single-map limits;
   stop as described above when the required Functional Specification is
   absent.
5. Choose the simplest technical direction that supports those features. Keep
   a shared abstraction only when current MVP behavior, repository convention,
   an external boundary, or an observed constraint requires it; otherwise omit
   or defer it.
6. Write or revise the map, then run the consistency check.

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
