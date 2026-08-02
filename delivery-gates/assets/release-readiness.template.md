# Release Readiness: {{RELEASE_ID}}

**Release ID**: {{RELEASE_ID}}
**Review status**: {{REVIEW_STATUS}}
**Human readiness decision**: {{PENDING_OR_AUTHORIZATION_DECISION}}
**Authorization evidence**: {{PENDING_OR_AUTHORIZATION_EVIDENCE}}
**Authorized by**: {{PENDING_OR_AUTHORIZER}}
**Authorized on**: {{PENDING_OR_AUTHORIZATION_DATE}}
**Scope**: {{FEATURE_IDS_OR_RANGE}}
**Artifact revision**: {{ARTIFACT_REVISION}}

## Included Acceptance Decisions

| Feature | Human decision | Evidence |
|---|---|---|
| {{FEATURE_ID}} | {{FEATURE_DECISION}} | {{FEATURE_DECISION_EVIDENCE}} |

## Release Gates

| Gate | Applicability | Result | Evidence / reason |
|---|---|---|---|
| Build provenance | required | {{BUILD_RESULT}} | {{BUILD_EVIDENCE}} |
| CI | required | {{CI_RESULT}} | {{CI_EVIDENCE}} |
| Dependency review | {{DEPENDENCY_APPLICABILITY}} | {{DEPENDENCY_RESULT}} | {{DEPENDENCY_EVIDENCE_OR_REASON}} |
| Security review | {{SECURITY_APPLICABILITY}} | {{SECURITY_RESULT}} | {{SECURITY_EVIDENCE_OR_REASON}} |
| Migration | {{MIGRATION_APPLICABILITY}} | {{MIGRATION_RESULT}} | {{MIGRATION_EVIDENCE_OR_REASON}} |
| Rollback | {{ROLLBACK_APPLICABILITY}} | {{ROLLBACK_RESULT}} | {{ROLLBACK_EVIDENCE_OR_REASON}} |
| Observability / operations | {{OPERATIONS_APPLICABILITY}} | {{OPERATIONS_RESULT}} | {{OPERATIONS_EVIDENCE_OR_REASON}} |
| User / operator documentation | {{DOCUMENTATION_APPLICABILITY}} | {{DOCUMENTATION_RESULT}} | {{DOCUMENTATION_EVIDENCE_OR_REASON}} |

## Blockers

- {{BLOCKER_OR_NONE}}

## Deferred Items

| Type | ID | Disposition | Owner |
|---|---|---|---|
| {{DEFERRED_TYPE}} | {{DEFERRED_ID}} | {{DEFERRED_DISPOSITION}} | {{DEFERRED_OWNER}} |

## Release Execution Result

**Execution**: {{NOT_RUN_OR_EXECUTION_RESULT}}
**Execution evidence**: {{NOT_AVAILABLE_OR_EXECUTION_EVIDENCE}}
**Confirmed by**: {{PENDING_OR_CONFIRMER}}
**Confirmed on**: {{PENDING_OR_CONFIRMATION_DATE}}

Pending execution result.
