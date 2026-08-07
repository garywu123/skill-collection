# Architecture Amendment Operation

Identify the accepted decision, human-authorized trigger, and affected
constraints/features. Use the
[amendment template](../assets/architecture-amendment-template.md) with base
paths/revisions, alternatives, constraint effects, and delivery/migration impact. Add a
proposed ADR when needed and name what it would supersede.

The proposal operation leaves accepted baseline/ADRs unchanged. Report
divergence, migration implications, and stale guidance without updating other
owners or `roadmap.yaml`.

On later explicit approval, keep the reviewed amendment proposal byte-identical,
apply the named baseline, domain-member, and ADR changes, and record supersession
in the ADRs. For a split root, enumerate the complete post-change member set,
update the root's `## Member Registry`, and verify exact registry coverage. Then
record the human's approval fields — actor, date, and decision evidence — in the
canonical baseline and each affected ADR, and stop. The reviewed proposal remains
unchanged throughout.
