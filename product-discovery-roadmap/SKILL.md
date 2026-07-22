---
name: product-discovery-roadmap
description: "Use when the user explicitly wants to clarify a product idea, turn spoken requirements into a product requirements document, or decompose a broad product into an ordered feature roadmap before Spec Kit specify."
argument-hint: "Product idea, requirements document path, or phase to resume"
user-invocable: true
disable-model-invocation: true
---

# Product Discovery Roadmap

## Purpose

Act as a product discovery consultant before Spec Kit delivery. Turn uncertain
product intent into an approved product requirements document and then into
small, ordered, independently verifiable feature handoffs.

This skill is manually invoked. It MUST NOT write code, choose a technical
architecture, run Spec Kit commands, create implementation tasks, commit files,
or hand off to an implementation-planning skill.

## Default Artifacts

- Discovery notes: `doc/product-discovery-notes.md`
- Product requirements: `doc/general-product-requirement.md`
- Feature roadmap: `doc/feature-roadmap.md`

Honor paths supplied by the user. If an artifact exists, update it rather than
creating a competing source of truth. Resolve the canonical artifact by explicit
user direction first, then an exact default-path match, then the only nearby file
whose title and content identify it as that artifact. If multiple candidates
remain, ask the user to choose.

## Workflow

Track these phases and resume from the first incomplete phase:

1. Discover, challenge, and record product requirements.
2. Review and approve the discovery record.
3. Write and approve the product requirements document.
4. Create and approve the Spec Kit feature roadmap.

Never silently continue across an approval gate.

### Phase 1: Discover

1. Read the existing product document and relevant nearby context first.
2. Create or resume the canonical discovery notes using
   [discovery notes template](./assets/discovery-notes-template.md). Treat it as
   the chronological evidence trail, not as a draft PRD.
3. Summarize the current understanding under:
   - users and problems;
   - desired outcomes;
   - product scope and non-goals;
   - business rules and safety constraints;
   - assumptions, contradictions, and unanswered decisions.
4. Build a decision tree. Ask only questions whose answers can change product
   scope, behavior, priority, safety, or success criteria.
5. Ask one decision round at a time. Include at most five independent questions,
   number them, and provide a recommended answer with its consequence. Do not ask
   for facts that can be learned from the workspace or authoritative sources.
6. After every answered round, append a dated entry that preserves:
   - the questions and the user's answers;
   - decisions and rationale;
   - rejected alternatives;
   - assumptions, contradictions, and open questions;
   - which prior conclusions changed.
   Present the concise recorded interpretation and allow the user to correct it
   before relying on it in later rounds. Do not silently rewrite earlier entries;
   supersede them with a new entry so the history remains reviewable.
7. Recompute the unanswered frontier after each response. Do not ask downstream
   questions whose prerequisites are unresolved.
8. Finish only when remaining uncertainty can be recorded as a bounded assumption
   without materially changing the product.

Keep the conversation at product level. API shape, classes, libraries, storage
layout, and framework choices belong to later planning.

### Phase 2: Approve Discovery

Before drafting product requirements:

1. Consolidate the current users, outcomes, scope, non-goals, rules, assumptions,
   unresolved questions, and superseded decisions in the discovery notes.
2. Check that every material interview answer is represented and contradictions
   are either resolved or explicitly open.
3. Ask the user to approve the discovery record as complete enough to draft the
   product requirements.

Do not draft or substantially rewrite the PRD before this approval. The discovery
notes remain evidence and history; the PRD becomes the concise approved product
source of truth.

### Phase 3: Product Requirements

Write the discovery understanding using
[product requirements template](./assets/product-requirements-template.md).

Requirements MUST be:

- stated from the user or business perspective;
- testable without prescribing implementation;
- separated into confirmed requirements, assumptions, and open questions;
- explicit about non-goals and destructive-operation safeguards;
- traceable with stable `PR-###` identifiers.

