# Bootstrap Agent Guidance

Generate a small, evidence-backed operating manual for your coding agents — the files that tell Codex, Claude Code, and GitHub Copilot *how* to work in your specific project.

**Full skill instructions:** [SKILL.md](SKILL.md)

---

## What it does

Reads your approved product documents (PRD, feature roadmap, architecture records, build files, CI config) and produces one or more of:

| Output file | Consumed by |
|-------------|-------------|
| `AGENTS.md` | Codex, Claude Code (via `@AGENTS.md`), Copilot (where supported) |
| `CLAUDE.md` | Claude Code — thin wrapper that imports `AGENTS.md` + Claude-specific overrides |
| `.github/copilot-instructions.md` | GitHub Copilot chat |

Every statement in the output is classified as **Approved** (from a product artifact), **Verified** (from a real file or CI step), or omitted. Nothing is invented.

---

## When to use

- After your PRD and feature roadmap are approved, **before** you start specifying or implementing features.
- When onboarding an existing repository — create baseline guidance from what the codebase already does.
- When the project scope changes significantly (new architecture decision, major PRD update) and the guidance files are stale.

**Position in the overall workflow:**
[spec-driven-flow.md](../spec-driven-flow.md) → this skill runs between *roadmap approval* and *Spec Kit specify*.

---

## Example

### Scenario

You have just finished the product discovery phase for a Warehouse Management System (WMS). The following are approved and committed:

- `doc/general-product-requirement.md` — defines the WMS scope, users, and constraints
- `doc/feature-roadmap.md` — lists features in priority order with delivery phases

Now you want to set up coding agents so they understand the stack, conventions, and which directories own which concerns.

### Step 1 — Invoke the skill

In VS Code Copilot chat:

```
/bootstrap-agent-guidance
```

The skill reads your approved documents and inspects the repository (manifests, CI, existing source).

### Step 2 — Review the evidence inventory

The skill presents a short proposal before writing anything:

```
Sources:
  [Approved]  doc/general-product-requirement.md  — WMS scope, user roles, constraints
  [Approved]  doc/feature-roadmap.md               — 6 features, Phase 1 = Receiving + Putaway
  [Verified]  package.json                         — Node 20, Express, Prisma, Vitest
  [Verified]  .github/workflows/ci.yml             — lint → test → build pipeline
  [Unknown]   Architecture record                  — not found, will be omitted

Target files:  AGENTS.md (create),  CLAUDE.md (create)
```

You confirm or correct the proposal.

### Step 3 — Generated output (excerpt)

```markdown
# AGENTS.md

## Project
Warehouse Management System — Phase 1 scope: Receiving and Putaway.
Source: doc/general-product-requirement.md (approved 2026-07-10).

## Stack
- Runtime: Node 20 / TypeScript
- Framework: Express 4
- ORM: Prisma (PostgreSQL)
- Tests: Vitest — run with `npm test`
- CI: GitHub Actions — lint → test → build

## Directory map
| Path | Responsibility |
|------|---------------|
| src/receiving/ | Inbound shipment processing |
| src/putaway/   | Location assignment & barcode scan |
| src/shared/    | Cross-cutting utilities — no domain logic |

## Constraints (from PRD)
- All location assignments must validate against the location master table.
- Barcode scan operations must be idempotent.
```

### Step 4 — Commit and use

Commit `AGENTS.md` and `CLAUDE.md`. Every subsequent Spec Kit or coding-agent session will read these files automatically and stay aligned with the approved product intent.

---

## Reference

- [Artifact contract](references/artifact-contract.md) — defines what counts as an approved source
- [Tool compatibility](references/tool-compatibility.md) — Codex vs Claude Code vs Copilot differences
- [Validation script](scripts/Test-AgentGuidance.ps1) — checks the generated files for common issues
