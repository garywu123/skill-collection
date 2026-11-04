---
name: simplification-review
description: Find what an existing repository's code and documents can simplify, judged against the business they serve. Surveys the repository, interviews the user about business scale, precision, trust boundaries and other constraints, records confirmed answers, writes one review plan of modules and cross-module chains, then reviews one batch per invocation (cross-module first, then modules), asking batch-specific questions and writing one findings document per batch. Invoke explicitly, by name, to plan or run a simplification, over-engineering, proportionality, or model-and-structure review. Do not use to change code (selected items go to feature-plan or feature-delivery), for diff code review, bug hunting, or code-style audits.
disable-model-invocation: true
---

# Simplification Review

Find complexity that does not serve the business, explain it to the user in
plain language, and record decisions as findings. Never edit product code or
tests. The user decides; selected items are executed later by `feature-plan`
or `feature-delivery`. Selected items of one batch that change the same rule or
cross several Features go into one `feature-plan` Change Plan, not one Plan per
Feature.

Use the strongest available model and reasoning effort. Run every interview in
the interactive session with the user. A non-interactive worker may draft a
batch only after that batch's questions are answered; never invent answers.

## Stages

One invocation completes one stage or one batch, then stops, unless the user
authorizes more. On resume, read the plan's current position and continue.

| Stage | Output | Stop |
|---|---|---|
| 0. Survey and business interview | Plan file with profile, answers and module preview; product constraints recorded in their owner | After the user approves the recorded text |
| 1. Review plan | Batches added to `docs/reviews/00.review-plan.md` | After the user approves batches and order |
| 2. Cross-module batch | `docs/reviews/<NN>.<slug>.md` | After `decide` items are explained and answers recorded |
| 3. Module batch, one per invocation | `docs/reviews/<NN>.<slug>.md` | Same |
| 4. Close | Review documents deleted | After the report |

The review folder is `docs/reviews/` unless the project already has a review
location. Name a batch file after its ID: batch R20 writes `20.<slug>.md`. Start from [the plan template](assets/review-plan.md) and
[the findings template](assets/findings.md).

## Interview rules

Interview at the start of Stage 0 and of every batch, but ask only what is not
yet recorded or what this batch's scope changes. Reuse recorded answers without
reconfirming them; with nothing open, say so and proceed.

- Ask in rounds of up to five related questions. Follow up on answers.
- For each question give, briefly: what it means in plain words; one concrete
  scenario showing what the user would see change; your recommended answer
  from industry and world knowledge, with the reason.
- Ask first what decides the most items: consumers, accuracy, input ranges,
  trust boundary and scale. A question that matters to one module waits for
  that module's batch.
- New evidence or a new answer that contradicts a recorded one is a decision
  for the user.
- There is no question limit: ask everything that changes a judgment, and
  nothing that does not. Stop when every quantity or policy the next stage
  judges has an answer or is explicitly left open.
- Prefer numbers with units. "Unknown" is a valid answer; record it as open.
- Explain in chat; documents record only each question and its answer. If the
  user cannot be reached, stop after listing the questions.
- Distinguish what must stay exact (identity, order, exactly-once, money,
  security) from quantities that only need to be close enough.

## Stage 0: survey and business interview

1. Survey cheaply: read `README`, `AGENTS.md` and the product brief; for long
   documents read headings, then only sections on purpose, scale, constraints
   and module boundaries. List entry points, module sizes and test layout. Do
   not read source wholesale.
2. Tell the user, in a few sentences, what the software is, who consumes its
   output, what "correct enough" means in this kind of product, and which
   qualities probably do not matter.
3. Interview. Cover what applies: purpose and consumers; scale (counts, sizes,
   ranges, durations); accuracy per quantity (position, angle, time, money);
   input trust boundary and realistic input ranges; consequence of wrong
   output; users and concurrency; persistence, sync, import/export, audit and
   retention needs; external integration fidelity; performance budgets; who
   tunes which settings and when; who reads the documents.
4. Write the plan file with the profile, a module preview from the survey, and
   each answer as it is confirmed, so an interrupted interview can resume.
