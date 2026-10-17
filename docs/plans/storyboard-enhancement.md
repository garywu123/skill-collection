# Feature Storyboard Enhancement Proposal

Status: brainstorm, revised after review round 1 and Orchestrator
counterpoints, not approved. Target Skill:
[feature-storyboard](../../skills/coding/25.feature-storyboard/SKILL.md).

## Problem

The user reports that Storyboards produced by the current Skill degrade feature
delivery for GUI work: the delivered page follows a wireframe whose structure
was weak, so the result is not the best-designed layout. The user accepts that a
wireframe is not visual design, but expects it to be correct at the UX and
page-structure level, because a Storyboard exists to:

- explain the business flow; and
- show an interaction people understand and like.

Reported observations (from the user's projects; no Storyboard output exists in
this repository to verify them):

- Feature frames usually omit the app shell (for example a left navigation
  sidebar), so layout decisions are made without the real app context.
- The user prefers the "fake mini app" experience (click through, fake data)
  over flipping between separate labelled screenshots.
- Navigation to a different screen (for example pressing New opens a separate
  editor page) should still feel like the same app.
- Token cost and edit cost must stay bounded.

Usage context confirmed by the user: a solo developer who needs each app to
have complete stories. On desktop the user opens the HTML directly in a
browser; on mobile the agent captures screenshots of states and sends them
(this proposal prefers a link instead; see Review Path). JavaScript that
integrates a shared component is acceptable; pure HTML and printing are not
required.

