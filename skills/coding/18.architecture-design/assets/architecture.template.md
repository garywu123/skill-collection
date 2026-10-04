# <System> Architecture Design

**Scope:** <What this design owns and which Feature Maps use it.>

**Sources:** [Product Brief](<relative-path>), [Functional Specification](<relative-path>)

<Keep only sources that exist. Link requirements instead of copying their wording.>

## System Context

<Upstream and downstream systems, external integrations, and the system's
responsibility at each boundary.>

## Components

<Major components, communication and data flow, and one small diagram only when
prose is less clear.>

| Component | Owns | Does not own |
|---|---|---|
| <component> | <stable responsibility> | <important boundary> |

## Technology

- **Runtime and language:** <required choices>
- **Framework, datastore, and test tools:** <required choices>
- **Significant dependencies:** <only dependencies that affect architecture or contracts>
- **Deployment:** <how the system runs and its operating assumptions>

## Contracts And Data Ownership

- <Contract, owner, consumers, and compatibility or data-ownership rule.>

## Quality Constraints

| Subject | Conditions | Property or budget | Source | Verification |
|---|---|---|---|---|
| <component or flow> | <workload, data, hardware> | <required property or `open decision`> | <requirement or evidence> | <Testing Strategy section or check> |

<Delete this section when no constraint affects the design.>

## Invariants

- <A rule every Feature must preserve.>

## Open Decisions

- <Unresolved decision or bounded validation question, the decision it informs,
  and its owner. Delete this section when empty.>

<Do not add requirement wording, Feature lists, delivery order, status, test
cases, class designs, code-level style rules, or speculative infrastructure.>
