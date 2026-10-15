---
name: code-style
description: Define, audit, or apply a project's code-style contract - docs/code-style.md plus one inheriting style file per project in a multi-project workspace - covering file and code structure, in-code module organization, comment intent, API documentation, and explanation of key steps and algorithms, with one section per language the repository actually uses, owner default rules, and the AGENTS.md route to it. Creates missing .editorconfig and VS Code workspace files from templates after the user sees them, and applies rules to code in bounded, formatter-first batches. Invoke explicitly, by name, to set up, init, extend, or review coding conventions, comment rules, or documentation rules, or to bring an authorized code scope into line with established rules. Do not use it for architectural dependency direction or system boundaries, general AGENTS.md guidance, changes to existing formatter, linter, analyzer, or editor configuration, product direction, feature plans, or new application behavior.
disable-model-invocation: false
---

# Code Style

Maintain one normative code-style contract for a repository:
`docs/code-style.md`. Every language the repository actually uses gets a
section; a language it does not use gets none.

This Skill is prescriptive, not merely descriptive. Where tooling already
enforces a rule, route to that tooling. Where tooling cannot enforce a rule -
structure, in-code module organization, comment intent, documentation,
explanation of key algorithms - write it as an instruction an agent can follow
without further interpretation, using the owner default profile unless the
user or a project document decides otherwise.

Component, project, and service boundaries and dependency direction between
them belong to the Architecture Design. Link the applicable section instead of
restating it, and report a missing or conflicting architectural decision for
`architecture-design`.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `define`: create or refresh the style rules, missing formatting
  configuration, and the `AGENTS.md` route. This is the default. A request to
  set up, init, write, create, refresh, or extend the style file means
  `define`.
- `audit`: report missing language sections, rules contradicted by current
  tooling configuration, configuration differences from the templates,
  unfollowable prose, a broken or absent route, and, when the request names a
  code scope, that code's deviations from established rules with locations. A
  code scope uses the same scope and batching as `apply`. Change no file.
- `apply`: edit only the code scope the user authorizes so it follows rules
  already established in the style files. Change no rule, rule file, or tooling
  configuration.

## Output

| File | This Skill may |
|---|---|
| `docs/code-style.md` | `define`: create and rewrite it from [the template](assets/code-style.template.md) |
| `<project>/docs/code-style.md` | `define`: in a multi-project workspace, create or rewrite one file for every confirmed project from [the project template](assets/code-style.project.template.md) |
| `.editorconfig`, `.vscode/settings.json`, `.vscode/extensions.json` | `define`: create from the Skill templates only when missing, after the user sees the content; otherwise read-only, and report differences |
| `.code-workspace` | Read-only; report the proposed `settings` block |
| `AGENTS.md` | `define`: add or correct the route to `docs/code-style.md` and the Working-rules line, and remove a code-style rule that the style files now own |
| Code files in the authorized scope | `apply`: edit them under established rules |
| Formatter, linter, analyzer, build, and package configuration | Read as evidence only; changing it is separate work that the user's request must explicitly include |
| Machine-level VS Code settings | Never written |

`code-style` owns the code-style route and the Working-rules line in
`AGENTS.md`. It may correct the code-style route line in an existing nested
`AGENTS.md` but never creates one. Everything else in `AGENTS.md` and any nested
`AGENTS.md` belongs to `coding-agent-instructions`. Report a needed change there
instead of making it.

A single-project repository uses one root file with a section per language and
no project files. In a multi-project workspace, a project is a top-level unit
such as `frontend/` or `vehicle-simulator/`, not each `.csproj` or package. The
root file holds cross-language rules, product-wide rules, and language rules
used by two or more projects. Every project gets one file that starts with
"Inherits all rules from" a link to the root file and holds only rules local to
that project, such as a language only that project uses, or `Local Rules:
None.` The root file lists every project file, so the single `AGENTS.md` route
reaches it. `AGENTS.md` files hold routes only. Never repeat a shared rule in a
project file.

About 200 lines per file and about 12 rules per language section are review
signals: route to configuration, an existing project document, or a project
file, and remove repetition, rather than expanding the file.

## Language Coverage

Detect candidate languages from repository evidence, then confirm the set with
the user in one question before writing. State what was detected, what will be
included, and what will be excluded. Include a language the user names even
without repository evidence yet, and exclude one they reject.

For `define`, always read the [owner default profile](references/default-profile.md).
Read a language reference only for a confirmed language:

