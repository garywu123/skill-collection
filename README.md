# Skill Collection

Reusable [Agent Skills](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
for GitHub Copilot, Claude Code, and Codex/Agents — designed, tested, and
deployed from this one repository instead of copy-pasted between projects.

This repository is a Skill *authoring workspace*, not an application. See
[AGENTS.md](AGENTS.md) for the canonical contributor rules; this file is the
human-facing overview.

## What's here

| Collection | Audience | Docs |
|---|---|---|
| [`skills/coding/`](skills/coding/README.md) | Solo devs, small teams, and AI-led delivery | [Coding Skill Kit guide](docs/coding-skill-kit.md) |
| [`skills/work/`](skills/work/README.md) | Presentation and workplace communication artifacts | [Work Skill Kit guide](docs/work-skill-kit.md) |

Each collection owns its own `README.md` as the source of truth for its
Skill list and capabilities. The guides under [`docs/`](docs/) are onboarding
tutorials that walk through one real, end-to-end example per collection —
they link back to the collection `README.md` rather than duplicating it.

<details>
<summary>Full repository structure</summary>

```text
skill-collection/
├── AGENTS.md                  # canonical contributor rules (read this first)
├── CLAUDE.md                  # thin adapter -> AGENTS.md
├── .github/copilot-instructions.md   # thin adapter -> AGENTS.md
├── docs/
│   ├── coding-skill-kit.md    # onboarding guide + real example (coding collection)
│   └── work-skill-kit.md      # onboarding guide + real example (work collection)
├── scripts/
│   ├── Install-Skills.ps1     # copy this repo's Skills into one target project
│   └── deploy-skill/
│       ├── Deploy-Skills.ps1  # sync configured Skills machine-wide
│       └── deploy-skills.json # explicit local + external Skill mappings
└── skills/
    ├── coding/                # product-brief -> ... -> feature-delivery, plus utilities
    └── work/                  # crown-ppt
```

</details>

## Quick start

**Use these Skills in another project** (local, project-scoped):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/Install-Skills.ps1
```

**Deploy them machine-wide** for GitHub Copilot, Claude Code, and Codex/Agents
(read [`skill-deployment`](skills/coding/skill-deployment/SKILL.md) first):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly
```

Drop `-ListOnly` once the preview looks right.

## Adding or changing a Skill

Read [`skill-authoring`](skills/coding/skill-authoring/SKILL.md) before
touching a Skill folder. It defines the smallest-reliable-Skill process: one
responsibility, concrete trigger language in the frontmatter `description`,
and a check for overlap with an existing Skill before creating a new folder.

## Repository rules

[AGENTS.md](AGENTS.md) is the single authoritative instruction file. `CLAUDE.md`
and `.github/copilot-instructions.md` are thin adapters that point back to it —
edit `AGENTS.md`, not the adapters, when a rule changes.
