---
name: functional-spec
description: Explore, create, revise, or review one optional Functional Specification that lists the numbered observable functional and product-level quality requirements of a product too large for one Feature Map. Invoke explicitly, by name, only when the Product Brief is final and the MVP needs more than one Feature Map, or to check an existing specification against its Brief and the user's authorized interview evidence. Do not use for a product that fits one Feature Map, for technical design, delivery order, or per-feature planning.
disable-model-invocation: false
---

# Functional Specification

Turn a final Product Brief into one numbered list of what the product must do,
so that several Feature Maps can be written without inventing scope. This
document exists only at scale: a product whose MVP stays clear in one Feature
Map does not need it, and the Product Brief plus Feature Map remain the default
pair.

## Gate

Create this document only when the Product Brief is final and the MVP clearly
needs more than one Feature Map because one map cannot stay readable. A
requirement count, a table length, or a product constraint alone does not
trigger it; a small project keeps its confirmed product constraints in the
Product Brief. If a single map would do, stop and say so. If the brief is
missing or unclear, report the gap; do not create or revise the brief here.

## Intent

- `explore`: Discuss functional areas, requirement wording, and boundaries in
  chat. Ask one to three questions per round. Do not write a file.
- `write`: Create or update the specification when the user clearly asks. Ask
  first only when a missing answer would change an observable requirement;
  otherwise state a small assumption and write.
- `review`: Check an existing specification against the Product Brief, the
  user's authorized discovery evidence, and the rules here. Report findings
  with locations; do not edit any file or run the write procedure.

## Evidence

Use only the brief, documents the user identifies, and authorized interview
notes or transcripts; never invent a transcript, quotation, or source locator.
Write a requirement only from a confirmed decision, not from a model suggestion
the user did not accept or a statement a later decision superseded. Keep a
material candidate under unresolved decisions. Cite a source location or short
exact quotation when the evidence provides one, and retrieve the original
passage for a disputed or high-impact requirement. A summary or note written by
the author of this specification or its draft is not, alone, independent
evidence of user intent; the final Brief and documents the user confirms as
authoritative remain valid sources. In `review`, report a suggestion or
superseded statement written as a requirement, a confirmed need that is
missing, and a requirement without supporting evidence, including one backed
only by its author's own summary.

## Output

Create or update `docs/functional-spec.md` from
[the template](assets/functional-spec.template.md), unless the project already
has one clear canonical specification.

Size follows the number of observable requirements; about 200 lines is a
readability signal for repetition, speculation, or design content, not a gate.
Include only:

- a one-line purpose that links the Product Brief;
- functional areas, each with a stable prefix such as `FS-PRJ`;
- one numbered requirement per observable behaviour, stated as what must be
  true, its boundary, and the evidence that would show it;
- confirmed product-level quality requirements, such as a memory, latency, or
  capacity budget, stated with subject, operating conditions, required
  property or budget, and source; and
- exclusions and unresolved decisions that block a requirement from being
  written, including any budget no owner has set.

Once this document exists it owns product-level constraints; move a constraint
recorded in the brief here only when the user authorizes that consolidation,
and leave a link behind.

Each requirement has a stable ID such as `FS-PRJ-004` and is never renumbered.
Retire a requirement by marking it `retired` in place with one line of reason.

Do not add status checkboxes, verification notes, traceability tables,
architecture, component ownership, technology, delivery order, or test design.
Delivery status lives only in Feature Map rows that list the requirement ID;
design lives in the Architecture Design; order lives in the Roadmap. Every active
requirement must be assigned to an existing Map row or a future Roadmap row. It
is delivered only when at least one Map row cites it and every citing Map row
is `verified`.

## Workflow

1. Read repository guidance, the Product Brief, any existing specification,
   Roadmap, Feature Maps, and user-identified domain documents. Read
   representative code only when documents do not explain current behaviour.
2. Confirm the gate. Report and stop when one Feature Map would suffice.
3. Group observable behaviour into functional areas. Write each requirement
   once, in the area that owns it, without repeating brief prose.
4. For `write`, write or revise the document, then run the consistency check.
   For `review`, report findings and stop.

## Consistency Check

For `write` intent only, re-read the Product Brief, Roadmap, and every Feature
Map. Compare every active requirement with the Roadmap and all Map rows: report
an active ID assigned to neither, a retired or missing ID still cited, and a
row whose outcome no longer matches its cited requirements. An ID assigned
only to a future Roadmap row is planned but not delivered. Do not edit a Map or
Roadmap here. When a requirement change invalidates a `verified` row, report
that its Map status and Plan evidence are stale and must be reconciled through
`feature-map` and `feature-plan`. Keep what the product must do only here, keep
product meaning only in the brief, and fix
stale IDs, names, and paths in this document.

## Completion

For `explore`, report the current understanding, assumptions, and next
questions. For `write`, report the file changed, requirement IDs added,
changed, or retired, affected Feature Map rows, unresolved decisions, and
validation performed. For `review`, report findings only. Stop without creating
a Roadmap, Feature Map, or design.
