---
name: ui-prototype
description: Build or extend one executable fake-data UI prototype from approved product UI structure and feature wireframes. Use when a user explicitly requests a clickable prototype, demo mode, or simulated feature UI; do not use for canonical UX decisions, production backend logic, or feature acceptance.
---

# UI Prototype

Create a reviewable executable UI that exercises approved flows and states with
deterministic fake data. Preserve it across feature iterations without treating
prototype behavior as product truth or completed production implementation.

## Authority and boundaries

- Require an explicit current request to bootstrap or extend a prototype and an
  explicit product, deployable, or feature scope. Never start from roadmap state
  alone.
- Consume approved requirements, roadmap entries, UI structure, and feature
  wireframes. Do not silently amend them or resolve a contradiction in code.
- Implement presentation behavior, navigation, local interaction state, and
  deterministic simulations only. Do not implement real network, protocol,
  database, authentication, billing, or other backend behavior.
- Do not claim production readiness, feature acceptance, backend feasibility,
  accessibility certification, performance, or native-device fidelity that was
  not tested.
- Record prototype state only in the prototype manifest. Never advance lifecycle
  state or invoke another Skill.

Stop when a source conflict or unresolved decision changes a screen, transition,
safety rule, or operator-visible result. Report the exact gap instead of
inventing behavior.

## Source contract

Read the smallest authoritative slice needed for the requested operation.

| Operation | Required input | Read |
|---|---|---|
| `bootstrap` | Approved product requirements, roadmap, product UI structure, target platform, and target repository | Experience constraints, product shell, screen inventory, target stack evidence, and requested initial feature IDs |
| `feature` | Existing prototype manifest, one approved roadmap feature, approved product UI structure, and approved feature wireframes | Manifest, the feature entry, its owned/bound requirement IDs, referenced shared patterns, wireframes, and affected source files |
| `revise` | Existing prototype manifest and explicit reviewed feedback or an approved changed source | Only the feedback or changed anchors, impacted scenarios, and affected source files |

If a source is not approved, proceed only when the user explicitly requests an
exploratory draft. Mark the manifest and visible prototype as `exploratory`, cite
the unapproved source status, and never present the result as canonical.

Do not load every feature document for a feature operation. If an input exceeds
8 KiB, extract the cited headings or stable IDs first. If the required slice is
still unclear, report the routing gap and stop.

## Product and app boundary

Use one prototype app per product UI shell or deployable by default. Add features
as routes or modules inside that app so navigation, components, terminology, and
visual rules stay consistent.

Create a separate app only when one of these is true:

- the target platform or interaction shell is different;
- the user explicitly wants isolated competing concepts;
- the work is a disposable spike with no planned feature growth; or
- the existing prototype cannot host the feature without misrepresenting the
  approved product structure.

Represent alternate outcomes as named data scenarios, not duplicate apps.

## Stack selection

Prefer the existing target UI stack. Do not replatform an established prototype.

1. When the production platform and UI stack are decided and prototype UI is
   expected to survive, use that UI stack with fake ports/adapters. For Android,
   default to Kotlin, Jetpack Compose, production navigation, and a `demo` build
   variant or equivalent dependency-injection boundary.
2. When the prototype is for early portable interaction review or the production
   stack is undecided, default to React, TypeScript, and Vite. Do not add SSR, a
   server framework, Redux, Storybook, or a large component framework without a
   demonstrated requirement.
3. Use plain HTML, CSS, and JavaScript only for a disposable prototype of at most
   three simple screens with no expected feature growth.
4. Use Vue, another framework, or an existing design system when the target
   repository or team has already chosen it.

Record the choice and reason in `prototype.yaml`. Optimize total lifecycle cost,
not just the first generated screen.

## Prototype architecture

Keep the dependency direction small and replaceable:

```text
screens/components -> presentation state -> ports -> fake adapters/scenarios
```

- UI code depends on stable presentation models or ports, never directly on fake
  fixture files.
- Fake adapters are deterministic and contain only enough delay, success, empty,
  offline, and failure behavior to exercise approved states.
