---
name: crown-ppt
description: Design and implement Crown PowerPoint presentations on Windows using Microsoft PowerPoint COM. Use design mode to turn slide content and optional pictures into reviewable PNG design references, or use implementation mode to turn an approved screenshot or storyboard into an editable PPTX on the bundled template's 960 x 540 point canvas. Do not use for image-only final decks, HTML slides, or unattended server-side Office automation.
---

# Crown PowerPoint

Design or implement a Crown presentation while keeping the design-review and editable-deck stages explicit.

## Modes

Select one mode at the start of the request. Do not silently run both modes.

### Design mode

Use when the user has content but does not yet have an approved visual design.

- Accept slide content as text, pictures, or a mixture of both.
- Apply the selected [font profile](references/font-policy.md#font-profiles), Crown design language, layout catalog, canvas, spacing, and conference-room legibility rules.
- Create a temporary PowerPoint working deck with native text, shapes, tables, charts, and supplied content images, then export each slide as a PNG design reference.
- Label the output as a design reference, not as the final editable deliverable.
- Stop after presenting the rendered design references and request approval or concrete design changes. Do not proceed to final implementation in the same mode.

Design mode may use placeholder copy only when the user has not supplied the final wording. Mark placeholder content clearly and replace it before implementation.

### Implementation mode

Use when the user supplies an approved screenshot, storyboard, or equivalent slide-by-slide visual specification.

- Recreate the approved design as an editable presentation that inherits the bundled Crown template.
- Preserve the selected font profile unless the user explicitly changes it.
- Treat the approved reference as an implementation specification, never as a slide image.

## Input contract

- In design mode, require the slide content and any supplied pictures or data; a completed design reference is not required.
- In implementation mode, require a completed design screenshot, storyboard, or equivalent slide-by-slide visual specification before authoring.
- Treat supplied text, data, documents, and factual instructions as the content source.
- Treat the approved design as the source for composition, hierarchy, proportions, spacing, and visual rhythm.
- Use sample text visible in a design reference only to understand hierarchy and density. Do not copy it unless the user identifies it as content.
- If implementation-mode design direction is incomplete or materially ambiguous, stop and request a completed design. Design mode creates a reviewable reference; it does not silently treat that reference as approved.

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

1. Confirm the requested mode and font profile, then inspect all content inputs and any approved design screenshot or storyboard frame.
2. In design mode, read [the layout catalog](references/layout-catalog.md) and select the closest useful Crown `CustomLayout` for each proposed slide. In implementation mode, map each storyboard slide to the closest useful layout. Treat the catalog as guidance, not a rigid content-to-layout rule.
3. Read [the design language](references/design-language.md).
4. Read [the font policy](references/font-policy.md) for font selection, dense content, code, or multilingual text.
5. Read [the icon policy](references/icon-policy.md) before sourcing a new icon.
6. Read [the COM automation contract](references/com-automation.md) before authoring or changing PowerShell automation.
7. Create a temporary working copy for design mode, or a caller-provided working copy for implementation mode. Never save over the bundled template.
8. Reuse or remove the working copy's example Cover and Sign-Off slides as required, then create remaining slides from existing Crown `CustomLayout` objects.
9. Implement the selected design with native PowerPoint objects. Preserve the master, layout, logo, footer, page number, photography, and other brand furniture.
10. When icons are required, obtain suitable open-source SVG icons before COM authoring, cache them under `assets/icons/`, and record source and license information as required by the icon policy.
11. Build text, tables, charts, diagrams, connectors, callouts, and labels as native editable objects. Use raster images only for actual content or evidence.
12. Export every slide to PNG with `scripts/Export-CrownPresentation.ps1` and inspect composition, clipping, overlap, contrast, hierarchy, footer clearance, and minimum font sizes.
13. In design mode, deliver the PNG references and stop for approval. In implementation mode, repair the editable objects and stop only when the PPTX, rendered slides, content source, approved design, and template hierarchy agree.

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

- Do not treat an unapproved design-mode PNG as an approved implementation reference.
- Do not save changes over `designs/Crown Template.pptx`.
- Do not recreate or flatten the Crown master from screenshots.
- Do not create an image-only deck.
- Do not call HTML or web-slide conversion workflows.
- Do not use icons without a verified open-source license and recorded provenance.
- Do not bundle or redistribute commercial font files.
- Do not silently substitute a missing display font.
- Do not automate PowerPoint COM from a shared server, service account, or parallel worker pool.
