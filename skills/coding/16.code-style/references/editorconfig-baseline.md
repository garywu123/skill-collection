# EditorConfig Comparison Baseline

## Purpose And Precedence

Use this reference to compare repository formatting and file hygiene with a
modest baseline. It is decision and audit guidance, not a copy-on-detection
template. Treat every inspected configuration surface as read-only evidence.

Existing repository configuration and approved project documents outrank this
baseline. Explicit user-selected defaults also outrank generic best practice.
When evidence is absent, propose the baseline rule to the user; write it into
`docs/code-style.md` only once they approve it, and never change project
configuration to match.

## Inspect

- Read the nearest applicable `.editorconfig` for each relevant path and the
  root `.editorconfig`, if present.
- Read IDE or editor settings only when they are repository-scoped.
- Read applicable formatter, linter, analyzer, and build configuration.
- Identify generated, vendor, third-party, and minified paths that tooling
  excludes or should leave untouched.

## Comparison Baseline

| Concern | Modest comparison default |
|---|---|
| Character encoding | UTF-8 |
| Final newline | Present in text files |
| Trailing whitespace | Remove it, except intentional Markdown hard breaks |
| C# indentation | Spaces, width 4 |
| Python indentation | Spaces, width 4 |
| Frontend indentation | Follow repository tooling; when absent, compare against spaces, width 2 |
| Generated or external content | Exclude generated, vendor, third-party, and minified files from formatting |

Do not automatically copy these values into `.editorconfig` or another file.
Do not invent diagnostic severity. Follow repository or platform policy for
line endings rather than imposing LF or CRLF. Language-specific formatters,
compilers, linters, and analyzers remain authoritative for language semantics.

## Audit Decision

- Existing and consistent: route to it from the style file's tooling table.
- Existing but different from the baseline: preserve it unless the user
  approves a change; report a conflict only when repository evidence disagrees.
- Missing: offer the baseline as a written rule in `docs/code-style.md`, but
  never create or edit `.editorconfig` itself.
