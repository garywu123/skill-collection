# [Product Name]: Product Requirements

**Status**: Draft | Ready for Review | Approved
**Last Updated**: YYYY-MM-DD
**Structure**: Split by domain area. This file is canonical for IDs, coverage,
waves, and cross-cutting rules.
**Approved By**: Not approved | [Name or role]
**Approval Evidence**: Not approved | [Explicit user statement or review reference]

Use this index form only when the single-file product requirements document has
outgrown one file. The threshold and splitting rules are in the skill's
`Draft Product Requirements` section. Everything below stays here; only
domain-specific requirement detail moves out.

## Product Vision

[The user or business outcome this product exists to create.]

## Users and Problems

### [User or Persona]

- **Problem**: [Current pain or unmet need]
- **Desired outcome**: [Observable improvement]

## Product Scope

### In Scope

- [Capability or behavior]

### Non-Goals

- [Explicitly excluded behavior]

## Requirement Waves

Discovery horizon. Only `Approved` requirements may be owned by a `Committed`
roadmap feature.

| Wave | Status | Covers | Interviewed |
|------|--------|--------|-------------|
| Wave 1 | Approved | [Areas] | YYYY-MM |
| Wave 2 | Candidate | [Areas] | Not yet |
| Wave 3 | Unknown | [Areas mentioned with no business owner] | No |

## Requirement Registry

Every `PR-###` in the product appears exactly once in this table. IDs are
append-only: a changed requirement gets a new ID and the old one is marked
superseded. Never renumber and never reuse.

| ID | Summary | Area | Wave | Status |
|----|---------|------|------|--------|
| PR-001 | [One line] | `{{AREA_1_PATH}}` | 1 | Approved |
| PR-002 | [One line] | `{{AREA_1_PATH}}` | 1 | Superseded by PR-014 |
| PR-050 | [One line] | `{{CROSS_CUTTING_PATH}}` | 1 | Approved |
| PR-100 | [One line] | `{{CROSS_CUTTING_PATH}}` | 1 | Approved |

Status values: `Draft`, `Approved`, `Superseded by PR-###`, `Withdrawn`.

## Domain Areas

| Area | File | Owns | Notes |
|------|------|------|-------|
| {{AREA_1_NAME}} | `{{AREA_1_PATH}}` | PR-001–PR-00X | |
| {{AREA_2_NAME}} | `{{AREA_2_PATH}}` | PR-0XX–PR-0YY | |
| Cross-cutting | `{{CROSS_CUTTING_PATH}}` | PR-050+, PR-100+ | Never split further |

Split by domain area, which is stable. Do not split by feature — features get
re-decomposed and the requirements would follow them, dissolving single
ownership. Do not split by wave — a wave is a time slice, and Wave 1 and Wave 2
requirements about the same area belong together.

## Cross-Cutting Rules

Cross-cutting rules live in exactly one file and are referenced from every area
that they constrain. They are listed here by ID only; the text lives in the
cross-cutting area file.

- **PR-050**: [One line] — experience requirement
- **PR-100**: [One line] — safety or policy rule

## Success Measures

- **SM-001**: [Technology-independent measurable outcome].

## Assumptions

- **A-001**: [Bounded assumption and impact if false].

## Open Questions

- **Q-001**: [Unresolved decision and why it matters].

## Decision Log

| Date | Decision | Rationale | Affected Requirements |
|------|----------|-----------|-----------------------|
| YYYY-MM-DD | [Decision] | [Reason] | PR-001 |
