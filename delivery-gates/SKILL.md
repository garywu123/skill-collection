---
name: delivery-gates
description: Perform one explicitly requested feature-acceptance, release-readiness, release-authorization, or release-result operation. Reviews create candidates; only dedicated deterministic decision commands may record human acceptance, release authorization, or execution results. Never implement fixes, run release tooling, publish, deploy, or invoke another lifecycle skill.
---

# Delivery Gates

Review independently from the implementation agent. A human controls every gate. Support
exactly five operations:

- `accept-feature <feature-id>`
- `record-feature-decision <feature-id> <Accepted|Rejected|Changes requested>`
- `release <release-id> <explicit-scope>`
- `authorize-release <release-id>`
- `record-release-result <release-id> <Succeeded|Failed|Held|Cancelled>`

## Shared contract

Before an operation:

1. Require the current user to name one operation and target. State and recommendations
   are never authority.
2. Read `.specify/flow-state.yaml`. Query the generated index with deterministic
   `resolve --id` or `resolve --path`; open the complete index only when its bounded size
   is known to be small.
3. Read only the scoped IDs, artifacts, changed implementation, and evidence required by
   this operation. Classify missing evidence as `missing`, `not_run`, or
   `not_applicable` with a reason.
4. Review operations write only their gate artifact. Decision operations pass
   human-provided values to the exact deterministic command so it updates only
   permitted fields. Report the result and stop.

Never invent evidence or authority; repair code; change product, architecture, roadmap,
or accepted history; invoke another lifecycle skill; or tag, publish, deploy, or run
release tooling.

When approved project policy does not already determine which independent
reviews apply, load the
[review applicability matrix](references/review-applicability.md). It routes
evidence only; it does not invoke code, security, or migration review.

## Operation-to-start mapping

| Operation | Deterministic start |
|---|---|
| `release` | May run `start --expect-revision N --kind release --work-id <release-id> --stage release_readiness` after prerequisites pass and no gate is pending. |
| Other four operations | Never run `start`; they extend the exact active gate named by the user. |

## `accept-feature`

Require active work kind `feature`, the named feature ID, status
`ready_for_acceptance`, and an approved spec with acceptance scenarios. There is no
recovery-review exception. Also read applicable constraints/wireframes, the fixed diff or
changed paths, verification, tests, coverage policy, CI, and applicable code/security
review evidence.

Evaluate user-visible and negative scenarios; a green build alone is insufficient. Create
or update `specs/NNN-feature/acceptance.md` from
[the acceptance template](assets/feature-acceptance.template.md). Use one concrete review
status:

- `ready`: every required scenario and gate has traceable evidence;
- `conditional`: no blocker exists, but named human-owned conditions remain;
- `not_ready`: a scenario failed, required evidence is missing, or truth conflicts.

Register the artifact with `record-output --expect-revision N --stage acceptance
--status ready_for_acceptance --artifact acceptance=<path>` plus exact evidence paths.
Leave the human gate pending and stop. Do not accept the feature.

Route bugs, implementation debt, future ideas, and cross-feature design debt to their
owners. Use [the debt template](assets/tech-debt.template.md) only when the current request
also authorizes creating that follow-up.

## `record-feature-decision`

Require the named feature to remain `ready_for_acceptance`, the recorded acceptance
artifact/hash to match, and an unambiguous current-user decision. Read its referenced
blockers, but do not alter review findings or evidence.

`Accepted` requires review status `ready` or `conditional` and no unresolved
blocker; otherwise stop and report the conflict. Do not edit the artifact first.
Run only the deterministic command below; it verifies the reviewed hash and
replaces exactly the four decision fields while preserving every review byte:

```text
record-feature-decision --expect-revision N \
  --decision accepted|rejected|changes_requested --artifact <acceptance-path> \
  --decided-by <human-name-or-role> --decision-date YYYY-MM-DD \
  --decision-evidence <exact-current-user-statement-or-reference>
```

Never use generic `decide` for feature acceptance. Stop after the durable artifact and
state result.

## `release`

Require an explicit release ID and fixed feature scope. Every included feature must have
a durable human acceptance decision. Read build provenance, CI, and risk-applicable code,
dependency, security, migration, rollback, observability, operations, documentation, and
compatibility evidence, plus explicit dispositions for known bugs and debt.

Create or update `doc/releases/<release-id>-readiness.md` from
[the readiness template](assets/release-readiness.template.md). Use `ready`,
`conditional`, or `not_ready` with the same evidence discipline as acceptance. Register
it with `record-output --expect-revision N --stage release_readiness --status
ready_for_release --artifact release_readiness=<path>` and stop. This operation can produce only
`ready_for_release`; it never authorizes or executes a release.

## `authorize-release`

Require active release work for the named ID in `ready_for_release`, a matching readiness
artifact/hash, review status `ready` or `conditional`, no unresolved blocker, and an
explicit current-user `Authorized` decision. Do not edit the artifact first. Run
only the command below; it verifies the reviewed hash and deterministically
replaces `Human readiness decision`, `Authorized by`, `Authorized on`, and
`Authorization evidence`:

```text
authorize-release --expect-revision N --artifact <readiness-path> \
  --authorized-by <human-name-or-role> --authorized-on YYYY-MM-DD \
  --authorization-evidence <exact-current-user-statement-or-reference>
```

The maximum result is `release_authorized`. Do not run, trigger, simulate, or claim a
release. Report the separately authorized project release command as a possible next
human action and stop.

## `record-release-result`

Require active status `release_authorized`, separately authorized release tooling to have
finished with a terminal result, an explicit current-user confirmation, and exact
execution evidence. A readiness recommendation or authorization alone is not execution.
The evidence must be a repository-contained YAML receipt produced by the external
CI/deployment/release mechanism from
[the receipt schema](assets/release-result-receipt.template.yaml). It binds schema
version, release ID, terminal result, producer, run ID, UTC completion time, and—on
success—the released artifact SHA-256. A chat string or bare run ID is insufficient.

Do not edit the readiness artifact first. Run only the deterministic command
below; it preserves the authorized review and replaces exactly `Execution`,
`Execution evidence`, `Confirmed by`, and `Confirmed on`:

```text
record-release-result --expect-revision N \
  --result succeeded|failed|held|cancelled --artifact <readiness-path> \
  --execution-evidence <repository-relative-receipt.yaml> \
  --confirmed-by <human-name-or-role> --confirmed-on YYYY-MM-DD
```

The deterministic command validates the receipt target/result, hashes it into
pointer evidence, and writes its path into the readiness artifact. Only
`succeeded` may produce `released`; every other result remains non-released.
Never run release tooling in this operation. Report the release ID, terminal
result, receipt path/hash, and state, then stop.

## Review report

For review operations, report the scope, review status, blockers with evidence, routed
follow-ups, pending human decision, files changed, state before/candidate after, and only
the allowed next human commands. Then stop.
