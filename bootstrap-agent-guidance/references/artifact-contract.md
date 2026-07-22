# Artifact Contract

Use this contract to keep project guidance small and prevent competing sources
of truth.

## Responsibilities

| Artifact | Owns | Must not own |
|---|---|---|
| Discovery notes | Interview evidence, rationale, rejected options, decision history | Concise approved product truth |
| Product requirements | Approved outcomes, scope, non-goals, product rules, success criteria | Technical architecture and task lists |
| Feature roadmap | Feature boundaries, dependencies, MVP, ownership, delivery status | Detailed feature behavior or implementation tasks |
| Assessment decision | Evidence and go, clarify, park, or kill decision for one idea | A permanently divergent roadmap |
| Constitution | Stable engineering governance and non-negotiable principles | Product scope and feature status |
| `AGENTS.md` | Agent operating rules, source precedence, routing, verified commands, boundaries | Copies of the artifacts above |
| Feature `spec.md` | Behavior, flows, edge cases, and acceptance for one approved feature | Later-feature responsibilities or architecture implementation |
| `plan.md` / `tasks.md` | Technical design and implementation work for one feature | Product truth for the whole system |

## Default precedence

Adapt this order only when the user or repository explicitly defines another:

1. Current explicit user instruction for the task.
2. Approved new-project product requirements.
3. Approved roadmap entry and current feature specification.
4. Constitution and accepted architecture decisions within their scope.
5. Current code, tests, CI, and manifests as evidence of implemented behavior.
6. Legacy documents and legacy code as reference only.

Do not claim that implemented behavior is desired behavior when it conflicts
with an approved requirement. Report the conflict.

## Generation timing

Create the product-context baseline after the PRD and roadmap are approved and
before the first feature enters assessment or specification. Refresh it after
real engineering commands and architecture exist. Later refreshes are required
only when project-wide sources, paths, commands, boundaries, or governance
change; do not regenerate it for every feature.

## Feature isolation

The root guidance should point to the roadmap without copying its feature list.
When delivering a feature, read its one roadmap entry, its applicable product
requirements, and its own `spec.md`. Do not absorb later-feature scope merely
because the roadmap describes it.
