# Alignment Matrix

Use this reference only for `pre-implement` or `post-implement`. A finding without
specific evidence in both artifacts is not a finding.

## Direction and precedence

Spec Kit analysis checks horizontally inside one feature:

```text
spec.md <-> plan.md <-> tasks.md
```

`spec-sync` checks vertically, using only the relevant IDs and sections:

```text
product requirements
        |
roadmap feature entry ----- architecture baseline ----- UI structure
        |                           |                         |
     spec.md -------------------- plan.md ------------- wireframes.md
        |
     tasks.md
```

When two approved artifacts disagree, report the conflict. The higher source of truth
remains authoritative until its owning workflow explicitly changes it. `spec-sync` edits
neither side.

## Pre-implementation checks

| # | Lower artifact | Higher artifact | Required evidence | Severity |
|---|---|---|---|---|
| 1 | `spec.md` | Roadmap `Owns Requirements` | Each owned `PR-###` maps to a named acceptance scenario | Blocking |
| 2 | `spec.md` | Other roadmap entries | No scenario implements a requirement owned by another feature | Blocking |
| 3 | `spec.md` | Roadmap scope/non-goals | Scope agrees and no non-goal is implemented | Blocking |
| 4 | `plan.md` | Applicable Plan Constraints | Each referenced `AC-###` is satisfied or superseded by an accepted ADR | Blocking |
| 5 | `plan.md` | Approved baseline decisions | No undeclared cross-feature technology or boundary is introduced | Blocking |
| 6 | `wireframes.md` | Roadmap `UI Surface` | Present when a new or changed UI is required; absence is explicit when `none` | Blocking |
| 7 | `wireframes.md` | `spec.md` | Every screen/state traces to a scenario and every UI-visible scenario is represented | Blocking |
| 8 | `tasks.md` | `spec.md` | Every acceptance scenario has work and no task exceeds scope | Blocking |
| 9 | Roadmap feature | Roadmap dependencies | Prerequisites are delivered or approved for parallel work | Blocking |
| 10 | Feature artifacts | Product glossary | Terms match approved domain language | Advisory |
| 11 | `wireframes.md` | Approved UI structure | Shared patterns are reused or deviations declared | Advisory |
| 12 | Project guidance | Repository | Commands and paths cited for this feature resolve | Advisory |
| 13 | Referenced artifacts | Repository/index | Relevant links and indexed paths resolve | Advisory |

`Blocking` means that cited artifacts contradict or violate an approved constraint.
`Advisory` means they remain compatible but traceability or maintainability has degraded.
Style preferences and uncited suspicions are out of scope.

## Missing inputs

Missing prerequisites (`spec.md`, `plan.md`, `tasks.md`, target identity, or explicit user
authorization) block the mode. For other inputs, report the exact skipped checks:

| Missing input | Result |
|---|---|
| Architecture baseline | Skip 4-5; report that the plan lacks an approved project constraint set |
| Approved UI structure | Skip 11; do not skip 6-7 when the feature has UI behavior |
| Roadmap `UI Surface` | Block 6-7; do not infer it from implementation |
| Project guidance | Skip 12 |
| Pointer or index | Continue only when the user gives an unambiguous target and canonical paths; report reduced routing assurance |

A skipped check is never reported as passed.

## Post-implementation evidence

Post-implementation review verifies readiness for a separate acceptance gate. It does not
perform or approve acceptance.

| Claim | Acceptable evidence | Not sufficient alone |
|---|---|---|
| Tasks complete | Every task checked, or each deferral has an ID, owner/destination, and reason | "Mostly done" |
| Checks complete | Named checklist or CI job with result and revision | A build badge without revision |
| Scenario implemented | Scenario ID linked to a focused test result or recorded demonstration | Code exists or PR merged |
| Constraints honored | Relevant code/test evidence checked against each applicable `AC-###` | No reported complaints |
| Ready for acceptance | All above, no blocking vertical drift, and all critical inputs were available | Green build, completed tasks, release tag, or UAT claim by itself |

Record evidence as citations, not conclusions: scenario/check ID, command or activity,
revision, result, and artifact/log path. Preserve failures and skipped checks. Never invent
a command result or infer that an absent test passed.

The maximum state this review may request is `ready_for_acceptance`. Human-authorized
acceptance owns `accepted` and durable delivery claims.
