---
name: cross-agent
description: "Act as the user's PM-style Orchestrator for a bounded task: design, roadmap, refactor planning and execution, or selected Features. Invoke explicitly as cross-agent or Orch; initiate creates repo-local configuration with model/effort defaults and checks Codex CLI freshness without starting workers. Coordinate Producer and read-only Reviewer stages, report live progress, retain worker time/token CSV history, adjudicate findings, and continue through user-authorized stages using Claude Code or Codex through the bundled CLI. Do not invent product scope, bypass a required human gate, or use for an ordinary one-pass review."
disable-model-invocation: true
---

# Cross-Agent

This session is the PM-style Orchestrator of the user's task. Understand the
outcome, choose the smallest sequence of stages, delegate the detailed design,
implementation, and review, and keep the user informed. Each stage is one
bounded Producer and Reviewer run; a task may authorize several runs. The
`cross-agent` CLI owns every mechanism: starting and replacing workers,
permissions, schemas, the review budget, snapshots, run state, and cleanup.
This Skill owns judgment: adjudicating findings, talking to the user, and
finalizing. Keep that split. A mechanism done by hand, such as launching
`claude` or `codex` yourself or editing run state, silently loses the budget,
the read-only guard, and recovery.

The CLI ships inside this Skill. Run it from the project root as
`python <skill-dir>/scripts/cross_agent.py <command>`, where `<skill-dir>` is
this Skill's base directory; below, `cross-agent <command>` is short for that.
Commands print one JSON object; `next --stream` emits progress JSONL followed
by one `event: result` object. Settings come from
`<project-root>/.cross-agent/config.toml` when it exists. `CROSS_AGENT_CONFIG`
explicitly overrides this path. Never search parent directories or implicitly
load the old `~/.cross-agent/config.toml`; different project roots are independent.
[the example](assets/config.example.toml) lists every key.

For a multi-project workspace, keep the settings in one shared file. Each
project's local config may contain only a single `config_file = "<path>"`,
resolved relative to that local config's directory. A pointer must reference
an existing settings file; pointers cannot be chained or mixed with settings.
Use explicit project-root keys in the shared file so commands and permissions
remain separate. Run state stays in the calling project's `.cross-agent/runs/`.

Required `[cli]` entries for selected providers specify absolute executable paths;
missing entries and unavailable executables fail without
falling back to another version. `status` and `init` report `cli_executables`;
version detection uses the selected Codex. CLI paths are read at each worker
call, including existing runs; saved roles, commands, and budgets are unchanged.

## Mode Selection

Resolve the mode before the run procedure. An explicit `initiate`, `init`, or
request to initialize Cross-agent configuration selects initialization below.
`initiate` is the conversational mode name; the executable CLI command is `init`.
Otherwise follow Inputs and the run procedure. A missing configuration alone
does not authorize initialization. Runtime calls require a complete configuration
file; missing settings are errors, never Python or provider CLI defaults.

Initialization alone stops after its report. If the user explicitly requests
initialization followed by a task, continue only through the authorized stages
after reporting missing prerequisites that would prevent them.

## Initialization

The Orchestrator identifies project settings; `cross-agent init` validates and
writes them. Do not delegate initialization to workers, manually copy the
template, or edit the configuration as a substitute for this command.

1. Work from the project root governed by the applicable `AGENTS.md`, which
   may be below the Git root. Check Python 3.11+, the existing Git work tree,
   and inspect existing settings with `cross-agent status` when a config exists.
   A missing config is expected only during explicitly requested initialization.
   Report missing prerequisites; do not initialize
   Git, install tools, or create lifecycle documents as part of this mode.
2. Read the applicable project instructions and the build/test definitions
   they reference, such as package scripts, project files, or CI commands.
   Prefer explicit documented commands backed by repository evidence. Ask
   only when the choice is ambiguous or changes permissions. Do not invent
   tests from the detected language alone.
