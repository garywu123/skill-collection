---
name: feature-storyboard
description: Create or revise low-fidelity HTML Storyboards for a UI Feature, or for an early product question taken from a Product Brief or Functional Specification section before Features are mapped, as clickable wireframe-app stories (one user story per file) that show the key screens, states, and transitions. Invoke explicitly, by name, to visualize, wireframe, preview, or confirm a desktop or mobile interaction. Do not use for non-UI work, production UI, confirming requirements, implementation planning, or high-fidelity prototypes.
disable-model-invocation: false
---

# Feature Storyboard

Make one UI Feature or early product question visually reviewable without
implementing it. This Skill is optional and independently invocable; work can
proceed without it when the visual behavior is already clear.

## Input

Use one of these sources:

- `feature`: a Feature Map row. Name a single-story file
  `docs/storyboards/<feature-id>-<slug>.html`, or revise the existing early
  Storyboard that already shows this behavior. A Feature with several stories
  uses `<feature-id>-<n>-<story-slug>.html` per story and keeps
  `<feature-id>-<slug>.html` as their index.
- `early`: before Feature mapping, a Product Brief, a Functional Specification
  section, or an explicit product question. Name the file with a stable topic
  slug, `docs/storyboards/<topic-slug>.html`, and never invent a Feature ID.
  Use the topic slug instead of a Feature ID in the title and eyebrow.

When a mapped Feature later covers an early Storyboard, keep its path, `S*`, and
`T*` IDs; that Feature's Plan links the same file, or the index for several
stories. Rename it only when the user asks, and then report every link to update.

A Storyboard illustrates; it does not confirm a requirement. Mark a state or
transition that shows unconfirmed behavior with `candidate` in its inventory
purpose or action cell, and list the unresolved question in the header. Report
it to the requirement owner instead of treating the sketch as a decision.

## Output

The default form is a story app: one file plays one complete user story, from
its starting screen to its goal, like the real app drawn as a wireframe. One
device is visible at a time; menus, dialogs, and feedback appear over the same
screen; the reviewer clicks the marked controls and can restart. Branches that
belong to the story, such as Cancel, a refusal, or a failure, stay in it and
return to its path. A different goal is a different story.

Create or update each story from [the template](assets/storyboard.template.html).
Copy [the shared stylesheet](assets/storyboard.css) and
[the runtime](assets/storyboard.js) to `docs/storyboards/` the first time and
reuse them unchanged. When the project has only the older `_storyboard.css` and
`_storyboard.js` copies, or copies that lack shell mounting and the overview,
replace them once from the Skill, point existing stories at the new names,
remove the old copies, and report it; do not edit them otherwise. Copy
[the default shell](assets/shell.js) once; the project then owns its copy. In
the copied template, replace the `F10` title, eyebrow, story number, and
placeholder fixtures.

A Feature with several stories also gets an index file with the template's
header but no device: a `.sb-list` linking every story with its goal and its
`S*` and `T*` ranges; each story keeps its own inventory. A
static board with every state visible is the exception, for comparing
alternatives of one screen side by side; omit `data-interactive` there.

The HTML is the source of truth and its browser rendering is the review view.
Export a PNG only when the user requests a shareable snapshot. For review on a
phone, and only on request, publish the story with `shell.js`, `storyboard.js`,
and `storyboard.css` as a private claude.ai Artifact link when the host offers
Artifact publishing; otherwise, or when the user declines, send one screenshot
per state opened through its `#S*` fragment. Never publish automatically. Do
not maintain a PNG, screenshot, or published copy as a second canonical
artifact.

A story usually has four to ten states; more than twelve, or a second goal,
means split it. A static board has two to four states and at most six. In a
story, give every state a stable ID `S<story>.<n>` such as `S2.3` and every
transition `T<story>.<n>`; a static board uses `S1`, `S2-error`, and `T1`.
Include a visible state and transition inventory so later work can reference the
behavior without reading CSS or JavaScript. Write each state's purpose cell as
`main task · primary action · entry/exit`, and say there why a step is an
overlay or a page change. End the inventory with a `Not drawn:` line that lists
each remaining scenario and its expected outcome in one line of text. Use the
smallest plausible non-sensitive dataset that exposes the layout decision under
review, such as enough rows to show scrolling or truncation when that is the
question; never `Item 1`.

