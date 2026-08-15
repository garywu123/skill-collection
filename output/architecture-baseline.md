# GEO Assist Anchor Field Initialization Tool: Architecture Baseline (Lite)

**Source Requirements**: [product requirements](./general-product-requirement.md)
**Source Roadmap**: [feature roadmap](./feature-roadmap.md)
**Mode**: lite
**Sizing test**: 7 features, 1 deployable, 1 datastore, 1 team, no regulatory constraint
**Status**: Ready for Review
**Artifact bundle**: single
**Last Updated**: 2026-08-15
**Approved By**: Not approved
**Approval Evidence**: Not approved

## Drivers

| Driver | Source | Consequence |
|---|---|---|
| One operator works on a handheld without VPN or remote services. | PR-050 | One offline-capable Android process owns the workflow. |
| Every command targets one selected anchor. | PR-005, PR-100 | Command datagrams are unicast and carry the selected CUWBID. |
| Success requires evidence from the addressed anchor. | PR-008, PR-101 | Send completion is never a successful result. |
| Failures use four product layers. | PR-011 | Network and protocol operations return structured layer results. |
| Write records and profiles remain available offline. | PR-010, PR-012 | One on-device store owns both durable data sets. |

## Stack

| Area | Choice | Why | Door |
|---|---|---|---|
| Host | Android handheld with USB-C Ethernet | It matches field ergonomics and the approved operating model. | one-way |
| Runtime | Kotlin on the Android SDK in one process | The wire surface is small and does not justify an embedded Python runtime. | one-way |
| Anchor protocol | CDP over UDP using the proven `0x8029` command envelope | Existing field scripts establish the current compatible route. | one-way |
| Local data | One on-device store for append-only writes and versioned profiles | Both data sets must remain available without a network. | two-way |

## Consequential Choices

| Area | Current choice | Constraint | Reversal cost |
|---|---|---|---|
| Host platform | Android rather than Windows | Use no vendor-specific or privileged network API. | Rewrites the application and invalidates handheld field proving. |
| Wire route | Proven `0x8029` encoding behind one module | Keep Route B `0x015B` replaceable through fixtures and module boundaries. | Contained to the protocol module if encoding does not leak. |

## Cross-Cutting Rules

| Concern | Rule |
|---|---|
| Errors | Every failed operation returns one named layer or the exact indistinguishable pair; transport exceptions never reach the operator unmapped. |
| Command safety | Device commands use unicast IPv4 and the selected CUWBID; wildcard serial `0xFFFFFFFF` is forbidden. |
| Evidence | Success requires a parsed response attributable to the addressed anchor. |
| Network binding | Every socket binds to the Ethernet `Network`; multicast receive holds a `MulticastLock`. |
| Persistence | Append the write record before showing its outcome; reads work offline after process death. |
| Configuration | MVP1 uses operator input; MVP2 uses a selected versioned profile, with manual entry limited to admins. |
| Testing | Packet builders and parsers use captured byte fixtures; real-anchor behavior is field-tested. |

## Boundaries

- The CDP module depends on no UI or feature code.
- The local store contains domain data, not CDP types.
- Features exchange values rather than screen state.
- Runtime sockets contact only anchors and the configured site bridge.
- This baseline owns the shared structured failure result contract; F001-F003
  return its values, and F005 applies, presents, and verifies that contract
  consistently across those flows.

## Plan Constraints

- **AC-001**: Every command datagram is unicast and carries the selected
  anchor's CUWBID; broadcast, multicast, and wildcard targets are defects.
- **AC-002**: No code path reports success without an attributable parsed
  response from the selected anchor.
- **AC-003**: Every surfaced failure uses a named layer or an explicit
  indistinguishable pair.
- **AC-004**: Every socket binds to the Ethernet `Network`; multicast receive
  holds a `MulticastLock` for its full duration.
- **AC-005**: A write record exists before its outcome is displayed and survives
  process death for offline reading.
- **AC-006**: Operator text does not say "cube network" or claim the anchor is
  online with its bridge.
- **AC-007**: CDP encoding lives in one UI-independent module covered by captured
  byte fixtures.
- **AC-008**: Reachability wording names the probe that actually ran and does
  not call a non-ICMP probe a ping.

## Deferred Decisions

| # | Undecided | Trigger | Keep the option open by |
|---|---|---|---|
| D-1 | Destination and format for records leaving the device | F007 delivery | Keep stored records self-describing and transport-independent. |
| D-2 | How profile bundles reach third-party devices | F006 delivery | Import a versioned file without assuming its transport. |
| D-3 | Final handheld and Ethernet adapter models | MVP1 field proving | Use standard unprivileged Android networking only. |

## Spikes

| ID | Question | Time box | Blocks | Output |
|---|---|---|---|---|
| SPK-001 | Can the handheld read the persistent bridge property before reset? | 1 bench day | F003 | Captured packets and a yes/no result. |
| SPK-002 | How does the handheld find an anchor already pointed at another bridge? | 1 bench day | F001, F003 | Captured discovery evidence and a yes/no result. |

## Risks

| Risk | Response |
|---|---|
| The unpublished vendor message surface changes. | Isolate encoding behind fixtures and retain the published Route B migration option. |
| Android or another site does not reproduce the tested laptop attachment model. | Prove F001 and F002 before any production write workflow is relied on. |
| Two failure layers are not distinguishable at the attachment point. | Report the exact pair rather than guessing. |
