---
name: product-brief
description: Explore, create, revise, or review one concise Product Brief that defines product purpose, users, core flows, MVP boundary, and confirmed product-level constraints. Invoke explicitly, by name, to clarify or record product direction, including a new product or direction change, or to check a Brief against the user's authorized interview evidence. Explore in chat; write only when the user clearly asks to create, finalize, or update the brief. Do not use for numbered requirements, technical design, feature design, or implementation planning.
disable-model-invocation: true
---

# Product Brief

Clarify product direction in conversation and persist it only when requested.
When written, create the shortest document that gives later work a stable
direction.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `explore`: Discuss purpose, users, core flows, and MVP scope in chat. Ask one
  to three high-value questions per round and briefly summarize the current
  understanding. Do not create or update a file.
- `write`: Create, finalize, or update the brief when the user clearly requests
  it. Ask first only when a missing answer would materially change product
  direction; otherwise state a small assumption and write.
- `review`: Check an existing or draft brief against the user's authorized
  discovery evidence and the rules below. Report findings with locations and
  the evidence for each; do not edit any file or run the write procedure.

Treat a request to save or checkpoint the current exploration as `write`, but
persist only established facts. Put unresolved decisions that could change
purpose, users, core flows, MVP scope, or a product constraint under
`## Open Questions`; never invent an answer to complete the checkpoint.

Treat a request to resume or continue an exploration as `explore`: read any
existing brief for context, then continue in chat unless the user clearly asks
to update the file.

Do not treat conversation length, repository state, or an existing draft as a
request to write.

## Discovery Evidence

Discovery evidence is the current conversation plus interview notes or
transcripts that the user supplies or names. Use only that
authorized evidence; never invent a transcript, quotation, or source locator.

- Distinguish the user's statements from model suggestions. A suggestion the
  user did not accept is not a need.
- Distinguish confirmed decisions from candidates, and the latest decision from
  a statement it supersedes. Record only the latest confirmed decision; keep a
  material candidate as an open question.
- Cite a source location, such as a file and line, turn, or timestamp, or a
  short exact quotation, when the evidence provides one. Otherwise say the
  source is unlocated.
- Work from relevant notes rather than a full transcript. For a disputed or
  high-impact claim, retrieve the original passage. A summary written by the
  author of the draft is not, alone, independent evidence of user intent.
- In `review`, report a suggestion recorded as a decision, a superseded
  statement still present, a confirmed need or constraint that is missing, and
  a claim without supporting evidence.

Save discovery notes only when the user asks or an authorized discovery
workflow includes them, at the path it names. Keep short excerpts with source
locations, never bulk-copy conversation content, and leave sensitive content
out of version control.

## Output

For `write` intent, create or update `docs/product-brief.md` from
[the template](assets/product-brief.template.md), unless the project already
has one clear canonical brief.

Keep the brief short; about 40 lines is a readability signal for repetition or
detail that belongs elsewhere, not a gate. Include only:

- the product purpose;
- target users and their main need;
- the main end-to-end flows;
- what is inside and outside the MVP;
- confirmed product-level constraints; and
- open questions that could change product direction.

A product-level constraint is a memory, latency, capacity, availability, or
similar limit that the user or an authoritative source has set for the product.
Write each as subject, operating conditions, required property or budget, and
source. This brief owns such constraints when no Functional Specification
exists; when one exists, report them for `functional-spec` instead. Never set a
number on the user's behalf: an unset budget is an open question.

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
   brief. For `review`, compare the brief with the discovery evidence and
   report findings.
3. For `write`, prefer replacing duplicated discovery/PRD prose with links or
   removing it only when the user has authorized consolidation.
4. After writing, run the consistency check below.

## Consistency Check

For `write` intent only, re-read the Functional Specification when present,
every Feature Map, the Architecture Design and Testing Strategy when they cite
a changed constraint, and any Storyboard or Feature Plan whose scope this brief
changed. Keep purpose, users, flows, and MVP boundary only here, and replace
repeated product prose downstream with a link. Keep product constraints here
only when no Functional Specification exists. When one exists, it owns them:
never remove or rewrite its requirements from this Skill; link them from the
brief, and report any constraint still recorded here for `functional-spec`,
moving it only when the user authorizes that consolidation. Fix stale names,
scope, and paths in the same task. If changed product direction or a changed
constraint invalidates visible states, design decisions, or planned behavior,
report the affected document and its status as stale for downstream revision
instead of redesigning it here.

## Completion

For `explore`, report the current understanding, assumptions, and next
high-value questions. For `write`, report the file changed, assumptions,
consistency edits, unresolved decisions, and validation performed. For
`review`, report findings only.
