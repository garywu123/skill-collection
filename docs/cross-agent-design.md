# Cross-Agent Review v1 Design

Historical v1 design. The current contract is
[Cross-Agent](../skills/coding/cross-agent/SKILL.md): it now supports PM-style
orchestration across user-authorized stages and live progress. The manual
single-stage invocation and buffered-output limitations below describe v1.

Status: implemented as v0.1.0, revision 5, 2026-09-26. The Skill and its CLI
live in `skill-collection/skills/coding/cross-agent/`: `SKILL.md`, the CLI in
`scripts/`, and the configuration example in `assets/`. This folder is a
temporary home for the design; move it next to the CLI after review.

## Summary

- The main session runs a thin `cross-agent` Skill and acts as Orchestrator. It
  talks to the user, adjudicates every review finding, and edits files only
  during finalization.
- A `cross-agent` CLI owns every deterministic mechanism: workers, permissions,
  schemas, the review budget, snapshots, run state, and cleanup. It ships in the
  Skill's `scripts/` folder, so deploying the Skill deploys the CLI. It needs
  Python 3.11 or later and only the standard library.
- Two resumable workers do the work: a Producer that follows the stage's
  lifecycle Skill, and a read-only Reviewer. One state file per run lets a
  replacement worker continue.
- Provider and model are chosen per run. Lifecycle Skills stay unchanged in v1.
- v1 is driven manually: the user names one stage and one artifact per run.
- Non-blocking leftovers go to a human-owned review backlog. All other process
  data is deleted at close.

Lean claim: the smallest reliable v1 is one Orchestrator Skill, one CLI, two
resumable workers, one state file per run, and one optional backlog. It needs
no platform agent definitions, nested delivery workers, run-file hierarchy, or
lock service. The recovery test under Validation can disprove this
claim; split the state file only if that check fails.

## Architecture

| Layer | Owns | Never does |
|---|---|---|
| Orchestrator: main session plus `cross-agent` Skill | Chat context, user questions, adjudicating findings, finalization, choosing the next run, the final report | Edit files outside finalization, change the sequence or budget |
| `cross-agent` CLI | Starting, resuming, and replacing workers; per-role permissions; schema checks; sequence and budget; snapshots; `state.json`; check runs; backlog output; cleanup | Judge content |
| Producer worker | Following the stage Skill, fixing accepted findings | Decide which findings are accepted |
| Reviewer worker | Findings within the review boundary | Modify any file, decide that more work must happen |

Calls go one way: the Orchestrator calls the CLI, and the CLI starts workers.
Workers never call the CLI or each other. The Skill knows only the stable
`cross-agent` commands; the CLI's provider adapters own the volatile Claude
Code and Codex flags, output parsing, session IDs, permissions, and cleanup.
Do not duplicate those flags in the Skill.

Workers run as headless sessions through the CLI, not as native subagents,
because:

- a native subagent always uses the main session's provider, while the
  Reviewer is often the other provider;
- the Orchestrator Skill must behave the same in Claude Code and Codex; and
- only an external process can pin each role's model and enforce a read-only
  Reviewer.

## Context Sources

Workers do not share a conversation, and no worker reads `state.json`.

| Source | Content | Read by |
|---|---|---|
| Project files | The stage Skill, `AGENTS.md`, the artifact, its upstream documents, and code | The worker itself |
| The worker's session | What it already read and reasoned about, kept across resumes | The worker itself |
| Run messages in the prompt | The request, accepted findings, earlier findings and adjudications, Producer outcomes, the diff since the previous review, check results, and user answers | The CLI, which takes them from `state.json` and Git |

`state.json` is the run's control state and message relay. For example, the
CLI stores a Reviewer's findings there and places the accepted ones in the
Producer's next prompt. A replacement worker also receives the short run
summary, then rereads the project files itself. Provider transcripts are never
the recovery record.

## Scope

v1 stages:

- `feature-map` and `feature-plan`;
- `feature-delivery`, validated after the documentation stages work; and
- `general`, for work without a lifecycle Skill, reviewed against `AGENTS.md`
  and the user's request.

A refactor is not a separate stage: `feature-plan` and `feature-delivery`
already cover behavior-preserving simplification.

Not in v1:

- running several stages or Features in one instruction;
- `feature-storyboard`, whose checks need browser rendering;
- parallel runs, commits, and audit records; and
- the items under Deferred.

