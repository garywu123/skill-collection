# GEO Assist Anchor Field Initialization Tool: Feature Roadmap

**Source Requirements**: [product requirements](./general-product-requirement.md)
**Status**: Ready for Review
**Artifact bundle**: single
**Last Updated**: 2026-08-15
**Approved By**: Not approved
**Approval Evidence**: Not approved
**Profile sizing**: lite
**Feature count**: 7
**Deployable count**: 1
**Datastore count**: 1
**Owning team count**: 1
**Regulatory/audit/contractual constraint**: no
**Sizing evidence**: PR-010, PR-012, PR-050

## Delivery Strategy

F001 and F002 test the handheld attachment model before a live anchor is
changed. F003 performs and records the first write before showing its outcome.
F004 provides restart-safe offline history review, and F005 integrates and
verifies one failure vocabulary across the MVP flows. F006 and F007 extend the
tool to operators outside Crown AET.

## Lifecycle Boundary

This roadmap owns feature boundaries, requirement ownership, dependencies, and
delivery grouping. Current implementation status lives in `roadmap.yaml` and
delivery evidence lives in each feature checklist.

## Domain Registry

| Domain key | Purpose | Feature IDs |
|---|---|---|
| network-diagnostics | Establish attachment, reachability, and failure facts. | F001, F002, F005 |
| anchor-configuration | Apply and verify one attributable anchor change. | F003 |
| write-history | Preserve and share write evidence. | F004, F007 |
| site-access | Select governed site configuration and operator permissions. | F006 |

## Feature Map

| ID | Feature | Domain | Outcome | Owns Requirements | Also Bound By | Depends On | Delivery | UI Surface |
|---|---|---|---|---|---|---|---|---|
| F001 | See what I am attached to | network-diagnostics | The operator sees handheld network state and every reachable anchor with physical identity. | PR-001, PR-003, PR-004, PR-050, PR-053 | PR-100, PR-102 | None | MVP | new screens |
| F002 | Check the bridge address | network-diagnostics | The operator sees whether the configured bridge test succeeds from the attachment point. | PR-002, PR-006 | PR-050, PR-051, PR-053, PR-101 | None | MVP | new screens |
| F003 | Write and verify one anchor | anchor-configuration | One selected anchor accepts the intended bridge address and returns attributable evidence. | PR-005, PR-007, PR-008, PR-009, PR-051, PR-100, PR-101, PR-102, PR-103 | PR-050, PR-053 | F001, F002 | MVP | new screens |
| F004 | Keep every write | write-history | The operator can review every write after process restart and while offline. | PR-010 | PR-050, PR-053, PR-101, PR-103 | F003 | MVP | new screens |
| F005 | Name the failed layer | network-diagnostics | Failures across discovery, reachability, and writing use one four-layer vocabulary. | PR-011 | PR-050, PR-051, PR-053, PR-101 | F001, F002, F003 | MVP | reuses existing |
| F006 | Select site and operator role | site-access | MVP2 operators use current site profiles while manual entry remains admin-only. | PR-012, PR-013, PR-014, PR-015, PR-016, PR-052 | PR-050, PR-053, PR-103 | F002, F003 | Post-MVP | new screens |
| F007 | Send the write record | write-history | The write record can be opened away from the handheld without losing content. | PR-017 | PR-050, PR-053 | F004 | Post-MVP | reuses existing |

## Feature Detail

### F001: See what I am attached to

**Description**: Show the handheld's own network state and identify all anchors
reachable from the attachment point, including already-configured anchors.

**Acceptance**:

- On a lift, the operator sees the handheld address and every anchor physically
  present on the attached chain, with MAC and CUWB identity.

### F002: Check the bridge address

**Description**: Accept a bridge address, run an available reachability probe,
and report exactly what was tested.

**Acceptance**:

- A reachable bridge and an address with no path produce different factual
  results, and neither path writes an anchor.

### F003: Write and verify one anchor

**Description**: Write the reachable bridge address to exactly one selected
anchor, verify the stored value from an attributable response, and record the
attempt and outcome before showing the result.

**Acceptance**:

- The result names the selected anchor and written address, and success is
  impossible without parsed evidence from that anchor.
- Every write attempt and outcome is recorded before the result is shown.
- No UI or protocol path can target all discovered anchors.

### F004: Keep every write

**Description**: Provide restart-safe, offline review of the write records
created by F003.

**Acceptance**:

- After two writes and an application restart, both records remain available
  offline with anchor, address, and outcome intact.

### F005: Name the failed layer

**Description**: Apply one operator-facing failure vocabulary to F001-F003.

**Acceptance**:

- Induced link, address, path, and anchor-acceptance failures produce distinct
  layer results or explicitly name the pair that cannot be separated.

### F006: Select site and operator role

**Description**: Load versioned site profiles, show the active site and address,
and restrict manual address entry to admins.

**Acceptance**:

- A user completes a profile-driven write without manual entry; importing a
  newer Crown profile changes the visible currency result.

### F007: Send the write record

**Description**: Export or send the existing record without coupling storage to
one destination.

**Acceptance**:

- A recipient opens the record away from the handheld and sees the same writes,
  anchors, addresses, and outcomes.
