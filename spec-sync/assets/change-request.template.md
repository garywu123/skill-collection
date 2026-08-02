# CR-NNNN: [Short title stating the change]

**Raised**: YYYY-MM-DD by [person/channel]
**Status**: Proposed
**Human decision**: Pending
**Highest impact**: {{HIGHEST_IMPACT_LAYER}}
**Horizon**: {{HORIZON}}
**Flow-state revision read**: [revision or not present]
**Artifact-index query**: [ID/path query or not present]

> This record is a routing proposal. It does not authorize or execute any action below.

## Request

[Original request in the requester's terms. Do not translate it into a solution.]

## Impact evidence

| Layer/artifact | ID/path | Current state | Evidence anchor | Effect |
|---|---|---|---|---|
| Product requirement | PR-0XX | Approved | [section/link] | Proposed successor PR-0YY |
| Feature | FNNN | Accepted | [acceptance record] | Preserve; propose successor FMMM |
| Plan constraint | AC-00X | Active | [baseline section] | Possible superseding ADR |

Delete unused example rows. List only cited impact.

## Proposed routing

Order actions from the highest source of truth downward. Assign one owner per action.

| # | Layer | Affected IDs | Proposed action | Owning workflow | Expected output | Authorization |
|---|---|---|---|---|---|---|
| 1 | Product truth | PR-0XX | Append successor requirement | `product-discovery-roadmap` | Approved PR-0YY and supersession link | Pending |
| 2 | Technical decision | AC-00X | Evaluate superseding decision | `architecture-baseline amend` | Accepted/rejected ADR and current constraint | Pending |
| 3 | Feature boundary | FNNN | Propose successor feature | `product-discovery-roadmap` | Approved roadmap entry FMMM | Pending |

## Stale downstream artifacts

| Artifact/evidence | Why stale | Revalidate after |
|---|---|---|
| [path or ID] | [specific dependency] | [approved output above] |

## Suggested next human action

```text
[Exact prompt or command the human may choose to authorize next. Do not run it.]
```

## Decision Receipt

Do not fill decision fields in this proposal. An explicit generic gate decision
creates a content-hashed `.specify/decisions/*.yaml` receipt containing outcome,
actor, date, evidence, and the reviewed role/path/hash set. Resolve that receipt
by this CR ID through the generated artifact index.

## Notes

[Information not already held by the authoritative artifacts. Do not restate requirement
text here.]
