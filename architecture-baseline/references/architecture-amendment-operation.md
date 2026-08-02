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
apply the named baseline/ADR changes, record supersession in the ADRs, re-register
the exact amendment/ADR set plus canonical `architecture`, then use generic
`decide` and stop.