5. After the user approves the text, record product-level constraints in their
   owner (the Functional Specification when one exists, otherwise the Product
   Brief), following that document's format and change process. When the owner
   has its own workflow or Skill, draft the change and name it instead. Other
   answers, such as document readers or setting tuners, stay in the plan. Do
   not record unconfirmed recommendations.

## Stage 1: review plan

1. Refine the module preview using dependency direction and any architecture
   document.
2. Identify cross-module chains: user scenarios that cross modules, named by
   entry points and callers, not directories.
3. Split work into batches of roughly 10,000 source lines, not counting
   comments and blank lines, plus their documents. Cross-module batches come
   first, because a decision there (for example an input envelope) can remove
   many module items. A module batch may start once the cross-module batches
   that touch it are reviewed; when the user orders it earlier, exclude the
   chains a later cross-module batch owns and say so.
4. Give every batch one table row. Write scope, draft questions and exclusions
   only for the next batch; later batches get notes when they start. Show the
   plan and stop for approval.

## Stages 2 and 3: batch review

1. Read the plan, the recorded constraints and the batch scope. Follow only
   the callers and writers each chain needs.
2. Ask the batch questions first, using the interview rules. Record answers in
   the batch document; product-level answers also go to Stage 0's location.
3. For each chain trace consumer, scenario, observable promise and mechanism.
   Compare each mechanism with the smallest alternative inside the confirmed
   constraints. Use [the patterns](references/patterns.md) as prompts, not as a
   quota. Review the batch's documents too.
4. Judge with these rules:
   - A `retain` needs a supported scenario inside the confirmed constraints.
     Inputs outside them never justify a mechanism; propose validating the
     constraint once at the trust boundary instead.
   - Existing contracts and tests show current policy, not necessity. When a
     contract is the only reason for complexity, raise a `decide` item.
   - A consumer is current code, a user flow, or a scheduled Roadmap or
     Feature Map item; an unscheduled future caller is not. Removing a
     delivered or planned Feature is a `decide` item that names the Feature.
   - Record a cross-module decision once, as a direction, in its batch. The
     module batch that owns the code records the details and links back.
   - Keep exact what the business needs exact.
   - Claim speed or memory gains only with a measurement.
   - "Nothing to simplify" is a valid result.
5. Write the findings document, keeping the template's sections and order.
   Item kinds: `simplify` (clear change, behavior kept), `decide` (needs the
   user: contract, precision or product change), `retain` (one sentence naming
   the scenario that needs it), and `defect` (found in passing).
6. Explain each `decide` item in chat: scenario, what each option changes, your
   recommendation. Record the decisions, update the plan's current position,
   write the notes for the next batch, and stop. After the last batch, when no
   item is left for execution, continue with Stage 4.

## Stage 4: close

Close the review when every checklist item in every batch is checked and every
Change Plan it requested is retired. `feature-delivery` closes it the same way
when it retires the Plan for the last open item. Confirm that each decision a later change
must respect already lives in its owner: product constraints from Stage 0,
rules promoted by `feature-delivery`. Write a `retain` or rejected item into an
owner document only when that document routes such rules and a later review
would otherwise raise it again. Then, only when their final contents are in a
known commit, delete the review plan and findings documents, and the review
folder when empty, and report that revision. Otherwise leave them and report
that they are uncommitted; closing never authorizes a commit.

## Document rules

Apply these to every document this Skill writes, and use them to review the
project's documents. Where a project rule requires what these rules remove,
such as evidence logs in plans, keep the project rule and raise a `decide`
item.

- Keep current facts only. Commands, test counts, review rounds, tool failures
  and history belong in commits and pull requests.
- Give each item one status, in one place: the checklist.
- Say what to do and why. No lists of non-claims or defensive disclaimers.
- Link upstream documents instead of restating them.
- Budgets: plan at most 1,000 words; batch document at most 2,000 words; item
  at most 150 words. When a batch does not fit, split the batch; do not
  compress into shorthand.

## Validation

Run the budget check on every document written, from this Skill's folder:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/Measure-ReviewDoc.ps1 -Path <review folder>
```

Fix every reported overrun. Run the project's documentation link check when
its `AGENTS.md` names one; report failures outside the review folder without
fixing them. Report the stage completed, documents written,
questions still open and the next stage.
