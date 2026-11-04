# Recovery And Delivery Controls

Use these commands only when the run's `next_action` or error calls for them and
the user has authorized the step. Each command refuses what it cannot do
safely; report a refusal instead of working around it. Never edit run state or
launch workers by hand.

## Failed Execution

- When `automatic_recovery_available` is true, call `next` once. Do not call
  `next` repeatedly to obtain more retries.
- After a Producer execution failure, such as a timeout or a transient
  connection or rate-limit error, fix the external cause, then with the user's
  authorization run `cross-agent retry-producer --run <id>` and
  `next --stream`.
- After a Reviewer execution failure, fix the cause, then with the user's
  authorization run `cross-agent retry-review --run <id>` and `next --stream`.
- Validation and write-guard failures cannot be retried. Configuration or
  discovery failures need their cause fixed first.
- When `status --run` reports `orphan_worker`, an earlier `next` was killed while
  its worker kept running. Report it and stop that process tree before calling
  `next` again.

## External Work-Tree Change

`error.kind = "work-tree-changed"` lists the `changed_files` that changed while
the read-only Reviewer ran; that review was discarded without spending budget.
Report the files. Do not revert them yourself: the change's owner or the user
restores them within their own write boundary. When the change belongs to the
run and is in scope, keep it with
`cross-agent adopt-external --run <id> --reason "<why it is kept>"`, which adds
it to the reviewed diff. After the files are restored or adopted, use
`retry-review`.

## Blockers

When the user explicitly resolves a Producer-reported blocker and asks to
continue, pass the decision with
`cross-agent answer --run <id> --text "<user decision>"`, then `next --stream`.
Other failed or blocked runs stay open until the user decides; close them with
`--abandon` only when the user abandons the work.

## Segment Review

With `segment_review = true`, a Delivery checkpoint enters `segment-review`: the
Reviewer judges only that segment's planned outcomes. Adjudicate as usual;
accepted findings go to `segment-repair`. A passed segment review is not a
whole-stage pass, and the final review still covers the whole run from its
original baseline.

At the segment review cap, `accepted` buys exactly one more repair and review,
and `decide` refuses it when that would consume the final-review reserve. Only
on the user's explicit approval pass `decide --max-reviews <larger>` or
`--waive-reserve`. Report any `segment_review_skipped` event; its open findings
reach the final review.

## Park And Resume Delivery

When the user redirects a failed Delivery to replanning:

1. Run `cross-agent park --run <id> --reason "<user-requested replan>"`. It
   releases the artifact while keeping history, baseline, and budgets.
2. Update and review the same Plan in a separate `feature-plan` run.
3. After that run is `independently-passed`, run
   `cross-agent resume-delivery --run <delivery-id> --plan-run <plan-id> --request "<reviewed segment handoff>"`,
   close the Plan run, then call Delivery `next --stream`.

Pass `--max-diff-kb <larger>` only when an earlier diff-size guard failed and
the user approves; it raises the review input capacity and never omits
changes. Never park a run to bypass a worker or review gate.
