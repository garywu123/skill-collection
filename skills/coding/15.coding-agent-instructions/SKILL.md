---
name: coding-agent-instructions
description: Create, refresh, audit, or assess the instruction impact of changes to a software project's canonical AGENTS.md and any genuinely scope-specific nested AGENTS.md files, and install and version-check the bundled read-only documentation link checker, scripts/Test-DocLinks.ps1. Invoke explicitly, by name, to establish or continuously calibrate repository guidance after project setup, structural or tooling changes, recurring agent failures, or delivery milestones, or to decide whether a change to architecture, testing strategy, commands, project structure, or document routes requires an instruction update. Do not use it for a repository with no code; do not create product direction, feature plans, application code, reports, tool-specific adapters, or code-style rules owned by the code-style files.
disable-model-invocation: false
---

# Coding Agent Instructions

Give every agent working in a software repository one short, evidence-based
operating contract. Maintain `AGENTS.md` as the only default instruction file.
Add a nested `AGENTS.md` only when a subtree has materially different commands,
boundaries, or workflow; never duplicate inherited rules.

This Skill covers repositories that contain code, including one that also holds
documentation. A repository with no code belongs to its own collection's agent
instruction Skill; report that and stop instead of writing files for it.

Route to applicable project documents instead of copying them. Product Briefs,
Feature Maps, and other lifecycle documents are routes only when the repository
actually uses them. This Skill creates agent instructions, not project content.

## Intent

Infer the intent from the request once the Skill has been invoked.

- `write`: create or continuously calibrate `AGENTS.md`. This is the default.
- `audit`: report stale routes, unverified commands, duplicated rules, missing
  boundaries, and candidate changes without modifying a file.
- `assess`: after a named change to architecture, testing strategy, commands,
  project structure, or instruction routes, decide its impact on each
  applicable instruction file, as described below.

## Instruction-Impact Assessment

Assessment is required after such a change, not an `AGENTS.md` edit after
every Feature. Read the change, its owning documents, and the root and nested
`AGENTS.md` files whose scope it touches, then record one result per file:

- `updated`: a mechanical correction caused by the change, such as a moved
  route or a renamed path, or a command whose new syntax is verified, applied
  with the evidence cited;
- `unchanged`: assessed, with the reason no instruction depends on the change;
- `unresolved`: with the reason and the decision or owner needed, such as a new
  boundary, convention, or other semantic policy, or a command that is not yet
  verified.

Apply only `updated` changes, and none when the request asks for a report only.
Escalate every semantic policy as `unresolved` instead of writing it, whatever
model or worker performs the assessment. A code-style route change stays with
`code-style`.

## Output

This Skill may create, refresh, or audit only:

- the repository root `AGENTS.md`;
- a nested `AGENTS.md` when a user-requested or verified subtree difference
  cannot be expressed by the root file or an existing project document;
- `scripts/Test-DocLinks.ps1` in the project: copy
  [the read-only link checker](scripts/Test-DocLinks.ps1) from this Skill when
  it is missing, creating `scripts/` if needed. Never overwrite an existing
  file.

It does not create tool-specific adapters or a state, history, approval, or
review file. It may read project and code-quality configuration as evidence but
must not modify that configuration.

Code style always lives in `docs/code-style.md`, which lists any project style
files, owned by the `code-style` Skill. Route `AGENTS.md` to that file and
write no code-style rule here. When the file does not exist yet, omit the route
and report that `code-style` should run. The code-style route and the
Working-rules line "Before changing code, read the matching language section of
the applicable code-style file and follow it." are owned by `code-style`: keep
both, and do not count them as code-style rules in the consistency check.

Create or update `AGENTS.md` from [the template](assets/agents.template.md).
When the user explicitly selects the Feature workflow for this project, use
[the optional profile](assets/feature-workflow.profile.md). Replace its app
name and preserve approved naming differences; include only supported routes.
Selection approves the profile's branch/local-commit policy for subsequently
authorized work, not implementation scope, push, merge, or history rewriting.
Reconcile its commit authorization with the template's default boundary rather
than keeping both. Without selection, omit it and preserve existing policy.
Keep model/effort and runtime parameters in cross-agent configuration; keep
step acceptance/results in the Plan and procedures in their owning Skills.
At 80 source lines, review duplicated explanations, nonexistent routes, empty
sections, and rules better owned by a linked document or nested `AGENTS.md`.
Treat 100 lines as a strong review threshold, not a validity gate. When a file
must remain longer, keep only decision-relevant content and report why routing
or scoping would make it less reliable.

