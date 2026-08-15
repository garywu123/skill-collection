# GEO Assist Anchor Field Initialization Tool: Product Requirements

**Status**: Ready for Review
**Artifact bundle**: single
**Last Updated**: 2026-08-14
**Approved By**: Not approved
**Approval Evidence**: Not approved
**Product UI structure applicability**: required
**Product UI applicability evidence**: PR-050

## Product Intent

Let one operator at an anchor point it at the correct bridge and verify, from
evidence returned by that anchor, that it accepted the address. The operator
gets the answer on the lift without a laptop, VPN, or remote site access.

## Users and Main Jobs

### Crown AET engineer

- Initialize or replace one anchor and compare the field result with GeoMonitor.

### Velociti installer

- Verify a newly mounted anchor before leaving the lift.

### Amazon RME maintenance

- Bring one replacement anchor into service without stopping the CUWB network.

## MVP

### MVP1

Show handheld network status, accept a bridge address, find and identify
anchors, test bridge reachability, write one selected anchor, verify read-back,
name the failed layer, and retain an on-device write record.

### MVP2

Add versioned site profiles, `user` and `admin` roles, profile currency, and a
way to send the write record off the device.

## User Journeys

### Initialize one anchor

1. The operator connects the handheld and sees its network status and address.
2. The operator supplies a bridge address and sees what reachability test ran
   and whether it passed.
3. The product lists anchors with physical identity information.
4. The operator selects exactly one anchor.
5. The product writes the address, reads evidence back from that anchor, and
   records the outcome before showing it.

### Replace an anchor

1. The operator replaces the failed unit and follows the initialization journey.
2. The operator retains the replacement identity and verified write result.
3. Crown performs the separate site-configuration update and final GeoMonitor
   confirmation.

## Product Experience Requirements

- **PR-050**: The product MUST be operable by one person on a handheld while
  working at height, without a laptop or remote site access.
- **PR-051**: The product MUST report only that the selected anchor accepted the
  intended bridge address and MUST NOT imply the anchor is online with the
  bridge.
- **PR-052**: From MVP2, the product MUST tell the operator that an AET engineer
  provides final online confirmation.
- **PR-053**: Operator-facing language MUST say "CUWB network" and describe the
  outcome in field terms rather than "set discovery" jargon.

## Product Requirements

- **PR-001**: The product MUST show the handheld's network status and address
  before any anchor action.
- **PR-002**: The product MUST accept a bridge address supplied by an operator.
- **PR-003**: The product MUST find anchors reachable from the attachment point
  regardless of their current bridge configuration.
- **PR-004**: The product MUST identify each listed anchor with its MAC address
  and enough identity information to match a physical unit.
- **PR-005**: The product MUST require exactly one listed anchor to be selected
  for a write.
- **PR-006**: The product MUST test the supplied bridge address from the
  attachment point and report the actual test result before a write.
- **PR-007**: The product MUST write the supplied bridge address to the selected
  anchor and cause it to take effect.
- **PR-008**: The product MUST confirm from evidence returned by the selected
  anchor that it holds the intended bridge address.
- **PR-009**: After a write, the product MUST report which anchor was written and
  what address was written.
- **PR-010**: The product MUST keep an offline-readable on-device record of every
  write and let the operator review it later.
- **PR-011**: A failed check MUST identify no link, no address, no path to the
  bridge, anchor rejection, or the exact pair that available evidence cannot
  distinguish.
- **PR-012**: MVP2 MUST carry profiles for all sites in one installation and let
  the operator select the current site.
- **PR-013**: MVP2 MUST show the selected site and bridge address at the moment
  of writing.
- **PR-014**: MVP2 MUST import an updated profile supplied by Crown on a device
  Crown does not control.
- **PR-015**: MVP2 MUST make the version and currency of the active profile
  visible.
- **PR-016**: MVP2 MUST establish the operator as `user` or `admin`; only an
  `admin` may supply a bridge address by hand.
- **PR-017**: MVP2 MUST send the write record off the handheld without changing
  the recorded writes, anchors, addresses, or outcomes.

## Product Rules and Safeguards

- **PR-100**: Every write and reset MUST target exactly one operator-selected
  anchor; the product MUST NOT offer a bulk action.
- **PR-101**: The product MUST NOT report success merely because a transmission
  completed.
- **PR-102**: Before acting, the product MUST tell the operator when the selected
  anchor has downstream anchors on the same chain.
- **PR-103**: Every write MUST be recorded, including writes using a manually
  supplied address.

## Success Measures

- **SM-001**: An operator completes the field-side sequence in about one minute
  without leaving the lift.
- **SM-002**: Every failed check identifies the failed layer or the exact
  indistinguishable pair.
- **SM-003**: A replacement anchor is initialized without stopping the CUWB
  network; the separate Crown configuration push still occurs.
- **SM-004**: During MVP1, no passed reachability test plus verified write is
  followed by an anchor that never appears in GeoMonitor.
- **SM-005**: MVP2 is usable by Velociti and Amazon RME without Crown staff or
  VPN access at the attachment point.

## Explicit Exclusions

- The product does not confirm that an anchor is online with its bridge.
- The product does not perform whole-site bulk commissioning, firmware updates,
  position verification, or physical cable certification.
- The product does not register a replacement identity in Crown's site
  configuration.

## Critical Assumptions

- **A-001**: An anchor port gives the handheld a usable path to the site network;
  if false, the attachment model and bridge reachability check fail.
- **A-002**: An Android handheld on the selected Ethernet adapter behaves like
  the field-tested laptop; if false, the host platform must change.
- **A-003**: Every anchor on the attached chain is discoverable from one
  attachment point; if false, the operator must attach at the target anchor.
- **A-004**: A passed reachability test plus verified write predicts the field
  result; MVP1 measures this against GeoMonitor.
- **A-005**: For MVP2, Crown can supply a correct, dated profile and an AET
  engineer remains available for final confirmation.