- A scenario registry gives every reviewable state a stable ID and one repeatable
  way to launch it. Prefer a debug menu, launch argument, or URL query parameter.
- Shared shell, tokens, and components live once at product level. Feature code
  owns feature-specific screens, presentation state, and scenarios.
- In a production repository, keep fakes out of release builds and preserve the
  target architecture boundaries. Prototype shortcuts must not leak into domain
  or infrastructure code.
- Keep dependencies and abstraction proportional to the current features. Do not
  recreate backend validation or protocol rules merely to make the demo appear
  realistic.

## Persistent manifest

Create or update `prototype/prototype.yaml`, unless the user specifies another
canonical path. Start from
[the prototype manifest template](assets/prototype-manifest.template.yaml).

The manifest is the next run's routing index. Keep it concise and record:

- product, prototype mode, target platform, stack, and entry command;
- authoritative source paths and approval status;
- shared shell and scenario-launch mechanism;
- each implemented feature, routes/screens, scenario IDs, and source anchors;
- validation commands and latest results; and
- unresolved gaps or intentional prototype-only deviations.

Do not duplicate full requirements, wireframes, prompts, or code summaries in
the manifest.

## Workflow

1. Inspect repository guidance, existing UI stack, build commands, and the
   prototype manifest when present. Preserve unrelated work.
2. Resolve `bootstrap`, `feature`, or `revise`, the target feature IDs, source
   approval status, app boundary, and stack using the contracts above.
3. Map each requested acceptance path and wireframe state to a stable scenario
   ID. Include applicable initial, loading, empty, success, offline, validation,
   failure, confirmation, and retry states; mark non-applicable states explicitly
   in the manifest rather than fabricating them.
4. For `bootstrap`, create the smallest runnable shell, shared visual tokens,
   scenario launcher, and one requested end-to-end path. For `feature` or
   `revise`, reuse them and touch only affected modules.
5. Implement every visible action in scope. Simulate its result through the fake
   boundary; do not leave inert controls that look complete.
6. Add focused deterministic tests for navigation, safeguards, and state
   transitions. Prefer repository-native tooling and a few high-value flows over
   broad snapshot output.
7. Run formatting, type checks, focused tests, and a production or demo build as
   applicable. Launch every changed scenario and visually inspect it at the
   approved viewport or device size. Capture screenshots when repository tooling
   supports stable artifacts.
8. Update the manifest after validation with actual commands and results.

## Token and cost discipline

- Bootstrap shared shell and architecture once; implement one bounded feature per
  later run.
- On later runs, open the manifest first, then only the named feature sources and
  affected code. Do not reread the full PRD, roadmap, or app tree.
- Reuse stable scenario schemas, components, and test helpers. Avoid copying
  prompts, requirements, or whole screens into each feature folder.
- Prefer deterministic commands for inventory, validation, and screenshots over
  asking the model to reason about generated summaries.
- Use a cost-balanced model for bounded feature work after the scaffold is stable.
  Escalate model capability for initial architecture, cross-feature redesign,
  ambiguous source reconciliation, difficult debugging, or independent review.
- Compare model and reasoning settings on representative features using pass rate,
  repair turns, total tokens, latency, and cost. A cheaper first pass is not a
  saving when it creates repeated repair work.

## Validation and report

Before reporting, verify:

- every implemented route, state, label, and safeguard traces to a source anchor
  or is visibly marked as a prototype-only assumption;
- every in-scope control responds and every named scenario is reproducible;
- no fake or debug implementation is reachable from a production release build;
- the app boundary and stack follow the selection rules;
- changed scenarios were visually inspected at the target size;
- tests and build checks report their actual result; and
- `prototype.yaml` matches the executable prototype.

Report the operation, app and manifest paths, stack choice, implemented feature
and scenario IDs, commands run, visual inspection result, deviations, unresolved
gaps, and the next human review action. Stop without implementing backend logic,
changing canonical product artifacts, or declaring the feature complete.
