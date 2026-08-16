# Baseline and Recovery Operations

## Create, Assess, Full, or Lite

For `create`, determine Lite or Full before choosing a template. Use roadmap
sizing plus actual cross-feature decision pressure; do not ask the user to pick
a mode when the evidence is sufficient. `assess` performs steps 1–3 and reports
the selected mode, bundle shape, evidence, and missing coverage without writing.
Explicit `full` or `lite` is an override and requires a rationale when it
conflicts with the evidence.

1. Derive drivers only from approved `PR-###`, constitution principles, and
   external constraints; drop unsupported quality attributes.
2. Separate baseline-owned from feature-owned decisions, then classify
   reversibility. Compare consequential alternatives; ask at most five
   decision-changing questions per round.
3. Record boundaries, dependency direction, cross-cutting strategies, deferred
   decisions, spikes, and risks; exclude single-feature design, default
   non-goals, and chronological decision logs.
4. Use the [Full single-file template](../assets/architecture-baseline.template.md)
   plus the [ADR template](../assets/adr.template.md), or the
   [Lite template](../assets/architecture-baseline-lite.template.md). When the
   Full baseline exceeds its size/concurrency budget, use the
   [split-root template](../assets/architecture-baseline-index.template.md) and
   [domain-detail template](../assets/architecture-domain.template.md).
5. Produce short, testable Plan Constraints last. Set every output only to
   `Ready for Review`.

The baseline states the current choice and links an ADR where one owns detailed
rationale. Do not duplicate the ADR's rejected alternatives, history, or
supersession record in the baseline.

Single roots declare `**Artifact bundle**: single` and omit a Member Registry.
Split roots declare `**Artifact bundle**: split`; after every domain and
ADR member is final, list every member path under the root's registry. The root
itself and product sources are not members. Verify that the domain and ADR
registries name the same set of files that exist on disk before reporting. No
member hashes are maintained — Git detects drift.

## Recover

Establish structure from repository evidence before inferring intent. Mark each
material claim `Verified` with a path/command citation or `Inferred` with pattern
and uncertainty. Separate deliberate architecture from drift. Prefer read-only
inspection and never execute setup/build code from an untrusted repository for
discovery. Report product contradictions without repairing them.
Select Lite or Full with the same decision rule used by `create`, and report the
evidence for that selection.
