# Decision Altitude

An architecture baseline fails in one of two ways. Too thin, and the first
feature's plan decides everything by default. Too thick, and it becomes a design
document that is stale by the second feature and that nobody reads. This
document fixes the altitude.

## The test

> Would two different features need to agree on this?

Yes → baseline. No → the owning feature's `plan.md`.

Apply it to the actual roadmap, not to an imagined system. That is why an
approved roadmap is required before creating a new `full` or `lite` baseline;
`recover` and a targeted `amend` may instead start from repository or trigger
evidence.

## Decision table

| Candidate decision | Altitude | Why |
|---|---|---|
| Language and runtime | Baseline | Every feature |
| Web framework, HTTP server | Baseline | Every feature with an endpoint |
| Datastore and access layer | Baseline | Any feature that persists |
| Schema migration mechanism | Baseline | Features would otherwise conflict |
| AuthN and authZ model | Baseline | Every protected feature |
| Transaction and consistency boundary | Baseline | Cross-feature correctness |
| Offline and sync strategy | Baseline | Determines what features can promise |
| Background job and scheduling mechanism | Baseline | Shared infrastructure |
| Error taxonomy and retry policy | Baseline | Cross-feature contract |
| Logging, metrics, tracing approach | Baseline | Uniformity is the point |
| Config and secret handling | Baseline | Security boundary |
| Test strategy and required layers | Baseline | Definition of done |
| Deployment target and packaging | Baseline | Constrains everything |
| Module or layer boundaries and dependency direction | Baseline | The rule plans are checked against |
| API style between components | Baseline | Two components must agree |
| Internal shape of one feature's service | `plan.md` | One feature |
| Table columns for one feature's entity | `plan.md` | One feature, within the shared schema mechanism |
| Whether a handler batches writes | `plan.md` | Local performance choice |
| Endpoint paths and payloads for one feature | `plan.md` | Within the agreed API style |
| Class and function decomposition | `plan.md` | Implementation detail |
| Which specific test cases to write | `tasks.md` | Work item |
| Library used by exactly one feature | `plan.md`, reported | Becomes baseline only on second use |

The last row matters. A library adopted by one feature is a local decision. The
moment a second feature reaches for it, it is a cross-feature decision and needs
to be promoted to the baseline — through `amend` mode, not by accretion.

## One-way and two-way doors

Classify every in-scope decision before spending effort on it.

**One-way door** — reversing it means rewriting features that already shipped, or
migrating data, or breaking an external contract. Examples: datastore engine,
consistency model, auth model, tenancy model, deployment target, public API
style.

Treat these properly: options with trade-offs and rejected alternatives; in
`full` mode, record the accepted result in an ADR. Use a spike when the evidence
is thin.

**Two-way door** — reversing it is a contained refactor. Examples: logging
library, HTTP client, test runner, formatter, most utility dependencies.

Decide these directly with one line of rationale. Do not hold a workshop about a
decision you can reverse in an afternoon; the cost of deliberation exceeds the
cost of being wrong.

The common failure is treating every decision as one-way, which stalls the
project, or treating a one-way decision as two-way, which is discovered at
feature six.

## Deferred decisions

A decision you cannot make from current evidence is not a decision to guess at.
Record it with:

- what is undecided;
- why it cannot be decided yet;
- the **trigger** — the feature, scale point, or fact that forces it;
- what the system must avoid doing in the meantime to keep the option open.

That last line is the valuable one. "Do not let feature code call the queue
directly; go through the outbox interface" is what keeps a deferred decision
genuinely deferred rather than accidentally made.

## Spikes

When a one-way door depends on an unknown, name a spike rather than deciding:

- the question, stated so an answer would settle it;
- a time box;
- the feature that blocks on the answer;
- what will be built, and explicitly that it will be thrown away.

Product uncertainty returns to an explicitly authorized discovery or amendment
operation; technical uncertainty gets a spike.

## What never belongs in the baseline

- Product requirements. They live in the PRD and are cited here by `PR-###`.
- Engineering values that survive a rewrite. They live in the constitution.
- Feature behavior, flows, or acceptance criteria.
- Class diagrams, function signatures, database column lists.
- Screen layout. That is `doc/ui-structure.md` and feature wireframes.
- Task breakdowns.
- Pinned versions without a reason to pin. `PostgreSQL 16` is a decision when the
  major version matters; `axios 1.6.7` in a baseline is noise.

## Size limits

- `lite` mode: one page. If it does not fit, the project failed the sizing test.
- `full` mode: the baseline document stays under roughly 200 lines; depth lives
  in ADRs, which are individually small and individually supersedable.
- More than about a dozen ADRs before the first feature ships usually means
  decisions are being made ahead of evidence. Convert the excess into deferred
  decisions.
