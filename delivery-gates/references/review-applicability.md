# Review Applicability Matrix

Use this only when approved project policy does not already decide applicability.
It selects evidence; it does not authorize or perform another operation.

| Change signal | Required independent evidence |
|---|---|
| Production behavior or non-trivial code path changed | Code review of the fixed revision/diff |
| AuthN/AuthZ, secrets, cryptography, privilege, destructive actions, untrusted input/path/parser, external network boundary, sensitive data, or dependency trust changed | Security review with threat/abuse cases and verification |
| Schema, stored data, protocol/state format, backfill, or compatibility boundary changed | Migration/compatibility review with dry-run and rollback/recovery evidence |
| Build, packaging, dependency lock, or release configuration changed | Build provenance plus dependency/supply-chain evidence |
| Operator-visible failure/recovery behavior changed | Observability/operations and rollback evidence |

An N/A result names the absent signal and cites the fixed changed-path/diff scope;
“low risk” alone is not evidence. Each review record names reviewer/producer,
reviewed revision and paths, checks performed, findings/blockers, disposition,
and a repository path or immutable external run reference. The implementation
agent may provide inputs but must not impersonate an independent reviewer.
