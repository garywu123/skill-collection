# Skill Collection Agent Instructions

## Purpose

This repository designs, maintains, and deploys reusable agent Skills. Treat it
as a Skill authoring workspace, not as an application repository.

Keep this file as navigation and repository-wide guidance. Put task procedures
in the relevant `SKILL.md` and detailed material in that Skill's resources.

## Repository map

- `coding/` contains Skills for programming and software delivery work. Read
  `coding/README.md` before changing its workflows.
- `scripts/` contains repository maintenance and deployment tools.
- A future top-level collection may serve another domain, such as presentation
  or content work. Give each collection its own `README.md`; do not assume the
  `coding/` workflow applies outside `coding/`.
- `_obsolete/` directories are retained as historical evidence. Do not deploy,
  modify, or restore their contents unless the user explicitly requests it.

## Working rules

1. Identify the target collection and read its `README.md`.
2. Read the target `SKILL.md` before editing it. Load `references/`, `assets/`,
   or `scripts/` only when the current task needs them.
3. Search for an existing or adjacent Skill before creating a new one. Prefer
   extending clear ownership over introducing overlapping capabilities.
4. Make the smallest change that satisfies the stated use case. Preserve
   unrelated user changes and avoid speculative framework or workflow design.
5. Keep machine-specific paths, credentials, tokens, and private configuration
   out of version control.
6. Run the narrowest relevant validation. If validation cannot run, report the
   reason and remaining risk.

## Skill design

- Give one Skill one clear, repeatable, on-demand responsibility.
- Make frontmatter `name` match the folder name. Write a concrete `description`
  that states when to use the Skill and important exclusions.
- Keep the always-needed contract and procedure in `SKILL.md`. Move optional
  detail and edge cases to `references/`, reusable output material to `assets/`,
  and deterministic automation to `scripts/`.
- Add a resource only when the workflow uses it. Do not prebuild agents,
  phases, state machines, templates, or validation machinery for hypothetical
  future needs.
- Keep Skills independently invocable. Do not make one Skill silently invoke
  another Skill or infer authorization from repository state.
- Update the collection `README.md` when adding, removing, or materially
  changing a Skill's public capability.

## Markdown style

- Use one level-one title and ATX headings without skipping heading levels.
- Separate paragraphs, lists, tables, and fenced code blocks with blank lines.
- Add a language identifier to fenced code blocks.
- Use backticks for paths, commands, field names, and literal status values.
- Use relative links for repository files and descriptive link text.
- Use tables only for genuinely tabular comparisons. Avoid deeply nested lists,
  repeated explanations, and filler introductions.
- Write executable agent instructions in concise English. Human-facing guides
  may use the language appropriate for their audience.

## Deployment

`scripts/deploy-skill/Deploy-Skills.ps1` deploys only the explicit mappings in the local,
gitignored `scripts/deploy-skills.json` to configured GitHub Copilot, Claude
Code, and Codex/Agents locations. Run it with `-ListOnly` to inspect the mapping
without writing to those locations.
Do not assume a future top-level collection is deployed until the script is
explicitly extended and validated for that collection.
