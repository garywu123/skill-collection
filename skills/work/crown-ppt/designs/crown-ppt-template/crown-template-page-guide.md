# Crown Light PowerPoint Template Guide

## Purpose

Use this guide to select the appropriate Crown layout for project updates, case studies, tool explanations, product introductions, and content-heavy technical presentations.

Source template: `Template - Crown Branded Powerpoint (MGT20013) Light Version.pptx`

## Recommended local technology stack

### Recommended for this Codex workflow

1. Use `mck-html-design` for read-only PPTX inspection, SVG extraction, visual review, and template documentation.
2. Use `@oai/artifact-tool` to import the original PPTX, duplicate source slides, edit inherited placeholders and objects, render every result, and export an editable PPTX while preserving the master → layout → slide hierarchy.
3. Open the final result in Microsoft PowerPoint for optional human acceptance testing when desktop PowerPoint is available.

This stack is selected because the requirement is not merely to generate a PPTX. It must reuse the existing Crown master, layouts, typography, footer, logo, page numbering, and editable PowerPoint objects.

### Market alternatives

| Tool | Strength | Limitation for this template | Recommendation |
|---|---|---|---|
| Microsoft PowerPoint Object Model / COM | Highest fidelity to desktop PowerPoint and native custom layouts | Windows-only; requires PowerPoint; unsuitable for portable headless automation | Best fallback for a Windows-only internal automation tool |
| Aspose.Slides | Strong import, edit, master/layout cloning, rendering, and cross-platform support | Commercial license; adds a proprietary runtime | Best general commercial SDK |
| Open XML SDK | Complete access to PresentationML parts and relationships | Very low-level; layout cloning and rendering require substantial engineering | Use only for narrowly scoped OOXML operations |
| PptxGenJS | Excellent for generating new editable decks, tables, charts, and code-defined masters | Best when masters are recreated in code; not the preferred route for lossless editing of this existing source template | Good for net-new decks after a Crown master has been deliberately rebuilt |
| python-pptx | Simple Python API for common slide, shape, text, table, and chart operations | Limited fidelity for complex master/layout reuse and slide cloning; no native renderer | Suitable for simple decks, not the primary engine for this template |

Official references:

- Microsoft custom layouts: https://learn.microsoft.com/en-us/office/vba/api/powerpoint.customlayouts
- Open XML slide masters: https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-slide-masters
- Aspose layout cloning: https://reference.aspose.com/slides/python-net/aspose.slides/globallayoutslidecollection/add_clone/
- PptxGenJS masters: https://gitbrent.github.io/PptxGenJS/docs/masters.html
- python-pptx documentation: https://python-pptx.readthedocs.io/

## Template inventory

| Property | Value |
|---|---|
| Canvas | 10 × 5.625 inches, 16:9 |
| Example slides | 6 |
| Slide masters | 1 |
| Master layouts | 20 |
| Major font | Arial |
| Minor/body font | Arial |
| Default master title | 30 pt |
| Default body level 1 | 18 pt |
| Default body levels 2–5 | 14 pt |

### Theme colors

| Token | Hex | Intended use |
|---|---:|---|
| Accent 1 | `#FD9827` | Primary Crown orange; top rule and main emphasis |
| Accent 2 | `#F27E22` | Secondary orange |
| Accent 3 | `#E0571D` | Dark orange; limited emphasis |
| Dark 1 | `#000000` | Primary text |
| Dark 2 | `#333333` | Secondary text |
| Accent 4 | `#515151` | Dark gray branding |
| Accent 5 | `#888888` | Logo/footer gray |
| Accent 6 | `#C2C2C2` | Rules and secondary separators |
| Light 2 | `#EEEEEE` | Subtle background divisions |

## Brand and layout contract

- Preserve the white/light visual system and Crown industrial imagery.
- Preserve the authentic Crown logo and `crown.com` assets from the source file.
- Preserve the orange top rule on standard content pages.
- Preserve the lower-right logo, orange vertical separator, and slide number on content pages.
- Use Arial unless the template is later revised.
- Prefer one assertion-style title per slide.
- Keep body text at 16–18 pt for new content-heavy pages; do not use the 14 pt nested master levels as the normal presentation body.
- Use Crown orange for hierarchy, flow, and action—not for large decorative surfaces.
- Use pale orange or warm gray only to separate evidence rows or one supporting band.
- Do not create dashboard-style grids of rounded cards.

## Six supplied example slides

| Source slide | Layout | Visual role | Best used for | Avoid when |
|---:|---|---|---|---|
| 1 | `Cover_Light` | Full photographic cover with translucent central title band | Deck title, project name, reporting period, presenter/team | Normal content, agenda, or dense text |
| 2 | `Section_Light` | Photographic section divider with large light panel | Category opening, major chapter break, transition between project phases | Detailed evidence or decision content |
| 3 | `Content Option 1_Light_2 Column` | Clean white content page with orange top rule and two equal content regions | Evidence + implication, comparison, issue + response, two related topics | Full-width long tables unless placeholders are deliberately restructured |
| 4 | `Content Option 2_Light_2 Column` | White central content panel with photographic side rails | Executive summary, paired themes, branded narrative page | Dense edge-to-edge tables or screenshots |
| 5 | `Content Option 3_Light_1/3 Left` | Strong left-side visual/feature region and larger right content region | Image or key message on left; explanation, case details, or product narrative on right | Three equal concepts or full-width evidence tables |
| 6 | `Sign-Off` | Minimal closing page with Crown Ideas That Advance mark | Closing statement, contact information, final discussion prompt | Generic “Thank you” with no useful close |

