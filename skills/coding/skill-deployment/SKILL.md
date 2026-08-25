---
name: skill-deployment
description: Repository-local guidance for deploying this Skill Collection's explicitly configured skills to GitHub Copilot, Claude Code, and Codex/Agents, while pruning only the collection's recorded or explicitly retired skills. Use only while working in this Skill Collection when the user asks to deploy, synchronize, preview, or clean its machine-wide skills. Do not deploy this Skill itself, use it from another workspace, or use it for arbitrary skill directories.
---

# Skill Deployment

Synchronize the machine-wide Skills owned by this repository. This is a
workspace-only Skill: `deploy-skills.json` must never map
`skills/coding/skill-deployment`, and this folder must not appear in any global
or reusable project preset. `Install-WorkspaceSkill.ps1` copies this Skill into
the current repository's `.github/skills/`, `.claude/skills/`, and
`.agents/skills/` discovery paths. This Skill owns the collection's deployment
configuration and deployed ownership manifest; it does not decide which
platform-provided or third-party Skills should be removed.

## Scope

Use only from this Skill Collection repository, identified by
`scripts/deploy-skill/Deploy-Skills.ps1` and `scripts/deploy-skill/deploy-skills.json`.
For a single project's local Skills, use `scripts/Install-Skills.ps1` instead.

Before relying on slash-command discovery in a platform, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Install-WorkspaceSkill.ps1
```

The deploy script uses these target directories unless its local path overrides
say otherwise:

| Platform | Default target |
|---|---|
| GitHub Copilot | `~/.copilot/skills` |
| Claude Code | `~/.claude/skills` |
| Codex / Agents | `~/.agents/skills` |

## Procedure

1. Read `scripts/deploy-skill/deploy-skills.json`, then run the script with
   `-ListOnly`. Report the active Skills, target directories, and any entries
   marked `managed stale skill`.
2. Confirm each stale entry is either in the target's
   `.skill-collection-deployment.json` or explicitly listed in
   `retiredSkillNames`. Do not infer ownership from a matching name, content,
   or platform directory.
3. If an intended active Skill is missing from `skills`, add its explicit
   `source` and frontmatter `name`. If an old collection Skill needs an initial
   cleanup, add only its verified name to `retiredSkillNames`.
4. Run `Deploy-Skills.ps1` after the preview is accepted. It replaces active
   managed Skill folders, removes only verified stale managed folders, and
   writes the target manifest.
5. Re-run `-ListOnly` and verify no unintended stale entries remain. Report
   retained third-party or platform Skill directories separately.

Use `-Target copilot`, `-Target claude`, or `-Target agents` when the user
requests one platform only. Do not use a blanket deletion command, or delete a
Skill that is not recorded by the manifest or explicit retirement list.

## Validation

Run this preview before every write:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly
```

After deployment, run the same preview again. The result must show the desired
active set and no unexpected `managed stale skill` entries. Stop after reporting
the verification result.