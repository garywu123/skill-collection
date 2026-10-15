# Apply And Audit Batching

Read this reference for `apply` and `audit` of a code scope.

## Procedure

1. Run the configured formatter first, limited to the scope, without a model.
   Use only a verified command; otherwise report that no formatter ran. For
   `audit`, use its check mode.
2. Scope: files changed since a given commit, including untracked files in
   scope, or a named folder or package. Use the whole repository only when the
   user asks.
3. Documentation scope: after the formatter run, keep only in-scope files of a
   confirmed language whose style section sets comment or documentation rules.
   Drop test code, identified from the project's test configuration and naming
   such as `*.test.*`, `*.spec.*`, `e2e/`, `tests/`, and `__tests__/`; tool
   configuration such as package, build, lint, format, and test configuration
   and lockfiles; and data or style files with no comment rules, such as JSON,
   YAML, and CSS unless the style file sets comment rules for them. Test code
   gets the formatter pass only. Sum the remaining bytes / 1024 as KB and list
   each file's KB for packing. A PowerShell 5.1-compatible command:

   ```powershell
   $files = @(git diff --name-only --diff-filter=ACMR <commit> -- <path>) + @(git ls-files --others --exclude-standard -- <path>)
   $doc = @($files | Where-Object { $_ -match '<source pattern>' -and $_ -notmatch '<test and configuration pattern>' -and (Test-Path -LiteralPath $_) } | Get-Item)
   [math]::Round(($doc | Measure-Object Length -Sum).Sum / 1KB)
   ```

   For a named folder, `$files` is `git ls-files` plus untracked files of that
   folder. Frontend example patterns: source `\.(ts|tsx|js|jsx)$`; excluded
   `(^|/)(e2e|tests?|__tests__)/|\.(test|spec)\.[cm]?[jt]sx?$|\.config\.[cm]?[jt]s$`.
4. At most 100 KB, one batch budget: the orchestrating session does the work
   itself, batch by batch, grouped by language and folder. Edit rules, for the
   session and every subagent: read each file once, where a shell read such as
   `cat` counts as a read, and do not read it again after your own edit; edit
   with targeted replacements (the `Edit` tool or an equivalent patch), never a
   whole-file write.
5. Above 100 KB: use documentation subagents on a strong model (Sonnet class),
   one per packed batch. Packing: a file larger than 100 KB gets its own
   batch. For the rest, `n = ceil(rest KB / 100)`; fill batches in folder
   order, grouped by language and folder, to about `rest KB / n` each and never
   above 100 KB; add a batch when a file does not fit. At most 5 subagents run
   at once, so waves = `ceil(batches / 5)`, counted from the packed batches,
   not from the total KB: a scope below the cap can still need a second wave.
   Start the next wave only after the current wave returns. Above 500 KB of
   documentation scope, ask the user to narrow the scope; continue above it
   only on the user's confirmation.
6. Subagent brief: the project's own `Comments` and `Documentation` sections
   from the root file and the matching language section from the root or
   project file, with the statement that these project rules win over anything
   else in the brief; the [Do Not Write](code-style-frontend.md#do-not-write)
   section only for a TS/JS batch whose project language section adopts the
   rules it illustrates, that is, it limits module headers to boundary modules
   and sets the export documentation depth; and the batch's file list with KB
   per file. Instruct the subagent to follow only the carried rules, including
   any wrapping rule they set, because the formatter does not wrap comments; to
   follow the edit rules of step 4; to start no subagents; and to return at
   most 10 lines: the changed files and at most 3 unsure items as `file:line`
   plus one sentence; no diffs or file contents. For `audit`, return files with
   gaps and rule names instead of changed files.
7. Use a cheap model (Haiku class) only for mechanical leftovers the formatter
   cannot do, such as turning a one-line `<summary>` into the indented layout,
   and only when the platform allows choosing a model.
8. Verify with `git diff --stat`, the formatter's check mode on the scope, the
   verified build and tests, and 2-3 spot-checked diffs. A documentation diff
   shows only comment lines and formatter output; report any reflowed or
   changed code line.
9. When no subagents are available, for example in Codex, run the same batches
   in sequence.
10. Budget and cap are defaults; a run may pass a temporary override. Record per
    batch the actual KB and file count, and per subagent the peak context and
    API calls when the platform reports them; otherwise record "not available".
    Never estimate them.

## Worked Numbers

Budget 100 KB, cap 500 KB, at most 5 running. The totals assume the files pack
into 100 KB batches as in step 5; the packed batch count, not the total,
decides the number of subagents and waves.

| Documentation scope | Plan |
|---|---|
| 80 KB | The orchestrating session does the work itself |
| 100 KB | The orchestrating session does the work itself; the scope fits one budget |
| 140 KB | 2 subagents of about 70 KB, one wave |
| 260 KB including one 130 KB file | 3 subagents: the large file alone, then two of about 65 KB; one wave |
| 319 KB, 46 files (agv-tools trial; 985 KB tracked before tests and configuration were excluded) | 4 subagents of about 80 KB, one wave |
| 480 KB | 5 subagents of about 96 KB, one wave |
| 480 KB as six 80 KB files | 6 subagents of one file each, because two files exceed 100 KB; waves of 5 and 1 |
| 520 KB | Ask the user to narrow the scope |
| 750 KB, confirmed by the user | 8 subagents of about 94 KB, waves of 5 and 3 |

About 100 KB of source is roughly 25-30k tokens. With about 53k tokens of fixed
overhead per subagent, the trial's 197 KB batch peaked at 188k context with
whole-file rewrites. The budget is a default to tune from recorded runs.
