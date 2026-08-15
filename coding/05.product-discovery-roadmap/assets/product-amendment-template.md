# Product Amendment: {{CR_ID}}

**Status**: Ready for Review
**Trigger**: {{REQUEST_OR_EVIDENCE_PATH}}
**Base artifacts**: {{CANONICAL_PATHS_AND_REVISIONS}}

## Proposed Product Change

{{USER_OUTCOME_SCOPE_RULE_OR_PRIORITY_CHANGE}}

## Stable-ID Effects

| Existing ID | Disposition | Successor ID / rationale |
|---|---|---|
| {{PR_OR_F_ID}} | {{unchanged | superseded | added}} | {{ID_OR_REASON}} |

## Canonical Bundle Effects

List only roots and members whose bytes or membership would change. Approval
recomputes the complete table for each listed split root; this proposal does not
replace that verification.

| Canonical root role | Member path | Disposition |
|---|---|---|
| {{requirements | roadmap}} | `{{REPO_RELATIVE_PATH}}` | {{add | modify | remove | none}} |

## Downstream Impact

- Affected roadmap features/dependencies: {{IDS_OR_NONE}}
- Existing specs/deliveries requiring follow-up: {{IDS_OR_NONE}}
- Architecture/UI/guidance routes: {{ROUTES_OR_NONE}}

## Validation

- [ ] Product intent, journeys, requirements, and explicit exclusions remain
      consistent.
- [ ] Requirement ownership and dependency graph remain valid.
- [ ] Stable IDs are never reused; successors exist only where both records
      require independent meaning or tracking.
- [ ] Split-root membership changes are complete and unambiguous.

Keep this proposal unchanged while it is under review. Approval fields in the
updated canonical artifact and Git history preserve the review record.
