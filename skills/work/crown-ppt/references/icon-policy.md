# Crown PowerPoint Icon Policy

## Source

Use the Iconify public API with the Microsoft Fluent icon set as the default external icon source. Request SVG files from `https://api.iconify.design/fluent/{icon-name}.svg` and cache the approved result under `assets/icons/` before building a deck.

Use `../scripts/Get-CrownIcon.ps1` for deterministic retrieval and basic SVG safety checks. Do not make live icon requests while PowerPoint is being generated.

## Selection rules

- Use the Fluent `regular` style by default.
- Use `filled` only for one selected state or high-priority warning.
- Use one icon family per deck.
- Use Crown dark gray `#515151` for neutral icons and Crown orange `#FD9827` for active or selected states.
- Use a native PowerPoint shape for simple arrows, lines, checks, circles, and connectors.
- Do not use an icon as decoration when a direct label is clearer.
- Do not mix emoji, multicolor icons, and Fluent line icons.

## Editability

Insert downloaded icons as SVG so they remain vector and recolorable. Keep every accompanying label in a native PowerPoint text object. If a user requires path-level editing, convert the SVG to a PowerPoint shape in desktop PowerPoint and verify the result after ungrouping.

## Provenance

Keep `assets/icons/icon-manifest.json` with the API URL, collection, icon name, color, retrieval time, and SHA-256 hash. Review the underlying icon-set license before external distribution.

References:

- Iconify API: https://iconify.design/docs/api/
- Iconify SVG endpoint: https://iconify.design/docs/api/svg.html
- Microsoft Fluent UI System Icons: https://github.com/microsoft/fluentui-system-icons

