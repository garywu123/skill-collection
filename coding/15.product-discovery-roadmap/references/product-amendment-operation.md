# Product Amendment Operation

Use the [amendment template](../assets/product-amendment-template.md). Record base
paths/hashes, exact product/ID change, downstream impact, and validation.
Approved IDs are append-only; propose successors rather than rewriting history.

The proposal operation registers only `product_amendment` and leaves canonical
truth unchanged. During later explicit approval, keep that reviewed proposal
byte-identical and apply only its named canonical changes. If an affected root
is split, enumerate its complete post-change member set, compute the current
SHA-256 of every member (including unchanged members), replace the root's
`## Approved Bundle` table, and verify that the table and ownership registry are
the same path set. Then re-register the same proposal role and every affected
canonical root role in one pending gate before generic `decide` with explicit
human actor, date, and decision evidence. A changed
member is promoted through its root bundle; it is not a competing canonical
root.
