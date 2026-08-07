# F[ID] Delivery Checklist - [function name]

Spec: `[path to spec]`

Written with the spec, not at delivery time. Verified in a **fresh
conversation**: the context that implemented a function does not tick its own
boxes.

If accepted behavior changes, rebuild the affected criteria and clear every
box, Evidence row, Decision, reviewer, and date. Git retains the prior result;
the current file must never display acceptance for changed behavior.

## Acceptance criteria

One box per acceptance criterion in the spec. Copy the criterion; do not
paraphrase it into something easier to pass.

- [ ] [criterion 1]
- [ ] [criterion 2]

## Quality bar

- [ ] Tests cover the changed behavior and pass
- [ ] Full project validation passes
- [ ] The diff contains no unrelated changes
- [ ] Explicit non-goals from the spec were not built
- [ ] Routed documents affected by this function are updated
- [ ] The `roadmap.yaml` entry reflects reality

## Evidence

Record what was actually run, not what should pass. A criterion with no evidence
row is unverified, however obvious it looks.

| Check | Command or method | Result |
|---|---|---|
| | | |

## Decision

- Verified by:
- Date:
- Decision: accepted / changes requested
- Notes:

An unchecked box, a missing evidence row, or an untested criterion blocks
`accepted`. The fresh verification conversation does not repair implementation
to make a check pass; it reports what is incomplete rather than lowering the
bar. Only an explicit human decision records `accepted` in `roadmap.yaml`.