## Commands

```text
cross-agent start  --stage <stage> --artifact <path> --first <produce|review>
                   [--request "<text>"] [--producer <spec>] [--reviewer <spec>] [--dry-run]
cross-agent next   --run <id>
cross-agent decide --run <id> --input <file>
cross-agent answer --run <id> --text "<answer>"
cross-agent status [--run <id>]
cross-agent close  --run <id>
```

- `<spec>` is `<provider>[:<model>[:<effort>]]`, such as `codex` or
  `claude:opus:high`. An omitted model uses the provider CLI's own default
  model. Omitted specs use the configured defaults.
- The user states roles in natural language, such as "Claude Opus produces and
  Codex reviews". The Orchestrator Skill translates that into `--producer` and
  `--reviewer` specs. Nobody writes `state.json` by hand: `start` creates it
  and records the resolved provider, model, and effort.
- `--first produce` requires `--request`; a Producer without a concrete request
  reruns its whole Skill and rewrites without purpose. `--first review` suits an
  existing artifact.
- `start` prints the run ID. With `--dry-run` it prints the prompts and command
  lines without creating a run.
- `next` performs the next action and prints a JSON event. After a review it
  stops at `awaiting-decision`; after a Producer question it stops at
  `awaiting-answer`. Called again while the run waits, it prints the same
  pending event.
- `decide` reads the Orchestrator's adjudications from a JSON file outside the
  work tree. A file avoids JSON quoting problems on the Windows command line,
  and its location keeps it out of snapshots.
- `answer` records the user's answer to a Producer question; the next `next`
  resumes the same Producer with it.
- `status` reports one run's phase, next action, and counts. Without an ID it
  lists open runs, so a later session can find unfinished work.
- `close` writes selected backlog items, then deletes the run's state and
  cleans up worker sessions. A run that is not `done`, `failed`, or `blocked`
  needs `close --abandon`.
- The Skill runs the CLI as `python <skill-dir>/scripts/cross_agent.py
  <command>`. Every command prints one ASCII-only JSON object, which reads the
  same in every Windows console code page; refused requests print `{"error"}`
  and exit with code 2.
- There are no `pause`, `resume`, `recover`, `handoff`, `unlock`, or `list`
  commands. An open run is resumable by `next`, which also replaces an
  unavailable worker.
- The CLI refuses a second open run for the same artifact by scanning the open
  `state.json` files.
- Run from the project root: the directory whose `AGENTS.md` governs the
  artifact, which may sit below the Git repository root. A dirty work tree is
  fine. While a run is open, only its workers, and the Orchestrator during
  finalization, edit the work tree; snapshots would count anyone else's edits
  as the run's.

## Configuration

The configuration is TOML, because Python's standard library reads TOML but not
YAML. It lives at `~/.cross-agent/config.toml`, or where `CROSS_AGENT_CONFIG`
points, and never inside the Skill folder: each deployment replaces that folder.
Every key is optional; `assets/config.example.toml` documents them. A run copies
its settings at `start`, so a later edit never changes an open run.

```toml
max_reviews = 2
timeout_minutes = 30
rotate_at_tokens = 350000
backlog_rejected = true
max_diff_kb = 200

[defaults]
producer = "claude"
reviewer = "codex"

[projects."D:/code/work-space/work-projects/sgvm/development/vehicle-simulator"]
allowed_commands = ["dotnet build", "dotnet test", "npm test", "npm run"]
delivery_checks = [
  "dotnet build VehicleSimulator.slnx",
  "dotnet test VehicleSimulator.slnx -f net10.0 --no-build --no-restore",
]
extra_dirs = ["../agv-algorithms"]
```

- `max_reviews` applies to every stage.
- `rotate_at_tokens` defaults to 350000 and is meant to be tuned from real use;
  `0` turns rotation off.
- `backlog_rejected` decides whether rejected findings reach the backlog;
  `status` prints it with the other effective settings.
- Stage Skills need no configuration: the CLI finds `<stage>/SKILL.md`, or
  `<ordinal>.<stage>/SKILL.md` in the authoring repository, next to its own
  Skill folder. `[stages.<stage>] skill = "<path>"` overrides that.
- `projects` keeps project commands out of the project tree. `extra_dirs` are
  readable by both workers and writable by the Producer.
- Run state has a fixed location, described under Run State, so that `status`
  can discover it.

## Run Flow

