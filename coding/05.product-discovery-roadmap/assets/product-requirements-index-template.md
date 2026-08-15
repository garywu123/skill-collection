# [Product Name]: Product Requirements

**Status**: Draft | Ready for Review | Approved
**Artifact bundle**: split
**Last Updated**: YYYY-MM-DD
**Approved By**: Not approved | [Name or role]
**Approval Evidence**: Not approved | [Explicit user statement or review reference]
**Product UI structure applicability**: required | not_applicable
**Product UI applicability evidence**: [Approved PR-### registry entry and member anchor]

This root owns product-wide scope, stable-ID routing and status, waves, success
measures, and bundle membership. Domain members own requirement wording and
domain-specific rules. Do not copy member summaries into this root.

Use `not_applicable` only when the cited cross-cutting approved requirement
states that no global shell, navigation, or shared cross-feature UI pattern
exists. Feature-level `UI Surface` remains independently authoritative.

## Product Intent

[Why users need the product and the result it promises.]

## Users and Main Jobs

### [User or Persona]

- [The main job this user needs to complete.]

## MVP

[The smallest useful product outcome and the core capabilities required for it.]

## Requirement Waves

| Wave | Status | Covers | Evidence date |
|---|---|---|---|
| Wave 1 | Approved | [Areas] | YYYY-MM-DD |
| Wave 2 | Candidate | [Areas] | Not yet |

## Requirement Registry

Every `PR-###` appears exactly once. Requirement text lives only at the linked
member anchor. IDs are append-only; never renumber or reuse them.

| ID | Detail path | Detail anchor | Area | Wave | Status |
|---|---|---|---|---|---|
| PR-001 | `{{AREA_1_PATH}}` | `#pr-001` | {{AREA_1_KEY}} | 1 | Approved |
| PR-050 | `{{CROSS_CUTTING_PATH}}` | `#pr-050` | cross-cutting | 1 | Approved |

Status values: `Draft`, `Approved`, `Superseded by PR-###`, `Withdrawn`.

## Domain Registry

| Domain key | Detail path | Purpose |
|---|---|---|
| {{AREA_1_KEY}} | `{{AREA_1_PATH}}` | Domain requirement detail |
| cross-cutting | `{{CROSS_CUTTING_PATH}}` | Shared experience, safety, or policy rules |

Split by stable domain area, never by feature or discovery wave. The requirement
registry is the sole ID-to-member mapping.

## Success Measures

- **SM-001**: [Technology-independent measurable outcome].

## Explicit Exclusions

Include only explicit or easily misunderstood exclusions. Delete when empty.

- [Explicitly excluded capability.]

## Critical Assumptions

Include only assumptions that could change the MVP, product promise, or
feasibility. Delete when empty.

- **A-001**: [Assumption and consequence if false.]

## Blocking Product Decisions

Include only unresolved decisions that block roadmap or delivery work. Delete
when empty.

- [Decision needed and what it blocks.]

## Member Registry

The complete set of external files owned by this root. List each member exactly
once; do not list this root or cited source artifacts. No hashes are recorded —
Git detects member drift.

| Path | Owns |
|---|---|
| `{{AREA_1_PATH}}` | `{{AREA_1_SCOPE}}` |
| `{{CROSS_CUTTING_PATH}}` | Cross-cutting rules constraining every area |
