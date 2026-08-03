---
name: bootstrap-agent-guidance
description: Compile approved product, roadmap, architecture, governance, and repository evidence into concise AGENTS.md guidance and optional thin tool adapters. Use only when the current user explicitly asks to create, refresh, or audit project agent guidance; never infer authorization from lifecycle state or another skill.
---

# Bootstrap Agent Guidance

Treat `AGENTS.md` as a routing and operating contract. Point to domain truth;
never copy or replace the PRD, roadmap, architecture baseline, ADRs, feature
specifications, or lifecycle state.

## Authority and boundaries

- Require explicit authorization in the current user request for `create`,
  `refresh`, or `audit`. A pointer that says this work is allowed is not
  authorization.
- One named lifecycle authorization may span turns. A context that creates or
  resolves a human gate, or emits a blocked/terminal handoff, must stop after
  read-only reporting. Any gate decision, downstream lifecycle operation, or
  independent review must begin in a new minimal context explicitly authorized
  by the user and rebuilt from canonical state; a fork or worker does not grant
  new authorization.
- Never invoke another lifecycle skill, approve a gate, or advance another
  phase.
- Write only agent guidance files. Do not modify domain artifacts, code,
  lifecycle state by hand, or delivery status.
- For a new product, require an approved PRD and roadmap. Include architecture
  or governance only when its owning artifact is approved. For an existing
  repository audit, distinguish repository evidence from desired product truth.

Read `.specify/flow-state.yaml` first to verify active scope, revision,
approvals, and canonical paths. Query the index only through `resolve --id` or
`resolve --path`. If state, the resolved slice, the user's request, and an
artifact conflict, stop and report the conflict.

Then read only the sources needed for the requested targets:

1. approved product and roadmap artifacts;
2. approved architecture, ADR, constitution, and governance artifacts in scope;
3. existing root and scoped agent guidance;
4. manifests, CI, test configuration, and representative files needed to verify
   paths, commands, or boundaries;
5. explicitly scoped legacy material, as reference only.

Use headings, IDs, and repository search before opening full documents. Root
guidance needs the roadmap's canonical path and status conventions, not every
feature body; never load all feature specifications to generate `AGENTS.md`.

Keep each opened slice at or below 8 KiB and the initial target payload at or
below 24 KiB. Beyond that, inspect path/command batches in fresh workers and
merge only verified facts, citations, conflicts, and a coverage ledger
(`| Batch | Stable IDs / paths | Result | Evidence |`). Never claim a complete
audit while a required batch is uncovered or truncated.

Select at most one runtime reference. Read
[artifact contract](references/artifact-contract.md) for a canonical-guidance
operation only when source ownership or precedence is unclear. Read
[tool compatibility](references/tool-compatibility.md) instead when a Claude or
Copilot adapter is requested; the ownership rules in this Skill remain
sufficient. If that operation also exposes an unresolved precedence conflict,
report it and stop rather than loading both references. Verify current official
behavior when compatibility determines the result.

Classify candidate statements as `Approved`, `Verified`, `Legacy reference`,
`Unknown`, or `Conflict`. Omit `Unknown`; surface `Conflict`. Never turn current
implementation or legacy behavior into desired behavior without an approved
source.

## Deterministic state command

```text
python <this-skill-dir>/../flow-state/scripts/flow_state.py --root . <operation> [options]
```

`flow-state/` deploys as this directory's sibling. Use `--help` for options;
never hand-edit state, index, or bundle tables. Use `<revision-from-status>`
for the first write in a context, then the revision each command returns; on
`stale revision` stop and report the conflict rather than retrying.

```text
start --expect-revision <revision-from-status> \
  --kind project --work-id <project-id> --stage agent_guidance

record-output --expect-revision <revision-returned-by-start> \
  --stage agent_guidance --artifact agent_guidance=AGENTS.md \
  --next "bootstrap-agent-guidance review"
```

Add `--check-only` to `record-output` to validate before writing. This skill
never runs `decide`: a later explicit generic approval supplies actor, date, and
evidence and creates the indexed decision receipt.

| Operation and scope | `kind` | `work-id` | `stage` |
|---|---|---|---|
| `create` | `project` | `pointer.project.id` | `agent_guidance` |
| project-wide `refresh` | `project` | `pointer.project.id` | `agent_guidance` |
| CR-scoped `refresh` | `change_request` | the authorized `CR-ID` | `agent_guidance` |

Run `start` only when the request explicitly asks for `create` or `refresh`, the
scope selects exactly one row, and prerequisites pass. Require an explicit
CR-ID for a CR-scoped refresh; never allocate or guess one. `audit` is read-only
and never starts or changes lifecycle state.

## Owned outputs

| Mode | Prerequisite | Creates or modifies |
|---|---|---|
| `create` | Explicit request; required sources approved | Root or scoped `AGENTS.md`; requested thin adapters |
| `refresh` | Explicit request; canonical guidance exists | Only stale guidance affected by changed approved or verified evidence |
| `audit` | Explicit request | No files unless the user also authorizes fixes |

Use root `AGENTS.md` as the cross-tool canonical file. Create nested
`AGENTS.md` only for materially different subtree commands or constraints. Use
the Claude and Copilot templates only when those consumers are in scope.
Register the root canonical guidance under state role `agent_guidance`; adapters
remain derived evidence, not competing canonical roles.

## Workflow

1. Resolve mode, target consumers, target paths, and canonical inputs. Ask only
   when multiple plausible sources or targets remain.
2. Inventory evidence and conflicts. Before writing, report source precedence,
   targets, verified commands, unresolved gaps, and any proposed nested scope.
3. Generate the smallest useful guidance with
   [the AGENTS checklist](assets/AGENTS.template.md). Prefer links and routing
   over summaries. Preserve valid human rules and reconcile conflicts visibly.
4. Keep wrappers derived and minimal. Do not maintain independent copies of
   universal rules.
5. Validate, record the result, report, and stop.

## Validation

Run the bundled validator against generated guidance:

```powershell
pwsh -NoProfile -File <this-skill-dir>/scripts/Test-AgentGuidance.ps1 -ProjectRoot <project-root>
```

Use `powershell.exe` if `pwsh` is unavailable. Add `-RequireClaude` or
`-RequireCopilot` only for requested adapters. Also verify that every command
and path has evidence, wrappers do not conflict, and feature work routes to one
feature rather than absorbing the whole roadmap.

An `audit` leaves lifecycle state unchanged.

Report targets changed, canonical versus derived status, approved and verified
sources used, conflicts or omitted unknowns, validation results, and the next
recommended human action. Stop; do not invoke that action.
