# Expert Exploration

An expert is the Producer using the selected domain Skill for a discussion
before production. "Discuss a product or map" selects exploration; "generate it
from the confirmed inputs" selects production directly; "decide the
decomposition and write it" delegates routine in-scope decisions. Clarify only
a material ambiguity before starting.

```text
cross-agent start --stage <stage> --first explore --skill <logical-name-or-path>
                  --request "<goal, background, scope and current questions>"
                  --adjudication <orch|auto> [--artifact <intended-path>]
cross-agent expert --run <id>
cross-agent promote --run <id> --artifact <path>
                    --request "<explicit write authorization and relevant evidence>"
                    [--reconcile "<user direction for intervening changes>"]
                    [--skip-review --reason "<explicit user opt-out>"]
cross-agent next --run <id> --stream
```

## Discussion

- `expert` runs a foreground interactive Claude session with read-only tools.
  Launch it in a user-visible terminal with the host's terminal mechanism; the
  CLI opens no window, and host-chat messages do not reach that terminal. Give
  the user a concrete launch request.
- Direct interactive Codex is not supported; with a Codex Producer, use the
  managed question relay instead.
- If `expert` returns before the provider session starts, run it again for the
  same run.
- One actor drives the session at a time. Exiting returns control; it is not
  submission, write authorization, completion, or review approval.
- If an interrupted terminal leaves the run under interactive control, verify
  that its process has stopped, then run `cross-agent expert --run <id> --release`.
  Releasing authorizes nothing.

## Promotion

Promote only after the user explicitly asks to produce or submit, in the
recorded discussion or this chat. Put that authorization and the relevant
evidence in `--request`; a request received only by you is Orch-attested. Do
not invent transcript locators. If promotion holds changes made since
exploration began, reconcile them only with the user's explicit direction in
`--reconcile`. `--skip-review` follows the same opt-out rule as `start`.

Keep original-language user excerpts, available session or message locators,
corrections, confirmed decisions, and unaccepted suggestions distinguishable.
Exclude unrelated private material. Give the worker a concise handoff with
source locators and let it open the originals.

## Close

The CLI protects user-driven sessions from cleanup; do not record session
markers or remove sessions by hand. An unpromoted exploration may be abandoned
with `close --abandon` even when its evidence import failed; report the
`discussion_evidence_gap`.