## Visual Contract

- Choose one generic `sb-phone` or `sb-desktop` shell unless the user needs both.
- A story names its shell with `data-shell` on the board, loads
  `<script src="shell.js" defer></script>` before `storyboard.js`, and the
  runtime mounts that shell into every state. When the project's design
  document defines an app shell, the project's `shell.js` mirrors it and that
  document stays the source; report drift instead of editing it. Otherwise
  `shell.js` is the Storyboard shell. Never put a project shell in this Skill or
  `storyboard.css`. A shell change restyles every story that uses it. A story
  without `data-shell` that draws the whole shell in every frame stays valid.
- Text inside `.sb-device` is only UI copy that would ship. Put reviewer
  explanations, fixture notes, and rationale outside it: in the header, the
  inventory, or a `p.sb-note` after `.sb-device`.
- Use CSS classes provided by `storyboard.css` and interaction data hooks
  established by the template, `shell.js`, and the runtime. Do not invent
  feature-specific classes or runtime hooks, or add inline styles, a UI
  framework, web fonts, a CDN, or a build step.
- Low visual, high structural: layout, hierarchy, controls, feedback, and
  decisions matter. Use the existing primitives for spacing and type levels.
  Text glyphs for icons that carry function or status are allowed; brand
  color, decorative icons, icon fonts, and animation are not.
- A story sets `data-interactive` on the board and loads the shared runtime
  with `<script src="storyboard.js" defer></script>`. The runtime shows one
  declared state at a time, starting at the state named by the URL fragment or
  else the initial one, and restarts at the initial one. The header's
  `data-overview-toggle` control, or the `#overview` fragment, shows every
  state with its outgoing transitions and marks end states and states no
  transition reaches. Stories require JavaScript; printing is not supported.
  Do not write feature-specific JavaScript.
- Every state is the whole screen at that moment once the shell is mounted. A
  shell-mounted state's `.sb-device` declares `data-nav` (the selected
  `data-nav-key`) and `data-title` (the title slot text) and contains its
  `.sb-content`, any `.sb-sidebar`, `.sb-panel`, or `.sb-inspector` that
  replaces the shell's region, and then overlays. Put a menu, dialog, or toast
  last in the same `.sb-device` so it overlays the screen. A missing `shell.js`
  or unknown shell name shows a visible error. Mark the control that continues
  the story with `.sb-hotspot`, and give each state one short `p.sb-note`
  saying what to try.
- Draw platform UI the story depends on, such as a native file dialog or a
  browser permission prompt, as a stand-in with plausible fixture content and
  say so in the header; never leave such a step undrawn.
- Never use network calls, storage, random outcomes, real delays, authentication,
  domain calculations, or product validation logic. Show each deterministic
  outcome as a declared state instead.

Keep the template scaffold: `.sb-document` contains `.sb-document__header`,
`.sb-flow`, and `.sb-inventory`; the header may use `.sb-eyebrow`, and each
state is an `.sb-frame` inside `.sb-flow`. Preserve the scaffold classes and
inventory structure while changing labels, fixtures, and the number of state
frames. A shell-mounted state authors only its device content:

```text
article.sb-frame.sb-desktop|sb-phone [id=S*, data-state, tabindex=-1]
├─ p.sb-frame__label
└─ .sb-device [data-nav, data-title]
   ├─ .sb-content
   ├─ .sb-sidebar | .sb-panel | .sb-inspector   optional region override
   └─ overlays
```

After mounting, or when a story draws the shell itself, each frame has one of
these public shells:

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
   ├─ .sb-topbar           titlebar
   ├─ .sb-window
   │  ├─ .sb-nav           app shell only: activity or navigation bar
   │  ├─ .sb-sidebar       side panel
   │  ├─ .sb-content       main area
   │  ├─ .sb-panel         app shell only: bottom panel
   │  └─ .sb-inspector     app shell only: inspector
   └─ .sb-statusbar        app shell only: status bar
