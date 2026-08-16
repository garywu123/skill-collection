# [Product Name]: Feature Roadmap

**Source Requirements**: [Relative link to approved product requirements]
**Status**: Draft | Ready for Review | Approved
**Artifact bundle**: split
**Last Updated**: YYYY-MM-DD
**Approved By**: Not approved | [Name or role]
**Approval Evidence**: Not approved | [Explicit user statement or review reference]
**Profile sizing**: full | lite
**Feature count**: [positive integer]
**Deployable count**: [positive integer]
**Datastore count**: [non-negative integer]
**Owning team count**: [positive integer]
**Regulatory/audit/contractual constraint**: yes | no | unknown
**Sizing evidence**: [Stable source anchor(s) only]

## Delivery Strategy

[How the sequence reaches a usable release while controlling product risk.]

## Ownership Boundary

This root owns feature routing, requirement ownership, dependencies, UI surface,
and delivery boundary. Domain members own concise descriptions and acceptance.
Product truth must appear under exactly one owner.

## Domain Registry

| Domain key | Detail path | Feature IDs |
|---|---|---|
| [stable-domain-key] | `{{DOMAIN_1_PATH}}` | F001, F002 |

## Feature Map

Requirement ownership appears only in this table. Every approved `PR-###` has
exactly one owner; `Also Bound By` never creates another owner.

| ID | Feature | Domain | Outcome | Owns Requirements | Also Bound By | Depends On | Delivery | UI Surface |
|---|---|---|---|---|---|---|---|---|
| F001 | [User capability] | [stable-domain-key] | [Observable result] | PR-001 | PR-100 | None | MVP | new screens |
| F002 | [Next capability] | [stable-domain-key] | [Observable result] | PR-002 | PR-100 | F001 | Post-MVP | reuses existing |

Allowed delivery values: `MVP`, `Post-MVP`, `Deferred`, `Candidate`.
Allowed UI values: `none`, `reuses existing`, `new screens`.

## Member Registry

The complete set of external files owned by this root. List each member exactly
once; do not list this root or cited source artifacts. No hashes are recorded —
Git detects member drift.

| Path | Owns |
|---|---|
| `{{DOMAIN_1_PATH}}` | `{{DOMAIN_1_SCOPE}}` |