3. Read [the initialization template](assets/config.example.toml) for configured
   runtime settings and complete role specs. Resolve the installed absolute CLI
   paths for its selected providers and pass them in the input's `cli` object;
   never persist the template's placeholder paths as if they were verified.
   Select the smallest `allowed_commands` needed for Producer work and exact
   `delivery_checks` suitable for the intended stage. Both `general` and
   `feature-delivery` run these checks, including document-only `general`
   work. Default `extra_dirs` to `[]`; add writable directories only when
   covered by the user's task. If no reliable checks exist, use `[]` and
   explicitly report that verification is unconfigured.
4. Write a JSON object to a temporary file outside the work tree, then run:

   ```text
   cross-agent init --input <absolute-temporary-json-path>
                    [--producer <provider:model:effort>]
                    [--reviewer <provider:model:effort>]
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

   These paths and commands are examples; use the project's actual values.
   Creating a config loads all runtime values from `assets/config.example.toml`,
   overlays explicit role/CLI inputs and project commands, then validates the
   complete result before writing. Omitted initialization inputs use template
   values, never Python defaults. `[projects."."]` keeps local commands portable.
   Roles must specify `<provider>:<model>:<effort>` in full, including run
   overrides; `codex`, `claude`, and `codex::high` are errors. The selected CLI and
   model determine supported effort values; do not invent or substitute them.
   Existing configuration, comments, and role defaults remain intact. A
   missing project section is appended; an existing matching section is
   preserved in full when valid; incomplete existing configurations fail without
   being backfilled from the template. Report `proposed_differences`,
   `proposed_role_differences`, and `proposed_cli_differences` rather than claiming
   they were installed.
   Changing existing settings requires an explicit configuration-change task.
   `CROSS_AGENT_CONFIG` remains an explicit override, including for a legacy
   shared file; it is never automatically selected or migrated.
5. Run `status` again and report the config path, action (`created`,
   `project-added`, or `unchanged`), effective project commands, role defaults,
   and remaining prerequisites. `init` runs `codex --version` and compares it
   with the npm registry's `@openai/codex` `latest` release, with bounded
   timeouts. Report `codex_version.installed`, `latest`, `status`, and `reason`:
   `current` means the versions match; `update-available` means the installed
   stable version is older; `ahead` means it is newer; `not-installed`,
   `unknown`, and `skipped` must never be reported as current. Network failures
   and prerelease builds yield `unknown`. Do not automatically upgrade the CLI.
   Use `--skip-version-check` only when the user requests skipping it.
   `providers_on_path` checks discovery, not the selected installation, login,
   or model access; `cli_executables` reports the explicitly configured paths.
   Inspect sibling stage Skills only for intended stages. Initialization does
   not execute project checks, start workers, or create a run. Remove the
   temporary input and stop unless a following task was authorized.

An optional `[stages.<stage>]` table may set `producer` and `reviewer` in the
same complete `<provider>:<model>:<effort>` format, so design, delivery, and
mechanical work can use different models or effort. Each role resolves as the
`start --producer` / `--reviewer` run override, then the stage role, then
`[defaults]`. Overrides do not change the current Orch session. `status` shows
`effective_roles` per stage with their source; `start`, `--dry-run`, and
`status --run` show the run's `roles` and `role_sources`. An unknown stage or
key, an incomplete spec, or a provider without its `[cli]` path fails before any
run or worker starts. A run keeps the roles, Skill path, commands, and budgets it
started with; later configuration edits never change them. Runs saved before
stage roles report `role_sources` as `null` and keep their saved roles.
After initialization, runtime calls read only the selected project/shared
configuration, not the template. All five runtime control settings, both complete
default roles, selected CLI paths, and all three fields in the matching project
section are required. Empty project lists must be written explicitly as `[]`.
Stage roles and Skill-path overrides are optional; sibling Skill discovery is a
routing convention for the three lifecycle stages. `general` loads a Skill only
when `[stages.general] skill` names one; configure that only when every `general`
run using this configuration belongs to that Skill.
Keep temporary inputs outside the work tree. Initialization uses Git's local
exclude to keep `.cross-agent/` configuration and run state out of snapshots
and commits, without editing the project's tracked `.gitignore`. Normal
sandbox permissions apply. If the path is unwritable, report the restriction;
do not silently switch to a user-level file. Configuration syntax validation
and version freshness do not prove model access, supported effort, or test success.

## Inputs

First resolve the requested outcome, sources, output artifacts, and stopping
point. Keep a short stage agenda in the conversation: stage, artifact, required
inputs, acceptance checks, and next gate. Do not create a separate project
management document. Infer routine paths and sequencing from repository
conventions; ask only when ambiguity changes scope or the user's gate.

- A refactor may be `general` plan -> review -> `general` execution -> review.
- Architecture uses `general` with a request that names the
  `architecture-design` Skill path and its deliverable; the CLI injects that
  Skill only when `[stages.general] skill` explicitly configures it. A roadmap
  or Feature Map then uses `feature-map` when its lifecycle inputs and
  ownership apply.
- Selected Features are processed in dependency order, one run per Feature
  and stage. Missing prerequisites are reported, not silently added to scope.
- A bounded validation question uses `feature-plan` to write
  `docs/plans/<topic>.md`, then `feature-delivery` to execute it, without a
  Feature ID. Report its execution status and conclusion separately.
- "Plan, then execute once review passes" authorizes both stages. "Make a
  plan" stops after planning. "Wait for my approval" requires the user's reply.

Keep detailed problem-solving with the workers. Give each stage a concrete
request naming inputs, owned outputs, checks, and exclusions. Use the matching
lifecycle Skill where applicable; `general` must not bypass its requirements.
For a standalone task with no lifecycle owner, `general` is sufficient and
does not require synthetic Feature IDs, a Product Brief, or a Feature Map.

Resolve these CLI inputs for each stage:

- **Stage**: `feature-map`, `feature-plan`, `feature-delivery`, or `general`.
  Infer it only when the request leaves no doubt. A Feature Plan path alone can
  mean `feature-plan` or `feature-delivery`, so ask.
- **Item**, optional: a stable Feature ID, function name, or topic for history.
  Pass the same `--item` at each stage of that work; it defaults to the artifact
  path. An item is only a reporting label, not new product scope.
- **Artifact**: the file the run centers on. The Producer may also change what
  its stage Skill owns, such as consistency fixes in related documents.
- **Start mode**: `review` for an existing artifact, or `produce` with a
  concrete request. A Producer without a concrete request reruns its whole
  Skill and rewrites without purpose. For `general`, always pass a request:
  with no lifecycle Skill, it is the only statement of the intended outcome.
- **Roles**, optional: translate the user's words into
  `<provider>:<model>:<effort>` specs. Resolve unspecified model/effort from the
  existing complete role configuration before applying a user-requested override;
  never invent a model name or rely on CLI defaults. Omitted overrides use the
  configured stage role, else the default. Missing configuration stops the run.

One CLI run handles one stage, while this conversation owns the agenda. After
closing a completed run, continue to the next already-authorized stage without
asking again. Start fresh Producer and Reviewer sessions at each stage or
independent work item; within a stage, use the CLI's resume/rotation mechanism.
Pass the reviewed artifact and a short handoff of scope, decisions, and checks,
not the prior transcript. An unresolved decision, failed check, or unaccepted
upstream result stops dependent stages. `completed-by-orchestrator` is not an
independent review pass: if the user's gate requires that pass, stop there.

A Producer may report that one Feature holds several independent outcomes, that
an upstream source is wrong, or the user may authorize a change mid-delivery.
Within the authorized objective, coordinate the owners upstream first: the
changed requirement or design owner, then every affected intermediate contract
such as the Architecture Design or Testing Strategy (`general` naming its
Skill), then affected Storyboards and `feature-map`, then `feature-plan`, then
Delivery in a new run or through `resume-delivery`. Downstream acceptance waits
until each affected owner is reconciled. An open Delivery run holds its
artifact: park a failed one as described below; closing a blocked one still
needs the user's consent. Ask the user only for an unresolved choice that
materially affects product behavior, accepted constraints, permissions, cost
commitments, or the user's explicit gate. Never invent product scope or let a
worker rewrite an authoritative input to make a check pass.

Each `feature-delivery` request names the run's independent review as a
selected gate, so the Producer records its results, leaves the Plan's gate row
`not run`, and reports readiness. For a Feature Plan, the Plan and Map row stay
`in_progress`. For a standalone validation Plan, the Producer records execution
status and conclusion as usual; no Map row, Feature status, or `verified`
exists, and the conclusion is not independently reviewed until the gate passes.

Before `close`, record content hashes of the acceptance-relevant files: the
Plan, the Map when a Feature has one, and every file in the run's reviewed
diff. `close` may append nonblocking items to `docs/review-backlog.md`; that CLI
bookkeeping is not acceptance-relevant, so do not hash or read it. After the
run ends `independently-passed` and is closed, and those hashes still match,
make one status-only edit: the gate row's result and the Plan's current
position, plus for a Feature `verified` in the Plan and Map row when every
other planned result already passed. A mismatch means the reviewed revision
changed; report it instead of finalizing. This edit is not a repair; anything
more needs a new run. After `completed-by-orchestrator`, leave the gate `not
run`, keep a Feature `in_progress`, and report the missing independent pass.

## Preconditions

1. Work from the project root: the directory whose `AGENTS.md` governs the
   artifact, which may sit below the Git repository root. Run
   `cross-agent status`; it needs Python 3.11 or later. If it cannot run,
   report why and stop. Its output lists open runs and the effective settings,
   such as `max_reviews` and whether rejected findings reach the backlog
   (`backlog_rejected`).
2. If `status` lists an open run for the same stage and artifact, continue it
   with `next`. If it lists an open run on this artifact for a different stage
   or request, report it and ask whether to continue or close it. The CLI
   refuses a second open run on one artifact.
3. A dirty work tree is fine; snapshots isolate the run's own changes. Tell the
   user that nobody else should edit the work tree while the run is open,
   because snapshots would count those edits as the run's.
4. Check the project's configured commands against the stage's verification
   needs. `delivery_checks` run after Producer changes for `feature-delivery`
   and `general`; use stage-appropriate configuration for document-only work.
   Missing commands must be reported, not silently counted as successful tests.
   An optional `test_reports` table in the project section maps a configured
   check command to the JUnit XML report it writes; only an explicit
   configuration-change task adds it.

## Run Loop

```text
cross-agent start --stage <stage> --artifact <path> --first <produce|review>
                  [--item "<Feature ID or topic>"] [--request "<text>"]
                  [--producer <spec>] [--reviewer <spec>] [--dry-run]
