# Review Backlog

Human-owned, non-authoritative follow-up items from cross-agent runs. Agents
read this file only when the user asks for a backlog review or names an item
ID. An item becomes work only after the user promotes it into the current
request or the applicable Feature Map and Plan. Keep each item's status
current: `open`, `promoted`, `resolved`, or `dismissed`.

## RB-0001: Architecture migration requires editing Feature Plan links, but the completion rule prohibits edi...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261003-180613-general-6666`, finding `R1-002`
- Artifact: `docs/coding-agent/coding-agent-design.md` (general)
- Base: `b43d6c4` with uncommitted changes
- Claim: Architecture migration requires editing Feature Plan links, but the completion rule prohibits editing Plans.
- Evidence: `skills/coding/18.architecture-design/SKILL.md:81 requires updating migration-only links in Feature Plans.`, `skills/coding/18.architecture-design/SKILL.md:127 says to stop without editing Plans, with an exception stated only for Maps.`
- Proposed change: Explicitly exempt migration-only Plan link corrections from the completion prohibition, while preserving Plan content, statuses, and results.
- Rationale: Valid minor wording contradiction between migration-only Plan link updates and the completion prohibition. A1 migration scope is specified in Workflow and preserved by samples. Retain for a local wording correction; no additional Producer revision is warranted for this minor item.

## RB-0002: The S4 receipt reports 15 unittest commands, but the saved final checker and results contain 14.

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261004-002719-general-4269`, finding `R1-001`
- Artifact: `skills/coding/40.feature-delivery/SKILL.md` (general)
- Base: `3b9f43a` with uncommitted changes
- Claim: The S4 receipt reports 15 unittest commands, but the saved final checker and results contain 14.
- Evidence: `docs/coding-agent/coding-agent-design.md:382 and :689 report 15 runs/commands.`, `.cross-agent/evidence/pm0-2/check_pm0_2.py:144 contains the first of 14 run calls; results.json:51 contains 14 corresponding run records. Independent write-free AST/JSON inspection confirmed both counts.`
- Proposed change: Report 14 captured commands and distinguish any earlier attempts from the final saved run.
- Rationale: Valid minor receipt discrepancy independently corroborated: the saved checker has 14 run calls and results.json has 14 run records. No rule or acceptance defect is shown. The Orchestrator will correct only the final saved-run count to 14 in the existing plan during post-close receipt finalization, distinguishing the earlier argument-order failed attempt, and record this correction. No Producer revision, retry, new gate or scope is needed.

## RB-0003: The region primitives impose one fixed shell instead of allowing the project's design document to...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261004-154121-general-1ef5`, finding `R1-001`
- Artifact: `skills/coding/25.feature-storyboard/SKILL.md` (general)
- Base: `8a6733b` with uncommitted changes
- Claim: The region primitives impose one fixed shell instead of allowing the project's design document to determine its structure. Horizontal navigation or a bottom panel spanning the inspector cannot be mirrored using the permitted scaffold.
- Evidence: `Request 1(b), 1(d): regions must mirror the project shell, whose definition must remain outside this Skill.`, `skills/coding/25.feature-storyboard/assets/_storyboard.css:119 fixes navigation, sidebar, main, inspector, and panel placement.`, `skills/coding/25.feature-storyboard/SKILL.md:66 prohibits custom classes and inline styles; :100 fixes the desktop nesting.`
- Proposed change: Keep the simple default shell and make the generic regions composable through minimal structural containers, allowing their arrangement to follow the project document without adding shell variants.
- Rationale: The fixed nav/side/main/panel/inspector grid matches the common desktop-tool shell and the target project's concept exactly. Making regions freely composable adds structure no current project needs (user asked for ponytail-level simplicity). Revisit only when a project defines a shell this grid cannot mirror.

## RB-0004: The new regions lack vertical scroll containment. Long content expands the desktop device and pus...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261004-154121-general-1ef5`, finding `R1-002`
- Artifact: `skills/coding/25.feature-storyboard/SKILL.md` (general)
- Base: `8a6733b` with uncommitted changes
- Claim: The new regions lack vertical scroll containment. Long content expands the desktop device and pushes bottom regions downward instead of scrolling within its region.
- Evidence: `Request 1(b) includes scroll containment in the structural CSS.`, `skills/coding/25.feature-storyboard/assets/_storyboard.css:106 and :123 specify only minimum heights.`, `skills/coding/25.feature-storyboard/assets/_storyboard.css:126 adds overflow:auto without a bounded height or shrinkable vertical track.`
- Proposed change: Give the app-shell viewport a bounded height and allow its content regions to shrink and scroll, while preserving the default and phone shells.
- Rationale: Minor: static boards rarely need to demonstrate in-region scrolling; add a bounded height and shrinkable tracks if a board needs it.

