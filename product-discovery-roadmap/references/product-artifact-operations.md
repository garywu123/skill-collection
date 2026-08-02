# PRD and Roadmap Operations

## Draft PRD

Use the [PRD template](../assets/product-requirements-template.md). State testable
user/business behavior; separate confirmed requirements, assumptions, open
questions, non-goals, and destructive-operation safeguards. Use append-only
`PR-###` IDs; changed approved requirements receive successor IDs. Capture
cross-feature experience requirements, but leave layout/style/components to UI
artifacts. Remove placeholders, contradictions, implementation detail, and
unbounded language before review.

Start with one PRD. Above roughly 400 lines/40 requirements, or for concurrent
domain ownership, use the
[PRD index template](../assets/product-requirements-index-template.md). The root
owns the global ID registry, coverage, waves, and cross-cutting IDs; domain files
own detail. Never split by feature or discovery wave.

## Draft Roadmap

Use the [roadmap template](../assets/feature-roadmap-template.md). Every vertical,
independently acceptable feature needs outcome, scope, non-goals, dependencies,
independent acceptance, one primary owning relation, stable `Product Domain`,
`Horizon`, `UI Surface`, release boundary, and one-spec/plan sizing.

Record concrete profile sizing. Choose `lite` only for at most eight features,
one deployable, at most one datastore, one team, and no regulatory/audit/
contractual architecture constraint; any failed or unknown condition is `full`.
Cross-cutting requirements may apply many times but have one owner.

Above roughly 300 lines/12 features, or for concurrent domains, root owns only
sizing, domain registry, dependency/order, horizon/release registry, and
coverage. Domain files use the
[roadmap-domain template](../assets/feature-roadmap-domain-template.md) and own
feature detail. Resolve one F-ID, then read only its domain file plus relevant
root rows. Roadmap never mirrors mutable delivery state.
