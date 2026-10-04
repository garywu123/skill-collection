# <Project> Testing Strategy

**Sources:** [Architecture Design](<relative-path>), [Functional Specification](<relative-path>)

<Keep only sources that exist. Link requirements instead of copying them.>

## Projects And Commands

| Production project | Test project | Command | Verified by |
|---|---|---|---|
| <path> | <path> | `<command>` | <configuration, CI, or observed run> |

## Test Levels

- **Unit:** <what is tested in isolation and what may be faked>
- **Integration:** <real boundaries exercised>
- **End-to-end:** <user-visible flows, only when used>

## Invariants And Oracles

| Subject | Invariant or oracle | Source |
|---|---|---|
| <behavior or algorithm> | <known answers, reference implementation, or property; seeds and tolerances> | <requirement or evidence> |

## Fixtures And Mocks

- <Fixture provenance, representative and worst supported scale, and mock limits.>

## Discovery, Skips, And Environments

- <How tests are discovered, when a skip is allowed, and isolation needs.>

## Resource Measurement

| Subject | Method | Budget and owner |
|---|---|---|
| <flow> | <metric, workload, hardware, repetitions> | <linked budget, or `open decision` and its owner> |

<Delete this section when no resource behavior matters.>

## Regression And Independent Testing

- **Regression triggers:** <changes that require broader checks>
- **Independent testing warranted when:** <concrete verification gaps>

## Open Decisions

- <Missing oracle, budget, or data decision and its owner. Delete when empty.>
