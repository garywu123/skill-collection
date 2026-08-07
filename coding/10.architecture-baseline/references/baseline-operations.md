# Baseline and Recovery Operations

## Full or Lite

1. Derive drivers only from approved `PR-###`, constitution principles, and
   external constraints; drop unsupported quality attributes.
2. Separate baseline-owned from feature-owned decisions, then classify
   reversibility. Compare consequential alternatives; ask at most five
   decision-changing questions per round.
3. Record boundaries, dependency direction, cross-cutting strategies, deferred
   decisions, spikes, and risks; exclude single-feature design.
4. Use the [Full single-file template](../assets/architecture-baseline.template.md)
   plus the [ADR template](../assets/adr.template.md), or the
   [Lite template](../assets/architecture-baseline-lite.template.md). When the
   Full baseline exceeds its size/concurrency budget, use the
   [split-root template](../assets/architecture-baseline-index.template.md) and
   [domain-detail template](../assets/architecture-domain.template.md).
5. Produce short, testable Plan Constraints last. Set every output only to
   `Ready for Review`.

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
