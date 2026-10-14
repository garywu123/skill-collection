# Code Style V2 Plan

## Current position

- Status: planning only. No Skill file is changed in this run.
- Base revision: `6fd18d9` on `feature/code-style-v2`.
- Next: independent review of this plan, then one implementation run that
  follows the segments below. Deployment happens only after review and commit.
- Source of decisions: the user's chat decisions of 2026-10-14 (items A1-A5 and
  B1-B2 below). Where those decisions leave a detail open, this plan states its
  choice under [Interpretations](#interpretations).

## Goal

1. `code-style` writes the owner's default comment and documentation rules
   without asking about each rule again, handles multi-project workspaces with
   one inheriting file per project, ships formatting templates for the missing
   case, and applies rules to code in bounded batches with a known token cost.
2. `coding-agent-instructions` ships a read-only link checker,
   `Test-DocLinks.ps1`, copies it into projects, and routes agents to run it
   after documentation edits.

Design claim for the implementation run: "Every decision fits in the two
existing Skills: four new references, four new assets, one new script with one
test script, and edits to existing files; no new Skill, agent file, or
deployment change is needed." Cheap disproof check: after the edits, the
consistency scan finds no rule that both Skills claim, and `Deploy-Skills.ps1
-ListOnly` still lists both Skills from their current folders.

## Inputs read

- [AGENTS.md](../../AGENTS.md) and the [skill-authoring](../../skills/coding/skill-authoring/SKILL.md)
  rules: smallest change, resources only when used, one owner per rule,
  collection README only for public capability changes.
- [Coding collection README](../../skills/coding/README.md).
- [code-style SKILL.md](../../skills/coding/16.code-style/SKILL.md), its
  references (C#, frontend, Python, EditorConfig baseline) and
  [template](../../skills/coding/16.code-style/assets/code-style.template.md).
- [coding-agent-instructions SKILL.md](../../skills/coding/15.coding-agent-instructions/SKILL.md)
  and its [AGENTS template](../../skills/coding/15.coding-agent-instructions/assets/agents.template.md).
- [Deploy-Skills.ps1](../../scripts/deploy-skill/Deploy-Skills.ps1) copies each
  mapped Skill folder recursively, so every file under a Skill folder, including
  tests, is deployed. Both Skills are already mapped in
  [deploy-skills.json](../../scripts/deploy-skill/deploy-skills.json).

## Current rules that change

| Current rule | Where | New rule |
|---|---|---|
| Never create or modify formatter or editor configuration | `SKILL.md` Output table and description; C#, frontend, Python references; EditorConfig baseline | `define` may create missing `.editorconfig`, `.vscode/settings.json`, and `.vscode/extensions.json` from Skill templates after the user sees them; existing configuration stays read-only and differences are reported (A3) |
| Do not create empty scoped files; scoped file only for a genuine difference | `SKILL.md` Output; template `Scoped Rules` | In a multi-project workspace every project gets a file that inherits the root file; empty ones say `Local Rules: None.` (A2) |
| `AGENTS.md` gets only the single route | `SKILL.md` Output and Define step 7 | `AGENTS.md` gets the route and one Working-rules line: read the matching language section before changing code (A4) |
| Unenforced rules are decided by user, project document, or confirmed pattern; otherwise ask | `SKILL.md` Define step 5 | The owner default profile fills an unenforced rule unless the user or a project document says otherwise; ask only where neither settles it (A1) |
| "Explain why, not what" | Template Comments section | Comments carry intent: a `Step n:` comment states what an important step achieves; other comments explain why; never restate one line (A1) |
| SQL and other languages have no reference; do not add one | `SKILL.md` Language Coverage | SQL and XAML get references (A1) |
| `apply` edits by hand after an optional formatter | `SKILL.md` Apply | Formatter first, bounded scope, size-based batching with optional subagents, fixed verification (A5) |
| `coding-agent-instructions` may create only `AGENTS.md` files | its `SKILL.md` Output | It may also copy `scripts/Test-DocLinks.ps1` into the project (B2) |

## Interpretations

The user decisions leave these details open. The plan chooses the simplest
reading; the reviewer may challenge any of them.

1. **Intent names.** "Setup" and "init" mean the existing `define` intent. No
   new intent is added.
2. **Where language defaults live.** `references/default-profile.md` is the
   entry point: precedence, the cross-language `Step n:` rule, the test-code
   exemption, and one link per language. Each language's concrete defaults and
   examples live in an `Owner Default` section of that language's reference, so
   `define` loads only confirmed languages. SQL and XAML defaults live in the new
   SQL and XAML references, as the user asked.
3. **What a "project" is.** A top-level unit of the workspace (for example
   `frontend/`, `vehicle-simulator/`), confirmed with the user in the same
   question as the language set. It is not each `.csproj` or package. A
   single-project repository keeps one root file and no project files.
4. **Language placement.** A language rule used by one project only lives in
   that project's file (agv-tools: TypeScript rules in
   `frontend/docs/code-style.md`). Cross-language rules, product-wide rules, and
   language rules used by two or more projects live in the root file
   (agv-tools: shared C# rules in `docs/code-style.md`).
5. **`AGENTS.md` ownership.** `code-style` adds or corrects the root route and
   the Working-rules line. It may correct the code-style route line in an
   existing nested `AGENTS.md`, but never creates one. `coding-agent-instructions`
   keeps both lines and treats them as routes, not code-style rules.
6. **VS Code settings level.** For a single-folder repository, the missing
   `.vscode/` files are created at the repository root. For a multi-root
   workspace, missing `.vscode/` files are created only in workspace root
   folders, never in nested non-root folders, which VS Code ignores. An existing
   `.code-workspace` file is existing configuration: the plan shows the proposed
   `settings` block and reports it, without editing the file.
7. **Format on save is language-scoped.** `editor.formatOnSave` goes inside each
   language block, so Markdown and other files are not reformatted by an
   unexpected default formatter.
8. **Default formatter IDs.** C#: `ms-dotnettools.csharp`; TS, JS, JSON, YAML:
   `esbenp.prettier-vscode`; Python: `charliermarsh.ruff`, or
   `ms-python.black-formatter` when the project already configures Black. XAML
   and SQL get no formatter entry. The user sees these values before any file is
   written.
9. **Print width 100.** It is set as `max_line_length = 100` for TS and JS in
   `.editorconfig`, which Prettier reads. The Skill ships no `.prettierrc`; a
   project Prettier `printWidth` wins and a difference is reported.
10. **Markdown whitespace.** The template keeps the current baseline's
    exception: `[*.md] trim_trailing_whitespace = false`, so intentional
    Markdown hard breaks survive. Line endings stay unset, as today.
11. **Gap scan script.** Not included in the first version. Reason: C# member
    detection without Roslyn (multi-line signatures, attributes, nested and
    implicit-internal types) gives false gaps, and a Roslyn tool adds a
    dependency. Formatter-first plus size-based batching already bounds tokens.
    Revisit when real runs show subagents spend most of their budget on files
    that need no change, or when audit results miss gaps.
12. **Link checker limits.** Anchors are checked only for Markdown targets
    (heading slugs and explicit `<a id>`/`<a name>`); HTML `#fragment` targets
    are checked for file existence only. Case-only mismatches pass on Windows and
    are not detected. Links inside fenced code and inline code are ignored.
    Angle delimiters are stripped and the destination is checked
    (`<missing.md>` and `<my file.md>` are checked). Only a recognized
    placeholder is skipped: a whole destination `<name>` whose name has no dot
    and no slash, such as `<architecture-path>`. Skill templates use such
    placeholders for every project-only link.
13. **Test fixture.** The checker's test builds its fixture in a temporary
    folder at run time. A committed fixture with broken links would make the
    link check of this repository fail and would be deployed with the Skill.
14. **Project copy refresh.** Refresh reports an older (or newer) project copy and
    does not overwrite it. A same-named file without a version header is
    reported, never replaced. Init runs the copied script once, so the
    `AGENTS.md` command is verified by an observed run.

## File changes: code-style

All paths are under `skills/coding/16.code-style/`.

### `SKILL.md` (edit)

- **Frontmatter `description`:** remove the blanket exclusion of formatter
  configuration; say it creates missing `.editorconfig` and VS Code workspace
  files from templates after the user sees them, keeps one inheriting file per
  project, and applies rules in bounded batches; exclude changes to existing
  formatter, linter, analyzer, or editor configuration. Keep it at or below
  1024 characters. Why: A3, A2, A5 change discovery boundaries.
- **Intent:** `define` also covers "set up" and "init" requests. `audit` uses the
  same scope and batching as `apply` but writes nothing. Why: Interpretation 1,
  A5.
- **Output table:** add rows for `<project>/docs/code-style.md` (every project
  in a multi-project workspace), `.editorconfig` and `.vscode/*.json` (create
  from templates only when missing, after showing them; otherwise read-only and
  report differences), `.code-workspace` (read-only), and the `AGENTS.md`
  route plus Working-rules line. Machine-level VS Code settings: never written.
  Why: A2, A3, A4.
- **Placement paragraph:** replace "Do not create empty scoped files" with the
  A2 rule and Interpretations 3-4: root file holds cross-language, product-wide,
  and multi-project language rules; each project file starts with "Inherits all
  rules from ..." and holds only local differences, or `Local Rules: None.`; the
  root file lists every project file; `AGENTS.md` files hold routes only. Why:
  A2.
- **Language Coverage:** add SQL and XAML references; add the default profile as
  always-read for `define`; replace the EditorConfig baseline link with the
  formatting reference. Keep the rule that other languages (Go, Java, shell)
  build their section from the template without a new reference. Why: A1, A3.
- **Define:** step 5 uses the precedence user > project document > owner default
  profile > ask. Add a step that confirms projects together with languages (one
  question). Add a step for formatting configuration (detect, render filtered
  templates, show, create on approval, report differences for existing files).
  Step 7 adds the route and the Working-rules line: "Before changing code, read
  the matching language section of the applicable code-style file and follow
  it." Why: A1-A4.
- **Apply:** replace steps 3-5 with a short ordered summary (formatter first,
  default scope, size estimate, self or subagent batches, verify) and link
  `references/apply-batching.md` for numbers, the subagent brief, and the
  fallback. Keep the existing rules: no rule or configuration change, preserve
  behavior and public names. Why: A5; details load only for apply and audit.
- **Consistency Check:** add: every confirmed project has exactly one file that
  links the root; no shared rule is repeated in a project file; `AGENTS.md` has
  the route and the Working-rules line; created configuration matches the shown
  content; existing configuration is unchanged. For `apply`/`audit`: in-scope
  files only, verification evidence present. Why: keeps checks aligned with the
  new outputs.
- **Completion:** report created or proposed configuration, differences found,
  projects and their files, and for apply the batch plan used (self or N
  subagents, waves) and verification results. Why: observable output.

Expected size: about 190 lines (today 158). The batching details stay in the
reference to keep the core file short.

### `references/default-profile.md` (new)

Contents:

- Purpose and precedence: used unless the user or a project document says
  otherwise; formatting values in existing configuration win and differences are
  reported.
- Cross-language: comments carry intent; every important step gets a
  `Step n:` comment that states what it does; a complex step adds a concrete
  example. Example:

  ```csharp
  // Step 2: Number the rows of each key in time order.
  //     Example: key A on rows 12 and 40 -> Seq 1 and 2.
  ```

- Test code: no API documentation is required; formatting rules still apply;
  test names describe behavior.
- One line per language with a link to its `Owner Default` section: C#,
  TS/JS, Python, SQL, XAML.

Why: A1 needs one entry point; language details load only for confirmed
languages (Interpretation 2).

### `references/code-style-csharp.md` (edit)

- Evidence section: replace "Never create or modify code-style configuration"
  with: read-only, except missing files created by `define` from the Skill
  templates; link `formatting-config.md` instead of the EditorConfig baseline.
- XML Documentation section: keep the element meanings; drop the condition
  "when the repository generates or requires XML documentation".
- New `Owner Default` section: full XML documentation on public and internal
  members (`summary`, `param`, `typeparam`, `returns`, `exception`, `remarks` for
  important reminders) and on key private members; every element on its own
  lines, content indented four spaces after `///`; test code exempt. Example:

  ```csharp
  /// <summary>
  ///     Builds the parameterized SELECT that reads one export window.
  /// </summary>
  /// <param name="end">
  ///     Window end, exclusive. Example: 01:00-05:00 reads rows with time >= 01:00 and < 05:00.
  /// </param>
  ```

Why: A1, A3.

### `references/code-style-frontend.md` (edit)

- Evidence section: same configuration change as C#; link `formatting-config.md`.
- New `Owner Default` section for TS/JS: each module starts with a description
  of what it owns and does not own; exported functions get JSDoc with
  `@param`, `@returns`, `@throws`, each tag on its own line and content indented
  four spaces after ` * `; `Step n:` comments; 2-space indentation; print width
  100 unless project configuration says otherwise. Example:

  ```ts
  /**
   * Loads one export window from the API.
   *
   * @param end
   *     Window end, exclusive.
   * @returns
   *     Rows ordered by time.
   * @throws
   *     ApiError when the server rejects the window.
   */
  ```

Why: A1, A3.

### `references/code-style-python.md` (edit)

- Evidence section: same configuration change; link `formatting-config.md`.
- New `Owner Default` section: module docstring; Google-style function
  docstrings (`Args`, `Returns`, `Raises`); 4 spaces; `Step n:` comments.

Why: A1, A3.

### `references/code-style-sql.md` (new)

- Evidence: SQL dialect, migration tool and file naming, any configured SQL
  formatter or linter, scripts that run the SQL.
- Owner Default: a header comment block (script, purpose, input, output), a
  `Step n:` comment before each main step, and an example for complex steps.

  ```sql
  /*
  Script:  export_window.sql
  Purpose: Reads one export window of vehicle events.
  Input:   @start, @end (end is exclusive)
  Output:  One row per event, with Seq per key.
  */
  -- Step 1: Keep rows inside the window.
  -- Step 2: Number rows per key in time order.
  --     Example: ROW_NUMBER adds a Seq column: key on rows 12 and 40 -> Seq 1 and 2.
  ```

- Rules to decide and write (only when the user or project settles them):
  keyword case, naming, parameterization at call sites.
- Placement table in the same form as the other references.

Why: A1 names this file.

### `references/code-style-xaml.md` (new)

- Evidence: UI framework (WPF, WinUI, Avalonia, MAUI) and its merge syntax,
  `App.xaml`, existing `Styles/` folders and resource dictionaries.
- Owner Default: views hold layout only; view-specific styles live in one
  resource dictionary per view (for example `Styles/ExportView.xaml`) merged by
  that view; shared styles live in `Styles/Shared.xaml` merged by `App.xaml`.
- Apply cautions: moving a style can change resource lookup (merge order,
  implicit `TargetType` styles, `StaticResource` order). Extraction is
  structural work for the strong model or the orchestrator, never the cheap
  model. Verify by build and, when available, by opening the view; otherwise
  report that visual behavior is unverified.

Why: A1, A5f.

### `references/formatting-config.md` (new; replaces `references/editorconfig-baseline.md`)

- When to read: `define` with missing or existing formatting configuration, and
  `audit` of configuration.
- Compare: existing `.editorconfig`, `.vscode/*.json`, `.code-workspace`, and
  formatter configuration are read-only; report each difference from the
  templates; never change them.
- Create (missing case only): render the templates, remove sections for
  languages that are not confirmed, show the full content to the user, create
  only after approval. In a non-interactive run, report the proposal instead.
- VS Code levels: Interpretation 6; language-scoped blocks; never write
  machine-level user settings.
- Optional machine check, only on request: read the user's VS Code settings and
  report recommendations (for example a global default formatter that overrides
  the workspace, or a missing EditorConfig extension); never print the file or
  edit it.
- Keep from the old baseline: do not impose line endings; exclude generated,
  vendor, and minified files; language tools stay authoritative for semantics.

Why: A3. The old baseline's value table would duplicate the template values and
its "never create `.editorconfig`" rule is replaced, so the file is removed and
its still-valid rules move here.

### `references/apply-batching.md` (new)

Holds A5 in full:

1. Run the configured formatter first, limited to the scope (no model). Only a
   verified command; otherwise report that no formatter ran. For `audit`, use
   its check mode.
2. Scope: files changed since a given commit (including untracked files in
   scope) or a named folder or package; the whole repository only when the user
   asks.
3. Estimate tokens as total bytes / 4, with a PowerShell 5.1-compatible
   command, for example:

   ```powershell
   $files = @(git diff --name-only --diff-filter=ACMR <commit> -- <path>) + @(git ls-files --others --exclude-standard -- <path>)
   ($files | Where-Object { Test-Path -LiteralPath $_ } | Get-Item | Measure-Object Length -Sum).Sum / 4
   ```

4. Under about 80k tokens: the orchestrating session fixes files itself, batch
   by batch (grouped by language and folder), no subagents.
5. Above: documentation subagents on a strong model (Sonnet class); count =
   ceil(tokens / 60k); at most 5 running; start the next wave only after the
   current wave returns. Above about 300k: ask the user to narrow the scope.
6. Subagent brief: only the matching language section and its file list; no
   subagents of its own; return at most 10 lines: changed files and at most 3
   unsure items as `file:line` plus one sentence; no diffs or file contents.
   For `audit`: files with gaps and rule names instead of changed files.
7. Cheap model (Haiku class) only for mechanical leftovers the formatter cannot
   do (for example turning a one-line `<summary>` into the indented layout),
   and only when the platform allows choosing a model.
8. Verify: `git diff --stat`, the verified build and tests, and 2-3 spot-checked
   diffs.
9. No subagents available (for example Codex): run the same batches in sequence.
10. Thresholds are defaults; a run may pass a temporary override. Record actual
    counts in the completion report so the defaults can be tuned.

Worked numbers to include: 60k -> self; 120k -> 2 subagents, one wave; 290k
-> 5 subagents, one wave; 320k -> ask to narrow; user confirms 450k -> 8
subagents, waves of 5 and 3. Note that waves only occur above 300k.

Why: A5 is needed only for `apply` and `audit`, so it loads on demand.

### `references/editorconfig-baseline.md` (delete)

Replaced by `formatting-config.md`; links in the three language references
change in the same run.

### `assets/code-style.template.md` (edit)

- Replace `Scoped Rules` with `Project Files`: a table of every project file and
  a one-line summary of its local rules or `None`; delete it for a
  single-project repository.
- Comments section: replace "Explain why, not what" with the intent rule and
  the `Step n:` rule (see Current rules that change).
- Documentation and Tests sections: add placeholders that `define` fills from
  the default profile, including the test-code documentation exemption.
- Project-only link targets become placeholders: line 6
  `[Architecture Design](architecture.md)` becomes
  `[Architecture Design](<architecture-path>)`, and `define` writes the real
  relative path when it renders the file. The existing `Scoped Rules` link
  `(../<subproject>/docs/code-style.md)` is not a whole-destination placeholder
  and would be checked, so in `Project Files` it becomes
  `(<project-code-style-path>)`; the link text keeps `<project>/docs/code-style.md`.
  No template link may point at a file that exists only in a project, so the
  template folder passes the link check (acceptance check 4).

Why: A1, A2, and the clean link check of the Skill folder.

### `assets/code-style.project.template.md` (new)

About 10 lines: title, "Inherits all rules from [root code
style](<root-code-style-path>). This file holds only local differences.", then
`## Local Rules` with `None.` or the local rules. `define` replaces
`<root-code-style-path>` with the relative path to `docs/code-style.md` (for
example `../../docs/code-style.md` from `frontend/docs/`).

Why: A2 asks for the same opening in every project file.

### `assets/editorconfig.template` (new)

Not named `.editorconfig`, so it does not apply to files in this repository.

```ini
root = true

[*]
charset = utf-8
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.md]
trim_trailing_whitespace = false

[*.{ts,tsx,js,jsx,json,yml,yaml}]
indent_size = 2

[*.{ts,tsx,js,jsx}]
max_line_length = 100

[*.cs]
indent_size = 4

[*.xaml]
indent_size = 4

[*.sql]
indent_size = 4

[*.py]
indent_size = 4
```

Why: A3. Explicit per-language sections let `define` delete sections for
unused languages.

### `assets/vscode-settings.template.json` and `assets/vscode-extensions.template.json` (new)

- Settings: one language block per language with `editor.defaultFormatter` and
  `editor.formatOnSave: true` (Interpretations 7-8): `[csharp]`, `[typescript]`,
  `[typescriptreact]`, `[javascript]`, `[javascriptreact]`, `[json]`, `[yaml]`,
  `[python]`.
- Extensions: `EditorConfig.EditorConfig`, `ms-dotnettools.csdevkit`,
  `esbenp.prettier-vscode`, `ms-python.python`, `charliermarsh.ruff`.
- Strict JSON (no comments), so they parse in checks. `define` removes entries
  for unused languages.

Why: A3.

## File changes: coding-agent-instructions

All paths are under `skills/coding/15.coding-agent-instructions/`.

### `scripts/Test-DocLinks.ps1` (new)

- Header: comment-based help with `.SYNOPSIS`, `.PARAMETER`, `.EXAMPLE`, and
  `.NOTES` containing `Version: 1.0.0`. Refresh reads it with
  `(?m)^\s*Version:\s*(\d+\.\d+\.\d+)\s*$` and compares as `[version]`.
- Parameter: `-Path` (folder to scan, default current folder). A missing path is
  an error with exit code 2.
- Walk all files below `-Path`, skipping folders named `node_modules`, `bin`,
  `obj`, `.git`. Read files as UTF-8 explicitly (Windows PowerShell 5.1
  `Get-Content` defaults to ANSI).
- Markdown (`*.md`): inline links and images `[text](target)`, and reference
  definitions `[id]: target`. Ignore fenced code blocks and inline code. Skip a
  recognized template placeholder: a whole destination `<name>` whose name has
  no dot and no slash, such as `<architecture-path>`. For every other target,
  strip angle delimiters (`<my file.md>` -> `my file.md`), titles, and
  `?query`; URL-decode `%20`. Skip `http:`, `https:`, `mailto:`, and other `scheme:`
  targets. A leading `/` resolves from `-Path`; others from the file's folder. A
  folder target must exist as a folder.
- Anchors: `#x` checks the same file; `file.md#x` checks that file. Slugs follow
  GitHub: lowercase, keep Unicode letters and digits, spaces, `-` and `_`; drop
  other characters; spaces to `-`; repeated headings get `-1`, `-2`. Explicit
  `<a id="x">` or `<a name="x">` also count.
- `AGENTS.md` route cells (any folder): in a Markdown table row (a line that
  starts with `|`, except the separator row), each backtick span inside a cell
  is a route candidate when it contains `/` or `\`, or ends with `.md`. Spaces
  inside the span are allowed, so `` `docs/User Guide.md` `` is checked. A
  candidate is resolved from that `AGENTS.md` folder. Not candidates:
  - spans with `<`, `>`, `{`, `*`, or `://` (placeholders, globs, URLs);
  - spans with a space whose first word has no `/` or `\` and that do not end
    with `.md`, which are commands such as `` `dotnet test src/App.Tests` ``;
  - values such as `` `Node.js` `` or `` `verified` ``, which have no separator
    and do not end with `.md`.
- HTML (`*.html`, `*.htm`): literal `href` and `src` attribute values. Skip
  external and `//` links, `#`-only, `data:`, `javascript:`, `mailto:`, and
  values with `{` or `$` (template code). Fragments are not checked
  (Interpretation 12).
- Output: one line per broken link, `file:line -> target (reason)`, with the
  file path relative to `-Path` using `/`. Reasons: `missing file`,
  `missing folder`, `missing anchor`. Then a count line. Exit 1 when any link is
  broken, else 0.
- Compatibility: no modules or packages; no PowerShell 7-only syntax (`??`,
  ternary, `-AsHashtable`, `[IO.Path]::GetRelativePath`); runs in Windows
  PowerShell 5.1 and pwsh 7.

Why: B1.

### `scripts/tests/Invoke-DocLinksTests.ps1` (new)

A plain PowerShell test (no Pester, which differs between 3.x and 5.x). It
creates a fixture in a temporary folder, runs `Test-DocLinks.ps1` under
`powershell` and, when installed, `pwsh`, compares exit codes and exact output
lines, deletes the fixture, and exits 0 on pass and 1 on failure.

Fixture cases:

| Kind | Valid case (no output) | Broken case (expected line) |
|---|---|---|
| Markdown file | `[a](b.md)`, `[a](my%20file.md)`, folder link | `[a](missing.md)` -> `missing file` |
| Anchor | `#intro`, `b.md#setup`, duplicate heading `#setup-1`, Chinese heading | `b.md#nope` -> `missing anchor` |
| Image and reference | existing image, `[r]: b.md` | missing image, `[r]: gone.md` |
| Ignored | link in fenced code, inline code, `https://`, `mailto:` | none |
| Angle destination | placeholders `[a](<architecture-path>)`, `[a](<root-code-style-path>)` beside no such file; existing `[a](<my file.md>)` | `[a](<missing.md>)` -> `missing file` |
| `AGENTS.md` table | `` `docs/b.md` `` in root and nested `AGENTS.md` (each from its folder); `` `<path>` ``; `` `Node.js` ``; `` `dotnet test src/App.Tests` `` | `` `docs/gone.md` `` -> `missing file`; `` `docs/User Guide.md` `` (no such file) -> `missing file` |
| HTML | existing `href` and `src`; `https://` | missing `href`, missing `src` |
| Skipped folders | broken links inside `node_modules`, `bin`, `obj`, `.git` | none |

It also runs on a clean subset and expects exit 0, and on a missing `-Path` and
expects exit 2.

Why: B1 needs a repeatable check against known broken links (Interpretation 13).

### `SKILL.md` (edit)

- **Frontmatter `description`:** add that it installs and version-checks the
  bundled read-only documentation link checker; change the "code" exclusion to
  "application code". Keep it at or below 1024 characters.
- **Output:** add `scripts/Test-DocLinks.ps1` in the project: copy the master
  from this Skill when missing (create `scripts/` if needed); never overwrite.
- **Workflow / write:** after copying, run it once from the repository root to
  verify the command (a reported broken link still verifies the command; report
  the links found), then add the Commands entry. On refresh, compare version
  headers and report an older or newer project copy, or a same-named file
  without a header. `audit` reports the same comparison without writing.
- **Code-style lines:** state that the code-style route and the Working-rules
  "read the code-style section first" line are owned by `code-style`; this Skill
  keeps them and does not count them as code-style rules in its consistency
  check.
- **Consistency Check and Completion:** include the script copy, its version
  result, and the Commands entry.

Why: B2, A4 (ownership is explicit in both Skills).

### `assets/agents.template.md` (edit)

Add one bullet in `Verified Commands And Checks`:

```markdown
- From the repository root, run
  `powershell -ExecutionPolicy Bypass -File scripts/Test-DocLinks.ps1` after
  editing documentation, and fix each reported link (use `pwsh -File` where
  Windows PowerShell is unavailable).
```

Why: B2 asks for a Commands entry; the template's command section is a bullet
list, so the entry is a bullet.

## File changes: collection

### `skills/coding/README.md` (edit, public capability changes)

- `coding-agent-instructions` row: add the copied `scripts/Test-DocLinks.ps1`
  and its `AGENTS.md` command to the default output.
- `code-style` row: owner default profile; one inheriting file per project in
  multi-project workspaces; missing `.editorconfig` and `.vscode` files from
  templates after confirmation; formatter-first bounded `apply`/`audit`.
- Document boundary row for `docs/code-style.md`: replace "only genuine local
  differences" with the inheriting project file rule; keep "tool configuration
  itself" out of the document.

The README stays in Chinese, as today.

## Files read and not changed

| File | Reason |
|---|---|
| `15.coding-agent-instructions/assets/feature-workflow.profile.md`, `references/branch-style.md` | Not affected |
| `scripts/deploy-skill/deploy-skills.json` | Both Skills are already mapped; folders do not move |
| `skills/coding/examples/wms-workflows.md` (lines 60-62, 73-76) and `skills/coding/_doc/coding-skill-kit.md` (lines 65-70) | Expected results become incomplete (no link checker copy, no Working-rules line, "stops at that one route"). Outside the target Skills and README, so reported, not changed, unless the user adds them to scope |
| `docs/coding-agent/coding-agent-design.md` (line 464) | Historical design record that says tool configuration stays outside `code-style`; reported as superseded, not changed |
| This repository's own `AGENTS.md` | Not a target project; no link-checker copy here |

## Implementation segments

1. code-style references and assets: default profile, SQL, XAML, formatting,
   apply-batching references; language reference edits; delete the baseline;
   template edits and new templates. Check: JSON parse, link check of the
   folder.
2. code-style `SKILL.md`. Check: frontmatter, description length, links, line
   count, apply-batching worked numbers walkthrough.
3. `Test-DocLinks.ps1` and its test; coding-agent-instructions `SKILL.md` and
   template. Check: parse, test script on both shells.
4. Collection README, consistency scan, and the full acceptance list.

Work is serial: the files share rules and wording, so parallel subagents would
add merge cost.

## Acceptance checks

Run in the implementation run; record command, exit code, and short result.

1. Parse check, no errors, for the new scripts:
   `[System.Management.Automation.Language.Parser]::ParseFile(...)` in
   Windows PowerShell 5.1 and pwsh 7.
2. `powershell -ExecutionPolicy Bypass -File skills/coding/15.coding-agent-instructions/scripts/tests/Invoke-DocLinksTests.ps1`
   exits 0; same with `pwsh -File` when pwsh is installed, else reported as not
   run.
3. `Test-DocLinks.ps1 -Path .` against this repository: record exit code and
   output; inspect every reported item; any false positive is a defect fixed
   before completion. Real broken links are reported, not fixed in that run.
4. `Test-DocLinks.ps1` on `skills/coding/16.code-style`,
   `skills/coding/15.coding-agent-instructions`, and `docs/plans`: exit 0. This
   includes the unrendered templates, whose project-only links are
   placeholders.
5. `ConvertFrom-Json` parses both VS Code templates.
6. Frontmatter: `name` matches the folder's logical name; each `description` is
   at or below 1024 characters and states triggers and exclusions.
7. Stale-rule search in `skills/coding/` (excluding `_obsolete/`): no remaining
   "never create or modify" configuration rule except the existing-file case, no
   "empty scoped files" rule, no link to `editorconfig-baseline.md`.
8. Walkthroughs written into the run report: agv-tools layout through `define`
   (root `docs/code-style.md` with shared C#, `frontend/docs/code-style.md` with
   TS rules, two `Local Rules: None.` files, root `AGENTS.md` route and rule),
   and the apply-batching worked numbers.
9. `git diff --check` reports nothing.
10. `powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly`
    lists `code-style` and `coding-agent-instructions` from their current
    folders.

Limits: these checks show structure and script behavior. They cannot prove
that a model follows the profile or that the batching thresholds keep token use
in budget; that needs real runs and later tuning.

## Out of scope

- Hooks for Claude Code, Codex, or Copilot.
- Any `cross-agent` change or a code-style stage.
- Obsidian `[[wikilinks]]`.
- Editing any project repository, including agv-tools.
- Deployment before review and commit.
- The gap scan script (Interpretation 11).
- Shipping `.prettierrc`, Ruff, analyzer, or other formatter configuration;
  C# style or severity settings in `.editorconfig`; XAML or SQL formatters;
  line-ending policy.
- Link checker: case-only mismatches, HTML fragment anchors, extra skip folders,
  fixing broken links it finds in this repository.
- Edits to examples, `_doc`, and `docs/coding-agent/` (reported only).

## Risks

- `define` asks fewer questions because the profile decides; a project with a
  different convention must say so in its own document, or the profile rules
  are written.
- A full XML documentation rule on internal and key private members makes C#
  apply runs larger; batching bounds context, not total cost.
- Token estimates by bytes / 4 are rough, especially for non-ASCII text.
- `AGENTS.md` route detection is a heuristic. A route with no separator that
  does not end with `.md` (for example `` `package.json` ``) is not checked, and
  a command whose first word is a path, or that ends with `.md`, is checked as a
  path. Acceptance check 3 shows whether either happens in practice.
- A real link whose whole destination is a dotless, slashless name in angle
  brackets, such as `[a](<LICENSE>)`, is treated as a placeholder and not
  checked.

## Implementation notes

Deviations and details the plan left open, recorded by the implementation run:

- The C#, frontend, and Python references also change their precedence line
  ("a consistent repository pattern the user confirms" becomes the owner
  default for an unenforced rule) and their placement tables ("scoped file"
  becomes "project file"). Why: mechanical consistency with the new Define
  step 5 and placement rule.
- The template's test-code documentation exemption is a placeholder in
  `Tests`; `Documentation` gets a layout placeholder. Why: one place per rule.
- `Test-DocLinks.ps1` prints the count line as `Broken links: N`, detects
  fences at any indentation, does not treat footnotes `[^id]:` as reference
  definitions, and strips `#fragment` and `?query` from `AGENTS.md` route
  candidates before the existence check. Why: the plan did not fix these
  details; each avoids a false positive.
- The test fixture adds `[o](nofolder/)` -> `missing folder` and a leading-`/`
  link in the clean subset. Why: cover the `missing folder` reason and root
  resolution.
- After review of real repository scans, three false-positive classes were
  fixed, each with a Git work-tree fixture case:
  - HTML `href`/`src` starting with `/` (Vite `/src/main.tsx`, built
    `/assets/x.js`) resolves from the HTML file's folder, not from `-Path`.
  - `AGENTS.md` route candidates starting with `/` (such as `/api/v1`) are URL
    paths and are skipped.
  - Inside a Git work tree, only files from
    `git ls-files --cached --others --exclude-standard` are scanned, so
    ignored generated or cached folders (`dist`, `TestResults`,
    `.cross-agent`, `scripts/external-skills/cache`) are skipped. The fixed
    `node_modules`/`bin`/`obj`/`.git` skip remains the fallback outside Git.
- Verification gap: the test passed in Windows PowerShell 5.1; pwsh 7 is not
  installed on the verifying machine, so the pwsh half is unverified.
- Follow-up outside this change: templates of other Skills (`feature-map`,
  `feature-plan`, `functional-spec`) still link to project-only files and are
  reported by the checker; convert them to whole-destination placeholders in
  a separate change.