- [C#](references/code-style-csharp.md) for C# or .NET evidence;
- [Frontend](references/code-style-frontend.md) for HTML, CSS, JavaScript,
  TypeScript, or a frontend framework;
- [Python](references/code-style-python.md) for Python evidence;
- [SQL](references/code-style-sql.md) for SQL scripts or migrations;
- [XAML](references/code-style-xaml.md) for WPF, WinUI, Avalonia, or MAUI
  views;
- [Formatting configuration](references/formatting-config.md) when
  `.editorconfig`, `.vscode/`, a `.code-workspace` file, or formatter
  configuration is present or missing.

A confirmed language with no reference here - Go, Java, shell, and others -
still gets a section. Build it from the cross-language rules in the template,
the repository's own configuration and prevailing patterns, and the user's
answers. Do not add a reference file for it as part of this run.

## Define

1. Read `AGENTS.md`, existing style files, the Architecture Design when
   present, and the configuration needed to identify languages and
   enforcement: project and package manifests, `.editorconfig`, `.vscode/`,
   `.code-workspace`, formatter, linter, analyzer, and type-checker settings,
   and the commands CI or repository scripts actually run.
2. Confirm the language set and, for a multi-project workspace, the project
   list with the user in one question.
3. Read the owner default profile and the confirmed languages' references.
4. Split every candidate rule into enforced and unenforced. A rule a configured
   formatter, linter, analyzer, or type checker already applies is enforced:
   name the authoritative surface and its verified command, and do not restate
   the rule. Everything else is unenforced and must be written out.
5. Decide each unenforced rule by explicit user direction, then an approved
   project document, then the owner default profile. Ask only where none of
   them settles it; never present an observed pattern as policy without
   confirmation. Place each rule in the root or a project file as described in
   Output.
6. Handle formatting configuration as described in the formatting
   configuration reference: report differences in existing files, and for a
   missing file render the template filtered to the confirmed languages, show
   it, and create it only after approval.
7. Write the style files from the templates. Keep the cross-language section
   for every project. Replace template placeholders such as
   `<architecture-path>` with real relative paths. Preserve a human-written rule
   that is still valid, and reconcile a conflicting rule visibly instead of
   deleting it silently.
8. Update `AGENTS.md` so it routes to `docs/code-style.md`, holds the
   Working-rules line "Before changing code, read the matching language section
   of the applicable code-style file and follow it.", and holds no other
   code-style rule. Add the route and line when missing, correct them when
   stale, and move a code-style rule found there into the style file. Change
   nothing else in `AGENTS.md`.
9. Run the consistency check.

## Apply

1. Confirm the authorized code scope and read the rules that govern it: the
   root file and the project file for that project. If a rule is missing or
   ambiguous, report it for `define` instead of inventing one.
2. Never edit a rule to excuse an existing violation. A deviation the user
   wants to keep is a `define` decision.
3. Work in this order, with the numbers, subagent brief, and fallback in
   [apply batching](references/apply-batching.md):
   1. run the configured formatter with a verified command, limited to the
      scope;
   2. use the default scope: files changed since a given commit, or a named
      folder or package;
   3. estimate the documentation scope in KB: in-scope files that need comment
      or documentation work, excluding test code and tool configuration once
      the formatter has run;
   4. fix the remaining deviations yourself when that scope fits one batch
      budget, otherwise in subagent batches by size; read each file once and
      edit with targeted replacements, never by rewriting a whole file;
   5. verify with the diff, the verified build and tests, and spot checks.
4. Do not install a tool or create or change its configuration; report a rule
   that needs one.
5. Restructuring code, renaming, or rewriting comments and API documentation
   can change meaning or public contracts: preserve observable behavior, public
   signatures, and serialized or wire names unless the user authorizes a
   contract change. When no verified check covers the change, report that
   behavior preservation is unverified.

State a command only when repository configuration, automation, or an observed
successful run verifies it. Omit an unverified command rather than guessing.

## Consistency Check

For `define`, confirm that every confirmed language has exactly one section in
its applicable file and no unused language has one; that every confirmed
project has exactly one file that links the root file and is listed there; that
no shared rule is repeated in a project file; that no written rule contradicts
current formatter, linter, analyzer, or type-checker configuration or restates
architectural dependency direction; that every routed path and command exists
and is verified; that `AGENTS.md` routes to `docs/code-style.md`, holds the
Working-rules line, and retains no other code-style rule; that created
configuration matches the content shown to the user and existing configuration
is unchanged; and that each rule is an instruction an agent can apply, not a
topic heading. Fix a stale name, path, or command here when the correction is
mechanical. Report a conflict that needs a technical or ownership decision.

For `apply` and `audit`, confirm that only files in the authorized scope were
changed or reported, no rule or configuration file changed, and verification
evidence is present or reported as not run.

## Completion

For `define`, report the files written, languages included and excluded,
projects and their files, the rules routed to tooling versus written out,
configuration created or proposed and differences found, the `AGENTS.md`
change, unresolved conflicts, and the questions left open. Recommend a refresh
when the language set, projects, tooling, or enforcement configuration later
changes. For `audit`, report findings only. For `apply`, report the files
changed, rules applied, the batch plan used (self or N subagents, and waves)
with the actual KB of each batch, and peak context and API calls per subagent
when the platform reports them, deviations left with reasons, verification
results, and behavior risks. Stop without modifying existing tooling
configuration, other instruction files, or code outside the authorized scope.
