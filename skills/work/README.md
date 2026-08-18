# Work Skills

This collection contains reusable Skills for presentations and other workplace communication artifacts.

## Crown PPT Workflow

Use [`crown-ppt`](crown-ppt/SKILL.md) in one of two explicit modes. The Skill runs on Windows with desktop PowerPoint and uses PowerPoint COM.

```text
content + optional pictures
	|
	v
design mode -> reviewable PNG slide references -> user approval
					       |
					       v
			 implementation mode -> editable Crown PPTX + PNG proof
```

### 1. Design mode

Choose design mode when the content exists but the visual direction has not been approved yet. Provide:

- the desired audience, meeting purpose, and conference-room or presentation context;
- slide-by-slide content, including required wording, data, and calls to action;
- optional photos, product screenshots, diagrams, or other evidence images;
- the expected slide count or a request to propose a slide sequence;
- a font profile: `standard` for Arial or `crown` for the expressive Amasis/Aptos treatment;
- any known brand, accessibility, confidentiality, or image-licensing constraints.

Example request:

```text
Use crown-ppt in design mode with the standard font profile.
Create a six-slide conference-room presentation for senior operations leaders.
Use the attached product screenshots on slides 3 and 4. Keep body text at or above
18 pt, use short assertion titles, and return PNG design references for approval.
```

The output is a set of reviewable PNG references. Review composition, density, image crops, contrast, font size, and factual content. Design mode stops at this review; its output is not automatically approved.

### 2. Implementation mode

Choose implementation mode after the design has been approved. Provide:

- the approved screenshot, storyboard, or slide-by-slide visual specification;
- the final content source and any required data or images;
- the selected font profile and the intended output path;
- any approved changes from the design-reference review.

Example request:

```text
Use crown-ppt in implementation mode with the approved PNG storyboard and the
standard font profile. Build an editable PPTX from the Crown template, preserve
the approved six-slide composition, and export PNG proofs for every slide.
```

The output is an editable PPTX that inherits the Crown template, plus rendered PNG proofs. Text, tables, charts, diagrams, labels, and connectors remain editable. Supplied photos and product screenshots remain raster content; explanatory text stays separate and editable.

### 3. Review and handoff

Before implementation approval, check:

- the narrative has one primary assertion per slide and no unnecessary sample text;
- the deck is readable from the back of the room: titles are generally 28 pt or larger and body text is generally 18 pt or larger;
- tables, charts, captions, footnotes, and source labels are not too small or overcrowded;
- images are legible, correctly cropped, high enough resolution, and approved for use;
- Crown footer, logo, page number, margins, and inherited layout elements remain visible;
- the final deck contains no full-slide screenshot flattening or unused template prompt text;
- fonts are available on the authoring machine and a representative recipient machine;
- the exported PNG proofs match the approved design and have no clipping, overlap, or contrast problems.

## Commonly missed inputs

The Skill can make layout and typography decisions, but it cannot infer every presentation constraint. State these when they matter:

| Missing input | Why it matters |
|---|---|
| Audience and room size | Determines density, hierarchy, and practical minimum font sizes |
| Final versus placeholder content | Prevents approving a layout that only works with shorter sample copy |
| Slide count and speaking time | Controls narrative pacing and how much evidence belongs on each slide |
| `standard` versus `crown` profile | Keeps design references and the final PPTX typographically consistent |
| Image, icon, and font rights | Avoids unusable or non-redistributable deliverables |
| Recipient Office/font environment | Prevents font substitution and layout changes after handoff |
| Accessibility or language requirements | Affects contrast, reading order, glyph support, and text alternatives |
| Notes, sources, and citations | Determines whether supporting material belongs on-slide or in speaker notes |

When an input is unknown, the Skill should make the smallest reasonable assumption, record it in the review output, and flag it before implementation rather than silently redesigning the presentation.

## Available Skills

| Skill | Capability |
|---|---|
| [`crown-ppt`](crown-ppt/SKILL.md) | Create reviewable Crown design-reference PNGs from text, pictures, or mixed slide content, or implement approved designs as editable PowerPoint decks from the bundled template on a 960 x 540 point canvas using Microsoft PowerPoint COM. |
