# <System or Stack> General Design

**Scope:** <What this design owns and which Feature Maps use it.>

**Sources:** [Product Brief](<relative-path>), [Functional Specification](<relative-path>)

<Keep only sources that exist. Link requirements instead of copying their wording.>

## System Context

<Upstream and downstream systems, external integrations, and the system's
responsibility at each boundary.>

## Architecture

<Major components, communication and data flow, and one small diagram only when
prose is less clear.>

## Responsibilities

| Component | Owns | Does not own |
|---|---|---|
| <component> | <stable responsibility> | <important boundary> |

## Technology

- **Runtime and language:** <required choices>
- **Framework, datastore, and test tools:** <required choices>
- **Significant dependencies:** <only dependencies that affect architecture or contracts>

## Contracts And Data Ownership

- <Contract, owner, consumers, and compatibility or data-ownership rule.>

## Quality Constraints

- <Source-backed performance, security, reliability, or deployment constraint
  and its design consequence. Delete this section when none affects the design.>

## Invariants

- <A rule every linked Feature Map must preserve.>

## Worked Example

<One representative end-to-end flow that clarifies the contracts.>

<Do not add requirement wording, delivery order, status, tests, exhaustive
dependency inventories, class designs, or speculative infrastructure.>
