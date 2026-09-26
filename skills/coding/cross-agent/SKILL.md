---
name: cross-agent
description: Orchestrate one bounded cross-agent run on one named artifact. The `cross-agent` CLI starts a headless Producer that follows the stage's lifecycle Skill and a read-only Reviewer, with Claude Code or Codex in either role, while this session adjudicates every finding, relays questions, and finalizes. Invoke explicitly, by name, with a stage (feature-map, feature-plan, feature-delivery, or general) and an artifact. Do not use to run an adjacent lifecycle stage, to review without the CLI, or for an ordinary one-pass review.
disable-model-invocation: true
---

# Cross-Agent

This session is the Orchestrator of one bounded Producer and Reviewer run. The
`cross-agent` CLI owns every mechanism: starting and replacing workers,
permissions, schemas, the review budget, snapshots, run state, and cleanup.
This Skill owns judgment: adjudicating findings, talking to the user, and
finalizing. Keep that split. A mechanism done by hand, such as launching
`claude` or `codex` yourself or editing run state, silently loses the budget,
the read-only guard, and recovery.

## Inputs

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

Ask only when the stage, the artifact, or a `produce` request is missing. One
invocation runs one stage. When the user also wants a later stage, finish and
report this run, then let the user invoke the next one; the passing result of
this run never authorizes it.

## Preconditions

1. Work from the project root: the directory whose `AGENTS.md` governs the
   artifact, which may sit below the Git repository root. Run
   `cross-agent status`. If the command is missing, report that the CLI is not
   installed and stop.
2. If `status` lists an open run for the same stage and artifact, continue it
   with `next`. If it lists an open run on this artifact for a different stage
   or request, report it and ask whether to continue or close it. The CLI
   refuses a second open run on one artifact.
3. A dirty work tree is fine; snapshots isolate the run's own changes. Tell the
   user that nobody else should edit the work tree while the run is open,
   because snapshots would count those edits as the run's.

## Run Loop

```text
cross-agent start --stage <stage> --artifact <path> --first <produce|review>
                  [--request "<text>"] [--producer <spec>] [--reviewer <spec>] [--dry-run]
cross-agent next  --run <id>
```

`start` prints the run ID. With `--dry-run` it prints the prompts and commands
without creating a run; use it when the user wants a preview. Then call `next`,
and call it again after every `decide` or `answer`, until the run is done. Each
`next` prints one JSON event; while a run waits, it prints the same pending
event again. Act on the event's phase:

| Phase | Action |
|---|---|
| `awaiting-decision` | Adjudicate every open finding, then run `cross-agent decide --run <id> --input <file>`. |
| `awaiting-answer` | Relay the Producer's questions, then pass the user's reply with `cross-agent answer --run <id> --text "<answer>"`. |
| `finalizing` | Follow Finalization. |
| `done` | Follow Close. |
| `failed` or `blocked` | Report the reason and the state path, then stop. |

Relay an answer only when the user gave it explicitly, now or earlier in this
chat, and quote it. Never supply your own answer: the question exists because
the Producer's Skill requires a user decision.

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
until the user decides. Close it only when the user says to abandon it.

## Boundaries

- Run only the named stage. The Producer may change what that stage's Skill
  owns; never start another stage.
- Do not run the lifecycle Skill in this session; the Producer does.
- Read and change run state only through `cross-agent` commands, never by
  opening `.cross-agent/`.
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
defects you noticed yourself, and a failed run's state path. Then stop.