## RB-0005: The revision introduced a UTF-8 byte-order mark at the start of the plan file: line 1 now begins...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261008-144809-general-0e4c`, finding `R2-001`
- Artifact: `docs/coding-agent/lean-workflow-plan.md` (general)
- Base: `27ef961` with uncommitted changes
- Claim: The revision introduced a UTF-8 byte-order mark at the start of the plan file: line 1 now begins with U+FEFF before the level-one heading, whereas the previous revision and the rest of the repository's Markdown start with a plain `#`. Strict parsers and scripts that read the file as plain UTF-8 see `﻿# ...` as the first line, so the title may not be recognized as an ATX heading, which conflicts with the repository Markdown style the plan claims to have checked.
- Evidence: `Review diff, first hunk: `-# Lean Skill Workflow Change Plan` replaced by `+﻿# Lean Skill Workflow Change Plan`; the only difference on that line is the leading byte-order mark`, `docs/coding-agent/lean-workflow-plan.md:1`, `AGENTS.md, Markdown Style: 'Use one level-one title and ATX headings without skipping levels'; plan line 'Planning verification: ... checked this plan's scope, relative links, headings and whitespace' did not catch the encoding change`
- Proposed change: Save the file as UTF-8 without a byte-order mark so line 1 starts with `#`; no content change is needed. Suitable for note-only disposition or the Orchestrator's finalization batch since it is a one-byte encoding fix.
- Rationale: Valid minor encoding regression; it does not earn another revision. After closing this planning run, remove the BOM as an explicitly reported mechanical correction, correct the check-result attribution, and record the final review outcome without changing the reviewed design. Both accepted R1 findings are resolved. The pre-existing invocation-policy check remains failed and the user decision remains open; do not claim independently-passed.

## RB-0006: The AGENTS.md heuristic misses valid route paths and reports unrelated table values as broken links.

- Type: `rejected`
- Status: `open`
- Priority: `none`
- Source: run `20261014-173922-general-7263`, finding `R1-002`
- Artifact: `docs/plans/code-style-v2.md` (general)
- Base: `6fd18d9` with uncommitted changes
- Claim: The AGENTS.md heuristic misses valid route paths and reports unrelated table values as broken links.
- Evidence: `Authoritative decision B1 requires checking backtick paths in AGENTS.md route tables.`, `docs/plans/code-style-v2.md:465 excludes every span containing spaces, so a broken route such as `docs/User Guide.md` is silently skipped.`, `docs/plans/code-style-v2.md:463 scans every table; lines 640-643 acknowledge that an unrelated value such as `Node.js` would be reported as a missing file.`, `The fixture at docs/plans/code-style-v2.md:499 covers neither spaced routes nor unrelated table values.`
- Proposed change: Define how route cells are identified, preserve spaces within route paths, and extend the existing AGENTS.md fixture with a broken spaced path and a non-route Node.js value.
- Rationale: Already resolved in P1: plan lines 478-484 define route candidates (separator or .md, spaces allowed, Node.js skipped) and the fixture at line 516 covers the spaced path and Node.js.

## RB-0007: The required Orchestrator acceptance gate remains unverified. The supplied checks do not establis...