### Sequence

A review is the budgeted operation. Each non-passing review may cause at most
one Producer revision.

```text
--first produce, max_reviews N: P0 -> R1 -> P1 -> ... -> RN -> PN -> Finalize
--first review,  max_reviews N:       R1 -> P1 -> ... -> RN -> PN -> Finalize
```

- `P0` creates or changes the artifact from `--request`.
- Each review `Rk` covers the artifact and the changes since the previous
  review.
- Each Producer revision `Pk` fixes the findings accepted after `Rk`.
- At most `N + 1` Producer calls run in `--first produce`, and `N` in
  `--first review`.
- The run stops early, as soon as an adjudication leaves no accepted `blocker`
  or `major` finding.
- Finalization runs only after `PN`, whose changes no Reviewer has seen.

### Adjudication

The Reviewer proposes findings; it does not decide that more work must happen.
After each review, the Orchestrator gives every open finding one disposition
through `decide`:

- `accepted`: a current `blocker` or `major` defect, sent to the Producer;
- `note-only`: a valid but nonessential improvement that triggers no Producer
  call and goes to the backlog;
- `rejected`: not a current defect, with a rationale that stops the same point
  from being raised again in this run. A new idea that would change direction
  is not a current defect; or
- `needs-user-decision`: a current defect whose fix would change product
  behavior, UI behavior, technical direction, or an authoritative document, and
  that the user chose to leave open. It goes to the backlog.

When such a defect blocks the run, the Orchestrator asks the user before
calling `decide` and records the answer as `accepted` with guidance, `rejected`,
or `needs-user-decision`. The run waits at `awaiting-decision` meanwhile, so the
adjudication needs no blocking flag.

Only accepted `blocker` and `major` findings consume a Producer call. Severity
is the Reviewer's; the Orchestrator cannot raise it, so a `minor` defect goes to
the backlog. The CLI rejects an adjudication that accepts a `minor` finding,
omits an open finding, or lacks a rationale for a non-accepted finding.

The Producer reports each accepted finding as `fixed` or `not-fixed` with a
rationale. A `not-fixed` finding returns to the Orchestrator at the next
adjudication; it never earns an extra Producer call.

A Producer `status` of `needs-user-decision` or `blocked` pauses the run; the
Producer uses it only when its Skill says to stop or ask.

### Review Boundary

A Reviewer may report only:

- an unmet requested outcome;
- a direct conflict with an authoritative input;
- a real validation failure;
- an internal contradiction;
- a regression caused by the latest change; or
- a concrete security, permission, data-loss, or irreversible-action risk.

Each finding cites a rule, a `path:line`, or a real failing command. Alternative
designs, unsupported style preferences, speculative future concerns, unrelated
cleanup, optional refactoring, and general improvement ideas belong in `notes`.

After the first review, the Reviewer reports every earlier finding as `resolved`
or `open`, and a new finding must be a `blocker` or a regression introduced by
the latest revision.

### Finalization

After `PN`, the CLI moves the run to `finalizing` and write ownership passes to
the Orchestrator; no separate handoff command exists.

- The `finalizing` event carries the final diff and the remaining accepted
  findings. The Orchestrator reads them and only what they cite, so its context
  stays small.
- It may make one bounded correction batch for accepted, local,
  non-scope-changing problems. It does not start another worker loop.
- It records each accepted finding it leaves unfixed, because the fix is not
  local or would change product behavior, UI behavior, technical direction, or
  another authoritative boundary, as `needs-user-decision` with `decide`.
- It then calls `next`. The CLI snapshots the correction batch, reruns the
  applicable checks once, and records the final status.

### Final Status

| Status | Meaning |
|---|---|
| `failed` | Timeout, non-zero exit, schema-invalid output, an oversized diff, or a Reviewer that changed files. |
| `blocked` | The Producer reported a concrete blocking condition from its Skill. |
| `needs-user-decision` | Finalization left an accepted finding unfixed because its fix is beyond the Orchestrator's authority. |
| `completed-by-orchestrator` | The final state was accepted in finalization rather than by an independent review. |
| `independently-passed` | An adjudicated review left no accepted `blocker` or `major` finding, and nothing changed afterward. |

When several statuses apply, the first row in the table wins.

## Run State

### State File

Each run keeps one state file in an ignored, project-local directory:

```text
.cross-agent/runs/<run-id>/state.json
```

