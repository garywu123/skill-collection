# Apply And Audit Batching

Read this reference for `apply` and `audit` of a code scope.

## Procedure

1. Run the configured formatter first, limited to the scope, without a model.
   Use only a verified command; otherwise report that no formatter ran. For
   `audit`, use its check mode.
2. Scope: files changed since a given commit, including untracked files in
   scope, or a named folder or package. Use the whole repository only when the
   user asks.
3. Estimate tokens as total bytes / 4. A PowerShell 5.1-compatible command:

   ```powershell
   $files = @(git diff --name-only --diff-filter=ACMR <commit> -- <path>) + @(git ls-files --others --exclude-standard -- <path>)
   ($files | Where-Object { Test-Path -LiteralPath $_ } | Get-Item | Measure-Object Length -Sum).Sum / 4
   ```

4. Under about 80k tokens: the orchestrating session fixes the files itself,
   batch by batch, grouped by language and folder, without subagents.
5. Above about 80k: use documentation subagents on a strong model (Sonnet
   class). Count = ceil(tokens / 60k), at most 5 running; start the next wave
   only after the current wave returns. Above about 300k, ask the user to
   narrow the scope.
6. Subagent brief: only the matching language section and its file list; no
   subagents of its own; return at most 10 lines: the changed files and at most
   3 unsure items as `file:line` plus one sentence; no diffs or file contents.
   For `audit`, return files with gaps and rule names instead of changed files.
7. Use a cheap model (Haiku class) only for mechanical leftovers the formatter
   cannot do, such as turning a one-line `<summary>` into the indented layout,
   and only when the platform allows choosing a model.
8. Verify with `git diff --stat`, the verified build and tests, and 2-3
   spot-checked diffs.
9. When no subagents are available, for example in Codex, run the same batches
   in sequence.
10. Thresholds are defaults; a run may pass a temporary override. Record actual
    counts in the completion report so the defaults can be tuned.

## Worked Numbers

| Estimated tokens | Plan |
|---|---|
| 60k | The orchestrating session fixes the files itself |
| 120k | 2 subagents, one wave |
| 290k | 5 subagents, one wave |
| 320k | Ask the user to narrow the scope |
| 450k, confirmed by the user | 8 subagents, waves of 5 and 3 |

Waves occur only above 300k, because ceil(300k / 60k) = 5 is the running limit.