- Type: `rejected`
- Status: `open`
- Priority: `none`
- Source: run `20261014-180603-general-82eb`, finding `R1-001`
- Artifact: `skills/coding/16.code-style/SKILL.md` (general)
- Base: `6fd18d9` with uncommitted changes
- Claim: The required Orchestrator acceptance gate remains unverified. The supplied checks do not establish that the new scripts work in either PowerShell host or that repository scans produce no false positives.
- Evidence: `docs/plans/code-style-v2.md:610 requires parsing both scripts in Windows PowerShell 5.1 and pwsh 7.`, `docs/plans/code-style-v2.md:613 requires Invoke-DocLinksTests.ps1 execution; subsequent checks require repository and scoped link scans.`, `Supplied P0 results cover cross-agent tests, deployment/install list commands, and git diff --check; none exercise the new checker.`
- Proposed change: Orch should run and attach the plan's outstanding acceptance results before closing the run, including `powershell -ExecutionPolicy Bypass -File skills/coding/15.coding-agent-instructions/scripts/tests/Invoke-DocLinksTests.ps1` and its pwsh equivalent when installed. Inspect every repository-scan diagnostic. This is missing validation evidence, not an observed test failure.
- Rationale: Resolved with evidence the Reviewer could not see: after P1 the Orchestrator ran Invoke-DocLinksTests.ps1 in Windows PowerShell 5.1 (fixture, clean subset, missing path, git work tree: all PASS) and Test-DocLinks on 16.code-style and 15.coding-agent-instructions (0 broken), database_sync_tool (0), agv-tools (3 genuine imprecise prose paths in the root AGENTS.md), and this repository (4 known links in other Skills' templates, recorded as follow-up). pwsh 7 is not installed on this machine; that gap is recorded in the plan's Implementation notes.

## RB-0008: Link-like text inside a quoted Markdown title is incorrectly checked as another destination. With...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261014-180603-general-82eb`, finding `R1-002`
- Artifact: `skills/coding/16.code-style/SKILL.md` (general)
- Base: `6fd18d9` with uncommitted changes
- Claim: Link-like text inside a quoted Markdown title is incorrectly checked as another destination. With b.md present, `[a](b.md "[example](missing.md)")` produces a false missing-file diagnostic even though missing.md appears only in the title.
- Evidence: `docs/plans/code-style-v2.md:474 requires titles to be stripped.`, `skills/coding/15.coding-agent-instructions/scripts/Test-DocLinks.ps1:205 searches for every subsequent `](`.`, `skills/coding/15.coding-agent-instructions/scripts/Test-DocLinks.ps1:242 resumes scanning at the destination's end, leaving its title eligible for extraction.`, `skills/coding/15.coding-agent-instructions/scripts/tests/Invoke-DocLinksTests.ps1:63 has no titled-link case.`
- Proposed change: Skip the optional title when resuming destination extraction, including reference-definition titles. Strengthen the existing valid-link fixture with a quoted title containing link-like text and expect no diagnostic.
- Rationale: Valid edge case (link-like text inside a quoted title); rare in practice. Fix in a later checker version with a fixture case.

## RB-0009: The explicit-anchor regex counts `data-id` as `id`. A document containing `[jump](#ghost)` and `<...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261014-180603-general-82eb`, finding `R1-003`
- Artifact: `skills/coding/16.code-style/SKILL.md` (general)
- Base: `6fd18d9` with uncommitted changes
- Claim: The explicit-anchor regex counts `data-id` as `id`. A document containing `[jump](#ghost)` and `<a data-id="ghost">text</a>`, without a real ghost anchor, incorrectly passes the anchor check.
- Evidence: `docs/plans/code-style-v2.md:480 permits explicit `<a id>` and `<a name>` anchors.`, `skills/coding/15.coding-agent-instructions/scripts/Test-DocLinks.ps1:130 uses a word boundary before `id|name`; that boundary also matches after the hyphen in `data-id`.`, `skills/coding/15.coding-agent-instructions/scripts/Test-DocLinks.ps1:190 accepts any fragment present in the resulting anchor set.`, `The existing anchor fixture at skills/coding/15.coding-agent-instructions/scripts/tests/Invoke-DocLinksTests.ps1:65 covers headings but no explicit-anchor attributes.`
- Proposed change: Match standalone id/name attributes rather than attribute-name suffixes. Extend the existing anchor fixture with a valid explicit anchor and a data-id-only target that must report missing anchor.
- Rationale: Valid edge case (data-id matched as id); rare in practice. Fix in a later checker version with a fixture case.

## RB-0010: The claim that waves occur only above 500 KB contradicts the file-based packing procedure.

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261014-233308-general-1324`, finding `R1-002`
- Artifact: `docs/plans/code-style-v2.1.md` (general)
- Base: `26ed4e7` with uncommitted changes
- Claim: The claim that waves occur only above 500 KB contradicts the file-based packing procedure.
- Evidence: `docs/plans/code-style-v2.1.md:86 says waves happen only after confirmation above the cap.`, `docs/plans/code-style-v2.1.md:88 keeps files intact, limits ordinary batches to 100 KB, and adds batches when necessary.`, `Six 80 KB files total 480 KB but require six batches and two waves; the table at docs/plans/code-style-v2.1.md:248 promises five batches and one wave.`
- Proposed change: Determine waves from the actual packed batch count, independently of the total-size cap. Qualify the worked totals as assuming packable files and include the six-file case.
- Rationale: Valid internal inconsistency in the worked numbers; the Orch will require the implementation run to derive waves from the packed batch count and add the six 80 KB files case.

## RB-0011: The "smallest complete workflow" requires support for two interaction paths and makes direct/rela...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261016-121642-general-81ba`, finding `R1-005`
- Artifact: `docs/plans/cross-agent-exploration.md` (general)
- Base: `6738c5b` with uncommitted changes
- Claim: The "smallest complete workflow" requires support for two interaction paths and makes direct/relay ownership an implementation acceptance item. But it also calls the direct interactive-to-managed transition an unverified feasibility question. Building ownership locks, duplicate-delivery protection, and an import path around an unverified capability is the speculative state-machine design that AGENTS.md rules out. It also works against U1's "保持简单".
- Evidence: `docs/plans/cross-agent-exploration.md:80-90 says to support two interaction paths, Relay and Direct`, `docs/plans/cross-agent-exploration.md:92-96 says the transition is a bounded feasibility question, not a verified capability`, `docs/plans/cross-agent-exploration.md:204 acceptance requires direct/relay ownership to prevent simultaneous driving and duplicate messages`, `AGENTS.md:67-68 says not to prebuild agents, phases, state machines, templates, or validation for hypothetical needs`, `docs/plans/cross-agent-exploration.md:16 U1 asks to reuse existing mechanisms and keep it simple`
- Proposed change: Scope the first version to relay. Make direct mode a separate feasibility spike whose only deliverable is a recorded capability/limitation result. Move the direct ownership acceptance items behind a positive spike result.
- Rationale: Agree with avoiding unproven direct-integration machinery. This is a simplification recommendation rather than a separate mandatory revision. Its concrete safety issues are addressed by accepted R1-003 and R1-004. Retain the user's interest in direct conversation: assess it first in a bounded spike and condition integration on results; relay is an interim managed option. No extra role, handoff file, or broad review-schema redesign is needed for the first implementation.

## RB-0012: `close` appends backlog items before `exploration.retain` runs. If `retain` then raises, for exam...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261016-153214-general-566f`, finding `R1-004`
- Artifact: `skills/coding/cross-agent/SKILL.md` (general)
- Base: `6738c5b` with uncommitted changes
- Claim: `close` appends backlog items before `exploration.retain` runs. If `retain` then raises, for example on tampered evidence or the import failure in R1-003, the run stays open but `docs/review-backlog.md` has already been written. Each later `close` attempt appends the same findings again under new `RB-NNNN` IDs, because `backlog.append` does not deduplicate. The result is duplicate, human-owned backlog entries.
- Evidence: `skills/coding/cross-agent/scripts/crossagent/engine.py:407-415 (`backlog.append` at 411 runs before `retain` at 415)`, `skills/coding/cross-agent/scripts/crossagent/backlog.py:45-62 (always allocates new IDs; no run/finding dedup)`, `skills/coding/cross-agent/scripts/tests/test_exploration.py:175-184 (`close` is expected to raise on a `retain` failure and leave the run open)`
- Proposed change: Call `exploration.retain(state)` before the backlog append, so evidence verification fails before any durable side effect. Alternatively, skip backlog items whose run and finding ID already exist.
- Rationale: Valid low-priority close ordering edge case; no finding-bearing close has been retried in this task. Preserve evidence verification before cleanup; do not expand review revision eligibility for a minor.

## RB-0013: `waive-review` accepts any run in phase `review` with `reviews_done == 0`, including a `--first r...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261016-153214-general-566f`, finding `R1-005`
- Artifact: `skills/coding/cross-agent/SKILL.md` (general)
- Base: `6738c5b` with uncommitted changes
- Claim: `waive-review` accepts any run in phase `review` with `reviews_done == 0`, including a `--first review` run that never produced anything. Such a run would end `completed-without-review` with no production and no review, although the contract allows waiver only 'after production, before the first review'.
- Evidence: `skills/coding/cross-agent/scripts/crossagent/exploration.py:154-160 (no check that a Producer step ran)`, `skills/coding/cross-agent/scripts/crossagent/engine.py:121 (`phase` starts as `first`, so `--first review` begins in `review` with `producer_steps` 0)`, `skills/coding/cross-agent/SKILL.md:285-289`
- Proposed change: Also require `state["producer_steps"] > 0` (and `state["first"] != "review"`) before waiving.
- Rationale: Valid boundary guard improvement for review-only cancellation; current task uses waiver after production. Do not label such a run independently passed.

## RB-0014: Discussion evidence import keeps every non-sidechain `user` record that has text as a `user` mess...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261016-153214-general-566f`, finding `R1-006`
- Artifact: `skills/coding/cross-agent/SKILL.md` (general)
- Base: `6738c5b` with uncommitted changes
- Claim: Discussion evidence import keeps every non-sidechain `user` record that has text as a `user` message. It does not exclude provider-generated user-role records such as compaction summaries or meta/local-command records. A long expert session that compacts could then present a model-written summary under the `user` role in `discussion.json`. That blurs the separation between user-confirmed decisions and candidates, and the provenance distinction is a stated goal. The worker prompt warns only that `user` includes Orch startup prompts. The transcript record fields are from my knowledge of Claude Code's transcript format, not from a fixture in this repository.
- Evidence: `skills/coding/cross-agent/scripts/crossagent/evidence.py:41-74 (filters only `type` and `isSidechain`; no handling of `isCompactSummary`/`isMeta`-style records)`, `skills/coding/cross-agent/scripts/crossagent/engine.py:732-738 (prompt caveat covers only Orch startup prompts)`, `docs/plans/cross-agent-exploration.md:291-304 (record speaker; keep source classes distinguishable; never reconstruct originals)`
- Proposed change: Exclude or separately label provider-generated user-role records, such as compaction summaries and meta/command caveats, in the export. Extend the existing evidence test with one such record.
- Rationale: Useful provenance hardening for long or meta-heavy sessions, but record-format fields are not established by the cited fixtures. Treat user-role transport as insufficient proof of human authorship as already instructed. Verify actual provider flags before extending import.

## RB-0015: The diagnosis overstates what the current Skill omits, which makes the proposed runtime expansion...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261016-173517-general-14bf`, finding `R1-002`
- Artifact: `docs/plans/storyboard-enhancement.md` (general)
- Base: `6738c5b` with uncommitted changes
- Claim: The diagnosis overstates what the current Skill omits, which makes the proposed runtime expansion appear more necessary than the evidence supports.
- Evidence: `docs/plans/storyboard-enhancement.md:44-49 describes checks as technical only and low fidelity as permission for loose layout.`, `skills/coding/25.feature-storyboard/SKILL.md:84-85 explicitly prioritizes layout, hierarchy, controls, feedback, and decisions.`, `skills/coding/25.feature-storyboard/SKILL.md:38-43 already requires Cancel/failure branches that return to the story; lines 157-171 require relevant happy/failure paths, readable content, shell regions, and playable paths.`, `skills/coding/25.feature-storyboard/assets/storyboard.template.html:29,41,57,78 already includes a sidebar in every example state.`, `skills/coding/25.feature-storyboard/assets/_storyboard.css:176-203 already provides consistent spacing and block treatment.`
- Proposed change: Describe the narrower supported gap: existing structural requirements lack an explicit UX review rubric and a representative navigation example. Distinguish reported output failures from missing instructions. Treat shell omission and loose-layout interpretation as reported observations until representative outputs or original discussion evidence are linked.
- Rationale: Valid narrowing; folded into the R1-001 revision guidance.

## RB-0016: The unqualified list of required states can force irrelevant screens and introduce behavior beyon...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261016-173517-general-14bf`, finding `R1-003`
- Artifact: `docs/plans/storyboard-enhancement.md` (general)
- Base: `6738c5b` with uncommitted changes
- Claim: The unqualified list of required states can force irrelevant screens and introduce behavior beyond the reviewed story.
- Evidence: `docs/plans/storyboard-enhancement.md:63-65 makes empty, loading, error, success feedback, and destructive-action confirmation required states without an applicability condition.`, `skills/coding/25.feature-storyboard/SKILL.md:157-159 requires only states needed to answer the visual question and distinguishes confirmed from candidate behavior.`, `skills/coding/25.feature-storyboard/SKILL.md:31-34 requires unconfirmed behavior to be marked candidate and reported to its owner.`, `skills/coding/25.feature-storyboard/SKILL.md:62-63 limits story size; AGENTS.md:45-46 requires proportionate scope.`
- Proposed change: Require an applicability check rather than every listed state. Draw only relevant, source-backed outcomes; mark proposed behavior as candidate. For example, omit loading from an immediate interaction and destructive confirmation from a story without a destructive action. Preserve declared deterministic outcomes without adding validation logic or real asynchronous behavior.
- Rationale: Valid; folded into the R1-001 revision guidance as an applicability check.

## RB-0017: The overview clips desktop screens on narrow viewports, hiding controls that reviewers need to in...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261016-231204-general-db65`, finding `R1-002`
- Artifact: `skills/coding/25.feature-storyboard/SKILL.md` (general)
- Base: `8f430e3` with uncommitted changes
- Claim: The overview clips desktop screens on narrow viewports, hiding controls that reviewers need to inspect.
- Evidence: `skills/coding/25.feature-storyboard/assets/storyboard.css:466 sets overflow: hidden on overview frames.`, `skills/coding/25.feature-storyboard/assets/storyboard.css:472 scales devices to 0.5, while line 477 fixes desktop devices at 920px wide, yielding a 460px rendered screen.`, `The overview grid permits columns narrower than 460px; at a 390px viewport, document and frame padding leave substantially less space. The right side of each screen is therefore clipped.`, `SKILL.md:110 promises an overview showing every state; Workflow step 4 uses it to inspect dead ends and missing branches.`
- Proposed change: Allow horizontal scrolling for undersized overview frames or size the preview to the available width. Verify the existing template's overview at a narrow phone viewport, checking that right-edge actions remain inspectable.
- Rationale: Valid for the mobile review path but minor; fix in a later polish pass by letting overview frames scroll horizontally or scale to available width.

## RB-0018: The proposal gives conflicting instructions for small Features containing both logic and visual w...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261016-232147-general-4708`, finding `R1-001`
- Artifact: `docs/plans/feature-delivery-ui.md` (general)
- Base: `8f430e3` with uncommitted changes
- Claim: The proposal gives conflicting instructions for small Features containing both logic and visual work.
- Evidence: `docs/plans/feature-delivery-ui.md:49-50 allows small Features to keep both kinds of work in one segment.`, `docs/plans/feature-delivery-ui.md:56-57 requires a separate visual segment whenever the Feature has both.`, `The supplied agreed position requires UI work in its own segment.`
- Proposed change: Remove the small-Feature exception so the explanation and exact proposed rule consistently follow the agreed split.
- Rationale: Valid inconsistency; resolve when the proposal is implemented by deciding whether small Features keep one combined segment.

## RB-0019: Open Question 2 reopens whether the browser self-check is mandatory, despite the agreed position...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261016-232147-general-4708`, finding `R1-002`
- Artifact: `docs/plans/feature-delivery-ui.md` (general)
- Base: `8f430e3` with uncommitted changes
- Claim: Open Question 2 reopens whether the browser self-check is mandatory, despite the agreed position and proposed delivery rule requiring it.
- Evidence: `docs/plans/feature-delivery-ui.md:20-22 requires rendering and self-check before review.`, `docs/plans/feature-delivery-ui.md:78-82 requires the check and recording its result, with an explicit rendering-unavailable path.`, `docs/plans/feature-delivery-ui.md:110-111 asks whether the check should occur only when the Plan selects it.`
- Proposed change: Keep the required self-check settled; narrow the question to where its evidence belongs in the Plan.
- Rationale: The browser self-check is agreed as required; narrow the open question to where its evidence is recorded when implementing.

## RB-0020: Plan item 1/2 reduces the Brief to purpose/users/main tasks/current boundary/future direction in...

- Type: `rejected`
- Status: `open`
- Priority: `none`
- Source: run `20261024-011924-general-1e47`, finding `R1-003`
- Artifact: `skills/coding/document-simplification/SKILL.md` (general)
- Base: `9554324` with uncommitted changes
- Claim: Plan item 1/2 reduces the Brief to purpose/users/main tasks/current boundary/future direction in 'roughly 4 sections, optional open issues'. That drops Product Constraints. The Brief owns confirmed product-level constraints whenever no Spec exists, and that stays the common case for small projects even after the Spec becomes optional. Without the section, those constraints have no owner.
- Evidence: `skills/coding/10.product-brief/SKILL.md:78,81-86 (Brief owns constraints when no Spec exists)`, `skills/coding/10.product-brief/assets/product-brief.template.md:23-25`, `skills/coding/README.md:37-39,180`
- Proposed change: Keep Product Constraints as a conditional section that is deleted when empty. The template already does this, so no new wording is needed.
- Rationale: The four-section outline did not authorize removing Product Constraints. Conditional ownership is retained explicitly in accepted R1-001 guidance; no constraint-removal defect is being introduced.

## RB-0021: The new 'Interview from concrete tasks' paragraph was inserted inside the Intent list, between th...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261024-011924-general-1e47`, finding `R2-001`
- Artifact: `skills/coding/document-simplification/SKILL.md` (general)
- Base: `9554324` with uncommitted changes
- Claim: The new 'Interview from concrete tasks' paragraph was inserted inside the Intent list, between the `write` and `review` bullets, with no blank line before the `review` bullet. This splits the list of three intents into two lists with a stray paragraph between them. A reader or agent scanning Intent now sees `review` cut off from the other two intents and attached to the interview paragraph. It also breaks the repository Markdown rule that paragraphs and lists are separated by blank lines.
- Evidence: `skills/coding/10.product-brief/SKILL.md:17-34 (list `explore`/`write` at 17-24, paragraph at 26-31, `- review` at 32 directly after the paragraph's last line)`, `AGENTS.md Markdown Style: 'Separate paragraphs, lists, tables, and fenced code with blank lines'`
- Proposed change: Move the interview paragraph after the Intent list, for example directly after line 34 or into Workflow step 2. Keep `explore`/`write`/`review` as one list. The wording does not need to change.
- Rationale: Valid nonblocking Markdown layout issue. The intent wording is unchanged; keep it out of another Producer revision. The host will tidy the list placement as a small direct formatting edit after this reviewed run closes, with no new behavior.

## RB-0022: The Architecture calls the Confluence conversion 'deterministic scripts plus MCP tools inside an...

- Type: `rejected`
- Status: `open`
- Priority: `none`
- Source: run `20261028-234946-general-82fc`, finding `R1-005`
- Artifact: `docs/diagram-conversion/architecture.md` (general)
- Base: `ada627a` with uncommitted changes
- Claim: The Architecture calls the Confluence conversion 'deterministic scripts plus MCP tools inside an assistant session'. But MCP tool results go back to the assistant model, not to a local script, and tool arguments are written by the model. Unless the host can hand raw MCP payloads to files, both page bodies and Whiteboard structures pass through the model twice: once to feed the script, once to pass the script's output to create/update. A long page or large Whiteboard JSON can then be silently changed, cut short or summarised. That undermines the 'deterministic' claim and the FS-CNF-003 rule that text and Whiteboards must not be lost. Assistant hosts also cap the size of MCP output (for example, Claude Code has a configurable MCP output token limit; from my knowledge, not checked in this session). OD3 doesn't test this transport path.
- Evidence: `docs/diagram-conversion/architecture.md:29 (assistant session calls deterministic scripts and MCP tools), :49 (deterministic conversion claim), :56 (attachments already fall back to curl/URL outside the tool payload), :84 (OD3 omits payload transport/size)`, `docs/diagram-conversion/functional-spec.md:39 (text and Whiteboard must not be lost)`
- Proposed change: Add one bounded question to OD3: on the company tenant and the chosen assistant host, can a full real page plus its Whiteboard be read and written without the model retyping the payload (for example, raw output saved to a file, or a size that fits under the host limit)? Also check whether MCP read/write already accepts or returns Markdown. If the model must relay the payload, record that the conversion is not deterministic end to end, and have the script check the published result against its own output before reporting success. Don't switch silently to REST. The fallback choice belongs to the product/architecture owners.
- Rationale: The host checked primary sources: MCP structuredContent is server-produced JSON, unrelated to model generation; current Claude Code documentation says oversized successful text results can be persisted to files. Thus mandatory model retyping/silent summary is not established. Keep concrete tenant/host payload transport as an OD3 validation question, not a proved architecture defect. Sources: modelcontextprotocol.io/specification/2025-06-18/server/tools and code.claude.com/docs/en/mcp.

## RB-0023: Images are explicitly important and Obsidian format is the standard. Yet the Spec leaves 'embed'...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261028-234946-general-82fc`, finding `R1-006`
- Artifact: `docs/diagram-conversion/architecture.md` (general)
- Base: `ada627a` with uncommitted changes
- Claim: Images are explicitly important and Obsidian format is the standard. Yet the Spec leaves 'embed' undecided, alongside optional extensions such as callouts. Meanwhile the Architecture binds images by 'local relative path'. In Obsidian-style notes, images are commonly written as `![[image.png]]` and resolved by vault name, not by relative path. An implementation following the Architecture would miss those images on publish and write them back to the wrong place. The FS-CNF-003 round-trip check would only catch this late, on real notes.
- Evidence: `docs/diagram-conversion/product-brief.md:26 (images important; Obsidian format as standard)`, `docs/diagram-conversion/functional-spec.md:39 (images must survive), :57 (embed syntax undecided)`, `docs/diagram-conversion/architecture.md:48 (relative image path → attachment ID), :49 ('本地图片')`
- Proposed change: Before Phase 2, look at a few real Work Hub notes to see which image syntax the author uses. Spec owner: take image embeds out of the open Obsidian-syntax question and put them in FS-CNF-001/003, leaving callouts and wikilinks open. Architecture owner: describe image identity as 'resolved file path' instead of 'relative path'. If wikilink embeds are in use, state that the Work Hub folder is resolved as an Obsidian vault.
- Rationale: Inspect actual notes before Phase 2 to settle Obsidian image syntax and vault resolution. No expanded syntax scope or assumption that Work Hub is a vault was approved for this revision.

## RB-0024: A Mermaid diagram stored as a separate file is a valid input, and every diagram must become a Whi...

- Type: `note-only`
- Status: `open`
- Priority: `medium`
- Source: run `20261028-234946-general-82fc`, finding `R1-007`
- Artifact: `docs/diagram-conversion/architecture.md` (general)
- Base: `ada627a` with uncommitted changes
- Claim: A Mermaid diagram stored as a separate file is a valid input, and every diagram must become a Whiteboard 'at its original position in the document'. But nothing defines how a note refers to a separate diagram file, which file's association entry owns that Whiteboard ID, or what happens when two notes refer to the same file and are published to two pages, where one Whiteboard ID slot would be overwritten. An implementer has to guess both the embed syntax and the binding owner.
- Evidence: `docs/diagram-conversion/product-brief.md:38 (embedded or separate file)`, `docs/diagram-conversion/functional-spec.md:18 (both valid inputs), :38 (Whiteboard at original position)`, `docs/diagram-conversion/architecture.md:48 (Whiteboard ID stored in 'the source file's' association data)`
- Proposed change: Question for Orch/author: how do notes refer to separate diagram files today, and is one diagram ever reused on several pages? If separate files are referenced from notes, state the syntax in FS-CNF-002. In the Architecture, key the Whiteboard binding by (note, diagram) rather than by the diagram file alone. If separate files are only edited on their own and never published inside a note, say so instead.
- Rationale: Standalone diagram embedding and multi-page reuse remain Phase-2 discovery questions. Do not invent an embed syntax or shared-publication requirement now.

## RB-0025: When association data is missing or doesn't match, the Architecture falls back to auto layout wit...

- Type: `note-only`
- Status: `open`
- Priority: `low`
- Source: run `20261028-234946-general-82fc`, finding `R1-008`
- Artifact: `docs/diagram-conversion/architecture.md` (general)
- Base: `ada627a` with uncommitted changes
- Claim: When association data is missing or doesn't match, the Architecture falls back to auto layout without telling anyone. Ordinary triggers will break the match: moving or renaming a note (for example, archiving out of Active), or the AI rewriting the fence and dropping the `%%` ID line. The author then sees an auto layout, may save over it, and the old geometry is left orphaned. The requirement that manual layout 'must be kept' is lost with no signal.
- Evidence: `docs/diagram-conversion/product-brief.md:40`, `docs/diagram-conversion/architecture.md:41 (`%%` ID inside the block), :42 (sidecar next to source file; silent fallback), :75 (invalid data → fall back only)`
- Proposed change: Keep the non-blocking fallback, but show a one-line notice when a diagram has a `%%` ID and no matching geometry (or when an entry for that ID exists but no longer fits), and don't prune unmatched entries on save. No extra machinery is needed.
- Rationale: Missing/mismatched layout feedback is useful for the future UI plan; preserve the note without adding recovery infrastructure to the confirmed-rules revision.
