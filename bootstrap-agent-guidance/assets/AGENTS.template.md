# Project Agent Instructions

## Mission

- Build [product outcome] for [primary users].
- Success means [observable result].
- Current non-goals: [material exclusions only].

## Sources of Truth

Use this precedence:

1. `[approved product requirements path]`
2. `[approved feature roadmap path]`
3. `[constitution and architecture decision paths, if present]`
4. Current code, tests, CI, and manifests as implementation evidence
5. `[legacy reference path]` as reference only

When sources conflict, report the evidence. Do not let legacy or current
implementation silently override approved new-project requirements.

## Task Routing

| Need | Read first |
|---|---|
| Product scope and rules | `[product requirements path]` |
| Feature boundary and dependencies | `[feature roadmap path]` |
| Engineering governance | `[constitution path]` |
| Architecture decisions | `[architecture path]` |
| Legacy behavior | `[legacy migration map or reference path]` |
| Tests and acceptance | `[test and acceptance paths]` |

## Feature Isolation

- Work from one roadmap entry and one feature specification at a time.
- Preserve the feature's non-goals and do not absorb later-feature scope.
- After an assessment, treat the approved PRD and roadmap update as authoritative.

## Architecture and Safety Boundaries

- [Only verified project-wide boundaries]
- Record new project-wide architecture decisions in `[ADR path]`.
- Ask before [materially risky project-specific actions].
- Never commit secrets or production data.

## Verified Commands

- Setup: `[command]`
- Run: `[command]`
- Targeted test: `[command]`
- Full validation: `[command]`

Omit commands that are not yet established. Do not invent them.

## Working Rules

- Read the relevant authoritative documents and scoped instructions first.
- Make the smallest change that satisfies the approved requirement.
- Avoid unrelated refactors and dependency upgrades.
- Add or update tests for changed behavior.
- Report conflicts, unknowns, unverified assumptions, and remaining risks.

## Definition of Done

- The change satisfies the current feature specification and applicable product requirements.
- Relevant tests and repository validation pass.
- Affected documentation and decision records are updated.
- Acceptance evidence is recorded before the roadmap feature is marked Done.