```

The default desktop shell uses `.sb-topbar`, `.sb-nav` with `.sb-nav-item`
entries, and `.sb-content`; the default phone shell uses `.sb-topbar` and
`.sb-content`. For a project app shell, include only the regions that shell
defines. Feature content belongs inside these regions. Its public
primitives are layout (`.sb-stack`, `.sb-row`, `.sb-actions`), blocks
(`.sb-card`, `.sb-banner`, `.sb-dialog`, `.sb-list`, `.sb-list-item`), overlays
(`.sb-menu` with `.sb-menu__separator`, `.sb-modal` around a `.sb-dialog`,
`.sb-toast`), state marks (`.sb-hotspot`, `.sb-selected`), and muted text
(`.sb-muted`, which also marks a disabled control together with
`aria-disabled="true"`). For controls, `.sb-field` can contain a native `input`
or `select`; add `.sb-field--error` and a `.sb-field__error` message for a
field-level error. Use `.sb-input` for the same control styling without that
wrapper. Use `.sb-button` and optional `.sb-button--primary` for actions. Use
only the established hooks that apply: `data-storyboard`, `data-initial`,
`data-state`, `data-active`, `data-go`, and `data-transition`; click-through
mode can also use `data-interactive`, `data-reset`, `data-overview-toggle`, and
`data-interactive-control`; shell mounting uses `data-shell`, `data-nav`, and
`data-title`, and `shell.js` uses `data-nav-key` and `data-slot`. `data-active`
marks only the current or initial state and is managed by the runtime.

If understanding the interaction requires a data model, asynchronous behavior,
router, production component system, or custom script, stop and report that the
request has crossed into a prototype or implementation task.

## Workflow

1. Read repository guidance, the Product Brief, the target Feature Map row or
   the named Brief, Specification section, or product question, the project's
   app-shell, layout, or design-language guidance such as a GUI design
   document, and any existing Storyboard for this Feature or topic.
2. State the visual question being reviewed. Per story, draw the happy path
   plus the one or two most important failure paths; list the remaining
   scenarios in the `Not drawn:` line. Separate behavior the sources confirm
   from candidate behavior.
3. List the user stories the question needs, one goal each, with their
   branches. If a story exceeds twelve states, split it; if the Feature needs
   many stories, recheck its scope and report the smallest useful narrowing;
   do not silently change the Feature Map or the product sources.
4. Reuse the shared assets, write the feature HTML, and render it in a browser.
   Check readable content, phone or desktop overflow, the mounted shell,
   in-device copy, unique stable IDs, and every declared transition target;
   open each state through its `#S*` fragment, and use the overview to find
   dead ends, unreached states, and missing branches. If browser rendering is
   unavailable, run structural checks and report the unverified visual risk
   instead of claiming the rendering passed.
5. Check structure on every story, skipping items that do not apply:
   - Main task and primary action: each screen has one main task, and its
     primary action leads the hierarchy and sits consistently across screens.
   - Orientation: the nav highlight and screen title show where the user is.
   - Return path: every page change has a visible back or cancel path.
   - Applicable states: draw empty, loading, error, success feedback, or
     destructive confirmation only where the review question needs it; mark
     unconfirmed outcomes `candidate`.
   - Recovery: an error state shows where and how to fix it.
   - Fixtures: the dataset exposes the layout decision under review.
6. Play each story: follow every declared path and Restart, and check that
   overlays do not hide the control they depend on. Fix only the Storyboard;
   do not implement product behavior.
7. Run the consistency check.

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

Report the Storyboard and story paths, form factor, source, state and
transition IDs, candidate behavior, fixture assumptions, rendering checks, and
unresolved visual decisions. Stop without creating a Feature ID, Map row,
Feature Plan, or implementation. Do not add approval metadata or a separate
approval gate. Pause when an unresolved visual decision would change observable behavior.
