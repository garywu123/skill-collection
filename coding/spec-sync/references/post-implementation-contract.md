# Post-Implementation Verification Contract

Use this reference only for `post-implement`. It is the complete runtime reference for
the operation. The review verifies vertical conformance and readiness for a separate
gate; it never performs acceptance, security certification, or release approval.

## Required evidence

| Claim | Acceptable evidence | Not sufficient alone |
|---|---|---|
| Tasks complete | Every task checked, or each deferral has an ID, destination/owner, and reason | "Mostly done" |
| Checks complete | Named command, checklist, or CI job with result and revision | A build badge without revision |
| Required behavior/control implemented | Applicable scenario, regression, invariant, or control ID linked to focused evidence | Code exists or PR merged |
| Constraints honored | Relevant code/test evidence checked against each applicable `AC-###` | No reported complaints |
| Ready for the kind's next gate | All applicable rows below, no blocking vertical drift, and no required evidence is skipped | Green build, completed tasks, tag, or UAT claim alone |

Record citations rather than conclusions: scenario/check ID, command or activity,
revision, result, and artifact/log path. Preserve failures, `not_run`, and skipped checks.
Never invent a result or infer that an absent test passed.

## Work-kind proof

Apply exactly one row for the explicitly named kind.

| Kind | Required post-implementation proof | Maximum claim |
|---|---|---|
| `feature` | Acceptance scenarios, tasks/checks, applicable `AC-###`, and relevant quality-gate evidence | `ready_for_acceptance`; never accepted |
| `bug` | Reproduction fails before/fixed after, regression test, targeted checks, and no scope expansion | `ready_for_review`; never new product behavior |
| `maintenance` | Named maintenance objective, unchanged-behavior evidence, targeted checks, and relevant regressions | `ready_for_review`; never product or architecture approval |
| `migration` | Dry-run/rehearsal, invariant checks, compatibility result, and rollback/recovery evidence | `ready_for_review`; never successful production migration or release |
| `security` | Control-focused test/review evidence, regression checks, and residual-risk disposition | `ready_for_review`; never broad certification or release approval |

## Completeness and missing inputs

The exact work ID/kind, matching pointer and generated index, approved and hash-matching
`pre_implementation`, converged implementation revision, tasks, and named evidence are
required. Missing or stale state, an uncovered required ID batch, a truncated query that
was not narrowed, any concrete blocker, or any skipped required check prevents a ready
result.

Batch exhaustive work by stable IDs. The verification artifact must retain a compact
coverage ledger identifying every required batch and its result. Do not treat batch
summaries as evidence; keep the cited repository paths/revisions.

The maximum state is feature `ready_for_acceptance` or non-feature
`ready_for_review`. Human-authorized acceptance owns `accepted`; a durable generic
decision receipt owns non-feature approval.
