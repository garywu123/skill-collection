# Architecture Amendment: {{CR_ID}}

**Status**: Ready for Review
**Trigger**: {{REQUEST_OR_EVIDENCE_PATH}}
**Base baseline / ADR revisions**: {{PATHS_AND_REVISIONS}}

## Challenged Decision

{{AC_OR_ADR_ID_AND_CURRENT_DECISION}}

## Proposed Change and Alternatives

{{PROPOSAL_ALTERNATIVES_AND_TRADEOFFS}}

## Constraint Effects

| Constraint | Proposed disposition | Affected features |
|---|---|---|
| {{AC_ID}} | {{unchanged | superseded | added}} | {{FEATURE_IDS}} |

## Delivery and Migration Impact

- Existing implementations: {{IMPACT_OR_NONE}}
- Migration/reversal work: {{WORK_OR_NONE}}
- Guidance that may become stale: {{PATHS_OR_NONE}}

## Decision Records

- Proposed ADRs: {{ADR_PATHS_OR_NONE}}
- ADRs to supersede only after approval: {{ADR_IDS_OR_NONE}}

## Canonical Bundle Effects

List only roots and members whose bytes or membership would change. Approval
recomputes the complete table for a split root.

| Canonical root | Member path | Disposition |
|---|---|---|
| `{{BASELINE_PATH}}` | `{{REPO_RELATIVE_PATH}}` | {{add | modify | remove | none}} |

Keep this proposal unchanged while it is under review. The explicit human
approval fields in the updated baseline or ADR and Git history are the durable
decision record.
