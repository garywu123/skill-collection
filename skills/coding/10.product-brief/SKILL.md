---
name: product-brief
description: Explore, create, or revise one concise Product Brief that defines product purpose, users, core flows, and MVP boundary. Use when the user wants to clarify or record product direction in natural language, including a new product or direction change. Explore in chat; write only when the user clearly asks to create, finalize, or update the brief. Do not use for feature design or implementation planning.
---

# Product Brief

Clarify product direction in conversation and persist it only when requested.
When written, create the shortest document that gives later work a stable
direction.

## Intent

Infer the intent from natural language; the user does not need to name this
Skill explicitly.

- `explore`: Discuss purpose, users, core flows, and MVP scope in chat. Ask one
  to three high-value questions per round and briefly summarize the current
  understanding. Do not create or update a file.
- `write`: Create, finalize, or update the brief when the user clearly requests
  it. Ask first only when a missing answer would materially change product
  direction; otherwise state a small assumption and write.

Treat a request to save or checkpoint the current exploration as `write`, but
persist only established facts. Put unresolved decisions that could change
purpose, users, core flows, or MVP scope under `## Open Questions`; never invent
an answer to complete the checkpoint.

Treat a request to resume or continue an exploration as `explore`: read any
existing brief for context, then continue in chat unless the user clearly asks
to update the file.

Do not treat conversation length, repository state, or an existing draft as a
request to write.

## Output

For `write` intent, create or update `docs/product-brief.md` from
[the template](assets/product-brief.template.md), unless the project already
has one clear canonical brief.

Keep the whole brief under 40 lines. Include only:

- the product purpose;
- target users and their main need;
- the main end-to-end flows;
- what is inside and outside the MVP; and
- open questions that could change product direction.

Do not add Domain Words, a glossary, requirement IDs, approval fields,
interview history, architecture, feature design, or delivery process. Use plain
language and short sentences.

## Workflow

1. Read repository guidance and existing product documents. Read domain
   documents only when the user identifies them; they are optional, read-only
   inputs. Never create `docs/domain/`, modify those sources, or edit
   `AGENTS.md` as part of this Skill. For an existing product, inspect
   representative code only when documents do not explain current behavior.
2. Follow the inferred intent. For `explore`, remain in chat and continue in
   small question batches. For `write`, resolve only material gaps and write the
   brief.
3. For `write`, prefer replacing duplicated discovery/PRD prose with links or
   removing it only when the user has authorized consolidation.
4. After writing, run the consistency check below.

## Consistency Check

For `write` intent only, re-read the feature map and any Storyboard or Feature
Plan whose scope this brief changed. Keep purpose, users, flows, and MVP boundary
only here; replace repeated product prose downstream with a link. Fix stale
names, scope, and paths in the same task. If changed product direction
invalidates visible states or planned behavior, report the affected Storyboard
or Plan for revision instead of redesigning it here.

## Completion

For `explore`, report the current understanding, assumptions, and next
high-value questions. For `write`, report the file changed, assumptions,
consistency edits, unresolved decisions, and validation performed.
