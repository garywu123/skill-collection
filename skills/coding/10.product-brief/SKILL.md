---
name: product-brief
description: Create or revise one concise Product Brief that defines product purpose, users, core flows, and MVP boundary. Use when starting a product, changing its direction, or simplifying existing discovery and requirements documents. Do not use for feature design or implementation planning.
---

# Product Brief

Create the shortest document that gives later work a stable product direction.
Discovery and requirements are one conversation and one artifact.

## Output

Create or update `docs/product-brief.md` from
[the template](assets/product-brief.template.md), unless the project already
has one clear canonical brief.

Keep the whole brief under 40 lines. Include only:

- the product purpose;
- target users and their main need;
- the main end-to-end flows;
- what is inside and outside the MVP; and
- open questions that could change product direction.

Do not add requirement IDs, approval fields, interview history, architecture,
feature design, or delivery process. Use plain language and short sentences.

## Workflow

1. Read repository guidance and existing product documents. For an existing
   product, inspect representative code only when documents do not explain what
   the product currently does.
2. Ask only questions whose answers would change purpose, users, core flows, or
   MVP scope. Otherwise state a small assumption and continue.
3. Write the brief. Prefer replacing duplicated discovery/PRD prose with links
   or removing it when the user has authorized consolidation.
4. Run the consistency check below.

## Consistency Check

Before finishing, re-read the feature map and any feature plan whose scope this
brief changed. Keep purpose, users, flows, and MVP boundary only here; replace
repeated product prose downstream with a link. Fix stale names, scope, and paths
in the same task; ask the user only when the conflict needs a product decision.

Report the file changed, assumptions, consistency edits, unresolved decisions,
and validation performed.