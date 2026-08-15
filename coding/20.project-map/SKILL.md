---
name: project-map
description: Create, refresh, or audit the project map - AGENTS.md routing, roadmap.yaml state, and the folder structure record - from approved product, roadmap, architecture, governance, and repository evidence. Use when the user explicitly asks to set up, update, or check a project's agent guidance, document routing, or recorded stage and function status. Records state; never gates a transition, approves work, or invokes another skill.
---

# Project Map

Own the map, not the territory. `AGENTS.md` routes to domain truth, `roadmap.yaml`
records where the project is, and neither one ever copies the PRD, roadmap,
architecture baseline, ADRs, or feature implementation plans.

## Owned files

| File | Holds |
|---|---|
| `roadmap.yaml` | Stage, document routes, one line per function |
| `AGENTS.md` | Agent routing, boundaries, verified commands |
| Nested `AGENTS.md` | Only a subtree with materially different commands or constraints |
| Thin adapters | `CLAUDE.md`, Copilot instructions, when those consumers are in scope |

Write nothing else. Domain artifacts, code, and specs belong to their own
skills. This skill owns the map schema, initialization, project-wide refresh,
and audit; the skill performing authorized work updates only the map fields
that its work directly changed.

## Record, never gate

This skill writes down what stage things are in. It does not decide whether a
transition is allowed, approve a document, or set a function to `accepted`.

- Recording is a line in `roadmap.yaml`.
- Gating is a decision, and the human owns every one of them.

`roadmap.yaml` is a shared bookkeeping file with bounded writers:

- `project-map` owns its schema and whole-file integrity;
- a product, architecture, UI, specification, implementation, or verification
  operation may update only the `docs` route or function entry it directly
  changed;
- no operation advances unrelated entries or records a state it did not
  establish with repository evidence.

If the requested change would move a function to `accepted`, stop and say that
acceptance happens by checklist verification in a fresh conversation.

## Operations

| Operation | Prerequisite | Creates or modifies |
|---|---|---|
| `init` | Explicit request; a repository without a map | `roadmap.yaml`; `AGENTS.md`; requested adapters |
| `refresh` | Explicit request; a map already exists | Only the entries and guidance affected by changed evidence |
| `audit` | Explicit request | Nothing, unless the user also authorizes fixes |

Require the operation in the current user request. Never infer it from the state
of the repository, and never continue into another operation afterwards.

## Sources

Read `roadmap.yaml` first when it exists. Then read only what the requested
target needs:

1. approved product and roadmap artifacts;
2. approved architecture, ADR, and governance artifacts in scope;
3. existing root and scoped agent guidance;
4. manifests, CI, and test configuration needed to verify paths and commands;
5. explicitly scoped legacy material, as reference only.

Use headings, IDs, and repository search before opening whole documents. Root
guidance needs the roadmap's path and status conventions, not every function
body; never load all feature specifications to write `AGENTS.md`.

Keep each opened slice at or below 8 KiB and the initial payload at or below
24 KiB. Beyond that, inspect path and command batches separately and merge only
verified facts, citations, conflicts, and a coverage ledger
(`| Batch | Paths | Result | Evidence |`). Never claim a complete audit while a
required batch is uncovered or truncated.

Classify every candidate statement as `Approved`, `Verified`, `Legacy
reference`, `Unknown`, or `Conflict`. Omit `Unknown`; surface `Conflict`. Never
promote current implementation or legacy behavior into desired behavior without
an approved source.

## References

Select at most one. Read
[the artifact contract](references/artifact-contract.md) when source ownership
or precedence is unclear. Read
[the roadmap specification](references/roadmap-spec.md) when writing or
repairing `roadmap.yaml` fields and statuses. Read
[tool compatibility](references/tool-compatibility.md) when a Claude or Copilot
adapter is requested. If an operation exposes an unresolved precedence conflict,
report it and stop rather than loading a second reference.

## Workflow

1. Resolve the operation, target consumers, target paths, and canonical inputs.
   Ask only when multiple plausible sources or targets remain.
2. Inventory evidence and conflicts. Before writing, report source precedence,
   targets, verified commands, and unresolved gaps.
3. Write the smallest useful map:
   - `roadmap.yaml` from [the template](assets/roadmap.template.yaml), following
     [the specification](references/roadmap-spec.md);
   - `AGENTS.md` from [the template](assets/AGENTS.template.md), preferring
     `roadmap.yaml` role/entry lookups over copied paths, feature lists, or
     summaries;
   - function `domain`, `plan`, optional `spec`, and `checklist` routes come from
     the approved roadmap and the owning feature-planning workflow. Record them;
     do not create their content.
4. Preserve valid human-written rules and reconcile conflicts visibly.
5. Keep adapters derived and minimal. Never maintain a second copy of a
   universal rule.
6. Validate, report, and stop.

Before the final response, reconcile `roadmap.yaml` with the routed artifacts
and function state changed in this turn. Update it only when those facts
changed; do not create a map diff merely to record that an operation ran.

## Validation

```powershell
pwsh -NoProfile -File <this-skill-dir>/scripts/Test-AgentGuidance.ps1 -ProjectRoot <project-root>
```

Use `powershell.exe` if `pwsh` is unavailable. Add `-RequireClaude` or
`-RequireCopilot` only for requested adapters. Then confirm by inspection that
every command and path has evidence, that adapters do not contradict the root
file, that `roadmap.yaml` parses, and that each function entry has the approved
roadmap's domain key and points at files that exist. Report profile drift,
missing domain keys, or incomplete plan/checklist routes.

Report targets changed, canonical versus derived status, sources used, conflicts
or omitted unknowns, validation results, and the next recommended human action.
Stop; do not take that action.
