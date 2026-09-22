---
name: functional-spec
description: Explore, create, or revise one Functional Specification that lists the numbered observable requirements of a product too large for one Feature Map. Invoke explicitly, by name, only when the Product Brief is final and the MVP needs more than one Feature Map. Do not use for a product that fits one Feature Map, for technical design, delivery order, or per-feature planning.
disable-model-invocation: true
---

# Functional Specification

Turn a final Product Brief into one numbered list of what the product must do,
so that several Feature Maps can be written without inventing scope. This
document exists only at scale: a product that fits one Feature Map under eight
rows does not need it, and the Product Brief plus Feature Map remain the
default pair.

## Gate

Create this document only when the Product Brief is final and the MVP clearly
needs more than one Feature Map. If a single map would do, stop and say so.
If the brief is missing or unclear, report the gap; do not create or revise
the brief here.

## Intent

- `explore`: Discuss functional areas, requirement wording, and boundaries in
  chat. Ask one to three questions per round. Do not write a file.
- `write`: Create or update the specification when the user clearly asks. Ask
  first only when a missing answer would change an observable requirement;
  otherwise state a small assumption and write.

## Output

Create or update `docs/functional-spec.md` from
[the template](assets/functional-spec.template.md), unless the project already
has one clear canonical specification.

Keep the whole document under 200 lines. Include only:

- a one-line purpose that links the Product Brief;
- functional areas, each with a stable prefix such as `FS-PRJ`;
- one numbered requirement per observable behaviour, stated as what must be
  true, its boundary, and the evidence that would show it; and
- exclusions and unresolved decisions that block a requirement from being
  written.

Each requirement has a stable ID such as `FS-PRJ-004` and is never renumbered.
Retire a requirement by marking it `retired` in place with one line of reason.

Do not add status checkboxes, verification notes, traceability tables,
architecture, component ownership, technology, delivery order, or test design.
Delivery status lives only in the Feature Map row that lists the requirement
ID; design lives in the General Design; order lives in the Roadmap.

## Workflow

1. Read repository guidance, the Product Brief, any existing specification,
   Roadmap, Feature Maps, and user-identified domain documents. Read
   representative code only when documents do not explain current behaviour.
2. Confirm the gate. Report and stop when one Feature Map would suffice.
3. Group observable behaviour into functional areas. Write each requirement
   once, in the area that owns it, without repeating brief prose.
4. For `write`, write or revise the document, then run the consistency check.

## Consistency Check

For `write` intent only, re-read the Product Brief, Roadmap, and every Feature
Map that cites a changed or removed requirement ID. Keep what the product must
do only here, and product meaning only in the brief. Report a Feature Map row
whose outcome no longer matches its cited requirements instead of editing the
row here. Fix stale IDs, names, and paths in this document.

## Completion

For `explore`, report the current understanding, assumptions, and next
questions. For `write`, report the file changed, requirement IDs added,
changed, or retired, affected Feature Map rows, unresolved decisions, and
validation performed. Stop without creating a Roadmap, Feature Map, or design.
