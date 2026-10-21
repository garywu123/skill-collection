# Simplification Patterns

Prompts for batch review. Each pattern names what to ask and the usual smallest
direction. Confirm the trigger in the code and the constraint in the recorded
answers before raising an item.

## Code and business

### Precision beyond the business

Exact equality, or nanometre, microsecond or one-ulp tolerances, on computed
values where the business accepts millimetres or tenths of a second.

- Ask: what difference would a user notice, and what visibly happens when two
  values differ by less than that?
- Direction: one named tolerance derived from the recorded constraints.

### Rigor where an estimate suffices

Certified error bounds, directed rounding, extended-range arithmetic or
adaptive solvers used for estimates, sampling or display.

- Ask: who consumes the result, and does a safety factor on a plain formula
  meet their need?
- Direction: plain arithmetic with a documented margin.

### Missing envelope at the trust boundary

No realistic range validation where input enters, so inner layers guard NaN,
overflow and extreme values, catch and convert exceptions, and treat exception
type or order as a contract. Mechanisms are kept because of inputs no real user
can produce.

- Ask: where does input enter, and what ranges are real?
- Direction: validate realistic ranges once at entry; inner code assumes valid
  input. This is usually a cross-module `decide` item.

### Data or results nobody reads

Retained alternatives, history, caches or intermediate collections.

- Ask: which consumer reads this, and when?
- Direction: keep only what a consumer reads; release the rest when done.

### Same work in several places

The same calculation, mapping or validation repeated across layers or types.

- Ask: is one copy the owner, and do the copies differ on purpose?
- Direction: one owner; callers reuse it.

### Guards implied by other guards

A check that an earlier or stronger check already guarantees.

- Ask: which input passes this guard but fails no other?
- Direction: remove it when no such input exists.

### Configurability without a tuner

Settings, options or extension points that nobody changes, or that serve one
caller.

- Ask: who changes this value, when, and why?
- Direction: a constant, or the existing input.

### Generic features without a need

Audit trails, sync, import/export, versioning, plug-in points or retries that
the product's users never asked for.

- Ask: which user flow needs it?
- Direction: remove, or record as an open product decision.

## Documents

### Process log in a document

Commands, test counts, review rounds, tool failures or dated histories inside
plans, designs or results.

- Direction: move to commits or pull requests; keep the current fact.

### Status in several places

The same status repeated in headers, tables and sections, which drift and
contradict each other.

- Direction: one status location; other places link to it.

### Defensive prose

Lists of non-claims, disclaimers, "does not authorize" and repeated caveats.

- Ask: what would a reader do differently without this sentence?
- Direction: delete sentences that change no decision.

### Restated rules

An upstream rule copied into downstream documents instead of linked.

- Direction: keep it in its owner; link elsewhere.

### Written for auditors, not readers

A document whose reader cannot find the decision or next action quickly.

- Ask: who reads this, and what decision do they need?
- Direction: lead with that decision; cut the rest or move it to history.
