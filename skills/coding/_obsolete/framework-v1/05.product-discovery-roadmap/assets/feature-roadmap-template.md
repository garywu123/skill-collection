# [Product Name]: Feature Roadmap

**Source Requirements**: [Relative link to approved product requirements]
**Status**: Draft | Ready for Review | Approved
**Artifact bundle**: single
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

[How the sequence reaches a usable release. Delete this section when the
feature map makes the order self-explanatory.]

## Domain Registry

Domains are stable business knowledge and ownership boundaries. A small domain
may currently contain one feature; do not collapse the two concepts.

| Domain key | Purpose | Feature IDs |
|---|---|---|
| [stable-domain-key] | [Business boundary] | F001 |

## Lifecycle Boundary

This roadmap owns product outcome, horizon, sequence, dependencies, and release
boundary. It does not mirror mutable delivery state. Current status per feature
lives in `roadmap.yaml`; delivery evidence lives in each feature's
`checklist.md`; history lives in Git.

## Feature Map

Requirement ownership appears only in this table. `Owns Requirements` must give
every approved `PR-###` exactly one owner. `Also Bound By` may reference a
requirement from another row without creating a second owner.

| ID | Feature | Domain | Outcome | Owns Requirements | Also Bound By | Depends On | Delivery | UI Surface |
|---|---|---|---|---|---|---|---|---|
| F001 | [User capability] | [stable-domain-key] | [Observable user result] | PR-001, PR-002 | PR-100 | None | MVP | new screens |

Allowed delivery values: `MVP`, `Post-MVP`, `Deferred`, `Candidate`.
Allowed UI values: `none`, `reuses existing`, `new screens`.

## Feature Detail

### F001: [User Capability]

**Description**: [What this feature enables.]

**Acceptance**:

- [Observable end-to-end result]
- [Important failure or boundary result, when needed]
