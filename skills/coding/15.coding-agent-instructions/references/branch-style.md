# Branch Policy Guidance

Infer and audit only approved project policy. Never turn a few historical
branch names into a rule. This guidance is independent of programming language
and applies to any Git repository.

## Evidence Precedence

Use the first applicable source in this order:

1. Explicit user direction for the current task.
2. `AGENTS.md` and governing branching or release documentation.
3. Verified CI or release tasks and scripts.
4. Protected-branch and default-branch settings when observable.
5. Consistent current branches as clues, never authority.
6. A default profile explicitly selected by the user for this repository.
7. Otherwise omit the rule and report the missing policy.

Report contradictions instead of silently choosing a lower-precedence source.

## Read-Only Inspection

Inspect only what is material:

- the current and default branch, remote and tracking refs;
- naming and lifecycle documentation;
- pull-request and merge settings when available;
- release tasks and scripts;
- tags and versioning evidence;
- multi-repository and worktree constraints.

This Skill's inspection is read-only. Do not create, rename, switch, merge,
rebase, push, tag, publish, release, or modify worktrees.

## Repository Topology

Classify topology only when evidence supports it. The following names illustrate
possible policies; they are never defaults:

- A standalone application may approve `feature/<name>`.
- A consumer-driven shared library may approve `<consumer>/<feature>`, such as
  `vehicle-simulator/clothoid`.
- A monorepo may approve `<area>/<feature>`.
- A documentation or content repository may define its own naming vocabulary
  and lifecycle.

For a consumer-driven shared library, the caller or consumer prefix identifies
which project needs the package. Preserve the repository's approved consumer
vocabulary. Check Git ref namespace collisions: if `a/b` exists, Git cannot
also create `a/b/c`. An approved policy may avoid that collision with a hyphen
suffix such as `a/b-c`; do not introduce that form without evidence.

## Placement

Keep only a short naming or lifecycle trigger rule in `AGENTS.md`. Route the
full merge, rebase, release, hotfix, version, and tag procedure to an existing
`docs/development/branching.md` or equivalent. An exact verified release task
may appear with commands and checks; detailed automation stays in its script.

`agent-instructions` does not create branching documentation. Creating or
changing that documentation requires a separate user request and is outside
this Skill.

## Publishing And Coordination

Preserve immutable tags and package versions when project evidence requires
them. Treat branch push, tag creation or push, package publication, and merge as
distinct operations. Do not assume one triggers another without verified
automation or governing documentation.

Record same-name branch coordination across repositories only when approved.
The repository-local `AGENTS.md` remains authoritative for work in that
repository. When documented coordination crosses into another repository,
route agents to that repository's `AGENTS.md` before they edit it.

## Audit Findings

Report rather than resolve semantic decisions about:

- contradictory naming, merge, release, or tag rules;
- stale documentation, tasks, or scripts;
- assumptions that repository evidence does not verify;
- missing branch, lifecycle, release, or cross-repository policy.
