# Product Amendment Operation

Use the [amendment template](../assets/product-amendment-template.md). Record base
paths/revisions, exact product/ID change, downstream impact, and validation.
Never reuse or renumber stable IDs. Update the same capability in place when it
replaces prior behavior; use a successor only when both records need independent
meaning or tracking.

The proposal operation writes only the amendment proposal and leaves canonical
truth and `roadmap.yaml` unchanged. During later explicit approval, keep that reviewed proposal
byte-identical and apply only its named canonical changes. If an affected root
is split, enumerate its complete post-change member set, update the root's
`## Member Registry`, and verify that the registry and ownership list are the
same path set. Then record the human's approval fields — actor, date, and
decision evidence — in each affected canonical root. A changed
member is promoted through its root bundle; it is not a competing canonical
root.
