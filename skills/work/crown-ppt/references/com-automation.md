# PowerPoint COM Automation Contract

## Scope

Use Microsoft PowerPoint COM as the native inspection, authoring, animation, rendering, and save engine for this Skill. Author only in a working copy of the bundled Crown template.

## Template facts

- Path: `../designs/Crown Template.pptx`
- Canvas: `960 x 540` points (`13.3333 x 7.5` inches, 16:9)
- Designs: 1
- Slide masters: 1
- Custom layouts: 20
- Source slides: 2, using `Cover_Dark` and `Sign-Off`

These facts were verified with PowerPoint COM. Stop if the template no longer matches them and inspect the updated template before authoring.

## Required lifecycle

1. Validate Windows, PowerPoint COM, the template path, output path, and required fonts.
2. Require the output path to differ from the template path.
3. Copy the template to the output path before authoring, or open the template read-only and immediately save a working copy.
4. Set `DisplayAlerts` to `1` (`ppAlertsNone`), not `0`.
5. Set `AutomationSecurity` to `3` (`msoAutomationSecurityForceDisable`) before opening files.
6. Open and edit only the working copy.
7. Verify `PageSetup.SlideWidth = 960` and `PageSetup.SlideHeight = 540`.
8. Resolve layouts by exact `CustomLayout.Name` and add slides with `Slides.AddSlide(index, customLayout)`.
9. Save only to the caller-provided output path.
10. Close presentations in `finally`.
11. Quit PowerPoint in `finally` only when the automation created the application instance.
12. Release COM objects in reverse ownership order and force final garbage collection.

## Source-slide handling

The template contains example Cover and Sign-Off slides. In the working copy only:

- reuse and edit them when the approved storyboard, or the design being proposed, contains those roles;
- otherwise delete the unused example slide;
- do not leave template prompt text or unused placeholders in the final deck.

## Known PowerShell pitfalls

- PowerPoint enum properties may reject `0` even when another Office application accepts it. Define and document numeric constants locally.
- COM collections are one-based.
- `HasTextFrame`, `HasText`, and other `MsoTriState` values use `-1` for true and `0` for false.
- Do not keep COM objects in long pipelines; assign them, use them, and release them.
- Do not call `ReleaseComObject` repeatedly until zero. Use `FinalReleaseComObject` once for objects owned by the script.
- Avoid reusing common environment variables for script state.
- Do not allow PowerPoint dialogs or a visible window during automation.

## Authoring requirements

- Create slides from the selected Crown `CustomLayout`.
- Prefer inherited placeholders when their semantic role matches the approved storyboard or the design being proposed.
- Preserve inherited master and layout objects; do not redraw or cover them.
- Use points for geometry and derive positions from placeholders or the `960 x 540` point canvas.
- Use native tables, charts, shapes, connectors, text boxes, and supported SVG icons.
- Create connectors before foreground nodes so connectors remain behind the nodes.
- Use `TimeLine.MainSequence.AddEffect` only for necessary sequence or state animation.
- Name generated objects predictably and add semantic metadata.
- Do not insert the approved design reference as a full-slide picture or background.
- Export the finished deck to PNG and inspect every slide before reporting completion.

## Cross-presentation geometry

PowerPoint preserves absolute object dimensions when content is copied between presentations. Two decks can both be 16:9 while using different physical canvases.

Before transferring objects:

1. Read `PageSetup.SlideWidth` and `PageSetup.SlideHeight` from the source presentation.
2. Use `960` and `540` as the target width and height.
3. Compute `scaleX = 960 / sourceWidth` and `scaleY = 540 / sourceHeight`.
4. If the aspect ratios match, map each object's `Left`, `Top`, `Width`, and `Height` with the corresponding ratio. Scale font sizes and line weights by the common ratio when PowerPoint has not already scaled them.
5. For a `720 x 405` point source, use a common scale ratio of `1.3333`.
6. If the aspect ratios differ, do not stretch the content non-uniformly. Recompose it inside the selected Crown layout.

Prefer rebuilding tables, charts, diagrams, and text over bulk-pasting source groups. Never resize the Crown canvas to make pasted content fit, and never flatten transferred content into a full-slide image.

## Validation

Before saving the final output:

- confirm `PageSetup.SlideWidth = 960` and `PageSetup.SlideHeight = 540`;
- confirm every slide uses an intended Crown `CustomLayout`;
- confirm required master and layout elements remain visible;
- confirm no unused template prompt text or placeholders remain;
- confirm no full-slide picture was derived from the approved design reference;
- confirm all narrative text and data structures are editable;
- export and visually inspect every slide at a 16:9 raster resolution.

Raster export dimensions affect only PNG resolution, not PowerPoint geometry.

## Operating boundary

Run COM interactively on a Windows workstation with desktop PowerPoint. Do not use it from a Windows service, web server, shared unattended automation host, or parallel background-worker pool.
