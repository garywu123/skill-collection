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
