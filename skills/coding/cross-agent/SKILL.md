---
name: cross-agent
description: "Act as the user's PM-style Orchestrator for a bounded task: design, roadmap, refactor planning and execution, or selected Features. Invoke explicitly as cross-agent or Orch; initiate creates repo-local configuration with model/effort defaults and checks Codex CLI freshness without starting workers. Coordinate Producer and read-only Reviewer stages, report live progress, adjudicate findings, and continue through user-authorized stages using Claude Code or Codex through the bundled CLI. Do not invent product scope, bypass a required human gate, or use for an ordinary one-pass review."
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

## Mode Selection

Resolve the mode before the run procedure. An explicit `initiate`, `init`, or
request to initialize Cross-agent configuration selects initialization below.
`initiate` is the conversational mode name; the executable CLI command is `init`.
Otherwise follow Inputs and the run procedure. A missing configuration alone
does not authorize initialization. No configuration file is required to use
the built-in defaults, but project commands are never inferred by the CLI.

Initialization alone stops after its report. If the user explicitly requests
initialization followed by a task, continue only through the authorized stages
after reporting missing prerequisites that would prevent them.

## Initialization

The Orchestrator identifies project settings; `cross-agent init` validates and
writes them. Do not delegate initialization to workers, manually copy the
template, or edit the configuration as a substitute for this command.

1. Work from the project root governed by the applicable `AGENTS.md`, which
   may be below the Git root. Check Python 3.11+, the existing Git work tree,
   and `cross-agent status`. Report missing prerequisites; do not initialize
   Git, install tools, or create lifecycle documents as part of this mode.
2. Read the applicable project instructions and the build/test definitions
   they reference, such as package scripts, project files, or CI commands.
   Prefer explicit documented commands backed by repository evidence. Ask
   only when the choice is ambiguous or changes permissions. Do not invent
   tests from the detected language alone.
3. Select the smallest `allowed_commands` needed for Producer work and exact
   `delivery_checks` suitable for the intended stage. Both `general` and
   `feature-delivery` run these checks, including document-only `general`
   work. Default `extra_dirs` to `[]`; add writable directories only when
   covered by the user's task. If no reliable checks exist, use `[]` and
   explicitly report that verification is unconfigured.
4. Write a JSON object to a temporary file outside the work tree, then run:

   ```text
   cross-agent init --input <absolute-temporary-json-path>
                    [--producer <provider[:model[:effort]]>]
                    [--reviewer <provider[:model[:effort]]>]
   ```

   ```json
   {
     "allowed_commands": ["python -m unittest"],
     "delivery_checks": ["python -m unittest discover -s tests -v"],
     "extra_dirs": []
   }
   ```

   These commands are examples; use the project's real commands. Omitted
   fields become empty lists. The CLI creates `.cross-agent/config.toml` in
   the current project root, using `[projects."."]` for portable project
   commands and `[defaults]` for its Producer/Reviewer model and effort.
   Pass only roles the user specified; `codex::high` sets effort while keeping
   the provider's default model, and `codex:<requested-model>:high` sets both.
   Omitted roles use the built-in defaults in a new file. The selected CLI and
   model determine supported effort values; do not invent or substitute them.
   Existing configuration, comments, and role defaults remain intact. A
   missing project section is appended; an existing matching section is
   preserved in full, even if fields are omitted. Report `proposed_differences`
   and `proposed_role_differences` rather than claiming they were installed.
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
   `providers_on_path` checks executable discovery, not login or model access.
   Inspect sibling stage Skills only for intended stages. Initialization does
   not execute project checks, start workers, or create a run. Remove the
   temporary input and stop unless a following task was authorized.

`start --producer` / `--reviewer` override this repo's saved defaults for one
run, including model and effort. They do not change the current Orch session.
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
- Architecture plus roadmap uses `feature-map` when its lifecycle inputs and
  ownership apply; otherwise use `general` with explicit design deliverables.
