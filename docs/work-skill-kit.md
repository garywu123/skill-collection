# Work Skill Kit — Getting Started

Audience: anyone producing presentations or other workplace communication
artifacts who wants a reviewable design step before an editable deliverable
gets built.

This guide is an onboarding tutorial with one real worked example. The
authoritative Skill list and full input checklist live in
[`skills/work/README.md`](../skills/work/README.md) — read that for full
detail; this page only shows what running the kit actually looks like.

## The flow

```text
content + optional pictures
    |
    v
design mode -> reviewable PNG slide references -> user approval
                                |
                                v
                  implementation mode -> editable Crown PPTX + PNG proof
```

`crown-ppt` runs on Windows with desktop PowerPoint via PowerPoint COM, and
always stops at a review point before producing the final deliverable.

## Real example: a six-slide operations briefing

These two prompts are taken directly from
[`skills/work/README.md`](../skills/work/README.md), which documents the
`crown-ppt` Skill this kit ships today.

### 1. Design mode — propose the visual direction

```text
Use crown-ppt in design mode with the standard font profile.
Create a six-slide conference-room presentation for senior operations leaders.
Use the attached product screenshots on slides 3 and 4. Keep body text at or above
18 pt, use short assertion titles, and return PNG design references for approval.
```

Output: a set of reviewable PNG references — not a final file. Check
composition, density, image crops, contrast, and factual content here. Nothing
is auto-approved.

### 2. Implementation mode — build the approved deck

```text
Use crown-ppt in implementation mode with the approved PNG storyboard and the
standard font profile. Build an editable PPTX from the Crown template, preserve
the approved six-slide composition, and export PNG proofs for every slide.
```

Output: an editable PPTX (text, tables, charts, and connectors stay editable;
supplied photos stay as raster images) plus rendered PNG proofs to confirm the
export matches what was approved.

## What to read next

- Full input checklist (audience, font profile, licensing, accessibility) and
  the review checklist before implementation approval:
  [`skills/work/README.md`](../skills/work/README.md)
- Skill contract and scope: [`crown-ppt/SKILL.md`](../skills/work/crown-ppt/SKILL.md)
- Adding a new Skill to this kit: [`skill-authoring`](../skills/coding/skill-authoring/SKILL.md)
  (shared across collections — it is not duplicated per collection)