Record product-level user experience requirements when they affect outcomes or
apply across features, including key journeys, required channels or device
contexts, accessibility expectations, terminology, feedback and confirmation
rules, and safeguards for destructive actions. Keep them technology-independent
and testable.

Do not prescribe screen layouts, component trees, visual styling, animation,
pixel measurements, or every transient UI state in the product requirements.
Capture those details in the specification and clarification cycle for the
feature that owns the interaction. A mandated brand standard or legally required
interaction may be referenced in the PRD as a cross-cutting constraint.

Self-review for placeholders, contradictions, ambiguous terms, unbounded scope,
and accidental implementation details. Fix those issues, then ask the user to
approve the product requirements document before Phase 4.

### Phase 4: Feature Roadmap

Read the approved product requirements and create the roadmap using
[feature roadmap template](./assets/feature-roadmap-template.md).

Decompose by vertical user capability, not by technical layer. A valid feature:

- produces an observable user outcome;
- can be specified and accepted independently;
- has explicit scope and non-goals;
- is small enough for one `speckit-specify` invocation and one plan/task cycle;
- declares prerequisite features without circular dependencies;
- does not duplicate ownership of a product requirement.

Shared foundations are allowed only when they produce an independently
demonstrable capability. Cross-cutting rules such as data-loss prevention remain
in the product requirements and are referenced by every affected feature. Give
each capability requirement one primary owning feature. Cross-cutting rules may
be referenced by multiple features without creating duplicate ownership; mark
them as `Applies` rather than `Owns` in the coverage matrix.

Split a candidate feature when it contains multiple user outcomes that can be
accepted or released separately, when one part can fail without invalidating the
other, or when its plan would require multiple largely independent work streams.
Do not split merely because work touches different technical components.

For each feature, provide a ready-to-use handoff prompt for `speckit-specify`.
Call out product-level experience requirements that the feature must refine into
concrete user flows, states, edge cases, and acceptance scenarios during
`speckit-specify` and `speckit-clarify`.
Do not invoke it. End by asking the user to approve feature boundaries and order.

Maintain the roadmap as an evidence-backed delivery checklist:

- include one summary checkbox for every feature and the same checkbox in its
   detailed entry;
- use the statuses `Proposed`, `Planned`, `Specified`, `In Progress`, `Blocked`,
   `Ready for Acceptance`, `Done`, `Deferred`, and `Cancelled`;
- keep the summary checkbox, detailed checkbox, and delivery status consistent;
- preserve existing checkbox states and delivery evidence when regenerating or
   revising the roadmap;
- update status as delivery progresses only from user-provided or workspace
   evidence, and cite the feature spec plus acceptance evidence where available;
- mark a checkbox `[x]` only when the feature's independent acceptance has passed
   and set its status to `Done` at the same time;
- never infer completion merely because a spec, plan, tasks file, code change,
   build, or individual test exists;
- do not check `Deferred` or `Cancelled` features.

The roadmap tracks product feature completion. Implementation task completion
remains in each feature's `tasks.md`; do not duplicate task-level checklists here.

## Roadmap Validation

Before presenting the roadmap, verify:

- every capability `PR-###` has exactly one owner or is explicitly deferred;
- every cross-cutting `PR-###` names all affected features using `Applies`;
- duplicate primary ownership is justified;
- no feature depends on a later feature;
- each feature has an independent acceptance demonstration;
- MVP and deferred boundaries are explicit;
- feature names describe user capability rather than components;
- the dependency diagram agrees with the feature entries;
- every feature appears exactly once in the delivery checklist;
- checked features have status `Done` and cited acceptance evidence;
- unchecked features do not have status `Done`;
- summary and detailed checkboxes agree;
- handoff prompts cite both the product document and roadmap entry.

If validation fails, revise the roadmap before asking for approval.

## Completion

Report:

- discovery notes path and approval status;
- product requirements path and approval status;
- roadmap path and approval status;
- feature count, MVP boundary, and first recommended feature;
- unresolved assumptions or deferred requirements;
- the exact handoff prompt for the first feature.

Stop there. The user decides whether and when to run `speckit-specify`.