`state.json` is the sole machine-state authority. It stores the run and schema
version, artifact, stage, request, start mode, current phase, next action,
review budget and count, Producer count, resolved provider, model, effort, and
CLI version per role, worker session IDs and generations, normalized findings
and adjudications, Producer outcomes, user answers, check results, Git tree IDs,
the final status, the error and truncated raw output of a failed call, and the
small run summary that seeds a replacement worker. The CLI writes it
atomically.

- The CLI builds each provider-neutral prompt from `state.json` and Git diffs.
  The prompt names the Skill and artifact paths; the worker reads those files
  itself.
- The snapshot index file sits beside `state.json` as scratch data, not state.
- Do not add separate `run.json`, `context.json`, `workers.json`, or
  `findings.json` files until a measured size, contention, or recovery problem
  requires one.
- On the first `start` in a repository, the CLI adds `.cross-agent/` to
  `.git/info/exclude`. This changes no tracked file, and it is required:
  otherwise snapshots would see the CLI's own writes as the run's changes.
- Parallel runs are outside v1, so there is no lock subsystem. Add an atomic
  artifact claim file only when parallel start is implemented or an observed
  race proves it necessary.

### Lifetime

- Unfinished, failed, and blocked runs keep their state and stay open until the
  user closes them; an open run blocks new runs on its artifact. `status` finds
  them, `next` continues an unfinished run, and a failed run prints its state
  path.
- `close` first appends the selected backlog items, and deletes the run
  directory only after that write succeeds. It then makes a best-effort
  deletion of the known local provider session files.
- The design never claims deletion of provider server-side data.
- A closed run is not resumable. Later work starts from the artifact, its
  authoritative documents, Git history, and any backlog item the user selects.

### Worker Sessions

- Each role keeps one session for the run and is resumed between steps. This
  saves rereading and lets a user answer reach the same Producer.
- Every prompt still carries its explicit inputs, so any worker can be replaced
  from `state.json` without resetting finding IDs or the review budget.
- Rotation replaces compression. When a worker's latest request used more than
  `rotate_at_tokens` context tokens, its next step starts a fresh session and
  increments that role's generation. In delivery, the Feature Plan's recorded
  results are the progress record. Built-in auto-compaction remains only a
  fallback inside one long step.
- Context size is the latest request's input, not a cumulative total. For
  Claude it comes from the last assistant message in the stream; for Codex, from
  the last `token_count` event in the session rollout file. When it is unknown,
  the worker is not rotated.
- When a resume fails, for example because the session files are gone, the CLI
  replaces the worker once with a fresh session seeded from the run summary. A
  second failure fails the run.
- Auto memory is disabled for every worker, so no process detail reaches
  future sessions.

## Review Backlog

The project owns one visible file:

```text
docs/review-backlog.md
```

- It holds adjudicated `note-only` and `needs-user-decision` items, plus
  `rejected` items while `backlog_rejected` is true (the default). `close`
  appends them; the CLI creates the file with a short header when it is absent.
- The user keeps each item's status current, so the file shows which items are
  still open and which are promoted, resolved, or dismissed.
- Each item records an ID, type, priority (`high | medium | low | none`),
  status (`open | promoted | resolved | dismissed`), source run and finding,
  affected Feature or artifact, symbols or `path:line`, base commit or
  `uncommitted`, proposed change, evidence, and the Orchestrator rationale. A
  rejected item normally has priority `none`.
- The backlog is human-owned, non-authoritative future work. Agents do not read
  or search it unless the user explicitly asks for a backlog review or names an
  item ID.
- An item becomes implementation scope only after the user promotes it into the
  current request or the applicable Feature Map and Plan.
- A current blocker reaches the backlog only after the user has been told it is
  open. Transcripts, prompts, token logs, and snapshots never go into it.
- Split the file by Feature only when its real size makes one file
  inconvenient.

## Result Schemas

All three use the strict subset both CLIs accept: every property required,
`additionalProperties: false`, and nullable values instead of optional ones.
The CLI derives changed files from snapshots. The shapes below are
illustrative.

Review result:

```json
{
  "findings": [
    {
      "id": "R2-001",
      "category": "unmet-outcome | authoritative-conflict | validation-failure | contradiction | regression | risk",
      "severity": "blocker | major | minor",
      "claim": "string",
      "evidence": ["rule citation, path:line, or failing command"],
      "recommendation": "string"
    }
  ],
  "earlier_results": [
    { "finding_id": "R1-001", "result": "resolved | open" }
  ],
  "notes": ["string"]
}
```

