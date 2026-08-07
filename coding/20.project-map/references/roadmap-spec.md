# roadmap.yaml Specification

One file per project, at the repository root. It replaces a workflow pointer, a
generated artifact index, and a decision log with one file a human can read in
under a minute.

## Purpose and limits

It stores **where things are and what state they are in**. It does not store
requirements, design rationale, or history. Domain truth lives in the routed
documents; history lives in Git. Never append a change log to this file.

## Top-level fields

| Field | Required | Value |
|---|---|---|
| `project` | yes | Short project identifier |
| `profile` | no | `lite` or `full`; an intent marker, it enforces nothing |
| `stage` | yes | `discovery`, `prd`, `roadmap`, `architecture`, `implementation`, `done`; descriptive context only |
| `docs` | yes | Map of role to repository-relative path |
| `functions` | yes | List of entries; empty before the roadmap stage |

Add a `docs` role only when that document exists. A path to a file that was
never written is worse than an absent row, because it reads as done.

## Function entries

| Field | Required | Value |
|---|---|---|
| `id` | yes | Stable identifier such as `F001`; never reused |
| `name` | yes | One short line |
| `status` | yes | `planned`, `as-built`, `specified`, `implementing`, `verifying`, `accepted` |
| `spec` | past `planned` / `as-built` | Repository-relative path |
| `checklist` | past `planned` / `as-built` | Repository-relative path |
| `verified` | at `accepted` | `YYYY-MM-DD by <name>` |
| `notes` | no | One line; blocker, supersession, or as-built location |

## Status meanings

`planned` -> `specified` -> `implementing` -> `verifying` -> `accepted`

`as-built` sits outside that line. It means a recognizable implementation
exists in the repository, but this process has not established a complete spec,
business conformance, or acceptance result. It is the honest entry state when
adopting an existing codebase, and it converts to `specified` when someone next
needs to change that function. Record any observed test or runtime evidence in
the routed as-built record or a concise `notes` value; the status itself never
claims that the function works.

## Status rules

- Move forward one status at a time. State the reason when moving backward.
- `specified` requires both a spec and a checklist to exist.
- Only a human sets `accepted`, and only after the checklist is verified in a
  fresh conversation.
- Never record `accepted` for work that predates this process. Use `as-built`
  and say where the code lives in `notes`.
- Changing an accepted function's behavior resets it to `specified` and removes
  its `verified` field. Rebuild changed acceptance criteria and clear every old
  checklist box, Evidence row, Decision, reviewer, and date; Git holds the
  previous spec, checklist, and evidence.
  Create a successor only when the old and new capabilities need independent
  deployment, support, acceptance, migration, or long-term tracking, and
  cross-reference both in `notes`.
- An agent updates only the routes and function entries directly changed by its
  authorized work, in the same turn as the work. `project-map` owns the schema,
  initialization, whole-file refresh, and audit; it is not the only writer.

## Write-back contract

Update the map when a routed artifact is created, moved, or removed, or when a
function's real delivery state changes. Do not update it merely because an
operation ran. Before the final response, reconcile the affected entries with
the files and evidence changed in that turn. Never advance unrelated entries.

The human may set `accepted` only in a fresh verification conversation after
every applicable checklist item has evidence. That verification context fills
the checklist Decision and then records `accepted` and `verified`; it does not
repair implementation in order to make the checklist pass.

## Size

One line per field, no nested prose. If an entry needs a paragraph, that
paragraph belongs in the function's spec and the entry points at it. A
`roadmap.yaml` that no longer fits on a screen is holding content that belongs
somewhere else.

## What this file deliberately cannot do

- It does not prevent an agent from editing an approved document. Your review of
  the Git diff does.
- It does not prove an approved artifact is unchanged. `git log <path>` is the
  substitute.
- It is not a concurrency-control system. Parallel writers must use ordinary
  Git coordination and resolve overlapping edits rather than treating the file
  as a lock.
