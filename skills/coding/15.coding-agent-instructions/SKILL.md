---
name: coding-agent-instructions
description: Create, refresh, or audit a software project's agent instruction files - the canonical AGENTS.md plus thin CLAUDE.md and .github/copilot-instructions.md adapters - for a repository that contains code, including one that also holds documentation. Invoke explicitly, by name, to set up, update, or check project agent guidance, custom instructions, memory, or context files for Claude Code, Codex, or GitHub Copilot. Do not use it for a repository with no code, such as a documentation, analysis, presentation, or operations workspace; do not use it to create product direction, feature plans, code, presentations, reports, or reusable Skills; and do not write code-style rules, which the code-style Skill owns in docs/code-style.md.
disable-model-invocation: true
---

# Coding Agent Instructions

Give every project agent working in a software repository one short routing
contract. `AGENTS.md` is canonical. The other files are thin adapters and never
hold a second editable copy of a universal rule.

This Skill covers repositories that contain code, including one that also holds
documentation. A repository with no code belongs to its own collection's agent
instruction Skill; report that and stop instead of writing files for it.

Route to applicable project documents instead of copying them. Product Briefs,
Feature Maps, and other lifecycle documents are routes only when the repository
actually uses them. This Skill creates agent instructions, not project content.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `write`: create or refresh the instruction files. This is the default.
- `audit`: report broken routes, unverified commands, duplicated rules, and
  adapter conflicts without changing a file. Use it when the user asks to check
  or review existing guidance.

## Output

For `write` intent, write all three instruction files unless the user names
fewer tools or the project clearly targets one. For `audit` intent, inspect the
same applicable files but do not change them.

This Skill may create, refresh, or audit only these files. It may read
code-quality configuration as evidence, but it must not modify that
configuration.

| File | Holds |
|---|---|
| `AGENTS.md` | Canonical routing, precedence, verified commands and checks, working rules |
| `CLAUDE.md` | An `@AGENTS.md` import plus verified Claude-only differences |
| `.github/copilot-instructions.md` | A pointer to `AGENTS.md` plus Copilot-only rules |
| Optional scoped instructions | Only a user-requested or verified subtree/surface difference; never a second universal rule set |

Code style always lives in `docs/code-style.md`, owned by the `code-style`
Skill. Route `AGENTS.md` to that file and write no code-style rule here. When
the file does not exist yet, omit the route and report that `code-style` should
run.

Create or update `AGENTS.md` from [the template](assets/agents.template.md) and
keep it within 100 source lines. At 80 lines, review duplicated explanations,
nonexistent routes, empty sections, and rules that belong in a linked document
or scoped `AGENTS.md`. Do not meet the limit by removing required
communication, precedence, safety, scope, verification, or reporting rules, or
by compressing natural language, commands, or paths. Write the adapters as
derived wrappers:

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

Do not copy project purpose, domain content, plans, status, technical direction,
architecture, or results into these files. Do not create product direction,
feature plans, code, presentations, or reports. Do not add approval metadata,
stage gates, a state file, or a second process description.

State a command or check only when project configuration, automation, or an
observed successful run verifies it. Omit every unverified item instead of
guessing.

## Workflow

1. Read repository guidance, existing instruction files, applicable governing
   and task documents, and only the configuration needed to verify paths,
   commands, and checks. Read Product Briefs or Feature Maps only when present
   and relevant. When branch naming, merge/rebase, release, hotfix, tag,
   worktree, or cross-repository branch coordination is material, read the
   [branch policy guidance](references/branch-style.md). It is independent of
   language.
2. Confirm from user, document, and repository evidence that the repository
   contains code, packages, or services. When it holds no code, report that it
   needs its own collection's agent instruction Skill and stop. When the
   evidence is ambiguous, report the gap and do not guess.
3. Detect the relevant language and tooling surfaces only far enough to verify
   the commands and checks `AGENTS.md` will list. Treat all code-quality
   configuration as read-only evidence. Do not derive code-style rules here;
   report that `code-style` should run when `docs/code-style.md` is missing or
   stale.
4. Classify each candidate statement as explicit user direction, approved by a
   document or configuration, verified by repository evidence, or unknown. Use
   evidence in that order; omit inferred defaults and unknowns, and report
   conflicts. Never promote observed behavior into intended behavior without
   approval.
5. Route Product Briefs, Feature Maps, and Feature Plans only for projects that
   use them. When no governing project-purpose document or stated direction
   exists, omit that route and report the gap; do not invent or create it.
6. Preserve human-written sections that are still valid, and reconcile a
   conflicting rule visibly instead of deleting it silently.
7. For `write`, write `AGENTS.md`, then derive the adapters from it. For
   `audit`, report findings without writing any file.
8. Run the consistency check.

Read [tool compatibility](references/tool-compatibility.md) only when the user
requests nested, path-scoped, or surface-specific files, or verified repository
differences require them. Otherwise write only the three root instruction files.

## Consistency Check

Before finishing, confirm every routed path exists, every listed command or
check is verified, `CLAUDE.md` imports `@AGENTS.md`, and no code-style rule
remains in `AGENTS.md` or an adapter once `docs/code-style.md` exists. Keep
project meaning, domain content, direction, task status, implementation, and
results in their applicable documents; replace repeated prose here with a
route. Remove any adapter rule that duplicates or contradicts `AGENTS.md`. Fix
stale names, paths, and commands in these files when the correction is
mechanical, and
report a conflict that needs a project, domain, technical, or ownership
decision. Count the generated `AGENTS.md` source lines. Review it at 80 lines
and reject output over 100 lines without weakening its protected rules or
natural language.

## Completion

Report the files written or audited, the sources used, the statements omitted as
unverified, unresolved conflicts, and remaining gaps. Recommend a refresh when
governing documents, verified commands or checks, or repository conventions
later change. Stop without creating product direction, feature plans, code,
presentations, or reports.
