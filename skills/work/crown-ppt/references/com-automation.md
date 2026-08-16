# PowerPoint COM Automation Contract

## Scope

Use Microsoft PowerPoint COM as the native inspection, authoring, animation, rendering, and save engine for this Skill. Keep the design judgment in the Skill rules; treat COM as the reader and executor.

## Required lifecycle

1. Validate Windows, PowerPoint COM, template path, output path, and required fonts.
2. Set `DisplayAlerts` to `1` (`ppAlertsNone`), not `0`.
3. Set `AutomationSecurity` to `3` (`msoAutomationSecurityForceDisable`) before opening files.
4. Open the source template read-only or open a working copy.
5. Resolve layouts by exact `CustomLayout.Name`.
6. Save only to a caller-provided output path.
7. Close presentations in `finally`.
8. Quit PowerPoint in `finally`.
9. Release COM objects in reverse ownership order and force final garbage collection.

## Known PowerShell pitfalls

- PowerPoint enum properties may reject `0` even when another Office application accepts it. Define and document numeric constants locally.
- COM collections are one-based.
- `HasTextFrame`, `HasText`, and other `MsoTriState` values use `-1` for true and `0` for false.
- Do not keep COM objects in long pipelines; assign them, use them, and release them.
- Do not call `ReleaseComObject` repeatedly until zero. Use `FinalReleaseComObject` once for objects owned by the script.
- Avoid reusing common environment variables for script state.
- Do not allow PowerPoint dialogs or a visible window during automation.
- Do not overwrite the source template.

## Refresh commands

```powershell
./scripts/Test-CrownPowerPointEnvironment.ps1
./scripts/Inspect-CrownTemplate.ps1
./scripts/Export-CrownLayoutPreviews.ps1 -LabelPlaceholders
```

`Inspect-CrownTemplate.ps1` writes a machine-readable profile with slide size, theme fonts, theme colors, layouts, placeholders, and geometry. `Export-CrownLayoutPreviews.ps1` creates one diagnostic PNG per layout without saving changes to the template.

## Authoring requirements

- Create slides with `Slides.AddSlide(index, customLayout)`.
- Prefer inherited placeholders when their semantic role matches the content.
- Use points for geometry and derive positions from placeholders or the slide size.
- Use native tables, charts, shapes, connectors, and text boxes.
- Use `TimeLine.MainSequence.AddEffect` only for necessary sequence or state animation.
- Name generated objects predictably and add semantic metadata.
- Export the finished deck to PNG and inspect every slide before reporting completion.

## Operating boundary

Run COM interactively on a Windows workstation with desktop PowerPoint. Do not use it from a Windows service, web server, shared unattended automation host, or parallel background-worker pool.

