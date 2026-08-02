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
- Never invoke another lifecycle skill, approve a gate, or advance another
  phase.
- Write only agent guidance files. Do not modify domain artifacts, code,
  lifecycle state by hand, or delivery status.
- For a new product, require an approved PRD and roadmap. Include architecture
  or governance only when its owning artifact is approved. For an existing
  repository audit, distinguish repository evidence from desired product truth.

Map an already-authorized state-changing operation to deterministic `start`
exactly as follows:

| Operation and scope | `kind` | `work-id` | `stage` |
|---|---|---|---|
| `create` | `project` | `pointer.project.id` | `agent_guidance` |
| project-wide `refresh` | `project` | `pointer.project.id` | `agent_guidance` |
| CR-scoped `refresh` | `change_request` | the explicitly authorized `CR-ID` | `agent_guidance` |

These mappings do not grant authority. Run `start` only when the current user
explicitly requests `create` or `refresh`, the scope selects exactly one table
row, and prerequisites pass; never infer it from the pointer or a recommendation.
For a CR-scoped refresh, require the current request to identify the CR-ID;
never allocate or guess one. Read the expected revision immediately before each
state-changing command and use the revision returned by the preceding command;
never hard-code or calculate it. `audit` is read-only and never starts or
changes lifecycle state.

## State and source contract

When present, read `.specify/flow-state.yaml` first. Use it only to verify the
active scope, current revision, approvals, and canonical paths. Query the
artifact index next through the deterministic `resolve` command by ID or path.
Open `.specify/artifact-index.yaml` in full only when it is clearly small. If
state, the resolved index slice, the user's request, and an artifact conflict,
stop and report the conflict.

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

Read [artifact contract](references/artifact-contract.md) when source ownership
or precedence is unclear. Read [tool compatibility](references/tool-compatibility.md)
only when Claude or Copilot output is requested; verify current official behavior
when compatibility determines the result.

Classify candidate statements as `Approved`, `Verified`, `Legacy reference`,
`Unknown`, or `Conflict`. Omit `Unknown`; surface `Conflict`. Never turn current
implementation or legacy behavior into desired behavior without an approved
source.

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

## Validation and state recording

Run the bundled validator against generated guidance:

```powershell
pwsh -NoProfile -File <skill-dir>/scripts/Test-AgentGuidance.ps1 -ProjectRoot <project-root>
```

Use `powershell.exe` if `pwsh` is unavailable. Add `-RequireClaude` or
`-RequireCopilot` only for requested adapters. Also verify that every command
and path has evidence, wrappers do not conflict, and feature work routes to one
feature rather than absorbing the whole roadmap.

For `create` or `refresh`, if the project provides a deterministic lifecycle
command, use it to validate state, register changed artifact paths/hashes in the
artifact index, and record this operation as `ready_for_review` with a
recommended next human action. Do not edit shared YAML directly or record
`approved`. If no command exists, leave the YAML unchanged and include the
proposed record in the report. An `audit` leaves lifecycle state unchanged.

Report targets changed, canonical versus derived status, approved and verified
sources used, conflicts or omitted unknowns, validation results, and the next
recommended human action. Stop; do not invoke that action.
