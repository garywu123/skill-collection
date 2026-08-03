# Architecture Amendment Operation

Identify the accepted decision, human-authorized trigger, and affected
constraints/features. Use the
[amendment template](../assets/architecture-amendment-template.md) with base
hashes, alternatives, constraint effects, and delivery/migration impact. Add a
proposed ADR when needed and name what it would supersede.

The proposal operation leaves accepted baseline/ADRs unchanged and registers
only amendment/proposed-ADR roles. Report divergence, migration implications,
and stale guidance without updating other owners.

On later explicit approval, keep the reviewed amendment proposal byte-identical,
apply the named baseline, domain-member, and ADR changes, and record supersession
in the ADRs. For a split root, enumerate the complete post-change member set,
compute the SHA-256 of every member including unchanged members, replace the
root's `## Approved Bundle` table, and verify exact registry coverage. Then
re-register the exact amendment/ADR set plus canonical `architecture`, use
generic `decide` with explicit human actor, date, and decision evidence, and
stop after its indexed receipt. The reviewed proposal remains unchanged throughout.
