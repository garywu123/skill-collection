# Product Discovery Roadmap

Turn a vague product idea into an approved Product Requirements Document (PRD) and a prioritised feature roadmap — without writing a single line of code.

**Full skill instructions:** [SKILL.md](SKILL.md)

---

## What it does

Acts as a product discovery consultant. Through a structured interview, it helps you:

1. Surface and challenge hidden assumptions in your product idea.
2. Record findings as a **Discovery Notes** document (the evidence trail).
3. Distil the notes into an approved **Product Requirements Document**.
4. Decompose the PRD into a **Feature Roadmap** — small, ordered, independently verifiable features ready for Spec Kit handoff.

The skill never writes code, chooses architecture, or creates implementation tasks. Its job is to make sure everyone agrees on *what* before any agent starts deciding *how*.

### Default output files

| Artefact | Default path |
|----------|-------------|
| Discovery notes | `doc/product-discovery-notes.md` |
| Product requirements | `doc/general-product-requirement.md` |
| Feature roadmap | `doc/feature-roadmap.md` |

---

## When to use

- You have a product idea — a sentence, a paragraph, a napkin sketch — and need to turn it into something a development team (human or AI) can act on.
- You are starting a new project and the requirements are still fuzzy.
- A stakeholder has asked "can we add X?" and you need to decide scope before committing to implementation.

**Position in the overall workflow:**
This is the *first* skill to invoke. See [spec-driven-flow.md](../spec-driven-flow.md) for where the PRD and roadmap feed into downstream skills.

---

## Example

### Scenario

A warehouse manager comes to you with this request:

> "I need a warehouse management system. It should handle receiving, putaway, inventory, picking, cycle counting, replenishment, waves, and reports — oh, and route optimisation for picking."

This is a multi-year programme described in one sentence. You cannot hand it directly to an AI coding agent.

### Step 1 — Invoke the skill

```
/product-discovery-roadmap

I need a warehouse management system. It should handle receiving, putaway,
inventory, picking, cycle counting, replenishment, waves, and reports.
```

### Step 2 — Discovery interview

The skill reads any existing documents first, then asks targeted questions to surface what matters:

```
Who are the primary users — warehouse operators, supervisors, or both?
What does "receiving" mean today — paper, spreadsheet, or an existing system?
What is the single most painful problem you want solved in the first three months?
Are there regulatory or audit requirements for inventory records?
```

You answer; the skill records everything in `doc/product-discovery-notes.md`. It challenges vague terms ("route optimisation — do you mean shortest path, fewest picks, or zone-based?") and flags risks.

### Step 3 — Approve the discovery notes

Before moving on, the skill presents a summary and asks for explicit approval:

```
Discovery summary:
  Core pain: mis-picks and inventory discrepancies from manual spreadsheet process.
  Primary users: 8 warehouse operators + 1 supervisor.
  Phase 1 must-have: Receiving and Putaway (barcode scan, location validation).
  Out of scope for now: route optimisation, wave management.

Approve discovery notes to continue? (yes / edit first)
```

### Step 4 — PRD and Feature Roadmap

After approval the skill writes:

**`doc/general-product-requirement.md`** — scope, users, constraints, success metrics.

**`doc/feature-roadmap.md`** — features in priority order:

| # | Feature | Phase | Depends on |
|---|---------|-------|-----------|
| 1 | Receiving | 1 | — |
| 2 | Putaway | 1 | Receiving |
| 3 | Inventory enquiry | 2 | Putaway |
| 4 | Picking | 2 | Inventory |
| 5 | Cycle counting | 3 | Inventory |
| 6 | Replenishment | 3 | Cycle counting |

Each feature entry includes a one-paragraph description, acceptance criteria, and a risk flag (low / medium / high) that guides whether a Spec Kit `assess` gate is needed.

### Step 5 — Hand off

The approved PRD and roadmap are now inputs for:
- **[bootstrap-agent-guidance](../bootstrap-agent-guidance/README.md)** — to configure your coding agents.
- **Spec Kit specify** — to write the detailed spec for each feature, one at a time.

---

## Templates

- [Discovery notes template](assets/discovery-notes-template.md)
- [Product requirements template](assets/product-requirements-template.md)
- [Feature roadmap template](assets/feature-roadmap-template.md)
