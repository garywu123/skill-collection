# Skill Collection

A personal collection of reusable VS Code Copilot skills for AI-assisted software development. Each skill packages a repeatable workflow — from product discovery through to coding-agent setup — into an invocable instruction set.

---

## Recommended Workflow

If you are starting a new software project with AI agents, the skills in this collection fit together in a specific order. See **[spec-driven-flow.md](spec-driven-flow.md)** for the full end-to-end walkthrough, including a worked example (a Warehouse Management System) that shows which skill to invoke at each stage and what artefacts it produces.

At a glance:

```
Product idea
    └─→ [product-discovery-roadmap]  →  Discovery notes, PRD, Feature Roadmap
            └─→ [bootstrap-agent-guidance]  →  AGENTS.md, CLAUDE.md, Copilot instructions
                    └─→ Spec Kit (specify → plan → tasks → implement)
```

---

## Skills

### Product & Planning

| Skill | When to use | README |
|-------|-------------|--------|
| [product-discovery-roadmap](product-discovery-roadmap/SKILL.md) | You have a vague product idea and need a structured PRD + feature roadmap before writing any code | [Details →](product-discovery-roadmap/README.md) |

### Agent Setup & Governance

| Skill | When to use | README |
|-------|-------------|--------|
| [bootstrap-agent-guidance](bootstrap-agent-guidance/SKILL.md) | You have an approved PRD + roadmap and need to generate `AGENTS.md`, `CLAUDE.md`, or Copilot instructions to govern coding agents | [Details →](bootstrap-agent-guidance/README.md) |

### Development Practice

| Skill | When to use | README |
|-------|-------------|--------|
| [guided-tdd-pairing](guided-tdd-pairing/SKILL.md) | You want to learn by writing the code yourself — the AI coaches you through a TDD red→green loop step by step instead of implementing everything for you | [Details →](guided-tdd-pairing/README.md) |

---

## Repository Structure

```
skill-collection/
├── spec-driven-flow.md              # End-to-end workflow reference (start here)
├── bootstrap-agent-guidance/
│   ├── README.md                    # Usage guide & example
│   ├── SKILL.md                     # Full skill instructions
│   ├── agents/                      # Agent definitions
│   ├── assets/                      # Output templates (AGENTS, CLAUDE, Copilot)
│   ├── references/                  # Artifact contract & tool compatibility
│   └── scripts/                     # Validation scripts
├── product-discovery-roadmap/
│   ├── README.md                    # Usage guide & example
│   ├── SKILL.md                     # Full skill instructions
│   └── assets/                      # Discovery notes, PRD, roadmap templates
└── guided-tdd-pairing/
    ├── README.md                    # Usage guide & example
    └── SKILL.md                     # Full skill instructions
```
