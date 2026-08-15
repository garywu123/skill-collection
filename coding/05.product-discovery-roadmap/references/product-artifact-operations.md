# PRD and Roadmap Operations

## Draft PRD

Use the [single-file PRD template](../assets/product-requirements-template.md).
Compress approved discovery into current product intent, main jobs, MVP, user
journeys, testable requirements, safeguards, and success measures. Use
append-only `PR-###` IDs; changed approved requirements receive successor IDs.
Capture cross-feature experience requirements, but leave layout, style, and
components to UI artifacts.

Add `Explicit Exclusions` only for a capability the user explicitly rejected or
one likely to be mistaken as included. Add a critical assumption only when it
could change the MVP, product promise, or feasibility. Add a blocking product
decision only when delivery cannot proceed without it. Omit empty optional
sections. Never copy a discovery decision history, question backlog, rejected
alternatives, or discovery-to-requirement coverage matrix into the PRD.

Start with one PRD. Above roughly 400 lines/40 requirements, or for concurrent
domain ownership, use the
[PRD index template](../assets/product-requirements-index-template.md). The root
owns the global ID registry, status, coverage, waves, and cross-cutting ID
routing; files created from the
PRD domain template](../assets/product-requirements-domain-template.md) own the
requirement text. The root registry points to detail and never copies a summary.
Never split by feature or discovery wave.

## Draft Roadmap

Use the [single-file roadmap template](../assets/feature-roadmap-template.md).
First identify stable business domains, then split each domain into vertical,
independently acceptable features. A small project may have one feature in a
domain; still record both the domain key and feature ID. Every feature needs outcome, scope,
dependencies, observable acceptance, one primary owning relation per
requirement, `UI Surface`, and a delivery boundary. Record `Owns Requirements`
and `Also Bound By` once in the feature map. Do not create a reverse requirement
coverage table or downstream specification handoff.

Record feature, deployable, and owning-team counts as positive integers,
datastore count as a non-negative integer, and the constraint field as `yes`,
`no`, or `unknown`; put only stable anchors in `Sizing evidence`.
Select `lite` only for at most eight features, exactly one deployable, at most
one datastore, exactly one owning team, and constraint `no`; any failed or
unknown condition is `full`. Cross-cutting requirements may apply many times
but have one owner. Before writing canonical F-IDs, split any candidate with
multiple independently valuable outcomes, independent lifecycle/state models,
unrelated acceptance paths, or separately schedulable dependencies.

Above roughly 300 lines/12 features, or for concurrent domains, use the
[roadmap index template](../assets/feature-roadmap-index-template.md). Its root
alone owns sizing, domain and feature routing, requirement ownership,
dependency/order, UI-surface, and delivery-boundary values. Domain files use
the [roadmap-domain template](../assets/feature-roadmap-domain-template.md) and
own concise descriptions and acceptance. Do not repeat root-owned values in a
domain member. Resolve one F-ID, then read only its root row plus its domain
file. Roadmap never mirrors mutable delivery state.

`assess-roadmap` applies the same tests read-only to an existing roadmap and
reports: selected profile, single or split recommendation, domain-key gaps,
over-broad features, temporary-label candidate splits, affected requirement
IDs, and the exact amendment prompt. Never change an approved roadmap during
assessment.

After drafting, validate that every PR ID has exactly one owner, every bound ID
exists, every dependency names a feature, and the dependency graph is acyclic.
Report a concise pass result or concrete issues; do not persist a second
coverage registry when the checks pass.

For either split artifact, set `**Artifact bundle**: split` on the root and add a
complete `## Member Registry`. It lists every owned detail file exactly once; it
excludes the root and cited source files.
Finalize all members and verify that the registry paths all resolve before
reporting. No member hashes are maintained — Git detects drift. Single-file
templates declare `single` and omit the registry.
