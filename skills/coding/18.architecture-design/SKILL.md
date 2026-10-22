---
name: architecture-design
description: Explore, create, migrate, update, or review one project Architecture Design - the single owner of durable cross-feature components, boundaries, contracts, data ownership, dependency direction, deployment assumptions, technology choices, and technical quality constraints. Invoke explicitly, by name, to design a new system, record or change shared technical direction, move architecture out of a Feature Map or General Design, or review an architecture. Do not use for product requirements, Feature lists or delivery order, code-level style rules, test strategy, per-feature plans, or implementation.
disable-model-invocation: false
---

# Architecture Design

Maintain one durable technical design that every Feature Map, Plan, and Delivery
links instead of restating. Record only decisions the current project needs;
preserve sound existing choices and never invent business requirements.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `explore`: discuss options, constraints, and trade-offs in chat. Ask one to
  three questions per round, each saying how its answer changes the design. Do
  not write a file.
- `write`: create, update, or migrate the Architecture Design. Ask first only
  when a missing answer would change a boundary, contract, data owner, or
  accepted constraint; otherwise state a small assumption and write.
- `review`: check an existing design against its sources and the criteria
  below. Report findings with locations and the owner that must decide each
  one. Do not edit any file or run the write procedure.

## Output

Use the project's existing canonical architecture document. An existing General
Design such as `docs/design/<scope>-general-design.md` is that document; keep
its path rather than duplicating it. Otherwise create `docs/architecture.md`
from [the template](assets/architecture.template.md).

Keep the design easy to navigate: one main design that holds the module map,
dependency direction and cross-domain contracts, plus one document per domain
only when a domain needs substantial distinct guidance. A domain is a cohesive
area with its own contracts and data, such as a backend host, a UI, a map
model, or a motion/runtime engine; a language, technology, or file type alone,
such as YAML or a DTO set, is not a domain. The main design links every domain
document, and each cross-domain contract, value, and setting has exactly one
owner; every other document links to it instead of restating it.

Budget: about 2,500 words per document. When a document exceeds it, first
simplify: delete history, dated decision narratives, superseded options,
restated values, speculation, and detail the code already shows. Split the
remaining content by domain only when it still does not fit, and update the
main design's links in the same change. A language or subsystem boundary alone
does not justify a separate document, service, or microservice.

Write the current state only. A decision states the rule and, when it is not
obvious, its reason in one sentence and its requirement or source link; dates,
run IDs, review rounds, and how the decision was reached stay in git history.

`feature-delivery` promotes each durable decision of a finished Plan into the
owning section here. Accept it as a current rule, merge it with what the
section already says rather than appending, and apply the budget above.

Cover only what applies:

- application form and frontend, backend, library, service, or job boundaries;
- contracts between components and external systems, with owner and consumers;
- data ownership and the direction of dependencies;
- runtime, language, framework, datastore, and architecture-significant
  dependencies;
- deployment and operating assumptions; and
- technical quality constraints.

Write each material constraint as subject, operating conditions, required
property or budget, source, and verification reference. A product-level
memory, latency, capacity, or reliability requirement stays with its product
owner, such as the Product Brief or Functional Specification; this design links
it and translates it into technical decisions or budget allocation. How it is
measured belongs to the Testing Strategy. When no owner has set a budget, record
the open decision instead of choosing a number.

When feasibility is uncertain, state a bounded validation question, what
decision it informs, and the evidence that would settle it. Record it as an
open decision and report it for separately authorized validation; do not design
or run the experiment here. Consume supplied validation evidence and record the
resulting decision with its source.

This document holds no requirement wording, Feature list, delivery order,
status, test cases, class designs, code-level style rules, or speculative
infrastructure. Component and project boundaries and dependency direction
belong here; in-code module, file, and comment rules belong to `code-style`.

## Migration

When architecture currently lives in a Feature Map (`Technical Direction`,
`Architecture`, `Shared Constraints`) or in General Designs:

1. Adopt the existing canonical design or create the default path. Move each
   still-valid decision once; merge duplicates and visibly reconcile conflicts
   instead of silently choosing one.
2. In each Map that held migrated content, replace only the moved sections with
   one link to the design. Do not change Feature rows, IDs, outcomes,
   requirement assignments, dependencies, or statuses.
3. Update links in Roadmaps and Feature Plans whose only change is the moved
   location. A pure move does not change Feature status or results.

## Workflow

1. Read repository guidance, the Product Brief, the Functional Specification
   when present, existing designs and Maps, the Testing Strategy when present,
   relevant manifests, configuration, and representative code. Read domain
   sources only when the user identifies them.
2. If product direction is too unclear to design without inventing scope,
   report the missing decision and stop.
3. Follow the inferred intent. For `write`, choose the simplest design that
   supports current requirements and repository conventions. Keep a shared
   abstraction only when current behavior, a repository convention, an
   external boundary, or an observed constraint requires it.
4. For `write`, update the design and perform any migration, then run the
   consistency check. For `review`, report findings and stop.

## Review Criteria

- Every decision traces to a requirement, repository evidence, or a named
  external constraint; nothing invents business scope.
- Each contract, data set, and shared rule has exactly one owner, and no Map,
  General Design, or Plan duplicates this design.
- Constraints have the five parts above; unknown budgets are open decisions,
  not invented thresholds.
- The design is no larger than current needs and preserves sound existing
  choices.
- Each document is within its budget, describes the current state only, and is
  reachable from the main design; any split follows a domain, not a technology.

## Consistency Check

For `write` only, re-read the Brief, the Specification, the Roadmap, every
Feature Map, the Testing Strategy when present, and each Feature Plan or
Storyboard that links a changed section. Check each changed document's budget
with `scripts/Test-DocBudget.ps1 -Path <document> -MaxWords 2500` when the
project has the checker, and simplify or split as in Output. Fix stale names, paths, and links in
the design and in migrated Map sections. Keep architecture only here. Report,
without editing, each Map row and Plan whose recorded evidence a semantic
change invalidates, for `feature-map` and `feature-plan` to reconcile; report
a measurement need for `testing-strategy`, and, after a semantic change or a
created, moved, renamed, split, or migrated design path, that an
instruction-impact assessment by `coding-agent-instructions` is needed; do not
edit instruction files here.

## Completion

For `explore`, report the current understanding, options, and next questions.
For `write`, report files changed, decisions added or changed, migrated
sections, open decisions and validation questions, affected rows and Plans,
and validation performed. For `review`, report findings only. Stop without
editing Maps beyond migration, Plans, tests, or code.