cross-agent next  --run <id> --stream
```

`start` prints the run ID. With `--dry-run` it prints the prompts and commands
without creating a run; use it when the user wants a preview. Then call `next`,
and call it again after every `decide` or `answer`, until the run is done. Each
`next --stream` prints sanitized observations while the worker runs, then its
final result; do not launch a second `next` while it is running. `status --run`
can inspect the latest saved observations. Act on the final result's phase:

| Phase | Action |
|---|---|
| `produce` or `review` | Call `next` again; a worker step is due. |
| `awaiting-decision` | Adjudicate every open finding, then run `cross-agent decide --run <id> --input <file>`. |
| `awaiting-answer` | Relay the Producer's questions, then pass the user's reply with `cross-agent answer --run <id> --text "<answer>"`. |
| `finalizing` | Follow Finalization. |
| `done` | Follow Close. |
| `failed` | If `automatic_recovery_available`, call `next` once; otherwise report the reason and state path and stop. |
| `blocked` | Report the blocker and stop until the user resolves it. |

Before each review, the CLI builds a deterministic test-change summary for the
same snapshot range as the review diff and adds it to the Reviewer prompt as
fixed input; a retried review rebuilds the identical text. It lists added,
modified, and deleted test, fixture/mock, and runner/configuration paths with
raw hunks; supported skip/disable/only and filter markers with `path:line`;
assertion-like line counts in test paths; and each check's exit code. Counts
come only from a configured JUnit XML report rewritten by that check command,
scoped to that command, whose suites declare totals matching their test cases
with one plain outcome each and only standard JUnit elements, placements and status values; stale, absent, unreadable, inconsistent,
unsupported, or duplicate/rerun reports and console output stay unknown. Detection follows naming conventions and fixed
patterns, so an empty section never means tests are unchanged, discovered, or
adequate. `next --stream` emits a `test-changes` event and events carry the
latest `test_changes` record with its `sha256`. Use these as review signals,
not as a verdict; the Producer's incremental TDD tests are not frozen.

Relay an answer only when the user gave it explicitly, now or earlier in this
chat, and quote it. Never supply your own answer: the question exists because
the Producer's Skill requires a user decision.

Talk to the user in the user's language. Workers and the backlog use English,
so write decisions, rationales, and relayed answers in English, and translate
the Producer's questions when you relay them.

Producer timeout and explicit transient connection/rate-limit errors receive at
most one automatic recovery per run. `next` resumes a compatible failed run or
the active call retries once; both share that counter. Prefer the previous
Producer session. Replace it only for the saved context threshold, an execution
checkpoint, or a recognized missing/unloadable session; retain old sessions for
history and later cleanup. A replacement receives the run summary and latest
checkpoint and must inspect existing edits. Each worker call still has the
configured hard timeout (default 30 minutes); output never extends it. Do not
keep calling `next` to obtain unlimited retries.

After the external cause of a failed Producer execution is fixed and recovery
is authorized, use `cross-agent retry-producer --run <id>`, then `next --stream`.
This explicit retry does not append another automatic retry. It preserves the
baseline, sessions, edits, findings, answer, and review budget. Schema/output
validation and write guards are not execution failures and cannot be retried.
Configuration/discovery failures require fixing their cause before proceeding.

An execution Producer may return `checkpoint` after a planned segment. The CLI
saves its acceptance/handoff summary and snapshot, stays in `produce`, and the
next call starts a fresh Producer session. Report the checkpoint and continue
the already-authorized Plan. There are at most eight checkpoints per run; they
do not consume or reset a revision/review budget. The original baseline remains
the final review boundary. Only `done` runs whole-stage checks and hands off for
independent review. Never treat a checkpoint as verified completion. When
commits are authorized, commit the checkpoint as described in Section Commits
before calling `next`.

When the user explicitly authorizes recovery after a Reviewer execution failure,
fix the external cause first, then use `cross-agent retry-review --run <id>`
and `next --stream`. This retains the run, Producer session, findings, and review
budget, while starting a fresh Reviewer. It refuses validation failures such as
Reviewer writes, and does not bypass the review limit. Do not edit run state or
launch workers manually to recover. When the user explicitly resolves a
Producer-reported blocker and asks to continue, pass that decision with
`cross-agent answer --run <id> --text "<user decision>"`, then `next --stream`.
This preserves both worker sessions, findings, snapshots, and the review budget;
it cannot resume a failed validation guard. Other failed or blocked runs stop; never edit state or launch workers manually.

When the user redirects a failed Delivery to replanning, use `park --run <id>
--reason "<user-requested replan>"`. This releases its artifact lock without
closing the run, deleting sessions or resetting its baseline/review budget.
`status --run` still reads parked history; `next` cannot run it. Update/review
the same Plan in a separate `feature-plan` run. After that run independently
passes, use `resume-delivery --run <delivery-id> --plan-run <plan-id> --request
"<reviewed segment handoff>"`, then close the completed Plan run and call
Delivery `next --stream`. This starts a fresh Producer while retaining Delivery
history and its original review boundary/budget. It refuses exhausted budgets,
other active artifact owners, and schema/read-only/snapshot validation failures.
For a prior diff-size guard only, an explicit `--max-diff-kb <larger-capacity>`
may increase that saved input ceiling; it does not omit changes from review.
Never use parking to bypass a worker or review gate.

## Live Reporting

Report the agenda before starting. Consume `next --stream` incrementally with
short tool yields so this conversation remains responsive. Report worker
start, handoff, review findings, revision, and stage completion promptly;
otherwise give one concise update about every 30-60 seconds. Group repetitive
tool events. A heartbeat means the process is still waiting/running, not that
useful work or a test has succeeded.

Report `skill-loaded` as complete Skill content injected into the worker prompt,
including the path, hash, and method; it proves supplied content, not native
Skill-tool invocation or compliance. `skill-started` follows worker readiness:
Producer executes that stage, Reviewer judges it read-only. Report subagent
requests, starts, completion and active counts only when observed; otherwise
say unknown. Do not equate a launch request with a running agent.

Feature Plan owns execution sizing, segment acceptance/handoffs, and proposed
delegation. Keep Orch's analysis to scope, dependencies, gates, and adjudication;
drive the reviewed Plan rather than designing an alternative execution map.

Include stage/item, role/provider, configured model and effort, observed model
and effort when available, session generation, latest parent context tokens,
rotation threshold, and observed subagent requests/starts/active count. Explain
the current work using the request, tool activity, and Producer summary; do not
invent details, expose hidden reasoning, or paste tool arguments/transcripts.

`null` means unknown, never zero. Model aliases/configuration are not observed
runtime values. Usage is a latest measurement, not a live context meter or
cumulative spend; never infer a percentage without an observed context limit.
Child context must not overwrite parent context. Provider compaction events
and CLI fresh-session rotation are different; report only observed events.
Rotation is evaluated between worker calls, not during a running call.

### Retained History

The CLI automatically maintains `.cross-agent/history/<run-id>.csv`, one row
per worker call, including revisions, checkpoint segments, and failed/retried
calls. A session can have multiple rows. Calls record item, stage, artifact,
role/provider, round (`P0`, `R1`, `P1`, ...), segment, configured and observed
model/effort, session ID/generation/reason, UTC start/end, elapsed seconds,
worker response status, current/final run status, and observed token counts.
Elapsed time covers the worker invocation, not user waiting or project checks.
`call_status` is a worker result, not proof that the stage passed its guards.

Run `cross-agent history` to refresh `.cross-agent/history.csv` from all retained
runs, then review/filter it in Excel by item, role, round, or session. CSVs use
UTF-8 with BOM. Scripts own these files; never ask an agent to handwrite rows.
`status --run` and `close` report the per-run history path. `close` preserves
history while deleting run state and worker sessions. `.cross-agent/` remains
locally excluded from Git; history stays in this checkout unless copied out.

Token columns count the parent worker call only (`usage_scope=parent-call`);
they exclude this Orch session and do not guarantee coverage of subagents or
provider-internal work. Input tokens include cache reads/writes, which are also
listed separately; reasoning tokens are an output subset. Sum `total_tokens`
alone to avoid double counting. Codex session counters become per-call deltas
against a saved or observed baseline; missing/reset baselines stay unknown.
Claude uses final result usage for the current call; timeout fallback counts
unique parent message input/cache tokens and leaves output unknown. Never sum
Claude session-level `modelUsage`/cost totals across resumed calls.

`usage_status` is `reported`, `partial`, or `unknown`; blank counts mean unknown,
not zero. Partial totals are not complete spend or billing amounts. A killed
Orch process may leave a `running` row without an end time; do not invent it.
Existing runs start recording only their subsequent calls; no past timestamps
or usage are fabricated. This history is telemetry, not a new lifecycle document.

Producer delegation must follow the stage Skill, or for `general` be limited
to substantial independent work with disjoint ownership. Reviewers do not
delegate. Missing provider telemetry is explicitly unknown; it does not block
useful work. Report a new session and its reason at every stage transition.

## Adjudication

The Reviewer proposes findings; it does not decide that more work must happen.
You decide, because you hold the chat context the workers lack: the user's
intent, the agreed scope, and earlier corrections. Give every open finding
exactly one disposition:

- `accepted`: a current `blocker` or `major` defect within the requested scope.
  Only accepted findings reach the Producer, and each non-passing review allows
  one revision. Add a rationale when the Producer needs guidance, such as the
  fix the user chose.
- `note-only`: valid but nonessential, such as polish, an optional refactor, or
  a `minor` defect. Severity is the Reviewer's call, so a `minor` defect never
  earns a revision; it goes to the backlog instead.
- `rejected`: not a current defect. It falls outside the review boundary, lacks
  real evidence, is contradicted by an authoritative source or an explicit user
  decision, or is already resolved. A new idea that would change direction is
  not a current defect either.
- `needs-user-decision`: a current defect whose fix would change product
  behavior, UI behavior, technical direction, or an authoritative document, and
  that the user chose to leave open. It goes to the backlog.

When such a defect blocks the run, ask the user before calling `decide`, then
record the answer as `accepted` with guidance, `rejected`, or
`needs-user-decision`. If the user needs time, stop; the run waits at
`awaiting-decision`.

A valid finding names an unmet requested outcome, a conflict with an
authoritative input, a real validation failure, an internal contradiction, a
regression from the latest change, or a concrete security, permission,
data-loss, or irreversible-action risk. It cites a rule, a `path:line`, or a
failing command. Read the cited evidence and the artifact lines the finding
concerns, and little else; a small context keeps your judgment sharp across
runs.

Give every non-accepted finding a rationale a person can act on later and a
priority (`high`, `medium`, `low`, or `none`), because it may reach the review
backlog. Write the decisions to a JSON file outside the work tree, such as the
system temporary folder, so the file never appears in a snapshot:

```json
{
  "decisions": [
    { "finding_id": "R1-001", "disposition": "accepted", "rationale": "Move F08 into R02, as the user chose.", "priority": null },
    { "finding_id": "R1-002", "disposition": "note-only", "rationale": "Heading wording only; the outcome is already met.", "priority": "low" }
  ]
}
```

A Producer `not-fixed` outcome returns at the next adjudication with its
rationale. Accept it again only when that rationale is wrong; otherwise reject
it or ask the user. It never earns an extra revision.

Put defects you notice yourself in the completion report. You adjudicate the
review; you are not a second Reviewer.

## Finalization

After the last permitted revision, the CLI hands write ownership to this
session for one bounded batch. The `finalizing` event lists the final diff and
the remaining accepted findings.

1. Read that diff, the remaining findings, and what they cite.
2. Fix, in one batch, the accepted problems that are local and do not change
   scope. Do not start another worker loop or make unrelated improvements.
3. For each accepted finding you leave unfixed, because its fix is not local or
   would change product behavior, UI behavior, technical direction, or an
   authoritative boundary, record `needs-user-decision` with `decide`.
4. Call `next`. The CLI snapshots the batch, reruns the applicable checks once,
   and records the final status.

Outside finalization, edit no project file while a run is open. The Reviewer's
independence depends on the Producer being the only writer.

## Close

When the run is done, run `cross-agent close --run <id>`. It appends the run's
backlog items to `docs/review-backlog.md`, preserves the history CSV, deletes
the run state, and cleans up worker sessions. A current blocker never reaches
the backlog silently: report
every unfixed accepted finding to the user as open before closing.

A `failed` or `blocked` run stays open, and blocks new runs on its artifact,
until the user decides. Close it only when the user says to abandon it; a run
stopped in any other unfinished phase also needs `--abandon`.

## Section Commits

Commit only when the user's explicit request or a project rule authorizes
commits for the current task. Neither this Skill nor a stage Skill grants that
authority; without it, report each section's outcome and leave changes
uncommitted. With it, this session commits every finished bounded section
before starting dependent work; workers never commit, and the Reviewer stays
read-only. A section is one bounded design, planning, review or delivery run,
or a reviewed Plan's execution segment ending in a checkpoint, not every
heading or file.

1. Commit only while no worker runs: after a checkpoint event, or after a run
   stops as `done`, `failed`, `blocked` or parked. For a completed stage,
   commit after `close` and any status-only finalization edit.
2. Inspect `git status` and the section's diff. Stage only the exact
   authorized source and result paths, then commit them by pathspec
   (`git commit -m <message> -- <paths>`), so the user's other staged entries,
   unrelated or untracked files, private configuration and the backlog that
   `close` appends stay out. Never use `git add -A`. If a section file also
   holds unrelated edits, report it instead of committing.
3. Base the message on actual evidence: name the task or item, the section,
   and its real outcome, such as `checkpoint, not independently reviewed`,
   `independently-passed`, `completed-by-orchestrator`, `failed` or
   `incomplete`, with the checks that actually ran. A checkpoint carries the
   Producer's targeted segment checks; whole-stage `delivery_checks` run only
   after a Producer returns `done` or finalization, and the selected independent gate only
   when the stage's review finishes. Neither a
   commit nor Orchestrator completion makes a section verified or passed, and
   no extra review is required per segment beyond the selected gates.
4. Do not amend, push, reset, check out, rebase or create empty commits unless
   the user asks. Without a relevant diff, record the outcome in an existing
   artifact that already owns it, such as the status-only edit, or in the next
   section commit's message; never create a document to force a commit.
5. A failed or incomplete section may be kept in a local recovery commit with
   that truthful outcome. It stops dependent work, not the run's own
   recovery: when `automatic_recovery_available`, still call `next` once as
   the Run Loop directs. The commit neither spends nor restores a recovery,
   revision or review allowance. `retry-producer`, `retry-review`, `park` and
   `close --abandon` keep their existing authorization rules; never roll back.
6. Committing changes neither the work tree nor run state. An open run's
   original baseline, findings, checkpoints and spent budgets stay
   authoritative, so the final review still covers earlier committed segments.
7. Report each commit's revision (`git rev-parse --short HEAD`). A checkpoint
   is saved before its commit, and a continuation Producer receives only the
   original request and that checkpoint, so an execution stage's
   `start --request` must tell every continuation Producer to read the current
   revision with `git log -1 --format=%h` (Producers may always run read-only
   `git log`) before more work. A new run's `start --request` names the
   actual revision with its scope, decisions and checks. The CLI neither
   records commits in history or run state nor edits saved checkpoints.

## Boundaries

- Each worker runs only its assigned stage. The Orchestrator advances only
  through stages covered by the user's task, respecting dependencies and gates.
- Do not run the lifecycle Skill in this session; the Producer does.
- Read and change run state only through `cross-agent` commands, never by
  opening `.cross-agent/runs/`. `.cross-agent/config.toml` is configuration;
  explicit configuration-change tasks may inspect and edit it, but workers
  must not change it as part of a stage.
- Do not read or search `docs/review-backlog.md` unless the user asks for a
  backlog review or names an item ID.
- Do not start another run on the same artifact to obtain more reviews; the
  budget is the point.
- Commit only as described in Section Commits; workers never commit.

## Completion

Report the final status and what it means: `independently-passed` means an
independent review left nothing accepted, while `completed-by-orchestrator`
means this session accepted the final state during finalization. Also report
reviews and Producer revisions used, findings by disposition, finalization
edits, checks and their results, backlog items written, section commits made
or why none was made, open user decisions,
defects you noticed yourself, and a failed run's state path. Report the retained
history path and any unknown or partial token coverage. Update the chat agenda
and continue an authorized next stage; stop at the requested endpoint.
"Finish development" means meet its checks, while CLI `close` only cleans up
run state and worker sessions. Never substitute cleanup for delivery.
