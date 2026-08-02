# [Product Name]: Architecture Baseline (Lite)

**Source Requirements**: [Relative link]
**Source Roadmap**: [Relative link]
**Mode**: lite
**Sizing test**: [Which conditions passed, e.g. 5 features, 1 binary, no datastore, solo]
**Status**: Draft | Ready for Review | Approved
**Artifact bundle**: single
**Last Updated**: YYYY-MM-DD
**Approved By**: Not approved | [Name or role]
**Approval Evidence**: Not approved | [Explicit user statement or review reference]

One page. Decisions that more than one feature depends on. Everything else is
`plan.md`.

## Drivers

| Driver | Source | Consequence |
|--------|--------|-------------|
| [Driver] | PR-0XX | [What it forces] |

## Stack

| Area | Choice | Why | Door |
|------|--------|-----|------|
| Language and runtime | [Choice] | [One line] | one-way |
| [Area] | [Choice] | [One line] | two-way |

Add a component diagram only if there is more than one process.

## Consequential Decision Notes

Use this section only when a one-way door exists. Lite mode removes the separate
ADR file, not the comparison or reversal analysis.

| Area | Alternatives considered | Why this choice | Reversal cost |
|------|-------------------------|-----------------|---------------|
| [Area] | [Options and material trade-offs] | [Evidence-backed reason] | [Migration, rewrite, or contract impact] |

## Cross-Cutting Rules

| Concern | Rule |
|---------|------|
| Errors | [How they surface and what the user sees] |
| Persistence or state | [Where state lives, or None] |
| Configuration | [Source and precedence] |
| Testing | [Required layers] |

## Boundaries

- [Dependency or layering rule a reviewer can check]

## Plan Constraints

- **AC-001**: [Constraint]
- **AC-002**: [Constraint]

## Deferred Decisions

| # | Undecided | Trigger | Keep the option open by |
|---|-----------|---------|-------------------------|
| D-1 | [Decision] | [What forces it] | [What code must avoid doing] |

## Spikes

| ID | Question | Time box | Blocks | Output |
|---|---|---|---|---|
| SPK-001 | [Question an answer would settle] | [e.g. 1 day] | [Owning feature/work item] | Disposable investigation; any architecture change requires a CR |

## Risks

| Risk | Response |
|------|----------|
| [Risk, including any failed sizing condition] | [Mitigation or accepted] |
