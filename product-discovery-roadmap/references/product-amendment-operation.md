# Product Amendment Operation

Use the [amendment template](../assets/product-amendment-template.md). Record base
paths/hashes, exact product/ID change, downstream impact, and validation.
Approved IDs are append-only; propose successors rather than rewriting history.

The proposal operation registers only `product_amendment` and leaves canonical
truth unchanged. During later explicit approval, keep that reviewed proposal
byte-identical, apply only its named canonical changes, then re-register the
same proposal role and every changed canonical role in one pending gate before
generic `decide`.
