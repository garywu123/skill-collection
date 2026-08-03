# Project Agent Instructions

## Scope

This file owns agent behavior, source routing, verified commands, and hard
working boundaries. It does not own product, architecture, feature, or delivery
truth; follow the canonical artifacts below.

## Canonical routing

| Need | Read |
|---|---|
| Current feature, phase, gate, and canonical paths | `.specify/flow-state.yaml`, then a targeted artifact-index query (`resolve` when large) |
| Product outcomes, scope, and rules | `[approved product requirements path]` |
| Feature boundary, dependency, and commitment | `[approved feature roadmap path]` |
| Engineering governance | `[constitution path]` |
| Cross-feature architecture | `[architecture baseline and ADR index path]` |
| Current feature behavior and acceptance | `[active feature spec path from artifact index]` |
| Legacy behavior | `[legacy reference path]`, as evidence only |

Use current explicit user instructions within their authorized scope. When
sources conflict, stop and report the evidence; do not silently choose current
code or legacy behavior over approved domain truth.

## Working boundaries

- Work on one active feature and its applicable requirement IDs at a time.
- Do not load unrelated roadmap entries or later-feature specifications.
- Do not change product or architecture truth through implementation files.
- Record new cross-feature decisions in `[ADR path]` through its owning process.
- Ask before `[project-specific risky action]`.
- Never commit secrets or production data.

## Verified commands

- Setup: `[verified command]`
- Run: `[verified command]`
- Targeted test: `[verified command]`
- Full validation: `[verified command]`

Omit any command not verified by a manifest, CI configuration, or successful
repository execution.

## Change rules

- Make the smallest change that satisfies the active specification.
- Preserve explicit non-goals; avoid unrelated refactors and dependency updates.
- Add or update tests for changed behavior.
- Report conflicts, unknowns, unverified assumptions, and remaining risks.

## Definition of done

- The active feature specification and applicable product requirements are met.
- Relevant tests and repository validation pass.
- Affected documentation and decision records are updated through their owners.
- Acceptance evidence exists before delivery status changes.
