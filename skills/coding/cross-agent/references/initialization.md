# Cross-Agent Initialization

Use this only for an explicit `initiate`, `init`, or request to initialize the
Cross-agent configuration. You identify the project settings; `cross-agent init`
validates and writes them. Do not delegate initialization to workers, copy the
template by hand, or edit the configuration as a substitute for the command.

1. Work from the project root governed by the applicable `AGENTS.md`. Check
   Python 3.11 or later and the existing Git work tree, and run
   `cross-agent status` when a configuration exists. Report missing
   prerequisites; do not initialize Git, install tools, or create lifecycle
   documents.
2. Read the project instructions and the build and test definitions they
   reference, such as package scripts, project files, or CI commands. Prefer
   documented commands backed by repository evidence, and never invent tests
   from the detected language. Ask only when a choice is ambiguous or changes
   permissions.
3. Choose the smallest `allowed_commands` for Producer work and exact
   `delivery_checks` for the intended stages; `general` and `feature-delivery`
   both run them, including document-only work. Keep `extra_dirs` as `[]`
   unless the task covers another writable directory. If no reliable checks
   exist, use `[]` and report verification as unconfigured. Resolve the
   installed absolute CLI paths of the selected providers; never persist the
   template's placeholder paths as verified.
4. Write the input to a temporary JSON file outside the work tree and run
   `init`. Pass complete `<provider>:<model>:<effort>` roles only from the
   template or the user's words, and `--skip-version-check` only when the user
   asks to skip the Codex version check.

```text
cross-agent init --input <absolute-temporary-json-path>
                 [--producer <provider:model:effort>]
                 [--reviewer <provider:model:effort>]
                 [--skip-version-check]
```

```json
{
  "allowed_commands": ["python -m unittest"],
  "delivery_checks": ["python -m unittest discover -s tests -v"],
  "extra_dirs": [],
  "cli": {
    "claude": "C:/Tools/Claude/claude.exe",
    "codex": "C:/Tools/Codex/codex.exe"
  }
}
```

These values are examples; use the project's actual commands and paths.

5. Run `status` again, remove the temporary input, and report the configuration
   path, `action`, effective project commands and roles, `cli_executables`,
   remaining prerequisites, and `codex_version` with its `installed`, `latest`,
   `status`, and `reason`. Only `current` means current; `not-installed`,
   `unknown`, and `skipped` never do. Do not upgrade the CLI. Report any
   `proposed_*_differences` as proposals, not installed changes.

`init` never overwrites existing settings. Changing them, or adding optional
keys the template documents such as stage roles, `[experts.*]` routes,
`test_reports`, or `check_paths`, needs an explicit configuration-change task.
For a multi-project workspace, a project's local configuration may hold only a
`config_file` pointer to one shared file with explicit project-root sections.
If the configuration path is unwritable, report the restriction instead of
switching to a user-level file. Valid syntax and a current version do not prove
model access, supported effort, or passing checks.

Initialization runs no project checks, starts no workers, and creates no run.
Stop after the report unless the user also authorized a task; then first report
missing prerequisites that would block its stages.
