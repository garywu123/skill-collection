---
name: ui-prototype
description: Build or extend one executable fake-data UI prototype host with a shared product frame and directly launchable, isolated feature demos. Use when a user explicitly requests a clickable prototype, demo mode, or simulated feature UI; do not use for canonical UX decisions, production backend logic, or feature acceptance.
---

# UI Prototype

Create a reviewable executable UI with a shared product frame and independently
launchable feature demos backed by deterministic fake data. Optimize for direct
feature review rather than replaying a complete app journey. Preserve the host
across feature iterations without treating prototype behavior as product truth
or completed production implementation.

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
| `bootstrap` | Approved product requirements, roadmap, product UI structure, target platform, and target repository | Experience constraints, product shell, screen inventory, target stack evidence, and the requested initial feature ID |
| `feature` | Existing prototype manifest, one approved roadmap feature, approved product UI structure, and approved feature wireframes | Manifest, the feature entry, its owned/bound requirement IDs, referenced shared patterns, wireframes, and affected source files |
| `revise` | Existing prototype manifest and explicit reviewed feedback or an approved changed source | Only the feedback or changed anchors, impacted scenarios, and affected source files |

If a source is not approved, proceed only when the user explicitly requests an
exploratory draft. Mark the manifest and visible prototype as `exploratory`, cite
the unapproved source status, and never present the result as canonical.

Do not load every feature document for a feature operation. If an input exceeds
8 KiB, extract the cited headings or stable IDs first. If the required slice is
still unclear, report the routing gap and stop.

## Prototype host and feature boundary

Use one prototype host per product UI shell or deployable by default. The host is
a review surface, not a requirement to simulate the complete app journey. Its
landing page lists the available feature demos and opens each one directly.

Give every feature demo its own route or equivalent deep link. Give every named
scenario a stable direct launch mechanism such as a query parameter, debug menu
selection, or launch argument. Do not require reviewers to traverse login,
menus, prerequisite features, or other production navigation before reaching
the feature under review. Establish necessary preconditions through the selected
fake scenario.

Keep each feature in an isolated module that owns its screens, presentation
state, feature-specific components, fixtures, and scenarios. A feature operation
touches only that module, its registry entry, and any shared frame element that
the feature strictly requires. Keep the shell, frame, tokens, terminology, and
components already used by multiple features at host level. Do not promote a
feature component to shared merely because it might be reused later.

Create a separate host only when one of these is true:

- the target platform or interaction shell is different;
- the user explicitly wants isolated competing concepts;
- the work is a disposable spike with no planned feature growth; or
- the existing prototype cannot host the feature without misrepresenting the
  approved product structure.

Represent alternate outcomes as named data scenarios, not duplicate hosts or
feature modules.

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
- A feature registry powers the demo landing page and records one direct entry
  for each implemented feature.
- A scenario registry gives every reviewable state a stable ID and one repeatable
  direct launch mechanism. Prefer a debug menu, launch argument, or URL query
  parameter.
- Shared shell, tokens, and components live once at product level. Feature code
  owns feature-specific screens, presentation state, components, fixtures, and
  scenarios.
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
- shared shell, demo index, feature registry, and scenario-launch mechanism;
- each implemented feature, direct entry, routes/screens, scenario IDs, and
  source anchors;
- validation commands and latest results; and
- unresolved gaps or intentional prototype-only deviations.

Do not duplicate full requirements, wireframes, prompts, or code summaries in
the manifest.

## Workflow

1. Inspect repository guidance, existing UI stack, build commands, and the
   prototype manifest when present. Preserve unrelated work.
2. Resolve `bootstrap`, `feature`, or `revise`, the target feature ID, source
   approval status, prototype-host boundary, and stack using the contracts above.
3. Map each requested acceptance path and wireframe state to a stable scenario
   ID. Include applicable initial, loading, empty, success, offline, validation,
   failure, confirmation, and retry states; mark non-applicable states explicitly
   in the manifest rather than fabricating them.
4. For `bootstrap`, create the smallest runnable host, shared product frame and
   visual tokens, demo index, feature registry, scenario launcher, and one
   requested feature demo. For `feature`, add or update exactly one named feature
   by default and give it a direct demo-index entry. For `revise`, reuse the host
   and touch only the affected feature module and strictly required shared code.
5. Implement every visible action in scope. Simulate its result through the fake
   boundary; do not leave inert controls that look complete.
6. Keep automated tests opt-in for a review-only prototype. Do not add unit,
   integration, end-to-end, or snapshot tests unless the user explicitly
   requests them or existing repository policy requires them for the touched
   files. If prototype code may survive into production or a failure risk seems
   high, recommend appropriate tests instead of adding them without
   authorization. Do not treat their absence as incomplete work.
7. Perform run-only validation by default: run the command needed to build or
   start the host, open the changed feature's direct entry, and confirm that its
   initial view renders without a startup or render-blocking error. Run existing
   mandatory repository checks when applicable, but do not introduce broader
   validation. Leave interaction quality, visual correctness, and product
   acceptance for human review unless the user explicitly requests additional
   inspection.
8. Update the manifest after validation with actual commands and results.

## Token and cost discipline

- Bootstrap the shared host once; implement one bounded, directly launchable
  feature demo per later run.
- On later runs, open the manifest first, then only the named feature sources and
  affected code. Do not reread the full PRD, roadmap, or app tree.
- Reuse stable scenario schemas, components, and launch helpers. Avoid copying
  prompts, requirements, or whole screens into each feature folder.
- Prefer deterministic commands for inventory, build, and launch checks over
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
- the demo index links directly to every implemented feature and the changed
  feature's initial entry is runnable;
- every in-scope control is wired to a presentation action or fake result; human
  review owns interaction quality and UX acceptance;
- no fake or debug implementation is reachable from a production release build;
- the prototype-host boundary and stack follow the selection rules;
- run-only or explicitly requested extended checks report their actual result;
- `prototype.yaml` matches the executable prototype.

Report the operation, host and manifest paths, stack choice, implemented feature
and scenario IDs, direct entry, commands run, smoke-open result, automated checks
not requested or run, deviations, unresolved gaps, and the next human review
action. Stop without implementing backend logic, changing canonical product
artifacts, or declaring the feature complete.
