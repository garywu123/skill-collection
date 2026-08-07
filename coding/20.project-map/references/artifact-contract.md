# Artifact Contract

Use this contract to keep project guidance small and prevent competing sources
of truth.

## Responsibilities

| Artifact | Owns | Must not own |
|---|---|---|
| Discovery notes | Interview evidence, rationale, rejected options, decision history | Concise approved product truth |
| Product requirements | Approved outcomes, scope, non-goals, product rules, success criteria | Technical architecture and task lists |
| Feature roadmap | Feature outcomes, boundaries, dependencies, horizon, MVP, and requirement ownership | Mutable delivery status, detailed behavior, or implementation tasks |
| `roadmap.yaml` | Descriptive project stage, canonical document routes, and one concise status entry per function | Domain truth, approval rationale, history, or authority to start work |
| Function `checklist.md` | Spec-derived acceptance criteria, actual evidence, fresh-context review, and human decision | Requirements, implementation fixes, product/architecture changes, or release authorization |
| UI structure | Navigation, global shell, device contexts, screen inventory, cross-screen patterns | Feature screen layout or visual style |
| Feature `wireframes.md` | Screen skeletons, control and state tables, and flows for one feature | Component library, styling, or framework choices |
| Constitution | Stable engineering governance and non-negotiable principles | Product scope, feature status, and named technologies |
| Architecture baseline | Cross-feature technology choices, boundaries, cross-cutting strategies, plan constraints | Feature-internal design and engineering values |
| ADR | Rationale, rejected alternatives, and supersession history for one decision | The current state of the system |
| `AGENTS.md` | Agent operating rules, source precedence, routing, verified commands, boundaries | Copies of the artifacts above |
| Feature `spec.md` | Behavior, flows, edge cases, and acceptance for one approved feature | Later-feature responsibilities or architecture implementation |
| `plan.md` / `tasks.md` | Technical design and implementation work for one feature | Product truth for the whole system |
| Optional release evidence | Release-scope build, migration, rollback, operations, and execution evidence required by project policy | Feature acceptance, deployment logic, or rewritten feature history |
| `TD-###` record | Concrete implementation debt, impact, owner, repayment trigger/evidence | Future product scope or cross-feature architecture truth |
| Change request | Original request, impact, and proposed routing | Requirement text or approval; decisions live in the artifact updated by each routed owner |

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

`roadmap.yaml` routes readers to canonical sources; it does not outrank or
summarize them. Report a mismatch instead of copying domain content into it.

A feature `plan.md` may refine the architecture baseline and may not contradict
it. A feature that needs to contradict it amends the baseline first, producing a
superseding ADR; it does not diverge quietly.

## Generation timing

An initial Project Map may create a routing-only `AGENTS.md` before product
documents exist. Refresh it after the PRD, product roadmap, real engineering
commands, and architecture exist, normally before the first function enters
specification. Later refreshes are required only when project-wide sources,
paths, commands, boundaries, or governance change; do not regenerate it for
every function.

## Feature isolation

The root guidance should point to the roadmap without copying its feature list.
When delivering a feature, read its one roadmap entry, its applicable product
requirements, and its own `spec.md`. Do not absorb later-feature scope merely
because the roadmap describes it.