## All 20 master layouts

### Opening and navigation

| # | Layout | Structure | Recommended content |
|---:|---|---|---|
| 1 | `Cover_Light` | Center title + subtitle over branded photography | Opening cover only |
| 2 | `Section_Light` | Large section title + short descriptor | Category or chapter divider |
| 3 | `Agenda_Light` | Title + single agenda/body region in branded frame | Agenda, meeting objectives, presentation roadmap |

### Content Option 1 — clean white evidence pages

| # | Layout | Structure | Recommended content |
|---:|---|---|---|
| 4 | `Content Option 1_Light_Blank` | Brand chrome only; no title/content placeholder | Highly custom diagram or full-page visual when another Crown source page cannot support it |
| 5 | `Content Option 1_Light_Title Only` | Full-width title; open content canvas | Custom tables, charts, timelines, process diagrams |
| 6 | `Content Option 1_Light_1 Column` | Title + full-width body | Executive narrative, large table, detailed case, code/explanation page |
| 7 | `Content Option 1_Light_2 Column` | Title + two equal columns | Evidence + implication, comparison, issue + resolution |
| 8 | `Content Option 1_Light_3 Column` | Title + three equal columns | Current/build/target, three workstreams, three product capabilities |
| 9 | `Content Option 1_Light_Image Right` | Text left + large picture right | Product or tool explanation with screenshot |
| 10 | `Content Option 1_Light_Image Left` | Large picture left + text right | Case study visual with findings or commentary |

### Content Option 2 — central white panel over branded image

| # | Layout | Structure | Recommended content |
|---:|---|---|---|
| 11 | `Content Option 2_Light_1 Column` | Title + wide central body; photo visible at edges | Branded executive summary, short narrative, key message |
| 12 | `Content Option 2_Light_2 Column` | Title + two central columns; photo side rails | Two-part project update or comparison with stronger brand presence |
| 13 | `Content Option 2_Light_1/3 Left` | Narrow left feature region + larger right narrative | Highlight metric/status on left, explanation on right |
| 14 | `Content Option 2_Light_1/3 Right` | Larger left narrative + narrow right feature region | Main analysis on left, callout/decision/image on right |

### Content Option 3 — strong asymmetric feature pages

| # | Layout | Structure | Recommended content |
|---:|---|---|---|
| 15 | `Content Option 3_Light_1 Column` | Title + wide body with narrow brand rail | General content requiring a lighter brand accent |
| 16 | `Content Option 3_Light_2 Column` | Title + two columns with narrow brand rail | Two related content groups, balanced comparison |
| 17 | `Content Option 3_Light_Image Right` | Text left + right picture | Product screenshot, architecture or case image with explanation |
| 18 | `Content Option 3_Light_1/3 Left` | One-third left feature/image + two-thirds right content | Case study, product feature, problem/evidence narrative |
| 19 | `Content Option 3_Light_1/3 Right` | Two-thirds left content + one-third right feature/image | Detailed analysis with right-side summary, risk or decision |

### Closing

| # | Layout | Structure | Recommended content |
|---:|---|---|---|
| 20 | `Sign-Off` | Centered Crown sign-off mark | Final action, discussion prompt, contact details |

## Selection rules for content-heavy slides

1. Define one assertion for the slide before choosing a layout.
2. Use one-column pages for a large table or a single detailed story.
3. Use two-column pages only when the two regions have distinct jobs, such as evidence and implication.
4. Use three-column pages only for three parallel concepts with similar information depth.
5. Use 1/3 layouts when one region is intentionally subordinate or acts as a summary/callout.
6. Use image layouts only when the image or screenshot is evidence; do not insert decorative stock imagery.
7. Put detailed source records, long incident descriptions, and complete code in the appendix.
8. Preserve a bottom action/decision region only when the audience is expected to act.

## Mapping for the two validation slides

### Slide A — Recent outages

- Base source slide: slide 3, `Content Option 1_Light_2 Column`.
- Keep: orange top rule, footer, logo, page number, Arial typography.
- Rewrite: title as an assertion.
- Restructure the inherited content zone into a wide evidence table and a narrower recurring-pattern/response region.
- Keep detailed incident wording out of the main table; use concise trigger, impact, and recovery labels.
- Add the complete original descriptions to speaker notes or appendix if needed.

### Slide B — Support operating model

- Base source slide: slide 3, `Content Option 1_Light_2 Column`.
- Keep: all inherited Crown brand chrome.
- Rewrite: title as an assertion.
- Restructure the content region into three aligned stages: Current State → Build Now → Target State.
- Reserve the bottom band for interim owner action and Tier I quote inputs.
- Use orange arrows only for the actual state transition.

## Design language summary

Name: **Crown Executive Evidence**

Core model: **Assertion → Evidence → Implication → Action**

- One slide, one primary claim.
- Assertion title instead of topic title.
- Maximum three visible text levels.
- Evidence is compact and comparable.
- Repeated wording becomes a shared category or pattern.
- The implication explains why the evidence matters.
- Action, decision, owner, or next step appears only when required.
- Use the Crown master as the brand system; do not recreate the template from screenshots.

## Current implementation status

- Template visual extraction: complete.
- Six example slides reviewed: complete.
- Twenty layouts structurally inventoried: complete.
- Theme fonts and colors extracted: complete.
- Two-slide editable PPTX: pending the approved `@oai/artifact-tool` presentation runtime required for lossless template import/edit/export.
