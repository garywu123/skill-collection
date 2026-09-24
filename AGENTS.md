# Skill Collection Agent Instructions

## Purpose

This repository designs, maintains, and deploys reusable agent Skills. Treat it
as a Skill authoring workspace, not as an application repository. Keep this
file as routing and repository-wide guidance; put task procedures in the
applicable `SKILL.md` and detailed material in that Skill's resources.

## Precedence

Resolve conflicts in this order: the current explicit user instruction,
applicable repository and collection guidance, the target `SKILL.md`, then
verified repository evidence. Report a conflict instead of promoting observed
behavior into intended behavior.

## Repository Map

- `README.md` is the short human-facing overview and routes into `docs/` and
  each collection's `README.md`.
- `docs/` contains onboarding tutorials, not capability sources of truth.
- `skills/coding/` contains software-delivery Skills. Read its `README.md`
  before changing those workflows.
- `skills/work/` contains workplace-artifact Skills. Read its `README.md`
  before changing those workflows.
- `scripts/` contains repository maintenance and deployment tools.
- `_obsolete/` is historical evidence. Do not deploy, modify, or restore it
  unless the user explicitly requests that scope.

## Boundaries

- Do not create, amend, or push commits unless the user explicitly requests it.
  When requested, include only task-scoped changes after applicable checks.
- Preserve unrelated user changes and untracked files.
- Keep machine-specific paths, credentials, tokens, and private configuration
  out of version control and disclosure.

## Working Rules

1. Identify the target collection and read its `README.md`.
2. Read the target `SKILL.md` before editing it. Load `references/`, `assets/`,
   or `scripts/` only when the current task needs them.
3. Search for an existing or adjacent Skill before creating a new one. Prefer
   extending clear ownership over introducing overlap.
4. Make the smallest change that satisfies the stated use case. Avoid
   speculative framework or workflow design.
5. Run the narrowest relevant validation. If it cannot run, report the reason
   and remaining risk.

## Collection Maintenance

For deployment, synchronization, preview, or cleanup, first read
`skills/coding/skill-deployment/SKILL.md`. Install that repository-local Skill
only through `scripts/deploy-skill/Install-WorkspaceSkill.ps1`; it writes the
project discovery copies and must never be installed under the user's home as
a machine-wide Skill.

## Skill Design

- Give one Skill one clear, repeatable, on-demand responsibility.
- An ordered collection may name a folder `<ordinal>.<skill-name>`; otherwise
  use `<skill-name>`. Frontmatter `name` matches the logical name after removing
  an ordinal prefix, and `description` states triggers and exclusions.
- Keep always-needed decisions and steps in `SKILL.md`. Put optional guidance
  in `references/`, reusable material in `assets/`, and deterministic
  automation in `scripts/`.
- Add a resource only when the workflow uses it. Do not prebuild agents,
  phases, state machines, templates, or validation for hypothetical needs.
- Keep Skills independently invocable. Do not let one Skill silently invoke
  another or infer authorization from repository state.
- Update the collection `README.md` when public capability changes.

## Markdown Style

- Use one level-one title and ATX headings without skipping levels.
- Separate paragraphs, lists, tables, and fenced code with blank lines; add a
  language identifier to fenced code blocks.
- Use backticks for paths, commands, fields, and literal statuses.
- Use relative links with descriptive text. Use tables only for real tabular
  comparisons; avoid deep nesting, repetition, and filler.
- Write executable agent instructions in concise English. Human-facing guides
  may use the audience's language.

## Deployment

`scripts/deploy-skill/Deploy-Skills.ps1` deploys only mappings in
`scripts/deploy-skill/deploy-skills.json` plus public Git Skills configured by
`externalSkillConfigPath`. External repositories are cached under the ignored
`scripts/external-skills/cache/`. Run it with `-ListOnly` to inspect mappings
and cached revisions without cloning, pulling, or writing targets. A future
collection is not deployed until the script is explicitly extended and
validated for it.

## Reporting

- Lead with the result and report what changed, important caveats, and checks
  actually run.
- State unresolved conflicts, omitted verification, and remaining risk.
