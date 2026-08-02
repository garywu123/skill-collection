# Product Amendment: {{CR_ID}}

**Status**: Ready for Review
**Trigger**: {{REQUEST_OR_EVIDENCE_PATH}}
**Base artifacts**: {{CANONICAL_PATHS_AND_HASHES}}

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

- [ ] Scope and non-goals remain explicit.
- [ ] Requirement ownership and dependency graph remain valid.
- [ ] Approved history is preserved by successor IDs.
- [ ] Split-root membership changes are complete and unambiguous.

This proposal remains byte-identical during promotion. The later canonical
review plus content-hashed generic decision receipt is the durable approval record.
