# Section Commits

Use this only when the user's explicit request or a project rule authorizes
commits for the current task; neither this Skill nor a stage Skill grants that
authority. You commit; workers never commit. A section is one bounded run, or a
reviewed Plan's execution segment ending in a checkpoint.

1. Commit only while no worker runs: after a checkpoint, or after a run stops as
   `done`, `failed`, `blocked`, or parked. For a completed stage, commit after
   `close` and any finalization edit, before dependent work starts.
2. Inspect `git status` and the section's diff. Commit only the exact authorized
   paths by pathspec (`git commit -m <message> -- <paths>`), never with
   `git add -A`, so the user's other staged entries, unrelated or untracked
   files, private configuration, and the backlog that `close` appends stay out.
   If a section file also holds unrelated edits, report it instead of
   committing.
3. Write the message from evidence: the task or item, the section, its real
   outcome, such as `checkpoint, not independently reviewed`,
   `independently-passed`, `completed-by-orchestrator`, `failed`, or
   `incomplete`, and the checks that actually ran. A commit never makes a
   section verified or passed.
4. Do not amend, push, reset, check out, rebase, or create empty commits unless
   the user asks. Without a relevant diff, record the outcome in the artifact
   that already owns it or in the next commit message; never create a document
   to force a commit.
5. A failed or incomplete section may get a local recovery commit with that
   truthful outcome. It stops dependent work, not the run's own recovery.
   Committing changes no run state: the original baseline, findings, and spent
   budgets stay authoritative, and the final review still covers earlier
   committed segments.
6. Report each commit's revision (`git rev-parse --short HEAD`). A continuation
   Producer receives only the original request and the latest checkpoint, so an
   execution stage's `start --request` must tell it to read the current
   revision with `git log -1 --format=%h` before more work. A new run's request
   names the actual revision.
