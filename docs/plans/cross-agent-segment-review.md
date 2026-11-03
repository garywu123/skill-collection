# Cross-Agent Session Reuse, Segment Review, and Automatic Adjudication

Status: implemented with tests on 2026-11-02; design reviewed, implementation not independently reviewed.

Target: the `cross-agent` Skill (`SKILL.md`, `scripts/crossagent/*.py`, `assets/config.example.toml`, `scripts/tests`).

## Current behavior (corrected)

- Every execution checkpoint sets `fresh_reason = "plan-checkpoint"`, so each segment starts a new
  Producer session. Retained history: 125 `plan-checkpoint` starts versus 16 `context-threshold`
  rotations in `feature-delivery` Producers (user-provided statistic, not independently verified).
- One scalar `rotate_at_tokens` applies to both roles.
- There is no checkpoint review; review/revision cycles begin only after Producer `done`. Later
  reviews diff from the previous review tree.
- Reviews with pending findings stop at `awaiting-decision` for Orch adjudication; clean reviews end
  the run directly.

## A. Per-role rotation thresholds

```toml
[rotate_at_tokens]
producer = 250000
reviewer = 400000
```

A scalar value remains valid and applies to both roles. `_session_choice` reads the role's value.

## B. Producer resume across checkpoints

`checkpoint_session = "resume" | "fresh"`. With `resume`, a checkpoint keeps saving summary and tree
but sets no `fresh_reason`; rotation happens only at the role threshold or a missing session.
`reviewed-replan` (`resume-delivery`) still starts fresh; `retry-review` still replaces the Reviewer.

## C. Segment review

`segment_review = true | false`. New phases, separate from final review:

```
produce --checkpoint--> segment-review --clean--> produce (next segment)
                              |findings
                              v
                        awaiting-decision (orch) / auto-adjudicate
                              v
                        segment-repair --> segment-review ...
produce --done--> review (final, unchanged) ...
```

- **Segment base.** Fixed through repairs: the tree accepted after the previous segment (or the run
  baseline). When a segment review passes, the base advances to the post-repair tree.
- **Segment acceptance.** The single strict Producer schema gains `segment_outcomes` (the Plan
  segment's planned outcomes) and `remaining_work` on every status; they must be nonempty for a
  checkpoint when `segment_review = true` and empty otherwise (legacy and `general` checkpoints
  unchanged), validated in the engine. The segment Reviewer prompt judges only those
  outcomes against the segment diff, and must not report unfinished later work. Whole-stage
  completeness stays with the final review.
- **Segment repair.** The Producer receives accepted findings and returns a new status
  `segment-repaired` with per-finding outcomes (`fixed` / `not-fixed` + rationale). Only targeted
  checks run; whole-stage `delivery_checks` still run only after `done`.
- **Final review.** Unchanged: whole diff from the original baseline, then the existing cycle.
- **Recovery.** A Producer or Reviewer execution failure persists the phase it failed in
  (`return_phase`). Automatic recovery, `retry-producer` and `retry-review` restore that phase
  instead of hard-coded `produce`/`review`.

## D. Budget

- `max_reviews` stays the run-wide ceiling; global numbering keeps IDs `R<n>-…`, budget and retry
  eligibility. Demotion ("after the first review only blockers/regressions") uses a scope-local
  attempt counter that resets for each segment and for the final review.
- New `max_segment_reviews` (automatic reviews per segment) and `final_review_reserve`. A segment
  review is skipped, and the skip reported, when the remaining run budget would fall below the
  reserve.
- Exhausting `max_segment_reviews` with accepted findings open escalates to Orch. An Orch
  `accepted` decision at that point authorizes exactly one more repair and one re-review of that
  segment, only while the remaining run budget exceeds `final_review_reserve`; otherwise `decide`
  rejects `accepted` until the user raises the budget or waives the reserve. If findings remain,
  it escalates again. No separate hard-coded round rule.
- Validation, not a conditional template: with `segment_review = true`, require
  `max_reviews >= max_segment_reviews + final_review_reserve`.

## E. Automatic adjudication

`adjudication = "auto" | "orch"`. `auto` is explicit delegation recorded at `start`
(`--adjudication auto`), bounded by the run's request, artifact ownership and recorded decisions.

Order of evaluation for each raw finding, before demotion or minor handling:

1. **Escalate** only when the Reviewer sets required boolean `needs_user_decision = true`. The
   schema is strict, so the flag cannot be omitted; the Reviewer prompt defines it as "the fix
   changes product behavior, requested scope, technical direction or an authoritative document,
   or the authority to decide is missing". Clear compliance or security fixes within scope are
   ordinary findings.
2. Existing demotion (no evidence; after the first review only blockers/regressions).
3. Any other `blocker`/`major` (every category, including `authoritative-conflict` and `risk`)
   -> `accepted` (rule name recorded).
4. `minor` -> `note-only`, priority `low`.
5. A `not-fixed` outcome is sent to the Reviewer at the next review; if the Reviewer keeps it open,
   escalate.

Any escalated finding pauses the whole round at `awaiting-decision` (no partial execution); Orch
decides with the existing `decide`. A run with an auto-escalated finding never ends
`independently-passed` until Orch has decided it.

Provenance: `finding.history` records `by = "auto" | "orch"` and the rule; `status` finding views
show them; backlog rationale is prefixed `[auto:<rule>]` without changing the backlog format.
Aggregate counts in the completion report are deferred.

`orch` remains the template default. The Producer never adjudicates.

## F. Compatibility

- Missing new keys mean legacy behavior: `checkpoint_session = "fresh"`, `segment_review = false`,
  `adjudication = "orch"`, scalar threshold for both roles. Existing configs need no edits.
- Saved run states are normalized on load with the same legacy values; a run keeps its settings.
- The config renderer gains valid TOML table serialization for `rotate_at_tokens`, with a
  round-trip test.
- New template values: `rotate_at_tokens = { producer = 250000, reviewer = 400000 }`,
  `checkpoint_session = "resume"`, `segment_review = false`, `max_segment_reviews = 3`,
  `final_review_reserve = 2`, `adjudication = "orch"`, `max_reviews = 5` (users enabling segment
  review raise it, e.g. 12).

## Tests

Per transition: checkpoint resume vs fresh; segment clean pass advances base; segment findings ->
repair -> re-review; segment budget exhaustion escalates; reserve skip; auto rules 1–5 incl.
escalation before demotion; paused round with mixed findings; legacy config and legacy saved state;
TOML round-trip; provenance in status, finding history and backlog.

Also: recovery restores `segment-review`/`segment-repair`; scope-local demotion resets; Orch
acceptance after cap exhaustion allows exactly one repair/re-review.

