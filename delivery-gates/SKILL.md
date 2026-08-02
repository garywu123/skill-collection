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

Use a fresh conversation, fork, or worker for each operation. Reconstruct truth
from the pointer/index and owning artifacts; do not rely on another Skill body,
an old pointer, or excerpts inherited across a gate. Fresh review workers may
batch one already-authorized review, but cannot select another operation.

## Shared contract

Before an operation:

1. Require the current user to name one operation and target. State and recommendations
   are never authority.
2. Read `.specify/flow-state.yaml`. Query the generated index with deterministic
   `resolve --id` or `resolve --path`; never load the complete index into semantic
   context. Full agreement belongs to deterministic `validate --check-paths`.
3. Read only the scoped IDs, artifacts, changed implementation, and evidence required by
   this operation. Classify missing evidence as `missing`, `not_run`, or
   `not_applicable` with a reason.
4. Review operations write only their gate artifact. Decision operations pass
   human-provided values to the exact deterministic command so it updates only
   permitted fields. Report the result and stop.

Keep each opened semantic or evidence slice at or below 8 KiB and the initial
target payload at or below 24 KiB. For a large diff, scenario set, or release
scope, review stable-ID/path batches in fresh independent worker contexts and
merge only citations, results, blockers, and a coverage ledger. A truncated or
uncovered required batch prevents `ready` and release authorization.

Every review artifact records `Reviewed by`, `Reviewed on`, and
`Independence: non-implementer`. Every gate row states whether it is applicable;
`not_applicable` requires a concrete reason and is never treated as passing evidence.

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

The spec must define stable `SC-###` IDs. `Scenario Evidence` must cover that
exact set once each, with no missing, extra, or duplicate row. Tests /
deterministic verification is always `required`; the other quality gates use
project policy and the applicability matrix.

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
state result. The command also creates an indexed, content-hashed
`.specify/decisions/*.yaml` receipt binding the reviewed acceptance hash to the
post-decision hash. Report the receipt path/hash; future release checks require
the latest receipt to be `accepted` and the acceptance artifact to remain
hash-matching.

## `release`

Require an explicit release ID and fixed feature scope. Every included feature must have
a durable, content-hashed human acceptance receipt bound to its unchanged
acceptance artifact. Build provenance is always required. Read build provenance,
CI, and risk-applicable code,
dependency, security, migration, rollback, observability, operations, documentation, and
compatibility evidence, plus explicit dispositions for known bugs and debt.
In `Included Acceptance Decisions`, record the acceptance Markdown artifact
path, not the internal decision-receipt path; the deterministic state validator
resolves and verifies the latest receipt separately.

Create or update `doc/releases/<release-id>-readiness.md` from
[the readiness template](assets/release-readiness.template.md). Use `ready`,
`conditional`, or `not_ready` with the same evidence discipline as acceptance.
For `ready` or `conditional`, register it with `record-output --expect-revision
N --stage release_readiness --status ready_for_release --artifact
release_readiness=<path>` and stop. For `not_ready`, use `block --expect-revision
N --stage release_readiness --artifact release_readiness=<path>` with every
concrete blocker; the result is `blocked`, not a pending release gate. It may be
retried by a later explicit `release` operation. This operation never authorizes
or executes a release.

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
human action and stop. The command creates an indexed, content-hashed
`release_authorization` receipt that binds the reviewed readiness hash to the
authorized artifact hash; report its path/hash.

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
`Execution evidence`, `Execution evidence SHA-256`, `Confirmed by`, and
`Confirmed on`:

```text
record-release-result --expect-revision N \
  --result succeeded|failed|held|cancelled --artifact <readiness-path> \
  --execution-evidence <repository-relative-receipt.yaml> \
  --confirmed-by <human-name-or-role> --confirmed-on YYYY-MM-DD
```

The deterministic command validates the external execution receipt target/result,
hashes it into pointer evidence, and writes its path and SHA-256 into the
readiness artifact. It also creates an indexed, content-hashed `release_result`
decision receipt chained to the prior authorization hash. Future index rebuilds
validate both the decision chain and external receipt binding even after the
pointer moves to another work item. Only
`succeeded` may produce `released`; every other result remains non-released.
Never run release tooling in this operation. Report the release ID, terminal
result, both receipt paths/hashes, and state, then stop.

## Review report

For review operations, report the scope, review status, blockers with evidence, routed
follow-ups, pending human decision, files changed, state before/candidate after, and only
the allowed next human commands. Then stop.

For decision operations, report the reviewed artifact path, pre/post hashes,
decision-receipt path/hash, resulting state/revision, and only human-controlled
next actions. Then stop.
