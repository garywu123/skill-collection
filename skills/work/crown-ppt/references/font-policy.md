# Crown PowerPoint Font Policy

## Status

This is a working recommendation for generated Crown presentations. It is not represented as an official Crown corporate typography standard. Follow an authoritative user-supplied design or brand guide when available, but do not guess or bundle an unavailable commercial font.

## Font profiles

Choose one profile at the start of design or implementation mode. The profile applies to the design reference and the final PPTX so that approval reflects the intended typography.

| Profile | Titles | Body and labels | Use |
|---|---|---|---|
| `standard` | Arial Bold | Arial | Broad compatibility, conservative business presentations, and recipients with uncertain font availability |
| `crown` | Amasis MT Pro Medium for short editorial titles; Aptos Semibold for long or technical titles | Aptos | The current expressive Crown treatment when the required fonts are available |

Both profiles use Consolas for code and logs and Microsoft YaHei, then DengXian, for Simplified Chinese. The `standard` profile is the recommended name for the user's regular design; `crown` replaces the ambiguous term "advanced design."

The selected profile overrides the generic role table below for Latin titles, body text, labels, tables, and captions. Use the `standard` profile's Arial choices when `standard` is requested.

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

## Conference-room size guidance

These are working minimums for a 16:9 presentation viewed in a conference room. Use larger sizes when the room, projector, viewing distance, or audience requires it.

| Element | Preferred range | Minimum |
|---|---:|---:|
| Cover or section title | 34-44 pt | 32 pt |
| Content slide title | 28-34 pt | 28 pt |
| Main body or bullets | 20-24 pt | 18 pt |
| Table and chart labels | 18-22 pt | 16 pt |
| Captions and secondary labels | 16-18 pt | 14 pt |
| Footnotes and sources | 14-16 pt | 12 pt |

Do not shrink all text to make an overcrowded slide fit. Shorten the content, split the slide, simplify the evidence, or choose a compatible layout. Text below the minimum requires an explicit user decision and must be called out during rendered-slide review.

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
