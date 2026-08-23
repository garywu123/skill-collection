# <F### — Feature Name> Implementation Plan

## Sources

- Roadmap: `<path>#<feature-id>`
- Product requirements: `<requirement IDs and links>`
- Architecture constraints: `<decision IDs and links>`
- Repository evidence: `<paths inspected>`

## Planning Assessment

- Domain: `<stable-domain-key>`
- Route: `compact`
- Cohesive outcome: `<one sentence>`
- Boundary notes: `<what is explicitly outside this feature>`

## Component Design

| Class / type / component | Responsibility | Key functions or contracts | Depends on | Likely path |
|---|---|---|---|---|
| `<name>` | `<one responsibility>` | `<function: behavior>` | `<dependency>` | `<path or new>` |

Use classes only when the repository and behavior justify them. Functions, modules, handlers, or schema changes may be the better unit.

## Delivery Slices

| Slice | Behavior delivered | TDD starting test | Implementation touchpoints | Depends on | Parallel with | Status |
|---|---|---|---|---|---|---|
| S1 | `<observable behavior>` | `<unit or integration test>` | `<components/files>` | `none` | `<slice or none>` | `planned` |

## Verification Plan

| Acceptance criterion | Planned evidence | Test level | Expected command or location |
|---|---|---|---|
| `<AC ID or exact criterion>` | `<behavior to prove>` | `unit / integration / other` | `<command or test path>` |

## Risks and Blockers

- `<risk, blocker, or decision>` — `<mitigation or owner>`
