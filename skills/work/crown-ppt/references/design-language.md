# Crown Executive Evidence Design Language

## Purpose

Use this system for content-heavy project updates, case studies, tool explanations, status reviews, and product introductions. It extends the supplied Crown Light template without redrawing its brand elements.

## Narrative model

Build each content slide in this order:

1. **Assertion:** state the conclusion in the title.
2. **Evidence:** show the minimum facts needed to support it.
3. **Implication:** explain why the evidence matters.
4. **Action:** show a decision, owner, or next step only when the audience must act.

Use one primary assertion per slide. Split the slide when two claims require separate evidence.

## Visual character

- Keep the white, restrained, industrial visual system.
- Preserve the orange top rule and authentic footer from the selected layout.
- Use Crown orange to guide attention, not as a large decorative surface.
- Prefer square corners, crisp rules, aligned columns, and deliberate negative space.
- Avoid generic rounded-card dashboards, gradients, shadows, and decorative stock imagery.
- Treat the template photography as brand context; use new imagery only when it is evidence.

## Typography

Use the detailed rules in [font-policy.md](font-policy.md).

- Use `Amasis MT Pro Medium` for covers, section dividers, and short one-line content titles.
- Use `Aptos Semibold` for long, technical, or identifier-heavy titles.
- Use `Aptos` for body text, labels, and tables.
- Use `Consolas` for code and logs.
- Use `Arial` only as the compatibility fallback for Latin text.
- Use `Microsoft YaHei` for Simplified Chinese when the Latin family cannot supply the glyphs.

Apply Amasis to a content-page title only when the title fits on one line at the intended size. Do not condense, stretch, or reduce it merely to force a fit.

## Type scale

| Role | Preferred size | Minimum | Notes |
|---|---:|---:|---|
| Cover title | 36-44 pt | 34 pt | Amasis Medium or Bold |
| Section title | 34-40 pt | 32 pt | Short phrase only |
| Content assertion | 28-32 pt | 26 pt | One line preferred |
| Key metric | 30-42 pt | 28 pt | Use sparingly |
| Body | 17-20 pt | 16 pt | Use sentence fragments where possible |
| Table body | 13-16 pt | 12 pt | Split the table before going smaller |
| Caption/source | 10-12 pt | 9 pt | Never use for primary evidence |
| Code/log | 13-16 pt | 12 pt | Crop to relevant lines |

## Color tokens

| Token | Hex | Use |
|---|---:|---|
| Crown orange | `#FD9827` | Primary emphasis, active flow, top rule |
| Secondary orange | `#F27E22` | Secondary emphasis |
| Dark orange | `#E0571D` | Limited warning or escalation emphasis |
| Primary text | `#000000` | Titles and essential text |
| Secondary text | `#333333` | Body and supporting labels |
| Brand gray | `#515151` | Icons and restrained emphasis |
| Muted gray | `#888888` | Footer-like metadata |
| Rule gray | `#C2C2C2` | Lines, table rules, inactive states |
| Light gray | `#EEEEEE` | Subtle grouping bands |

Use pale orange fills only for one selected row, status, or action band. Never color every cell or card.

## Grid and spacing

- Align all new content to the inherited title and content placeholder boundaries.
- Use a consistent 8 pt spacing rhythm where the layout permits it.
- Keep at least 18 pt between distinct information groups.
- Keep generated content clear of the footer and page-number region.
- Use a maximum of three main columns.
- Make unequal columns purposeful: evidence/detail receives more width; implication/action receives less.

## Content patterns

### Project status

Use an assertion title, three to five comparable workstream rows, one status vocabulary, and a compact decision or next-step region. Show trend only when historical evidence exists.

### Case study

Use `Context -> Intervention -> Evidence -> Result`. Use the product image or screenshot as evidence, not decoration. Keep the result visually dominant.

### Tool explanation

Use `Input -> Logic -> Output -> Operational value`. Combine a small native process diagram with one real screenshot or code extract.

### Incident or outage evidence

Compress repeated wording into common categories. Show incidents in a native table, then isolate the recurring pattern, operational implication, and owner action.

### Product introduction

Use `Problem -> Capability -> How it works -> Proof -> Adoption`. Prefer one strong product visual and a few annotated callouts over a feature list.

## Tables

- Use native PowerPoint tables.
- Use a short noun phrase for each column header.
- Keep row height consistent unless one exception must be explained.
- Use thin neutral rules and one orange header or emphasis element.
- Highlight only the row or cell that changes the conclusion.
- Move full source wording to notes or an appendix.

## Diagrams and icons

- Use native shapes and connectors for systems, flows, ownership, and state changes.
- Use orthogonal connectors where practical and avoid decorative crossing lines.
- Use monochrome SVG icons from the approved local cache for concepts that cannot be represented cleanly with a basic PowerPoint shape.
- Keep icon style, optical size, and stroke weight consistent within a slide.

## Animation

- Use no animation by default.
- Add simple appear, fade, or wipe effects only to explain a sequence, build, or state transition.
- Animate logical groups, not individual words or decorative objects.
- Keep the final slide understandable when printed or exported to PDF.

