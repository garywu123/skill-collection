# Reporting And History

## Live Telemetry

Report from stream events: stage and item, role and provider, configured and
observed model and effort, session generation and its reason, latest parent
context tokens against the rotation threshold, and observed subagent requests,
starts, and active count. Report a new session and its reason at every stage
transition.

- `skill-loaded` means the Skill's full content was injected into the worker
  prompt, not that the worker invoked or followed it.
- Usage is the latest parent-call measurement, not a live context meter or
  cumulative spend. Never infer a percentage without an observed context limit,
  and never let child context overwrite parent context.
- Report provider compaction and CLI session rotation only when observed;
  rotation happens between worker calls.

## Retained History

The CLI writes `.cross-agent/history/<run-id>.csv`, one row per worker call;
`status --run` and `close` report its path. `cross-agent history` refreshes
`.cross-agent/history.csv` from all retained runs for filtering by item, role,
round, or session. Never handwrite rows.

- Token columns cover the parent worker call only (`usage_scope=parent-call`),
  not this Orch session or all subagent work. Sum `total_tokens` alone; cache
  and reasoning columns are subsets.
- `usage_status` is `reported`, `partial`, or `unknown`. Blank counts mean
  unknown, and partial totals are not complete spend.
- Elapsed time covers the worker invocation only, and `call_status` is the
  worker result, not proof that the stage passed its guards.
- Do not invent an end time for a `running` row left by a killed process.

## Orchestrator Context Handoff

Manage this session's context at stage boundaries, such as after a Plan passes
and before Delivery, or after a Feature finishes and before the next, when old
transcripts, repeated review rounds, or superseded instructions crowd it.
Worker rotation never rotates this session. At a checkpoint, the Producer keeps
the Plan's completed and next segment, actual checks, and blockers current.

1. Prepare the handoff while no worker runs, after consuming its result and
   recording decisions.
2. Keep task and authorization scope, artifact locators, stage, item, and run
   ID, branch and revision, roles and configuration locator, current position,
   pending questions, unresolved findings, failures, required gates, remaining
   checks, evidence locators, and the next action. Link the Plan and CLI status
   instead of copying them. Keep private paths and credentials out of tracked
   artifacts and worker requests.
3. Use the host's compaction mechanism only when it is available; otherwise keep
   the handoff for automatic compaction or an authorized chat transition.
   Report compaction only when observed.
4. Afterwards, re-read the applicable instructions, run `cross-agent status`,
   inspect the revision and diff, and read the Plan's current position and the
   cited evidence. Continue the existing run with its saved budgets and gates.

Durable Feature position belongs in the Plan and Map. Do not edit project files
or create a memory file to prepare a handoff.
