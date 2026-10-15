# Formatting Configuration

Read this reference for `define` when formatting configuration is missing or
present, and for an `audit` of configuration.

## Templates

- [EditorConfig template](../assets/editorconfig.template) for `.editorconfig`;
- [VS Code settings template](../assets/vscode-settings.template.json) for
  `.vscode/settings.json`;
- [VS Code extensions template](../assets/vscode-extensions.template.json) for
  `.vscode/extensions.json`.

Default formatters: C# `ms-dotnettools.csharp`; TypeScript, JavaScript, JSON,
and YAML `esbenp.prettier-vscode`; Python `charliermarsh.ruff`, or
`ms-python.black-formatter` when the project already configures Black. XAML and
SQL get no formatter entry. The Skill ships no `.prettierrc`; a project
Prettier `printWidth` wins over `max_line_length`. Prettier reads `indent_size`
from `.editorconfig` when no `tabWidth` is set, so the EditorConfig template
covers every extension Prettier formats in a frontend project, including CSS,
SCSS, Less, and HTML.

## Compare Existing Configuration

Existing `.editorconfig`, `.vscode/*.json`, `.code-workspace`, and formatter
configuration are read-only. Report each difference from the templates and
never change these files.

## Create Missing Files

1. Render the templates and remove sections and entries for languages that are
   not confirmed.
2. Show the full content of each file to the user.
3. Create a file only after the user approves it. In a non-interactive run,
   report the proposal instead of writing.

## VS Code Levels

- Single-folder repository: create missing `.vscode/` files at the repository
  root.
- Multi-root workspace: create missing `.vscode/` files only in workspace root
  folders, never in nested non-root folders, which VS Code ignores.
- An existing `.code-workspace` file is existing configuration: show the
  proposed `settings` block and report it without editing the file.
- Keep `editor.formatOnSave` inside each language block, so Markdown and other
  files are not reformatted by an unexpected default formatter.
- Never write machine-level user settings.

## Optional Machine Check

Only when the user asks: read the user's VS Code settings and report
recommendations, such as a global default formatter that overrides the
workspace or a missing EditorConfig extension. Never print or edit that file.

## Always

- Do not impose LF or CRLF line endings.
- Exclude generated, vendor, third-party, and minified files from formatting.
- Language formatters, compilers, linters, and analyzers stay authoritative for
  language semantics.
