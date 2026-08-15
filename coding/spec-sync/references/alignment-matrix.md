# Pre-Implementation Alignment Contract

Use this reference only for `pre-implement`. It is the complete runtime reference for
that operation: common checks, feature checks, kind applicability, and missing-input
behavior. A finding without specific evidence in both artifacts is not a finding.

## Direction and precedence

The direct feature route uses the approved roadmap entry as its behavior source:

```text
product requirements -> roadmap feature -> checklist
                              |                 |
                    architecture/UI        implementation
```

The detailed route adds feature-local refinement:

```text
product requirements
        |
roadmap feature entry ----- architecture baseline ----- UI structure
        |                           |                         |
     spec.md -------------------- plan.md ------------- wireframes.md
        |
     tasks.md ------------------- checklist.md
```

When two approved artifacts disagree, report the conflict. The higher source of truth
remains authoritative until its owning workflow explicitly changes it. `spec-sync` edits
neither side.

## Direct feature checks

| # | Lower artifact | Higher artifact | Required evidence | Severity |
|---|---|---|---|---|
| D1 | `checklist.md` | Roadmap description and acceptance | Every acceptance item is preserved without weakening or added behavior | Blocking |
| D2 | Roadmap feature | Owned and bound `PR-###` | Description and acceptance are sufficient to implement every applicable behavior | Blocking |
| D3 | Proposed implementation approach | Applicable `AC-###`/ADRs | No shared constraint is contradicted or silently decided | Blocking |
| D4 | `wireframes.md` or N/A | Roadmap `UI Surface` and behavior source | Required UI states are represented; `none` has no UI artifact | Blocking |
| D5 | Roadmap feature | Roadmap dependencies | Prerequisites are delivered or explicitly approved for parallel work | Blocking |
| D6 | Project guidance | Repository | Cited commands and paths resolve | Advisory |

If D2 cannot pass from the roadmap entry, block with the missing behavior and
recommend the detailed route. Do not invent detail or create the spec.

## Detailed route checks

| # | Lower artifact | Higher artifact | Required evidence | Severity |
|---|---|---|---|---|
| T1 | `spec.md` | Roadmap description, acceptance, and PR IDs | Behavior agrees, every owned PR maps to acceptance, and no other feature's behavior is absorbed | Blocking |
| T2 | `plan.md` | Spec and applicable `AC-###`/ADRs | The plan covers the behavior and honors shared constraints | Blocking |
| T3 | `tasks.md` | Spec, plan, and checklist | Every required proof has work and no task exceeds scope | Blocking |
| T4 | `checklist.md` | Spec acceptance | Criteria are preserved without weakening | Blocking |
| T5 | `wireframes.md` or N/A | UI Surface, behavior source, and UI structure | Required screens/states are represented or correctly absent | Blocking |
| T6 | Roadmap feature | Roadmap dependencies | Prerequisites are delivered or explicitly approved for parallel work | Blocking |
| T7 | Project guidance | Repository | Cited commands and paths resolve | Advisory |

`Blocking` means that cited artifacts contradict or violate an approved constraint.
`Advisory` means they remain compatible but traceability or maintainability has degraded.
Style preferences and uncited suspicions are out of scope.

## Work-kind applicability

Only a `feature` may use the direct route. Detailed-route inputs must be mutually
consistent. Read and apply only the row for the explicitly named kind.

| Kind | Higher truth and required pre-checks | Must not claim |
|---|---|---|
| `feature` | Owning roadmap entry and PR IDs; description/acceptance; dependencies; applicable architecture and UI truth | Acceptance before fresh-context checklist verification |
| `bug` | Approved expected behavior and affected feature/requirement anchors when applicable; regression boundary; architecture constraints | New product behavior or feature acceptance |
| `maintenance` | Explicit non-behavioral scope; repository/guidance facts; architecture constraints | Product-scope or architecture change |
| `migration` | Migration/compatibility contract; data or protocol invariants; rollback/recovery plan; applicable architecture decisions | Successful production migration or release |
| `security` | Approved threat/control objective; affected trust boundaries and security requirements; disclosure constraints | Broad security certification or release approval |

If the proposed work changes a higher source of truth, block and route a change request.
A work-kind label never authorizes skipping an applicable later code, security,
migration, compatibility, acceptance, or release review required by project policy.

## Missing inputs

Missing route prerequisites, target identity, kind, or explicit user
authorization block the mode. A missing spec is not a blocker for the direct
feature route. For other inputs, report the exact skipped checks:

| Missing input | Result |
|---|---|
| Architecture baseline | Block D3 or T2; the work lacks an approved project constraint set |
| Approved UI structure | Block D4 or T5 unless an approved product-UI N/A rationale applies |
| Roadmap `UI Surface` | Block D4 or T5; do not infer it from implementation |
| Project guidance | Skip D6 or T7 |
| `roadmap.yaml` missing, or its entry contradicts the files on disk | Block; a review cannot establish which function it is reviewing |

A skipped check is never reported as passed.

## Completeness

Batch exhaustive work by stable IDs/paths. Record every required batch in the
output's `Coverage Batches` table with concrete evidence. A truncated resolver
result, uncovered required batch, or missing/stale state prevents `Pass`; never
infer that the uninspected remainder matches the first batch.
