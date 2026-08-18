# Crown PowerPoint Font Policy

## Status

This is a working recommendation for generated Crown presentations. It is not represented as an official Crown corporate typography standard. Follow an authoritative user-supplied design or brand guide when available, but do not guess or bundle an unavailable commercial font.

## Font roles

| Role | Primary | Fallback | Rule |
|---|---|---|---|
| Cover and section title | Amasis MT Pro Medium | Aptos Semibold, then Arial Bold | Use for short editorial statements |
| Short content-page title | Amasis MT Pro Medium | Aptos Semibold, then Arial Bold | Use only when it fits naturally on one line |
| Long or technical title | Aptos Semibold | Arial Bold | Use for identifiers, paths, code terms, or long assertions |
| Body and labels | Aptos | Arial | Default Latin body family |
| Tables | Aptos | Arial | Prefer Regular and Semibold |
| Code and logs | Consolas | Cascadia Mono | Keep exact spacing |
| Simplified Chinese | Microsoft YaHei | DengXian | Do not force Amasis or Aptos onto missing glyphs |

## Why Aptos replaces Arial as the preferred body font

Aptos is contemporary and has clear differentiation between weights while retaining Office-native behavior. It pairs with the warmer slab-serif character of Amasis without competing with it. Arial remains the compatibility fallback for broad Office support.

Do not claim that Aptos is an official Crown font. Treat it as the preferred working recommendation until the corporate brand owner confirms a body family.

## When to use Amasis for page titles

Use Amasis when all of the following are true:

- the title is a natural-language assertion rather than a file name or technical token;
- it fits on one line at 28 pt or larger;
- the slide is not dominated by a dense table whose title must be visually compact;
- Amasis is available in PowerPoint on the authoring machine.

Use Aptos Semibold when any condition fails. This two-mode rule preserves Crown character without making technical pages feel editorial or crowded.

## Availability and licensing

- Do not place font files in this Skill.
- Run `../scripts/Test-CrownPowerPointEnvironment.ps1` before authoring.
- Do not silently substitute missing Amasis text after layout is complete.
- Prefer Microsoft 365 cloud-font availability where the organization supports it.
- Confirm corporate rights before embedding or distributing commercial fonts.
- If recipients use older or offline Office versions, export a PDF proof and test the PPTX on a representative recipient machine.
