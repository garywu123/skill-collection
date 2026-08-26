---
name: agent-instructions
description: Create, refresh, or audit a project's coding-agent instruction files - the canonical AGENTS.md plus the thin CLAUDE.md and .github/copilot-instructions.md adapters - from the Product Brief, existing documents, and verified repository evidence. Use when the user asks to set up, update, or check agent guidance, custom instructions, memory, or context files for Claude Code, Codex, or GitHub Copilot. Do not use it to decide product scope or technical direction, plan or implement a feature, or author reusable Skills.
---

# Agent Instructions

Give every coding agent working in a project one short routing contract.
`AGENTS.md` is canonical. The other files are thin adapters and never hold a
second editable copy of a universal rule.

Route to the project's documents instead of copying them. This Skill can run as
soon as a Product Brief exists, because product meaning stays in the brief and
technical direction stays in the Feature Map.

## Intent

Infer the intent from natural language.

- `write`: create or refresh the instruction files. This is the default.
- `audit`: report broken routes, unverified commands, duplicated rules, and
  adapter conflicts without changing a file. Use it when the user asks to check
  or review existing guidance.

## Output

Write all three files, unless the user names fewer tools or the project clearly
targets one.

| File | Holds |
|---|---|
| `AGENTS.md` | Canonical routing, precedence, verified commands, working rules |
| `CLAUDE.md` | An `@AGENTS.md` import plus verified Claude-only differences |
| `.github/copilot-instructions.md` | A pointer to `AGENTS.md` plus Copilot-only rules |

Create or update `AGENTS.md` from [the template](assets/agents.template.md) and
keep it under 60 lines. Write the adapters as derived wrappers:

```markdown
@AGENTS.md

## Claude Code differences

- Add only verified Claude-specific rules here.
```

```markdown
# Copilot Instructions

<!-- Derived from AGENTS.md. Change universal rules there. -->

- Follow the routing, precedence, commands, and working rules in the repository
  root `AGENTS.md`.
- Add only Copilot-specific rules below this line.
```

Do not copy product purpose, user lists, MVP boundary, feature tables, feature
status, technical direction, architecture, or test results into any of these
files. Do not add approval metadata, stage gates, a state file, or a second
process description.

State a command only when a manifest, CI configuration, or an observed
successful run verifies it. Omit every unverified command instead of guessing.

## Workflow

1. Read repository guidance, `docs/product-brief.md`, `docs/feature-map.md` when
   present, the existing instruction files, and the manifests, CI, and test
   configuration needed to verify commands and paths. Do not open every Feature
   Plan.
2. Classify each candidate statement as approved by a document, verified by
   repository evidence, or unknown. Write the first two, omit unknowns, and
   report conflicts. Never promote current code behavior into intended behavior
   without an approving document.
3. When no Product Brief and no stated product direction exist, omit the product
   line and report the gap. Do not invent product purpose or create the brief
   here.
4. Preserve human-written sections that are still valid, and reconcile a
   conflicting rule visibly instead of deleting it silently.
5. Write `AGENTS.md`, then derive the adapters from it.
6. Run the consistency check.

Read [tool compatibility](references/tool-compatibility.md) only when the user
needs nested, path-scoped, or surface-specific files beyond these three.

## Consistency Check

Before finishing, confirm every routed path exists, every listed command is
verified, and `CLAUDE.md` imports `@AGENTS.md`. Keep product meaning in the
brief, technical direction and feature status in the map, and implementation and
results in Feature Plans; replace repeated prose here with a route. Remove any
adapter rule that duplicates or contradicts `AGENTS.md`. Fix stale names, paths,
and commands in these files when the correction is mechanical, and report a
conflict that needs a product, technical, or ownership decision.

## Completion

Report the files written or audited, the sources used, the statements omitted as
unverified, unresolved conflicts, and remaining gaps. Recommend a refresh when
the Feature Map, build commands, or directory conventions later change. Stop
without planning or implementing a feature.
