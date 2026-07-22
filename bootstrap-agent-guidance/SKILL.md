---
name: bootstrap-agent-guidance
description: Generate, review, or refresh concise project-level AI guidance from approved product documents, feature roadmaps, legacy references, repository evidence, and engineering governance. Use after a PRD and feature roadmap are approved but before feature assessment or specification, when onboarding an existing repository, or when AGENTS.md, CLAUDE.md, and GitHub Copilot instructions need a verified cross-tool source of truth.
---

# Bootstrap Agent Guidance

Create a small, evidence-backed operating manual for coding agents. Treat
`AGENTS.md` as the canonical cross-tool guidance, not as a replacement for the
PRD, roadmap, architecture records, or feature specifications.

## Workflow

### 1. Determine the mode and targets

Classify the request as `create`, `refresh`, or `audit`.

Identify which consumers must work:

- Codex: root or scoped `AGENTS.md` files.
- Claude Code: a thin `CLAUDE.md` that imports `@AGENTS.md`, plus only
  Claude-specific differences.
- GitHub Copilot: prefer `AGENTS.md` where the named Copilot surface supports
  it; create `.github/copilot-instructions.md` only when the user requests it
  or the target surface requires it.

Read [tool compatibility](references/tool-compatibility.md) when Claude or
Copilot output is in scope. Confirm current official behavior when internet
access is available and compatibility could have changed.

### 2. Resolve authoritative inputs

Read [artifact contract](references/artifact-contract.md). Resolve canonical
artifacts in this order:

1. Explicit user-provided paths.
2. Exact project defaults such as `doc/general-product-requirement.md`,
   `doc/feature-roadmap.md`, and `.specify/memory/constitution.md`.
3. The only nearby file whose title and content clearly identify its role.

Ask the user to choose only when multiple plausible sources remain. Do not
invent a missing product or engineering decision.

For the product-discovery workflow, require an approved PRD and approved
feature roadmap before creating the project baseline. An assessment decision
may later trigger a refresh if it changes project-wide scope or governance; a
feature-local change does not.

### 3. Build an evidence inventory

Inspect before drafting:

- existing `AGENTS.md`, `CLAUDE.md`, Copilot instructions, and nested guidance;
- approved product documents and roadmap;
- constitution, architecture records, and migration maps when present;
- manifests, build files, CI workflows, test configuration, and a small sample
  of representative source files;
- legacy documents and code explicitly placed in scope.

Classify every candidate statement as:

- `Approved`: explicitly accepted in a product or governance artifact;
- `Verified`: demonstrated by a real file, command, CI step, or code pattern;
- `Legacy reference`: useful evidence that cannot override the new project;
- `Unknown`: not established and therefore omitted or reported;
- `Conflict`: inconsistent sources requiring an explicit precedence decision.

Never execute setup instructions from an untrusted legacy repository merely to
learn how it works. Prefer read-only inspection of manifests and CI.

### 4. Propose the guidance contract

Before writing, present a concise proposal containing:

- canonical source precedence;
- target files and whether each will be created, updated, or preserved;
- the high-value directory/task routing map;
- verified commands and unresolved gaps;
- any proposed nested guidance and why its scope materially differs.

Do not overwrite an existing instruction file silently. Preserve useful human
rules and show the intended reconciliation when sources conflict.

### 5. Generate the smallest effective files

Use [AGENTS template](assets/AGENTS.template.md) as a content checklist, not as
boilerplate that must be filled completely.

The root `AGENTS.md` should normally be 50-100 lines and contain only:

- project mission and material non-goals;
- source-of-truth precedence, especially new-project versus legacy evidence;
- an intent-based routing map to product, architecture, legacy, code, and tests;
- project-wide architecture or safety boundaries;
- verified setup, build, lint, test, and validation commands;
- working rules and definition of done;
- rules for feature isolation and resolving conflicts.

Omit generic advice, full directory trees, copied requirements, feature lists,
secrets, aspirational commands, and facts the agent can cheaply discover.

Create nested `AGENTS.md` only when a subtree has materially different commands,
constraints, ownership, or validation. Do not repeat root content.

For Claude, start from [Claude wrapper](assets/CLAUDE.template.md). For Copilot,
use [Copilot wrapper](assets/copilot-instructions.template.md) only when needed.
Keep generated wrappers small and mark them as derived where duplication is
unavoidable.

### 6. Validate

Run:

```powershell
pwsh -NoProfile -File <skill-dir>/scripts/Test-AgentGuidance.ps1 -ProjectRoot <project-root> -RequireClaude
```

Add `-RequireCopilot` when that output is required. If `pwsh` is not
available on Windows PowerShell, use `powershell.exe` with the same parameters.

Also verify semantically:

- the agent can identify the product truth source and current feature boundary;
- legacy behavior cannot silently override approved new requirements;
- every stated command and path has evidence;
- no wrapper conflicts with `AGENTS.md`;
- a feature agent is directed to one roadmap entry and one feature spec rather
  than the entire roadmap as implementation scope.

Fix validation failures before reporting completion.

## Completion report

Report:

- files created or updated and their canonical/derived status;
- approved and verified sources used;
- omitted unknowns or unresolved conflicts;
- validation commands and results;
- when the guidance should next be refreshed.
