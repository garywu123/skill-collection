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
