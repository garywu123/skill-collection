# Feature Delivery UI Proposal

Status: brainstorm proposal. No Skill is edited by this document.

## Problem

Delivered GUI pages copy the low-fidelity Storyboard look (grey boxes, wireframe
fonts) instead of the product's visual design. The
[Storyboard follow-up](storyboard-enhancement.md#follow-up-proposal-feature-delivery)
already rejects raising Storyboard fidelity and proposes treating a Storyboard
as a contract for structure, flow, and states only. This proposal places that
rule in `feature-plan` and `feature-delivery`.

## Agreed Position

1. No new permanent role and no Orchestrator-level Skill orchestration; the
   Producer stays general.
2. `feature-plan` puts UI work in its own segment that names the Storyboard as
   a structure, flow, and state contract and names the visual source.
3. `feature-delivery` adds a UI rule: do not copy the wireframe look, apply the
   design language, render in a browser, and self-check against the Storyboard
   structure rubric before review.
4. A subagent for a large UI segment is an optional Plan delegation, not fixed
   architecture.

## Fit With Current Rules

| Rule | Location | Fit |
| --- | --- | --- |
| Link a Storyboard by `S*`/`T*` IDs; "do not copy its visual content" | `skills/coding/30.feature-plan/SKILL.md:57-60` | Says what not to copy into the Plan, not into code. Extend, do not replace. |
| UI placement line naming shell regions and linking the design document | `skills/coding/30.feature-plan/SKILL.md:61-63` | Structure only; no visual source is named. Natural place for the visual-source line. |
| Segments: outcome, owned areas, contracts, constraints, checks | `skills/coding/30.feature-plan/SKILL.md:159-169` | A UI segment fits the existing table; no new mechanism needed. |
| Subagents only for independent, disjoint, verifiable work | `skills/coding/30.feature-plan/SKILL.md:171-178`, `skills/coding/40.feature-delivery/SKILL.md:119-157` | Already covers point 4; a UI segment qualifies only when state and data contracts are stable. |
| Read any linked Storyboard | `skills/coding/40.feature-delivery/SKILL.md:19-21` | No statement of what the Storyboard governs. This is the gap. |
| "Use multiple Skills only when the user's original request covers their outcomes" | `skills/coding/40.feature-delivery/SKILL.md:43-44` | Matches AGENTS.md "Skills stay independently invocable"; a design Skill must be named, never silently invoked. |
| "Keep visual flow in the Storyboard" | `skills/coding/40.feature-delivery/SKILL.md:274-276` | Documentation rule; it does not tell the implementer the wireframe is not the visual target. |
| Structure rubric (main task, orientation, return path, states, recovery, fixtures) | `skills/coding/25.feature-storyboard/SKILL.md:214-223` | Reusable as the delivery self-check by link. |
| Project shell mirrors the design document; that document is the source | `skills/coding/25.feature-storyboard/SKILL.md:89-92` | Confirms the design document, not `storyboard.css`, owns visuals. |

## Two Kinds Of UI Work

- Logic and front-end state: view models, stores, validation, routing,
  persistence, and state transitions matching Storyboard `S*`/`T*`. Verified
  by ordinary unit or component tests; no rendering judgment needed.
- HTML structure, UX, and visual: markup, layout, hierarchy, design tokens,
  responsive behavior, and the look. Verified by rendering in a browser and
  checking the Storyboard rubric plus the design language.

The Plan orders logic before visual when the visual layer depends on stable
state; small Features may keep both in one segment.

## Proposed Changes: `feature-plan`

Replace the UI placement sentence at `SKILL.md:61-63` with:

> For a UI Feature, put HTML structure, UX, and visual work in its own segment,
> separate from logic and front-end state when the Feature has both. That
> segment names the linked Storyboard as the contract for structure, flow, and
> states only, and names the visual source: the project's design language or
> GUI design document. When that document defines an app shell, name the shell
> regions this Feature uses and link it instead of restating it. When no design
> language exists, record an open question; the Plan may name an available
> frontend design Skill, such as `frontend-design`, only when the user selects
> it.

Add to Execution Planning (`SKILL.md:171-178`) one clause: a large UI segment
may be proposed as a delegation under the same conditions; it is never
required.

## Proposed Changes: `feature-delivery`

Add a short `## UI Work` section after Execution Segments:

> A linked Storyboard is a contract for structure, flow, and states; never copy
> its wireframe look, classes, or `storyboard.css`. Apply the visual source the
> Plan names. Use a frontend design Skill only when the Plan or request names
> it; never invoke one silently. When the Plan names no visual source, stop the
> visual work and report the missing decision. Before reporting readiness,
> render each changed screen in a browser, walk the Plan's `S*`/`T*` paths, and
> check the Storyboard structure rubric and the design language; record the
> result as a Plan row. When rendering is unavailable, record `not run` with
> the reason and the unverified visual risk.

No change to Delegation, Status, or Consistency Check.

## Non-Goals

- No higher-fidelity Storyboards and no change to `feature-storyboard`.
- No new UI Designer role, agent, or Orchestrator routing.
- No creation of a design language by `feature-plan` or `feature-delivery`.
- No visual regression tooling or screenshot-diff gate.

## Risks

- Codex reviewer cannot render a browser: visual acceptance rests on the
  Producer's self-check. Mitigation: record screenshots or a render locator in
  the Plan row; the reviewer checks structure and code against the rubric.
- No design language in the project: delivery stalls on visual work, or the
  user is pushed toward a design Skill they did not choose. Mitigation: the
  open question is raised at planning, not mid-delivery.
- A design Skill's aesthetic may diverge from later project direction; naming
  it in the Plan keeps the choice visible and reversible.
- Browser rendering may be unavailable in some runtimes; the `not run` path
  keeps the gap explicit instead of claiming success.

## Open Questions

1. When no design language exists, should `feature-plan` block the UI segment,
   or allow a named frontend design Skill as a recorded one-Feature default?
2. Should the rendered self-check be a required Validation row for every UI
   segment, or only when the Plan selects it?
3. Where does a project's design language live by convention (for example
   `docs/design-language.md`), or does each Plan link whatever exists?
