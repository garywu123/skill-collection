# GEO Assist Anchor Field Initialization Tool: Discovery Notes

**Status**: Ready for PRD
**Artifact bundle**: single
**Last Updated**: 2026-08-14

## Why This Product

An installer or maintenance engineer standing at an anchor cannot currently
tell whether that anchor accepted the correct bridge address. The existing
bridge-side process can take hours, depends on remote access, and often requires
a second lift trip or a second person to diagnose failure.

## What It Should Do

Give one person on a handheld an immediate, honest answer at the attachment
point: what network the handheld is on, which anchors are reachable, whether the
site bridge can be reached, and whether one selected anchor accepted the bridge
address written to it.

## Primary Workflow

1. Attach an Android handheld to an anchor chain through USB-C Ethernet.
2. Show the handheld's network state and address.
3. Accept or select the site's bridge address and test reachability.
4. List reachable anchors with identity information that can be matched to a
   physical unit.
5. Select exactly one anchor, write the bridge address, and read evidence back
   from that anchor.
6. Show the verified result and keep it in an on-device record.

## Users and Operating Context

- Crown AET engineers use the first release and can compare the result with
  GeoMonitor.
- Velociti installers and Amazon RME are later users. They work at height, have
  no VPN or GeoMonitor access, and use devices Crown does not control.
- The product operates from one handheld with no server component and no runtime
  dependency on Crown or Amazon services.
- A replacement anchor still requires Crown to update and push the site
  configuration. This tool removes the bridge-side discovery mode, not that
  organizational handoff.

## Domain Knowledge

- An anchor stores its bridge destination as persistent property 122 and needs a
  reset before the new value takes effect.
- Existing field-proven scripts send CDP device commands over UDP. They report
  completion after sending but do not read back a result.
- Default-state multicast announcements cannot be the only discovery method;
  already-configured anchors are normal in replacement work.
- The operator needs MAC address and CUWB identity to match a network result to a
  physical anchor.
- Operator language uses "CUWB network" and describes an anchor as pointed at
  its bridge. It does not claim that the anchor is online with the bridge.

## Critical Unknowns

- Can an Android handheld enumerate every anchor on an attached chain when one
  anchor is already configured for another bridge?
- Can the handheld observe persistent-property read-back before reset so that a
  positive result comes from the selected anchor itself?

## Discovery Approval

- **Approved for PRD**: Yes
- **Approved By**: Gary Wu
- **Date**: 2026-08-12
- **Approval Evidence**: Existing approved discovery source; this condensed
  rendering is ready for review.
