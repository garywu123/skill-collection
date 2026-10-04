---
name: feature-storyboard
description: Create or revise one low-fidelity HTML Storyboard that shows the key screens, states, and transitions of a UI Feature or of an early product question taken from a Product Brief or Functional Specification section before Features are mapped. Invoke explicitly, by name, to visualize, wireframe, preview, or confirm a desktop or mobile interaction. Do not use for non-UI work, production UI, confirming requirements, implementation planning, or high-fidelity prototypes.
disable-model-invocation: true
---

# Feature Storyboard

Make one UI Feature or early product question visually reviewable without
implementing it. This Skill is optional and independently invocable; work can
proceed without it when the visual behavior is already clear.

## Input

Use one of these sources:

- `feature`: a Feature Map row. Name a new file
  `docs/storyboards/<feature-id>-<slug>.html`, or revise the existing early
  Storyboard that already shows this behavior.
- `early`: before Feature mapping, a Product Brief, a Functional Specification
  section, or an explicit product question. Name the file with a stable topic
  slug, `docs/storyboards/<topic-slug>.html`, and never invent a Feature ID.
  Use the topic slug instead of a Feature ID in the title and eyebrow.

When a mapped Feature later covers an early Storyboard, keep its path, `S*`, and
`T*` IDs; that Feature's Plan links the same file. Rename it only when the user
asks, and then report every link to update.

A Storyboard illustrates; it does not confirm a requirement. Mark a state or
transition that shows unconfirmed behavior with `candidate` in its inventory
purpose or action cell, and list the unresolved question in the header. Report
it to the requirement owner instead of treating the sketch as a decision.

## Output

Create or update the file named above from
[the template](assets/storyboard.template.html). Copy
[the shared stylesheet](assets/_storyboard.css) to
`docs/storyboards/_storyboard.css` the first time and reuse it unchanged for
later Features. Copy [the optional runtime](assets/_storyboard.js) to
`docs/storyboards/_storyboard.js` only for explicit click-through mode.
Do not overwrite existing shared assets unless the user asks to upgrade them.
In the copied template, replace the `F01` title and eyebrow with the Feature ID
or topic slug.

The HTML is the source of truth and its browser rendering is the review view.
Export a PNG only when the user requests a shareable snapshot; do not maintain
HTML and PNG as two canonical artifacts.

Two to four states is normal and six is the maximum. Give every state a stable
ID such as `S1` or `S2-error` and every transition a stable ID such as `T1`.
Include a visible state and transition inventory so later work can reference the
behavior without reading CSS or JavaScript. Use representative, non-sensitive
fixture values only.

## Visual Contract

- Choose one generic `sb-phone` or `sb-desktop` shell unless the user needs both.
- Use CSS classes provided by `_storyboard.css` and interaction data hooks
  established by the template and optional runtime. Do not invent
  feature-specific classes or runtime hooks, or add inline styles, a UI
  framework, web fonts, a CDN, or a build step.
- Keep the design deliberately low fidelity: layout, hierarchy, controls,
  feedback, and decisions matter; brand polish and production animation do not.
- Default to a static board with every state visible. Links to `#S*` targets can
  express the flow without JavaScript.
- For explicit click-through review, add `data-interactive` to the board and
  load the shared runtime with `<script src="_storyboard.js" defer></script>`.
  It may only switch declared states and reset to the declared initial state.
  Do not write feature-specific JavaScript.
- Never use network calls, storage, random outcomes, real delays, authentication,
  domain calculations, or product validation logic. Show each deterministic
  outcome as a declared state instead.

Keep the template scaffold: `.sb-document` contains `.sb-document__header`,
`.sb-flow`, and `.sb-inventory`; the header may use `.sb-eyebrow`, and each
state is an `.sb-frame` inside `.sb-flow`. Preserve the scaffold classes and
inventory structure while changing labels, fixtures, and the number of state
frames. Inside each frame, use one of these public shells:

```text
phone:
article.sb-frame.sb-phone [id=S*, data-state, tabindex=-1]
├─ p.sb-frame__label
└─ .sb-device
   ├─ .sb-topbar
   └─ .sb-content
desktop:
article.sb-frame.sb-desktop [id=S*, data-state, tabindex=-1]
├─ p.sb-frame__label
└─ .sb-device
   ├─ .sb-topbar
   └─ .sb-window
      ├─ .sb-sidebar
      └─ .sb-content
```

Feature content belongs inside `.sb-content` or `.sb-sidebar`. Its public
primitives are layout (`.sb-stack`, `.sb-row`, `.sb-actions`), blocks
(`.sb-card`, `.sb-banner`, `.sb-dialog`, `.sb-list`, `.sb-list-item`), and muted
text (`.sb-muted`). For controls, `.sb-field` can contain a native `input` or
`select`; use `.sb-input` for the same control styling without that wrapper.
Use `.sb-button` and optional `.sb-button--primary` for actions. Use only the
established hooks that apply:
`data-storyboard`, `data-initial`, `data-state`, `data-active`, `data-go`, and
`data-transition`; click-through mode can also use `data-interactive`,
`data-reset`, and `data-interactive-control`. `data-active` marks only the
current or initial state and is managed by the optional runtime.

If understanding the interaction requires a data model, asynchronous behavior,
router, production component system, or custom script, stop and report that the
request has crossed into a prototype or implementation task.

## Workflow

1. Read repository guidance, the Product Brief, the target Feature Map row or
   the named Brief, Specification section, or product question, relevant
   visual guidance, and any existing Storyboard for this Feature or topic.
2. State the visual question being reviewed. Identify only the states and
   transitions needed to answer it, covering relevant happy and failure paths.
   Separate behavior the sources confirm from candidate behavior.
3. If more than six states seem necessary, recheck Feature or question scope
   and report the smallest useful narrowing or split; do not silently change
   the Feature Map or the product sources.
4. Reuse the shared assets, write the feature HTML, and render it in a browser.
   Check readable content, phone or desktop overflow, stable IDs, every declared
   transition target, and static behavior without JavaScript. If browser
   rendering is unavailable, run structural checks and report the unverified
   visual risk instead of claiming the rendering passed.
5. For click-through mode, also exercise each declared path and Reset. Fix only
   the Storyboard; do not implement product behavior.
6. Run the consistency check.

## Consistency Check

Before finishing, re-read the Feature Map row and any existing Feature Plan for
this Feature, or for `early`, the named Brief or Specification section and any
Plan that already links this file. Keep visible states and
transitions here; do not copy product scope, shared architecture,
implementation design, tests, or lifecycle status. Fix stale IDs, names, and
paths in this Storyboard. If its behavior conflicts with an existing Plan, the
Plan does not link this HTML, or its referenced `S*`/`T*` IDs changed, report
that the Plan needs revision instead of silently editing it. Report candidate
behavior for the Brief or Specification owner without editing those sources.

## Completion

Report the Storyboard path, form factor, source, state and transition IDs,
candidate behavior, fixture assumptions, rendering checks, and unresolved
visual decisions. Stop without creating a Feature ID, Map row, Feature Plan, or
implementation. Do not add approval metadata or a separate approval gate. Pause
when an unresolved visual decision would change observable behavior.
