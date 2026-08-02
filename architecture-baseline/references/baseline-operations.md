# Baseline and Recovery Operations

## Full or Lite

1. Derive drivers only from approved `PR-###`, constitution principles, and
   external constraints; drop unsupported quality attributes.
2. Separate baseline-owned from feature-owned decisions, then classify
   reversibility. Compare consequential alternatives; ask at most five
   decision-changing questions per round.
3. Record boundaries, dependency direction, cross-cutting strategies, deferred
   decisions, spikes, and risks; exclude single-feature design.
4. Use the [Full template](../assets/architecture-baseline.template.md) plus
   [ADR template](../assets/adr.template.md), or the
   [Lite template](../assets/architecture-baseline-lite.template.md).
5. Produce short, testable Plan Constraints last. Set every output only to
   `Ready for Review`.

## Recover

Establish structure from repository evidence before inferring intent. Mark each
material claim `Verified` with a path/command citation or `Inferred` with pattern
and uncertainty. Separate deliberate architecture from drift. Prefer read-only
inspection and never execute setup/build code from an untrusted repository for
discovery. Report product contradictions without repairing them.