- Selected Features are processed in dependency order, one run per Feature
  and stage. Missing prerequisites are reported, not silently added to scope.
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
- **Artifact**: the file the run centers on. The Producer may also change what
  its stage Skill owns, such as consistency fixes in related documents.
- **Start mode**: `review` for an existing artifact, or `produce` with a
  concrete request. A Producer without a concrete request reruns its whole
  Skill and rewrites without purpose. For `general`, always pass a request:
  with no lifecycle Skill, it is the only statement of the intended outcome.
- **Roles**, optional: translate the user's words into
  `<provider>[:<model>[:<effort>]]` specs. "Claude Opus produces and Codex
  reviews" becomes `--producer claude:opus --reviewer codex`. Pass only what
  the user named; never invent a model name. Omitted specs use the configured
  defaults.

One CLI run handles one stage, while this conversation owns the agenda. After
closing a completed run, continue to the next already-authorized stage without
asking again. Start fresh Producer and Reviewer sessions at each stage or
independent work item; within a stage, use the CLI's resume/rotation mechanism.
Pass the reviewed artifact and a short handoff of scope, decisions, and checks,
not the prior transcript. An unresolved decision, failed check, or unaccepted
upstream result stops dependent stages. `completed-by-orchestrator` is not an
independent review pass: if the user's gate requires that pass, stop there.

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

## Run Loop

```text
cross-agent start --stage <stage> --artifact <path> --first <produce|review>
                  [--request "<text>"] [--producer <spec>] [--reviewer <spec>] [--dry-run]
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
| `failed` or `blocked` | Report the reason and the state path, then stop. |

Relay an answer only when the user gave it explicitly, now or earlier in this
chat, and quote it. Never supply your own answer: the question exists because
the Producer's Skill requires a user decision.

Talk to the user in the user's language. Workers and the backlog use English,
so write decisions, rationales, and relayed answers in English, and translate
the Producer's questions when you relay them.

When the user explicitly authorizes recovery after a Reviewer execution failure,
fix the external cause first, then use `cross-agent retry-review --run <id>`
and `next --stream`. This retains the run, Producer session, findings, and review
budget, while starting a fresh Reviewer. It refuses validation failures such as
Reviewer writes, and does not bypass the review limit. Do not edit run state or
launch workers manually to recover. When the user explicitly resolves a
Producer-reported blocker and asks to continue, pass that decision with
`cross-agent answer --run <id> --text "<user decision>"`, then `next --stream`.
This preserves both worker sessions, findings, snapshots, and the review budget;
it cannot resume a failed validation guard. Other failed or blocked runs stop.

## Live Reporting

Report the agenda before starting. Consume `next --stream` incrementally with
short tool yields so this conversation remains responsive. Report worker
start, handoff, review findings, revision, and stage completion promptly;
otherwise give one concise update about every 30-60 seconds. Group repetitive
tool events. A heartbeat means the process is still waiting/running, not that
useful work or a test has succeeded.

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
backlog items to `docs/review-backlog.md`, deletes the run state, and cleans up
worker sessions. A current blocker never reaches the backlog silently: report
every unfixed accepted finding to the user as open before closing.

A `failed` or `blocked` run stays open, and blocks new runs on its artifact,
until the user decides. Close it only when the user says to abandon it; a run
stopped in any other unfinished phase also needs `--abandon`.

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
- Do not commit.

## Completion

Report the final status and what it means: `independently-passed` means an
independent review left nothing accepted, while `completed-by-orchestrator`
means this session accepted the final state during finalization. Also report
reviews and Producer revisions used, findings by disposition, finalization
edits, checks and their results, backlog items written, open user decisions,
defects you noticed yourself, and a failed run's state path. Update the chat
agenda and continue an authorized next stage; stop at the requested endpoint.
"Finish development" means meet its checks, while CLI `close` only cleans up
run state and worker sessions. Never substitute cleanup for delivery.