`category` mirrors the review boundary, so the schema rejects out-of-bounds
findings. `evidence` must not be empty. `earlier_results` is empty in the first
review. Finding IDs carry the review prefix.

Adjudication input for `decide`:

```json
{
  "decisions": [
    {
      "finding_id": "R1-001",
      "disposition": "accepted | note-only | rejected | needs-user-decision",
      "rationale": "string or null",
      "priority": "high | medium | low | none | null"
    }
  ]
}
```

`rationale` is required for every non-accepted finding; for an accepted finding
it is optional guidance for the Producer, such as the fix the user chose.
`priority` is required for non-accepted findings and null otherwise.

Producer result:

```json
{
  "status": "done | needs-user-decision | blocked",
  "summary": "string",
  "questions": ["string"],
  "blocker": "string or null",
  "outcomes": [
    { "finding_id": "R1-001", "result": "fixed | not-fixed", "rationale": "string" }
  ]
}
```

## Prompts

The CLI builds the same text for either provider. A fresh or replacement
session receives every section; a resumed session receives the sections that
changed.

Producer:

```text
You are the Producer for stage <stage>. You cannot ask the user directly.
Read and follow this Skill completely, including its consistency check: <skill path>
Artifact: <path>
Request: <request text, or "Fix the accepted findings below.">
Run summary: <present for a replacement session>
Accepted findings: <JSON with the Orchestrator's guidance, when present>
User answer: <text, when present>

- When the Skill says to ask the user or to stop, return needs-user-decision or blocked and make no further edits.
- For feature-delivery, work in auto mode.
- Report every accepted finding as fixed or not-fixed, with a rationale.
- Do not commit, and do not start the next lifecycle stage.
- Return only the Producer result object.
```

Reviewer:

```text
You are the read-only Reviewer for stage <stage>, review <k>. Do not modify any file.
Judge the artifact and the changes against this Skill, AGENTS.md, and the artifact's upstream documents: <skill path>
Artifact: <path>
Changes since the previous review: <diff, or "none: review the artifact as it stands">
Earlier findings, adjudications, and Producer outcomes: <JSON, after the first review>
Check results: <delivery only: command, exit code, log excerpt>
Report only: an unmet requested outcome, a conflict with an authoritative input, a real validation failure, an internal contradiction, a regression from the latest change, or a concrete security, permission, data-loss, or irreversible-action risk. Cite a rule, path:line, or failing command for each. Put everything else in notes.
After the first review: report every earlier finding as resolved or open, and add a finding only for a blocker or a regression caused by these changes.
Return only the review result object.
```

## Provider Adapters

Role flags, passed on every call including resumes:

| Provider | Producer | Reviewer |
|---|---|---|
| Claude Code | `--permission-mode acceptEdits`, plus `--allowedTools` built from `allowed_commands` for delivery | `--tools "Read,Grep,Glob"` |
| Codex | `-c sandbox_mode="workspace-write"` | `-c sandbox_mode="read-only"` |

Codex uses `-c sandbox_mode=...` everywhere because `codex exec resume` has no
`-s` flag, and the local `~/.codex/config.toml` defaults to `workspace-write`.

Claude calls, with the prompt on stdin:

```text
start:  claude -p --session-id <uuid> [--model <model>] [--effort <effort>] <role flags> <common>
resume: claude -p --resume <uuid> [--model <model>] [--effort <effort>] <role flags> <common>
common: --output-format stream-json --verbose --json-schema '<schema>' --strict-mcp-config
        --permission-prompts none --add-dir <skill folder> [--add-dir <extra dir>]
env:    CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
```

Codex calls, with the prompt on stdin (`-`):

```text
start:  codex exec --json [-m <model>] [-c model_reasoning_effort="<effort>"] <role flags> <common> -
resume: codex exec resume <thread id> --json [-m <model>] [-c model_reasoning_effort="<effort>"] <role flags> <common> -
common: --skip-git-repo-check --disable memories --output-schema <file> -o <file>
        [-c sandbox_workspace_write.writable_roots=[<extra dirs>]]
```

- The CLI chooses the Claude session ID in advance and reads the Codex thread ID
  from the `thread.started` event.
