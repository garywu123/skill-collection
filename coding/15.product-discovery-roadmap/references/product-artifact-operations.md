# PRD and Roadmap Operations

## Draft PRD

Use the [single-file PRD template](../assets/product-requirements-template.md).
State testable user/business behavior; separate confirmed requirements,
assumptions, open questions, non-goals, and destructive-operation safeguards.
Use append-only `PR-###` IDs; changed approved requirements receive successor
IDs. Capture cross-feature experience requirements, but leave layout, style,
and components to UI artifacts. Remove placeholders, contradictions,
implementation detail, and unbounded language before review.

Start with one PRD. Above roughly 400 lines/40 requirements, or for concurrent
domain ownership, use the
[PRD index template](../assets/product-requirements-index-template.md). The root
owns the global ID registry, status, coverage, waves, and cross-cutting ID
routing; files created from the
[PRD domain template](../assets/product-requirements-domain-template.md) own the
requirement text. The root registry points to detail and never copies a summary.
Never split by feature or discovery wave.

## Draft Roadmap

Use the [single-file roadmap template](../assets/feature-roadmap-template.md).
Every vertical, independently acceptable feature needs outcome, scope,
non-goals, dependencies, independent acceptance, one primary owning relation,
stable `Product Domain`, `Horizon`, `UI Surface`, release boundary, and
one-spec/plan sizing.

Record feature, deployable, and owning-team counts as positive integers,
datastore count as a non-negative integer, and the constraint field as `yes`,
`no`, or `unknown`; put only stable anchors in `Sizing evidence`.
Choose `lite` only for at most eight features, exactly one deployable, at most
one datastore, exactly one owning team, and constraint `no`; any failed or
unknown condition is `full`. Cross-cutting requirements may apply many times
but have one owner.

Above roughly 300 lines/12 features, or for concurrent domains, use the
[roadmap index template](../assets/feature-roadmap-index-template.md). Its root
alone owns sizing, domain and feature routing, requirement ownership/coverage,
dependency/order, horizon, UI-surface, and release-boundary values. Domain files
use the [roadmap-domain template](../assets/feature-roadmap-domain-template.md)
and own outcomes, scope, non-goals, risks, independent acceptance, and handoff
names. Do not repeat root-owned values in a domain member. Resolve one F-ID,
then read only its root rows plus its domain file. Roadmap never mirrors mutable
delivery state.

For either split artifact, set `**Artifact bundle**: split` on the root and add a
complete `## Approved Bundle` `Path`/`SHA-256` table. The table contains every
owned detail file exactly once; it excludes the root and cited source files.
Finalize all members, hash all members (including unchanged ones), update the
table, and verify that its paths exactly equal the root registry before
`record-output`. Single-file templates declare `single` and omit the table.
