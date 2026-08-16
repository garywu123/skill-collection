---
name: crown-ppt
description: Create, revise, inspect, and visually validate editable Crown-branded PowerPoint presentations from the bundled Crown template on Windows using Microsoft PowerPoint COM. Use for project updates, case studies, tool explanations, project status, product introductions, and other content-heavy Crown decks. Do not use for HTML slide decks, image-only slides, or unattended server-side Office automation.
---

# Crown PowerPoint

Create editable PowerPoint decks that preserve the Crown master, layouts, brand chrome, and narrative discipline.

## Required environment

- Run on Windows with desktop Microsoft PowerPoint installed.
- Use the bundled template at `assets/Template - Crown Branded Powerpoint (MGT20013) Light Version.pptx`.
- Treat the source template as read-only. Open a copy or save to a new output path.
- Run `scripts/Test-CrownPowerPointEnvironment.ps1` before the first COM operation in a session.

## Core workflow

1. Read [the design language](references/design-language.md).
2. Read [the layout catalog](references/layout-catalog.md) and map each slide to one layout.
3. Read [the font policy](references/font-policy.md) when the deck contains dense text, tables, code, or multilingual content.
4. Read [the icon policy](references/icon-policy.md) before sourcing a new icon.
5. Read [the COM automation contract](references/com-automation.md) before running or changing PowerShell automation.
6. Convert the source content into an assertion-led story. Give every content slide one claim and one evidence structure.
7. Create slides from existing Crown `CustomLayout` objects. Do not redraw the master, footer, logo, page number, photo rails, or top rule.
8. Build text, tables, charts, diagrams, connectors, and callouts as native PowerPoint objects. Keep all presentation text editable.
9. Use cached, approved SVG icons for semantic icons. Use native PowerPoint shapes for simple arrows, lines, checks, and process geometry.
10. Export every generated slide to PNG with `scripts/Export-CrownPresentation.ps1` and inspect clipping, overlap, contrast, hierarchy, and footer clearance.
11. Repair the editable objects, re-export, and stop only when the PPTX and rendered slides agree.

## Content rules

- Use the model `Assertion -> Evidence -> Implication -> Action`.
- Keep no more than three visible text levels.
- Prefer restructuring or splitting content over shrinking text.
- Use tables for comparable records, diagrams for relationships, and screenshots only when the visual itself is evidence.
- Put full logs, long code, and detailed incident histories in an appendix or speaker notes.
- Use animation only when it explains sequence or change. Keep it subtle and native to PowerPoint.

## Editable-object contract

- Use placeholders or text boxes for titles and body text.
- Use `Shapes.AddTable` for tables.
- Use `Shapes.AddShape` and `Shapes.AddConnector` for diagrams.
- Use native Office charts for data-driven charts.
- Use text boxes with the code font for code and logs.
- Keep photos and product screenshots as images, but never bake labels or explanatory text into them.
- Give generated objects stable names and semantic alternative text or tags.

## Refreshing template references

Refresh the machine-readable profile when the source template changes:

```powershell
./scripts/Inspect-CrownTemplate.ps1
./scripts/Export-CrownLayoutPreviews.ps1 -LabelPlaceholders
```

Compare the refreshed outputs with [the design language](references/design-language.md) and [the layout catalog](references/layout-catalog.md), then update only rules contradicted by the new evidence. Existing SVG exports may be inspected as additional visual evidence when present, but SVG conversion is not a runtime dependency.

## Boundaries

- Do not call HTML or web-slide conversion workflows.
- Do not fetch arbitrary icons during deck generation.
- Do not bundle or redistribute commercial font files.
- Do not silently substitute a missing display font.
- Do not automate PowerPoint COM from a shared server, service account, or parallel worker pool.
- Do not save changes over the bundled template.