- Claude's structured result comes from the stream's final `result` event;
  Codex's comes from the `-o` last-message file. Both are then validated
  against the schema.
- `--permission-prompts none` denies anything that would ask for permission,
  so a headless call never hangs.
- A test-only `fake` provider replays scripted results from
  `CROSS_AGENT_FAKE_SCRIPT`, so the automated tests exercise the whole state
  machine without model calls.
- Claude stores sessions per project directory and Codex filters its session
  list by working directory, so every call uses the project root as its
  working directory.
- `--strict-mcp-config` loads no MCP server, because snapshots cannot detect
  writes made through MCP.
- The main Orchestrator is the current chat session; the CLI does not select
  its model.
- Smoke tests on 2026-09-26 with Claude Code 2.1.280 and codex-cli 0.135.0
  confirmed, for both providers: structured output, session resume, context
  size, a refused Reviewer write, a Producer write, reading a Skill outside the
  work tree, and cleanup of the session files.
- Every Codex call also passes `-c approval_policy="never"`. Newer Codex
  releases honor the user's `approval_policy = "on-request"` with an automatic
  approvals reviewer, and a smoke test on 0.158.0-alpha.2 showed a Reviewer
  escaping its read-only sandbox through an approved escalation. With `never`,
  the same probe was refused.