## Evidence And Rule Promotion

Use evidence in this order:

1. explicit user direction for the current project;
2. applicable governing, project, and task documents;
3. verified automation, configuration, and successful commands;
4. consistent repository behavior as a clue, never authority;
5. otherwise unknown.

Promote a candidate rule into `AGENTS.md` only when it has authoritative
support, applies across multiple tasks in its scope, changes an actionable
decision, and is not owned by another project document or deterministic
control. Never turn a one-off task, current Feature goal, incidental code
pattern, or generic engineering preference into permanent policy.

Automatically correct mechanical drift during `write`: broken routes, renamed
paths, verified command changes, stale names, and exact duplication. A new
boundary, convention, authorization rule, architectural invariant, or other
semantic policy requires explicit user direction or an authoritative project
source. Otherwise report it as a proposal and leave the file unchanged.

## Refresh Triggers

Recommend a refresh after initial project setup; a new subproject, language, or
toolchain; a build, test, generator, CI, release, branch, security, or document
route change; a structural refactor; or a repeated agent failure that may expose
a missing rule. During early development, an audit after roughly three to five
verified Features or at a delivery milestone is useful. Do not refresh after
every Feature Plan, routine Feature, bug fix, dependency update, or internal
refactor when the repository contract did not change.

## Workflow

1. Read repository guidance, the existing applicable `AGENTS.md` files, routed
   governing documents, and only the configuration needed to verify paths,
   commands, checks, and boundaries. When useful and Git history is available,
   inspect structural and tooling changes since the root `AGENTS.md` last
   changed; do not exhaustively scan business code.
2. Confirm from user, document, and repository evidence that the repository
   contains code, packages, or services. When evidence is ambiguous, report the
   gap and do not guess.
3. Detect languages and tooling only far enough to verify instruction content.
   Treat code-quality configuration as read-only evidence and report when
   `code-style` should run.
4. Compare current guidance with the evidence. Classify each finding as keep,
   mechanical update, semantic proposal, removal, or content owned elsewhere.
5. Apply the rule-promotion gate. Preserve human-written rules that remain
   authoritative and reconcile conflicts visibly instead of silently choosing
   from lower-precedence evidence.
6. Route lifecycle documents only when the project maintains them. Do not copy
   their content or reconstruct project state from conversation history. Route
   an existing `docs/review-backlog.md` only with its boundary: agents read or
   search it only when the user asks for a backlog review or names an item ID.
   Never create the backlog or copy its items into `AGENTS.md`.
7. Create a nested `AGENTS.md` only for a real local difference. If the subtree
   inherits root commands and boundaries unchanged, create nothing.
8. Handle the link checker. For `write`, when `scripts/Test-DocLinks.ps1` is
   missing, copy it, run it once from the repository root to verify the
   command, and then add the Commands entry from the template. A reported
   broken link still verifies the command; report the links found. When the
   project has a same-named file, read both version headers with
   `(?m)^\s*Version:\s*(\d+\.\d+\.\d+)\s*$`, compare them as `[version]`, and
   report an older or newer project copy, or a file without a header; never
   replace it. `audit` reports the same comparison without writing.
9. For `write`, update the applicable files. For `audit`, report findings and
   proposals without writing. For `assess`, apply only the `updated` results.
   Then run the consistency check.

When branch naming, merge/rebase, release, hotfix, tag, worktree, or
cross-repository coordination is material, read the
[branch policy guidance](references/branch-style.md).

## Consistency Check

Confirm every routed path exists; every command states its working directory or
scope, trigger, and verified syntax; no code-style rule remains once
`docs/code-style.md` exists; the project copy of `scripts/Test-DocLinks.ps1`
exists or its absence is reported, its version comparison is recorded, and the
Commands entry routes to it; nested files contain only local differences; and no
instruction copies project meaning, task status, implementation detail, or a
rule enforced more reliably elsewhere. Remove stale or redundant content during
`write`. Report conflicts requiring a product, domain, technical, or ownership
decision. Review line count as a signal, never as a substitute for relevance.

## Completion

Report files written or audited, the link-checker copy with its version result,
first-run result, and Commands entry, evidence used, mechanical updates, semantic
proposals left unapplied, removals, content kept in another owner, unverified
statements omitted, unresolved conflicts, and remaining risk. For `assess`,
also report each file's `updated`, `unchanged`, or `unresolved` result with its
reason. Stop without
creating project content, tool adapters, application code, or a separate review
artifact.
