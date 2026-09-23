---
name: code-style
description: Create, refresh, or audit a project's docs/code-style.md - the single normative code-style contract covering module boundaries, file and code structure, comment intent, API documentation, and explanation of key steps and algorithms - with one section per language the repository actually uses, then update the AGENTS.md route to it. Invoke explicitly, by name, to set up, extend, or review coding conventions, comment rules, or documentation rules for a project. Do not use it to author AGENTS.md routing or tool adapters, to modify formatter, linter, or analyzer configuration, or to write product direction, feature plans, or application code.
disable-model-invocation: true
---

# Code Style

Produce one normative code-style contract for a repository:
`docs/code-style.md`. Every language the repository actually uses gets a
section; a language it does not use gets none.

This Skill is prescriptive, not merely descriptive. Where tooling already
enforces a rule, route to that tooling. Where tooling cannot enforce a rule -
module boundaries, structure, comment intent, documentation, explanation of key
algorithms - decide the rule with the user and write it as an instruction an
agent can follow without further interpretation.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `write`: create or refresh `docs/code-style.md` and its `AGENTS.md` route.
  This is the default.
- `audit`: report missing language sections, rules contradicted by current
  tooling configuration, unfollowable prose, and a broken or absent `AGENTS.md`
  route, without changing a file.

## Output

| File | This Skill may |
|---|---|
| `docs/code-style.md` | Create and rewrite it from [the template](assets/code-style.template.md) |
| `AGENTS.md` | Only add or correct the single route to `docs/code-style.md`, and remove a code-style rule that the style file now owns |
| Formatter, linter, analyzer, build, and package configuration | Read as evidence only; never create or modify |

Everything else in `AGENTS.md`, the `CLAUDE.md` and Copilot adapters, and any
scoped instruction file belongs to `coding-agent-instructions`. Report a
needed change there instead of making it.

Keep `docs/code-style.md` under 200 lines and each language section under about
12 rules. Beyond that, route to configuration or to an existing project document
rather than expanding the file.

## Language Coverage

Detect candidate languages from repository evidence, then confirm the set with
the user in one question before writing. State what was detected, what will be
included, and what will be excluded. Include a language the user names even
without repository evidence yet, and exclude one they reject.

Read a language reference only for a confirmed language:

- [C#](references/code-style-csharp.md) for C# or .NET evidence;
- [Frontend](references/code-style-frontend.md) for HTML, CSS, JavaScript,
  TypeScript, or a frontend framework;
- [Python](references/code-style-python.md) for Python evidence;
- [EditorConfig baseline](references/editorconfig-baseline.md) when
  `.editorconfig` is present or cross-language file hygiene is material.

A confirmed language with no reference here - SQL, Go, Java, shell, and others -
still gets a section. Build it from the cross-language rules in the template,
the repository's own configuration and prevailing patterns, and the user's
answers. Do not add a reference file for it as part of this run.

## Workflow

1. Read `AGENTS.md`, any existing `docs/code-style.md`, and the configuration
   needed to identify languages and enforcement: project and package manifests,
   `.editorconfig`, formatter, linter, analyzer, and type-checker settings, and
   the commands CI or repository scripts actually run.
2. Confirm the language set with the user as described above.
3. Read the confirmed languages' references.
4. Split every candidate rule into enforced and unenforced. A rule a configured
   formatter, linter, analyzer, or type checker already applies is enforced:
   name the authoritative surface and its verified command, and do not restate
   the rule. Everything else is unenforced and must be written out.
5. Decide each unenforced rule by explicit user direction, then an approved
   project document, then a consistent repository pattern the user confirms.
   When none of those settle it, ask or omit; never present an observed pattern
   as policy without confirmation.
6. Write `docs/code-style.md` from the template. Keep the cross-language section
   for every project. Preserve a human-written rule that is still valid, and
   reconcile a conflicting rule visibly instead of deleting it silently.
7. Update `AGENTS.md` so it routes to `docs/code-style.md` and holds no
   code-style rule of its own. Add the route when it is missing, correct it when
   it is stale, and move a code-style rule found there into the style file.
   Change nothing else in `AGENTS.md`.
8. Run the consistency check.

State a command only when repository configuration, automation, or an observed
successful run verifies it. Omit an unverified command rather than guessing.

## Consistency Check

Confirm that every confirmed language has exactly one section and no unused
language has one; that no written rule contradicts current formatter, linter,
analyzer, or type-checker configuration; that every routed path and command
exists and is verified; that `AGENTS.md` routes to `docs/code-style.md` and
retains no code-style rule; and that each rule is an instruction an agent can
apply, not a topic heading. Fix a stale name, path, or command here when the
correction is mechanical. Report a conflict that needs a technical or ownership
decision.

## Completion

Report the languages included and excluded, the rules routed to tooling versus
written out, the `AGENTS.md` route change, unresolved conflicts, and the
questions left open. Recommend a refresh when the language set, tooling, or
enforcement configuration later changes. Stop without modifying tooling
configuration, other instruction files, or application code.
