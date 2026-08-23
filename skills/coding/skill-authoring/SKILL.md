---
name: skill-authoring
description: "Create, review, update, or simplify one reusable agent Skill in this repository. Use when the user asks to add a Skill, revise SKILL.md behavior or discovery metadata, reorganize Skill resources, or remove unnecessary Skill complexity. Do not use for executing the domain workflow described by a Skill or for general application coding."
---

# Skill Authoring

Create the smallest reliable Skill that captures one repeatable workflow. Follow
the repository `AGENTS.md` and the target collection's `README.md`.

## Scope

This Skill owns changes inside one Skill folder and its entry in the collection
`README.md`. It may create or modify:

- `SKILL.md` for the always-needed contract and procedure;
- `references/` for optional guidance loaded only when needed;
- `assets/` for templates or reusable output material;
- `scripts/` for deterministic operations worth automating;
- `agents/` only when a bounded subtask genuinely needs isolated context or a
  distinct role.

Do not redesign adjacent Skills, deployment infrastructure, or repository-wide
guidance unless the current request explicitly includes them.

## Inputs

Resolve these before editing:

1. the target user and concrete task;
2. phrases or situations that should trigger the Skill;
3. expected output and stopping point;
4. important exclusions or neighboring Skill boundaries;
5. the owning collection and target folder.

Ask only when a missing answer would change ownership or observable behavior.
Otherwise, state the smallest reasonable assumption and proceed.

## Procedure

1. Read `AGENTS.md`, the collection `README.md`, and the nearest related
   `SKILL.md`. Search for responsibility overlap before creating a folder.
2. State one falsifiable design claim, such as: "this workflow needs one
   `SKILL.md` and no supporting resource." Choose one cheap check that could
   disprove it.
3. Define one responsibility, its trigger boundary, output, and stop condition.
   Prefer updating an existing owner when a new Skill would overlap it.
4. Write concise frontmatter. The `name` must be lowercase kebab-case and match
   the folder. The `description` must say what the Skill does, when to use it,
   and any exclusion needed to prevent false activation.
5. Put only always-needed decisions and steps in `SKILL.md`. Add a supporting
   resource only when it reduces the core file or provides executable value.
6. Update the collection capability map when the public Skill set or behavior
   changed.
7. Inventory active project Markdown and YAML files. Check the changed Skill,
   collection map, deployment documentation, and adjacent Skills for conflicting
   ownership, repeated rules, stale names, and broken paths. Fix mechanical
   conflicts now; ask only when ownership requires a user decision.
8. Validate the changed files and report scope, design choices, checks run, and
   remaining uncertainty. Stop without executing the new domain workflow.

## Lean test

Before adding any section, file, agent, or script, ask:

- Does the Skill fail a current stated use case without it?
- Is this information always needed, or can it load progressively?
- Is deterministic automation safer or substantially cheaper than instructions?
- Does an existing Skill or repository document already own this rule?

If the answer does not justify the addition, omit it. Do not encode speculative
future workflows.

## Validation

At minimum, verify:

- the folder and frontmatter `name` match;
- `description` contains concrete discovery language and boundaries;
- referenced relative paths exist and use forward slashes;
- headings follow repository Markdown style;
- the procedure has an observable output and stopping point;
- no new content duplicates or contradicts an adjacent Skill;
- the Skill is explicitly mapped in the deployment config when it should be
   available machine-wide.

Use the narrowest available parser, test, or deployment list command. For an
active `coding/` Skill, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly
```