Part of the reported degradation likely starts in delivery rather than in the
Storyboard; see [Follow-Up Proposal](#follow-up-proposal-feature-delivery).

## Industry Context

- Narrative UX storyboards (comic-style scenarios) cover context and
  motivation, not screen structure.
- Wireflows (described by NN/G) place many screens on one canvas with arrows;
  good for overview, weak for experiencing the interaction. A click-through
  review follows the happy path, so dead ends and missing branches are easier
  to see in an overview. A solo developer who is both author and reviewer is
  most exposed to this.
- Clickable prototypes (Figma prototype mode, ProtoPie, Framer) are the common
  review and usability-test medium.
- Wireframe tools keep structure consistent through masters or components:
  Axure masters, Balsamiq symbols, and Figma components with variants and
  instance overrides. The shell is defined once; each screen overrides only the
  selected nav item, title, or a replaced region. This is the model for change 3.
- Platform navigation patterns (Fluent `NavigationView`, Material navigation
  rail and drawer, Apple HIG sidebar and tab bar, list-detail) are the usual
  structure reference for shell regions and for choosing an overlay versus a
  page change, instead of inventing a layout per Feature.
- Structure review commonly uses Nielsen's ten heuristics and a per-screen
  state checklist (ideal, empty, loading, error, partial; Scott Hurff's "UI
  stack"), plus content-first priority ranking before layout.

The current Skill already provides the click-through format. The gaps are a
structure rubric, a navigation example, and shell repetition cost.

## Gaps In The Current Skill

1. No UX structure rubric (evidenced). Workflow step 4
   (`SKILL.md:164-169`) checks rendering, overflow, IDs, and transition targets
   only. The Visual Contract (`SKILL.md:84-85`) names layout, hierarchy,
   controls, and feedback as important, but nothing checks them.
2. No navigation example (evidenced). The template
   (`assets/storyboard.template.html`) shows only overlays on one screen (menu,
   dialog, toast). It has no full-screen change, no nav highlight, and no
   return path; `.sb-selected` exists (`assets/_storyboard.css:413`) but is not
   used. The default desktop shell has no `.sb-nav` (`SKILL.md:130-131`).
3. Shell repetition (evidenced cost, reported effect). The rules already
   require a full shell in every state (`SKILL.md:73-76`, `SKILL.md:92`), but
   each state copies it: the template repeats the topbar and sidebar in all
   four states (`storyboard.template.html:25-80`). Edit and token cost grow
   with the state count. The reported shell omission is plausibly a result of
   this cost; it is not a missing rule.
4. "Deliberately low fidelity" read as permission for loose layout (reported).
   `SKILL.md:84-85` already says layout and hierarchy matter; the rubric in
   change 1 addresses this without new wording about fidelity.

## Proposed Changes

Ordered by value per cost.

1. UX structure rubric, inline in the Workflow. Add about six checkable items
   to step 4 or 5, applied to every story and skipped where they do not apply:
   - Main task and primary action: each screen has one main task, and its
     primary action is first in the hierarchy and placed consistently across
     screens.
   - Orientation: the nav highlight and the screen title show where the user is.
   - Return path: every full-screen change has a visible back or cancel path;
     the inventory purpose cell says why a step is an overlay or a page change.
   - Applicable states: for each screen, check whether empty, loading, error,
     success feedback, or destructive-action confirmation applies to the review
     question; draw only those that apply. An outcome the sources do not
     confirm is marked `candidate`, as `SKILL.md:31-34` already requires.
   - Recovery: an error state shows where and how to fix it.
   - Fixtures: use the smallest plausible dataset that exposes the layout
     decision under review (for example enough rows to show scrolling or
     truncation when that is the question), never `Item 1`.

   The structure-first note becomes one line per screen in the inventory
   purpose cell (main task, primary action, entry and exit), not a separate
   artifact.
2. Navigation example in the template. Replace or extend the template states
   so one transition changes the page (list -> New -> editor) with the nav
   highlight following the state and a visible return path, alongside the
   existing overlay examples.
3. Runtime-mounted shared shell.
   - On first use per project, copy a new asset to
     `docs/storyboards/_shell.js`. It only declares shell markup per form factor
     (nav regions, fake nav items, fake app data) as a string assigned to one
     global, with slot and nav-key hooks. It contains no behavior. When the
     project's design document defines an app shell, `_shell.js` mirrors it.
   - A story loads it with `<script src="_shell.js" defer></script>` before
     `_storyboard.js`; `defer` keeps that order. This is a local script load
     like the existing runtime, not `fetch`, so it works under `file://` and
     keeps the "no network calls" rule.
   - A board opts in with a generic hook naming the shell. Each state writes
     its `.sb-content` and any overlays. Per-state shell variation uses
     declared hooks: one names the selected nav key (the runtime adds
     `.sb-selected`), one supplies the title slot text, and a state that
     includes its own shell region, such as a `.sb-sidebar` with a selected
     row, replaces that region of the shell. Overlays are placed after the
     window as today.
   - The runtime mounts the shell into every state once on load, before the
     click-through starts, so each state is a complete screen in the DOM and
     `#S*` fragments still open any state directly. The mounting is generic;
     no story contains script. A missing `_shell.js` or unknown shell name
     shows a visible error instead of content-only frames.
   - Edit cost: a shell change touches one file; a feature edit touches the
     story's content plus any nav, title, or region override it declares. Not
     every edit is content-only.
   - Trade-off: the shell is a shared component, so changing `_shell.js`
     changes the appearance of every existing story, including stories already
     reviewed. That is intended for an app-wide shell change; a story cannot
     keep an older shell.
   - Stories written in the current complete-frame form stay valid and are
     not migrated unless revised.
4. Runtime all-states overview. Replaces the dropped no-JavaScript view. A
   generic header control toggles it, and the `#overview` fragment opens it
   directly. The runtime stops the click-through and shows every state, after
   shell mounting, with its declared outgoing transitions (`T*` -> `S*`) read
   from the existing transition hooks. It marks a non-initial state that no
   transition reaches and a state with no outgoing transition, so the reviewer
   can judge dead ends and missing branches. It reuses the stylesheet's
   existing all-states layout and needs no story-specific markup beyond the
   template's control.
5. Fixture and fidelity wording. "Low visual, high structural": use existing
   primitives for spacing and type levels, and add no classes unless the
   validation example shows a gap. Meaningful icons that carry function or
   status (as text glyphs, no icon font or CDN) are allowed; brand color,
   decorative icons, and animation are not.

## Current Rules This Would Change

| Current rule | Location | Proposed change |
| --- | --- | --- |
| Without JavaScript, or when printed, every state is shown with working `#S*` links. | `SKILL.md:89-90`, `_storyboard.css:450-467` | Dropped. Shell-mounted stories require JavaScript; printing is not supported. The runtime overview in change 4 replaces the all-states view. |
| Workflow step 4 checks the all-states view without JavaScript. | `SKILL.md:166-167` | Replaced by checking the runtime overview for dead ends, unreached states, and missing branches, opening each state through its `#S*` fragment, and the rubric in change 1. |
| Export a PNG only on request; the HTML is the source of truth. | `SKILL.md:58-60` | Unchanged. Adds an on-request private Artifact link as the preferred mobile review view; the published copy is not maintained. |
| Copy the stylesheet and runtime once and reuse them unchanged. | `SKILL.md:46-49` | Still true for both; `_storyboard.js` is replaced once from the Skill to add mounting and the overview. The new `_shell.js` is copied once and then owned by the project. |
| The shell definition stays in the design document, never in this Skill or `_storyboard.css`. | `SKILL.md:73-76` | Unchanged when a design document defines it; `_shell.js` mirrors it. Without one, `_shell.js` is the Storyboard shell definition. The Skill ships only the generic default shell. |
| Use only the established hooks. | `SKILL.md:80-83`, `SKILL.md:141-145` | Adds the generic shell, nav-key, title-slot, slot, and overview-control hooks to the established list. |
| Frame structure tree with the shell in every frame. | `SKILL.md:107-128` | Adds the shell-mounted authoring form: a state contains `.sb-content`, optional overriding regions, and overlays. |
| Draw every state as the whole screen at that moment. | `SKILL.md:92` | Unchanged in effect: true after mounting; authoring declares variations instead of copying the shell. |

The "no network calls" (`SKILL.md:99`), "no feature-specific JavaScript"
(`SKILL.md:91`), and one-story-per-file rules are unchanged.

## Review Path

- Desktop: the user opens the story HTML directly in a browser and clicks
  through.
- Mobile: static screenshots reproduce the screen-flipping the user disliked.
  On request only, the agent publishes the story with `_shell.js`,
  `_storyboard.js`, and `_storyboard.css` as a private claude.ai Artifact link
  that the user opens and clicks through on the phone. Publishing is never
  automatic. The fixtures are already non-sensitive, but publishing still
  sends the story to an external service. When the host offers no Artifact
  publishing, or the user declines, the agent opens each state through its
  `#S*` fragment and sends one screenshot per state. Neither the published
  copy nor the screenshots are maintained artifacts, as `SKILL.md:58-60`
  already requires for PNGs.
- Overview: after the click-through, the reviewer opens the runtime overview
  (change 4) to check dead ends and missing branches the happy path skipped.
  The inventory tables stay the reference for IDs.

## Explicit Non-Goals

- One file containing the whole app with shared cross-feature state. Each story
  stays one file; only the shell and runtime are shared.
- Runtime composition beyond mounting one declared shell, such as includes of
  other stories or shared state between files.
- Feature-specific JavaScript, frameworks, or high-fidelity visuals.
- A no-JavaScript fallback, print layout, or PNG export pipeline.
- Automatic publishing of stories.
- Raising Storyboard fidelity to fix delivered visual quality; see the
  follow-up proposal.

## Resolved Questions

- Mount or inline the shell? Mount it from `_shell.js` loaded with
  `<script src>`. No `fetch`, so it works under `file://`, the same way the
  template already loads `_storyboard.js` (`storyboard.template.html:8`).
- Where does the shell live without a design document? In
  `docs/storyboards/_shell.js`. Do not add a section to a design document
  another Skill owns; Skills stay independently invocable (`AGENTS.md`, Skill
  Design). When the design document exists, it stays the source and the
  Storyboard reports drift instead of editing it.
- Is the rubric mandatory? Yes, for every story, with items skipped when they
  do not apply (navigation items apply only when the story changes pages). It
  is always needed, so it lives inline in `SKILL.md`, not in `references/`, and
  runs in the Workflow, not in the source-alignment Consistency Check.

## Remaining Questions

- Does the phone shell need a bottom tab bar region? The current phone shell has
  only `.sb-topbar` and `.sb-content`. Decide from the validation example; do
  not add a region in advance.

## Follow-Up Proposal: Feature Delivery

Separate from this proposal and not part of its changes; it targets the
feature-delivery Skill, which this proposal does not edit.

- Likely cause (unverified): an agent implementing from a low-fidelity
  wireframe tends to copy its look, so the delivered page looks like a
  wireframe.
- Raising Storyboard fidelity is a poor fix: Walker et al. (2002) found that
  low- and high-fidelity prototypes surface similar usability issues, a
  trade-off Rudd et al. (1996) also discuss. Fidelity adds cost without adding
  much review value.
- Proposed rule for feature-delivery: a Storyboard is a contract for
  structure, flow, and states only. Visual design comes from the project's
  design language, not from the wireframe's appearance.

## Next Step

After review, validate with one example: a desktop app with a left sidebar,
list -> New -> separate editor page -> save / cancel / validation failure,
built once with the current Skill and once with the proposed changes. Compare
rubric results, story file size, the files touched by one shell change, and
whether the overview exposes a deliberately removed branch. Exercise the
mobile review path by publishing the example as a private Artifact link and
playing it on a phone, with screenshots as the fallback check. Raise the
feature-delivery follow-up separately.
