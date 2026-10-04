---
name: code-style
description: Define, audit, or apply a project's code-style contract - docs/code-style.md plus scoped subproject style files only for genuine local differences - covering file and code structure, in-code module organization, comment intent, API documentation, and explanation of key steps and algorithms, with one section per language the repository actually uses, then keep the AGENTS.md route to it. Invoke explicitly, by name, to set up, extend, or review coding conventions, comment rules, or documentation rules, or to bring an authorized code scope into line with established rules. Do not use it for architectural dependency direction or system boundaries, general AGENTS.md guidance, formatter, linter, or analyzer configuration changes, product direction, feature plans, or new application behavior.
disable-model-invocation: false
---

# Code Style

Maintain one normative code-style contract for a repository:
`docs/code-style.md`. Every language the repository actually uses gets a
section; a language it does not use gets none.

This Skill is prescriptive, not merely descriptive. Where tooling already
enforces a rule, route to that tooling. Where tooling cannot enforce a rule -
structure, in-code module organization, comment intent, documentation,
explanation of key algorithms - decide the rule with the user and write it as
an instruction an agent can follow without further interpretation.

Component, project, and service boundaries and dependency direction between
them belong to the Architecture Design. Link the applicable section instead of
restating it, and report a missing or conflicting architectural decision for
`architecture-design`.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `define`: create or refresh the style rules and the `AGENTS.md` route. This
  is the default. A request to write, create, refresh, or extend the style file
  means `define`.
- `audit`: report missing language sections, rules contradicted by current
  tooling configuration, unfollowable prose, a broken or absent route, and,
  when the request names a code scope, that code's deviations from established
  rules with locations. Change no file.
- `apply`: edit only the code scope the user authorizes so it follows rules
  already established in the style files. Change no rule, rule file, or tooling
  configuration.

## Output

| File | This Skill may |
|---|---|
| `docs/code-style.md` | `define`: create and rewrite it from [the template](assets/code-style.template.md) |
| `<subproject>/docs/code-style.md` | `define`: create or rewrite a scoped file for a genuine local difference |
| `AGENTS.md` | `define`: only add or correct the single route to `docs/code-style.md`, and remove a code-style rule that the style files now own |
| Code files in the authorized scope | `apply`: edit them under established rules |
| Formatter, linter, analyzer, build, and package configuration | Read as evidence only; introducing or changing it is separate work that the user's request must explicitly include |

Everything else in `AGENTS.md` and any nested `AGENTS.md` belongs to
`coding-agent-instructions`. Report a needed change there instead of making it.

Keep shared rules once, in the root file. Create a scoped file only when a
subproject genuinely differs, such as its own language, framework, or confirmed
local convention; it holds only those differences and links the root file. List
each scoped file in the root file so the single `AGENTS.md` route reaches it. A
small project uses one root file with a section per language. Do not create
empty scoped files or repeat shared rules in each language project.

About 200 lines per file and about 12 rules per language section are review
signals: route to configuration, an existing project document, or a genuine
scoped file, and remove repetition, rather than expanding the file.

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

## Define

1. Read `AGENTS.md`, existing style files, the Architecture Design when
   present, and the configuration needed to identify languages and
   enforcement: project and package manifests, `.editorconfig`, formatter,
   linter, analyzer, and type-checker settings, and the commands CI or
   repository scripts actually run.
2. Confirm the language set with the user as described above.
3. Read the confirmed languages' references.
4. Split every candidate rule into enforced and unenforced. A rule a configured
   formatter, linter, analyzer, or type checker already applies is enforced:
   name the authoritative surface and its verified command, and do not restate
   the rule. Everything else is unenforced and must be written out.
5. Decide each unenforced rule by explicit user direction, then an approved
   project document, then a consistent repository pattern the user confirms.
   When none of those settle it, ask or omit; never present an observed pattern
   as policy without confirmation. Place it in the root file unless it is a
   genuine local difference.
6. Write the style files from the template. Keep the cross-language section for
   every project. Preserve a human-written rule that is still valid, and
   reconcile a conflicting rule visibly instead of deleting it silently.
7. Update `AGENTS.md` so it routes to `docs/code-style.md` and holds no
   code-style rule of its own. Add the route when it is missing, correct it when
   it is stale, and move a code-style rule found there into the style file.
   Change nothing else in `AGENTS.md`.
8. Run the consistency check.

## Apply

1. Confirm the authorized code scope and read the rules that govern it: the
   root file and any scoped file for that subproject. If a rule is missing or
   ambiguous, report it for `define` instead of inventing one.
2. Never edit a rule to excuse an existing violation. A deviation the user
   wants to keep is a `define` decision.
3. Prefer a configured formatter or fixer with a verified command for
   deterministic rules, limited to the scope. Do not install a tool or create
   or change its configuration; report a rule that needs one.
4. Edit the remaining deviations by hand. Restructuring code, renaming, or
   rewriting comments and API documentation can change meaning or public
   contracts: preserve observable behavior, public signatures, and serialized
   or wire names unless the user authorizes a contract change.
5. Inspect the diff for scope and behavior, then run the relevant verified
   build, test, or lint commands for each changed scope. When no verified check
   covers the change, report that behavior preservation is unverified.

State a command only when repository configuration, automation, or an observed
successful run verifies it. Omit an unverified command rather than guessing.

## Consistency Check

For `define`, confirm that every confirmed language has exactly one section in
its applicable file and no unused language has one; that no shared rule is
repeated in a scoped file; that no written rule contradicts current formatter,
linter, analyzer, or type-checker configuration or restates architectural
dependency direction; that every routed path and command exists and is
verified; that `AGENTS.md` routes to `docs/code-style.md` and retains no
code-style rule; and that each rule is an instruction an agent can apply, not a
topic heading. Fix a stale name, path, or command here when the correction is
mechanical. Report a conflict that needs a technical or ownership decision.

For `apply`, confirm that only files in the authorized scope changed, no rule or
configuration file changed, and the checks above ran or are reported as not
run.

## Completion

For `define`, report the files written, languages included and excluded, the
rules routed to tooling versus written out, scoped files and why each exists,
the `AGENTS.md` route change, unresolved conflicts, and the questions left
open. Recommend a refresh when the language set, tooling, or enforcement
configuration later changes. For `audit`, report findings only. For `apply`,
report the files changed, rules applied, deviations left with reasons, commands
run with results, and behavior risks. Stop without modifying tooling
configuration, other instruction files, or code outside the authorized scope.
