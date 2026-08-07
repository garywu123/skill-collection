# Pre-Implementation Alignment Contract

Use this reference only for `pre-implement`. It is the complete runtime reference for
that operation: common checks, feature checks, kind applicability, and missing-input
behavior. A finding without specific evidence in both artifacts is not a finding.

## Direction and precedence

Spec Kit analysis checks horizontally inside one work item:

```text
spec.md <-> plan.md <-> tasks.md
```

`spec-sync` checks vertically, using only relevant IDs and sections. Product,
roadmap, and UI branches apply to features; every kind checks its approved
work-item inputs and applicable architecture/repository constraints:

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

## Common pre-implementation checks

| # | Lower artifact | Higher artifact | Required evidence | Severity |
|---|---|---|---|---|
| C1 | `spec` | Approved work request/source anchors | Scope and exclusions agree; no higher-truth change is hidden | Blocking |
| C2 | `plan` | Applicable Plan Constraints/ADRs | Every applicable `AC-###` is honored or superseded by an accepted ADR | Blocking |
| C3 | `tasks` | `spec` and `plan` | Every required proof has work; no task exceeds scope | Blocking |
| C4 | `requirements_checklist` | `spec` | No unresolved requirement-quality blocker remains | Blocking |
| C5 | All inputs | `roadmap.yaml` | Paths and IDs resolve, and the entry's status matches the operation being run | Blocking |
| C6 | Project guidance | Repository | Cited commands and paths resolve | Advisory |

Apply exactly one selected row from the work-kind table after these common checks.

## Additional feature checks

| # | Lower artifact | Higher artifact | Required evidence | Severity |
|---|---|---|---|---|
| 1 | `spec.md` | Roadmap `Owns Requirements` | Each owned `PR-###` maps to a named acceptance scenario | Blocking |
| 2 | `spec.md` | Other roadmap entries | No scenario implements a requirement owned by another feature | Blocking |
| 3 | `spec.md` | Roadmap scope/non-goals | Scope agrees and no non-goal is implemented | Blocking |
| 4 | `plan.md` | Approved baseline decisions | No undeclared cross-feature technology or boundary is introduced | Blocking |
| 5 | `wireframes.md` | Roadmap `UI Surface` | Present when a new or changed UI is required; absence is explicit when `none` | Blocking |
| 6 | `wireframes.md` | `spec.md` | Every screen/state traces to a scenario and every UI-visible scenario is represented | Blocking |
| 7 | Roadmap feature | Roadmap dependencies | Prerequisites are delivered or approved for parallel work | Blocking |
| 8 | Feature artifacts | Product glossary | Terms match approved domain language | Advisory |
| 9 | `wireframes.md` | Approved UI structure | Shared patterns are reused or deviations declared | Advisory |

`Blocking` means that cited artifacts contradict or violate an approved constraint.
`Advisory` means they remain compatible but traceability or maintainability has degraded.
Style preferences and uncited suspicions are out of scope.

## Work-kind applicability

All kinds require approved, mutually consistent `spec`, `plan`, `tasks`, and
`checklist` files at the paths recorded for the work item. Read and apply only
the row for the explicitly named kind.

| Kind | Higher truth and required pre-checks | Must not claim |
|---|---|---|
| `feature` | Owning roadmap entry and PR IDs; scope/non-goals; dependencies; applicable architecture and UI truth | Acceptance before fresh-context checklist verification |
| `bug` | Approved expected behavior and affected feature/requirement anchors when applicable; regression boundary; architecture constraints | New product behavior or feature acceptance |
| `maintenance` | Explicit non-behavioral scope; repository/guidance facts; architecture constraints | Product-scope or architecture change |
| `migration` | Migration/compatibility contract; data or protocol invariants; rollback/recovery plan; applicable architecture decisions | Successful production migration or release |
| `security` | Approved threat/control objective; affected trust boundaries and security requirements; disclosure constraints | Broad security certification or release approval |

If the proposed work changes a higher source of truth, block and route a change request.
A work-kind label never authorizes skipping an applicable later code, security,
migration, compatibility, acceptance, or release review required by project policy.

## Missing inputs

Missing prerequisites (`spec`, `plan`, `tasks`, `requirements_checklist`, target identity,
kind, or explicit user authorization) block the mode. For other inputs, report the exact
skipped checks:

| Missing input | Result |
|---|---|
| Architecture baseline | Block C2 and feature check 4; the plan lacks an approved project constraint set |
| Approved UI structure | Block feature checks 5-6 unless an approved product-UI N/A rationale applies; otherwise skip only check 9 |
| Roadmap `UI Surface` | Block feature checks 5-6; do not infer it from implementation |
| Project guidance | Skip C6 |
| `roadmap.yaml` missing, or its entry contradicts the files on disk | Block; a review cannot establish which function it is reviewing |

A skipped check is never reported as passed.

## Completeness

Batch exhaustive work by stable IDs/paths. Record every required batch in the
output's `Coverage Batches` table with concrete evidence. A truncated resolver
result, uncovered required batch, or missing/stale state prevents `Pass`; never
infer that the uninspected remainder matches the first batch.
