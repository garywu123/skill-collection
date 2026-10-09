---
name: testing-strategy
description: Create, update, or review one project Testing Strategy - reusable rules for test levels, business invariants, correctness oracles, fixtures and data scale, mocks, test discovery and skips, environments, resource measurement, regression triggers, and when independent testing is warranted. Invoke explicitly, by name, to establish or revise how a project tests, or to review a strategy against its requirements and architecture. Do not use for per-feature test cases or results, writing or running tests, product requirements or budgets, architecture, or code style.
disable-model-invocation: false
---

# Testing Strategy

Maintain one concise project rule set that Feature Plans and Delivery apply.
It states how the project establishes correctness; it is not an inventory of
future cases and never reports test results that did not run.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `write`: create or update the strategy. Default.
- `review`: check an existing strategy, or the test design of a supplied
  artifact, against the strategy, its sources, and the criteria below. Report
  findings with locations, missing decisions, and the owner of each decision.
  Do not edit any file or run the write procedure.

## Output

Use the project's existing canonical testing document; otherwise create
`docs/testing.md` from [the template](assets/testing.template.md). Add a scoped
document only when a subproject needs substantial distinct guidance, and link
it from the main strategy. About 200 lines is a review signal, not a gate.

Include only what applies:

- production and test projects, their locations, and verified entry commands;
  use separate test projects where the stack expects them, such as .NET test
  `.csproj` files, without requiring one per test category;
- unit, component, integration, and end-to-end boundaries, choosing the
  smallest level that detects each distinct failure; multiple levels need
  different failure coverage, including real browser/native boundaries;
- business invariants with links to their requirement sources;
- correctness oracles for algorithms and data transformations;
- fixture provenance, representative and worst supported scale, and limits on
  mocks;
- test discovery, skip and disable rules, and environment or isolation needs;
- resource measurement methods;
- regression triggers; and
- conditions under which independent testing or review of a change is
  warranted.

State a command only when configuration, automation, or an observed successful
run verifies it. Line coverage and a green exit code do not establish behavior
coverage or assertion strength. Reuse adequate cases and strengthen existing
assertions before adding cases, fixtures, mocks, or another test project.
Apply this rule in Feature Plans; do not turn the strategy into a case list.

## Oracles And Measurement

For algorithm or data work, name an oracle independent of the implementation:
known answers, a small independent reference implementation, justified
properties, or another external source. Define seeds, tolerances, baselines,
and scale profiles where they matter.

Keep three things distinct: the requirement and its owner, the oracle that
decides correctness, and the measurement method. A memory, latency, or capacity
budget belongs to the product requirement owner and its allocation to the
Architecture Design. This strategy defines how to measure it, such as peak
versus steady state, workload, hardware, and repetitions. When no owner has set
a budget, record it as an open decision; an observed value is a measurement,
not a pass or fail criterion.

Independent-testing conditions describe concrete verification gaps, such as
algorithm correctness, realistic-scale resource behavior, migration or
recovery, or cross-component state. Complexity alone is not a condition. This
Skill neither selects nor launches a tester.

## Evidence And Questions

Inspect project evidence first: requirements, the Architecture Design, existing
tests and runners, CI, and fixtures. Then ask a small number of high-value
questions about users, workloads, data, failure consequences, or target
hardware, each saying why the answer changes testing or acceptance. Search
external sources only for a relevant uncertainty, cite primary sources, and
mark applicability; never turn outside advice into a project rule without the
user's authority.

Promote a rule into the strategy only when it is reusable across Features and
supported by a requirement, the architecture, verified tooling, or user
direction. A missed case under an existing requirement belongs in the current
Feature Plan. A new business rule or resource budget first needs a decision by
its owning source; report it instead of writing it here.

## Workflow

1. Read repository guidance, the Product Brief, the Functional Specification
   and Architecture Design when present, any existing strategy, test projects,
   runner and CI configuration, and representative tests.
2. Follow the inferred intent. For `write`, resolve material gaps with the
   questions above, then write or update the strategy.
3. For `write`, run the consistency check. For `review`, report findings and
   stop.

## Review Criteria

- Each rule is reusable, sourced, and actionable; no per-feature case lists.
- Algorithm and data rules name an independent oracle.
- Requirements, oracles, and measurements are distinct; unknown budgets are
  open decisions with owners, not invented thresholds.
- Commands are verified; skip, discovery, and isolation rules prevent silent
  non-execution.
- Independent-testing conditions name concrete verification gaps.
- Additional test levels or infrastructure close an identified coverage gap;
  they do not merely repeat the same assertions at greater cost.

## Consistency Check

For `write` only, re-read the requirements and Architecture Design it cites
and the Feature Plans that link it. Fix stale names, paths, and commands here.
Keep testing rules only here: link requirements and architecture instead of
copying them, and report a conflict with them to their owner. Report Plans
whose tests no longer satisfy a changed rule for `feature-plan` to revise, and,
after a changed rule, command, or strategy path, that an instruction-impact
assessment by `coding-agent-instructions` is needed.

## Completion

For `write`, report the file changed, rules added or changed, verified and
omitted commands, open decisions with owners, affected Plans, and validation
performed. For `review`, report findings only. Stop without writing tests,
running test suites, editing Plans, or changing requirements or architecture.
