---
name: crown-ppt
description: Implement completed PowerPoint design screenshots or storyboards as editable Crown presentations from the bundled Crown template on Windows using Microsoft PowerPoint COM. Use when the visual design is already approved and the output must be a native PPTX on the template's 960 x 540 point canvas. Do not use for design ideation, image-only decks, HTML slides, or unattended server-side Office automation.
---

# Crown PowerPoint

Turn an approved design screenshot or storyboard and its content into an editable PowerPoint deck that inherits the bundled Crown template.

## Input contract

- Require a completed design screenshot, storyboard, or equivalent slide-by-slide visual specification before authoring.
- Treat supplied text, data, documents, and factual instructions as the content source.
- Treat the approved design as the source for composition, hierarchy, proportions, spacing, and visual rhythm.
- Use sample text visible in a design reference only to understand hierarchy and density. Do not copy it unless the user identifies it as content.
- If the design direction is incomplete or materially ambiguous, stop and request a completed design. This Skill implements designs; it does not create the upstream design concept.

## Required environment

- Run on Windows with desktop Microsoft PowerPoint installed.
- Use Microsoft PowerPoint COM for creation, editing, rendering, and saving.
- Use the bundled template at `designs/Crown Template.pptx`.
- Treat the bundled template as read-only. Create and edit a working copy at the caller-provided output path.
- Run `scripts/Test-CrownPowerPointEnvironment.ps1` before the first COM operation in a session.

## Canvas contract

- Preserve the template `PageSetup`: `960 x 540` points (`13.3333 x 7.5` inches, 16:9).
- Treat points as the authoring units. Pixel dimensions such as `960 x 540`, `1600 x 900`, or `1920 x 1080` describe raster exports only.
- Do not resize the template canvas to fit imported material.
- Normalize geometry imported from another presentation as described in [the COM automation contract](references/com-automation.md).

## Core workflow

1. Inspect all content inputs and every approved design screenshot or storyboard frame.
2. Read [the layout catalog](references/layout-catalog.md) and map each storyboard slide to the closest useful Crown `CustomLayout`. Treat the catalog as guidance, not a rigid content-to-layout rule.
3. Read [the design language](references/design-language.md).
4. Read [the font policy](references/font-policy.md) for font selection, dense content, code, or multilingual text.
5. Read [the icon policy](references/icon-policy.md) before sourcing a new icon.
6. Read [the COM automation contract](references/com-automation.md) before authoring or changing PowerShell automation.
7. Create a working copy of `designs/Crown Template.pptx` at the output path. Never save over the bundled template.
8. Reuse or remove the working copy's example Cover and Sign-Off slides as required by the storyboard, then create remaining slides from existing Crown `CustomLayout` objects.
9. Implement the approved design with inherited placeholders and native PowerPoint objects. Preserve the master, layout, logo, footer, page number, photography, and other brand furniture.
10. When icons are required, obtain suitable open-source SVG icons before COM authoring, cache them under `assets/icons/`, and record source and license information as required by the icon policy.
11. Build text, tables, charts, diagrams, connectors, callouts, and labels as native editable objects. Use raster images only for actual content or evidence.
12. Export every slide to PNG with `scripts/Export-CrownPresentation.ps1` and compare it with the approved design for composition, clipping, overlap, contrast, hierarchy, and footer clearance.
13. Repair the editable objects, re-export, and stop only when the PPTX, rendered slides, content source, approved design, and template hierarchy agree.

## Layout-selection contract

- Choose layouts by the storyboard's composition and evidence form first, then by the desired amount of Crown brand imagery.
- Multiple layouts may be valid for the same content. Prefer the one that requires the least distortion of the approved design.
- Do not force an agenda onto `Agenda_Dark` when the approved design is better served by a one-column, two-column, or blank layout.
- Use a `Blank` or `Title Only` layout when the approved design requires a custom table, chart, timeline, or diagram that fixed placeholders cannot support.
- If no layout matches exactly, choose the closest brand treatment and construct the remaining design with native objects inside the safe content area.
- Do not modify the master or layout to solve a one-slide problem.

## Design-reference contract

- Use the approved design as an implementation specification, not as a slide asset.
- Do not insert a complete design image into the presentation, set it as a background, crop it into panels, or trace it into one opaque full-slide object.
- Recreate simple visual structure with native shapes, lines, fills, text boxes, tables, and charts.
- Preserve the selected Crown layout's inherited elements instead of redrawing them from the screenshot.
- When content cannot fit the approved composition, shorten the copy, split the slide, or select another compatible layout. Do not uniformly shrink the whole slide or allow overflow.
- Make only implementation-level adjustments needed for editability, legibility, or template fit; do not redesign the approved concept silently.

## Editable-object contract

- Use inherited placeholders when their role matches the storyboard.
- Use text boxes for additional titles, body text, labels, captions, and notes.
- Use `Shapes.AddTable` for tables.
- Use `Shapes.AddShape` and `Shapes.AddConnector` for diagrams.
- Use native Office charts for data-driven charts.
- Use text boxes with the code font for code and logs.
- Keep photos and product screenshots as images, but keep labels and explanatory text separate and editable.
- Give generated objects stable names and semantic alternative text or tags.

## Boundaries

- Do not generate the upstream design screenshot or storyboard as part of this Skill.
- Do not save changes over `designs/Crown Template.pptx`.
- Do not recreate or flatten the Crown master from screenshots.
- Do not create an image-only deck.
- Do not call HTML or web-slide conversion workflows.
- Do not use icons without a verified open-source license and recorded provenance.
- Do not bundle or redistribute commercial font files.
- Do not silently substitute a missing display font.
- Do not automate PowerPoint COM from a shared server, service account, or parallel worker pool.