- The Codex CLI is still maintained (0.157.1 released on 2026-09-26); the Codex
  desktop app merged into the ChatGPT desktop app and keeps its own binary under
  `%LOCALAPPDATA%\OpenAI\Codex\bin\<hash>\`. The `codex` on this machine's PATH
  is a stale standalone 0.135.0, which cannot run the configured default model
  `gpt-5.6-sol`. Update the standalone CLI, or name a supported model such as
  `codex:gpt-5.5` until then.
- On Windows, Codex's elevated sandbox creates files as a sandbox user. Under
  the user profile, such as the temporary folder, the real user then cannot
  read them; project folders that inherit `Authenticated Users` access, like
  `D:\code`, are unaffected.
- Codex records each new working directory as trusted in
  `~/.codex/config.toml`; project roots are normally trusted already.

## Snapshots

The CLI snapshots the work tree before and after every worker call and the
finalization batch, without touching the user's index or files:

```text
copy the user's index to <run>/snap.index           # first snapshot only
GIT_INDEX_FILE=<run>/snap.index git add -A
GIT_INDEX_FILE=<run>/snap.index git write-tree      # prints the tree id
```

- Copying the user's index keeps its file stat cache, so `add -A` rehashes only
  changed files; the private index then persists for the rest of the run.
- `git diff <before> <after>` is the call's full change, including new files.
- Any change across a Reviewer call fails the run.
- Ignored files, including `.cross-agent/`, are invisible to snapshots. The
  written objects are unreferenced, and normal Git garbage collection removes
  them.
- A diff over 200 KB fails the run.

## Delivery Stage

- After each Producer revision and after finalization, the CLI runs the
  project's `delivery_checks` and records exit codes and log excerpts. A
  read-only Reviewer cannot build or test, and it should judge real results
  rather than the Producer's report.
- Two review layers stay separate. The delivery Producer checks its own
  subagents' diffs and real test output; that is integration. The cross-agent
  Reviewer judges the result against the Plan and the Skill; that is
  independent review.
- The Producer's own subagents follow the current feature-delivery Delegation
  rules. The Orchestrator does not manage them.

## Deferred

Tiered `feature-delivery` delegation and platform `delivery-worker` agent
definitions wait until real runs show that nested delegation pays for its
briefing and integration cost. When revisited:

- the current Delegation section in `40.feature-delivery/SKILL.md` blocks the
  tiered flow at line 71 (no subagent for context isolation), line 74 (value
  counts time, not model cost), and line 79 (only independent parallel steps);
- Skills should name tiers, and platform agent definitions should map a tier
  to a model and effort, because Skills deploy to several platforms and model
  names change within months; and
- the Skill deployment script does not deploy agent definitions yet.

Community evidence for the tiered split: Anthropic's research system, with an
Opus lead and Sonnet subagents, beat a single Opus agent by 90.2% at about 15
times the tokens of a chat, and Anthropic notes that most coding tasks have
fewer truly parallel parts than research. Claude Code's `opusplan` alias plans
with Opus and executes with Sonnet. Claude Code and Codex both let an agent
definition pin a subagent's model and effort.

## Skill Collection Impact

v1 makes only these collection changes:

1. Add one `cross-agent` Skill. It requires the user to name the stage and
   artifact, adjudicates reviews, operates the CLI, performs finalization, and
   stops without executing an adjacent lifecycle stage.
2. Add it to `skills/coding/README.md`, and state that
   `docs/review-backlog.md` is a non-authoritative, explicitly routed exception
   to the rule against checklist and approval documents.
3. Teach `coding-agent-instructions` to route an existing review backlog with
   the explicit-read-only boundary. It still neither creates the backlog nor
   stores task state in `AGENTS.md`.
4. Add the Skill to `deploy-skills.json`. The CLI lives in the Skill's
   `scripts/` folder, so Skill deployment installs it too.

`feature-map`, `feature-plan`, and `feature-delivery` stay unchanged. The worker
prompt supplies the orchestration boundary, and each lifecycle Skill remains
independently invocable.

## Design Review Record

An external review recommended a "current session is the Producer" design
(mode A) over a CLI with headless workers (mode B) or an LLM Orchestrator
(mode C).

Accepted:

- The evaluator-optimizer loop (Producer, Reviewer, bounded reviews) fits fixed
  reviews better than a dynamic manager.
- One writer at a time: the Producer, or the Orchestrator during finalization.
- Every later review receives earlier findings, adjudications, and the diff
  explicitly.
- The CLI, not an agent, enforces the sequence and the review budget.

Chosen differently:

- Mode A keeps chat context in the Producer, but a long Feature Map to Delivery
  chain would overflow one session, and it cannot put Codex under a Claude
  session or the reverse. This design keeps chat context in the Orchestrator,
  which adjudicates and finalizes but does not produce. The CLI still owns the
  sequence, so the Orchestrator is not a ceremonial manager.

Rejected:

- Routing lines inside each lifecycle Skill. The collection `AGENTS.md` (line
  69) forbids one Skill silently invoking another. The user invokes
  `cross-agent` explicitly.
- Review ledgers, transcripts, and hashes. Run state is one ignored file
  deleted at close; only adjudicated leftovers reach the human backlog.
- Per-stage review limits that are all the same. One global value suffices.

## Validation

Automated: `python -m unittest discover -s skills/coding/cross-agent/scripts/tests`,
run from the skill-collection root, passed all 22 tests on 2026-09-26. With the
fake provider it proves:

1. with `max_reviews = 3`, at most four Producer steps in `--first produce` and
   three in `--first review`, and an early stop after a clean review;
2. only an accepted defect reaches the Producer, a polish finding reaches the
   backlog, a `minor` finding cannot be accepted, every pending finding needs a
   decision, and `backlog_rejected = false` keeps rejections out;
3. a failed resume is replaced by a fresh worker seeded from `state.json`,
   keeping finding IDs and the budget, and a large context rotates the worker;
4. a Reviewer write fails the run and keeps its state;
5. a Producer question waits for `answer` and resumes the same session;
6. finalization records an unfixed finding for the user, and `close` writes the
   backlog before deleting the state;
7. `--dry-run` saves nothing, one artifact has one open run, `.cross-agent/`
   stays out of Git, and closing an unfinished run needs `--abandon`.

Manual smoke tests with real providers are recorded under Provider Adapters. An
end-to-end run in a throwaway repository, with Claude Haiku producing and Codex
`gpt-5.5` reviewing, ended `independently-passed`, and `close` deleted its state
and both session files.

Still to run on real artifacts:

1. `--first review` on
   `docs/features/10.foundation/R01-F03-react-map-viewer.md` with Claude
   producing and Codex reviewing, then with the roles swapped.
2. `--first produce` with one small, concrete request on a Plan.
3. Delivery on one small planned Feature.

## Resolved Decisions

- Rejected findings reach the backlog by default; `backlog_rejected` turns that
  off.
- Backlog items keep a status field that the user maintains.
- `rotate_at_tokens` defaults to 350000 and stays configurable.
- The CLI is written in Python with only the standard library.
- One provider may fill both roles, although cross-provider review is the
  normal use.
- The user chats in their own language; prompts, worker output, decisions, and
  the backlog use English.

## Sources

- [Claude Code: Subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code: Model configuration](https://code.claude.com/docs/en/model-config)
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Codex: Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [openai/codex issue #26948](https://github.com/openai/codex/issues/26948)
