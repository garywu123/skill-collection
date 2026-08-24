---
name: feature-storyboard
description: Create or revise one low-fidelity HTML Storyboard that shows a UI Feature's key screens, states, and transitions. Use when the user asks in natural language to visualize, wireframe, preview, or confirm a desktop or mobile interaction. Do not use for non-UI work, production UI, implementation planning, or high-fidelity prototypes.
---

# Feature Storyboard

Make one UI Feature visually reviewable without implementing it. This Skill is
optional and independently invocable; a Feature can proceed without it when its
visual behavior is already clear.

## Output

Create or update `docs/storyboards/<feature-id>-<slug>.html` from
[the template](assets/storyboard.template.html). Copy
[the shared stylesheet](assets/_storyboard.css) to
`docs/storyboards/_storyboard.css` the first time and reuse it unchanged for
later Features. Copy [the optional runtime](assets/_storyboard.js) to
`docs/storyboards/_storyboard.js` only for explicit click-through mode.
Do not overwrite existing shared assets unless the user asks to upgrade them.

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
- Use only the semantic primitives defined by the shared stylesheet. Do not add
  feature-specific CSS, inline styles, a UI framework, web fonts, a CDN, or a
  build step.
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

If understanding the interaction requires a data model, asynchronous behavior,
router, production component system, or custom script, stop and report that the
request has crossed into a prototype or implementation task.

## Workflow

1. Read repository guidance, the Product Brief, the target Feature Map row,
   relevant visual guidance, and any existing Storyboard for this Feature.
2. State the visual question being reviewed. Identify only the states and
   transitions needed to answer it, covering relevant happy and failure paths.
3. If more than six states seem necessary, recheck Feature scope and report the
   smallest useful narrowing or split; do not silently change the Feature Map.
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
this Feature. Keep visible states and transitions here; do not copy product
scope, shared architecture, implementation design, tests, or lifecycle status.
Fix stale IDs, names, and paths in this Storyboard. If its behavior conflicts
with an existing Plan, the Plan does not link this HTML, or its referenced
`S*`/`T*` IDs changed, report that the Plan needs revision instead of silently
editing it.

Report the Storyboard path, form factor, state and transition IDs, fixture
assumptions, rendering checks, and unresolved visual decisions. Stop without
creating a Feature Plan or implementation. Do not add approval metadata or a
separate approval gate. Pause when an unresolved visual decision would change
observable behavior; otherwise a coordinator may continue only when the user's
original request already covers another outcome.
