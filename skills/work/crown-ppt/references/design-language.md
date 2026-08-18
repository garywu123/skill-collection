# Crown PowerPoint Design Language

## Purpose

Produce a coherent Crown PowerPoint deck, whether design mode is composing a new design reference from raw content or implementation mode is recreating an approved screenshot or storyboard. The storyboard or proposed composition controls layout; the content source controls facts; the Crown template supplies the master, layouts, and brand furniture.

## Precedence

Apply inputs in this order:

1. Preserve facts, terminology, data, and required messages from the content source.
2. In implementation mode, follow the approved storyboard for slide sequence, composition, hierarchy, proportions, alignment, and visual rhythm. In design mode, propose that same structure from the content and this document.
3. Preserve inherited brand elements from the selected Crown layout.
4. Use the defaults in this document where the storyboard is silent or does not yet exist.

Do not create a new design direction or reproduce sample copy from a design image unless the user explicitly requests it.

## Storyboard interpretation

For each approved frame, or each frame being proposed in design mode, identify:

- slide role and primary reading order;
- content regions and their relative proportions;
- title, body, metric, label, and caption hierarchy;
- alignment anchors, margins, gutters, and repeated spacing;
- dominant, supporting, and emphasis colors;
- rule, border, icon, image, table, and chart treatment;
- repeated footer, page number, or brand elements.

Choose the Crown layout that best supports that structure. The storyboard is not itself a slide asset; recreate its content structure with inherited placeholders and editable PowerPoint objects.

## Narrative model

Preserve the approved storyboard's narrative. When implementation details are unspecified, use this order for content slides:

1. **Assertion:** state the conclusion in the title.
2. **Evidence:** show the minimum facts needed to support it.
3. **Implication:** explain why the evidence matters.
4. **Action:** show a decision, owner, or next step only when the audience must act.

Use one primary assertion per slide. Split the slide rather than overfill the approved composition.

## Template visual character

- Preserve inherited Crown logo, footer, page number, orange rules, photography, and layout furniture.
- Use Crown orange to guide attention, not as a large decorative surface unless the storyboard explicitly requires it.
- Prefer square corners, crisp rules, aligned columns, and deliberate negative space.
- Avoid generic rounded-card dashboards, gradients, shadows, and decorative stock imagery.
- Use new imagery only when it is content or evidence.
- Do not redraw inherited template elements from the storyboard screenshot.

## Typography

Use the detailed rules in [font-policy.md](font-policy.md), starting with the selected `standard` or `crown` font profile. The template theme declares Arial for major and minor Latin fonts. Follow an approved storyboard or brand direction when it explicitly requires a font outside the selected profile; otherwise follow the profile.

## Template color tokens

| Token | Hex | Use |
|---|---:|---|
| Crown orange | `#FD9827` | Primary emphasis and active flow |
| Secondary orange | `#F27E22` | Secondary emphasis |
| Dark orange | `#E0571D` | Limited warning or escalation emphasis |
| Primary text | `#000000` | Titles and essential text |
| Secondary text | `#333333` | Body and supporting labels |
| Brand gray | `#515151` | Icons and restrained emphasis |
| Muted gray | `#888888` | Metadata and captions |
| Rule gray | `#C2C2C2` | Lines and separators |
| Light gray | `#EEEEEE` | Subtle grouping bands |

Use pale orange fills only for one selected row, status, or action band. Never color every cell or panel.

## Grid and spacing

- Work within the inherited `960 x 540` point canvas.
- Derive outer margins and anchors from the selected layout and the approved storyboard or proposed composition.
- Use a consistent 8 point spacing rhythm when neither source provides a clearer system.
- Keep at least 18 points between distinct information groups.
- Keep generated objects clear of inherited footer and page-number regions.
- Use no more than three main columns unless the storyboard clearly demonstrates another readable structure.

## Tables, diagrams, and icons

- Use native PowerPoint tables for comparable records.
- Use native shapes and connectors for systems, flows, ownership, and state changes.
- Keep diagram labels concise and connector semantics consistent.
- Download open-source SVG icons before authoring when a basic PowerPoint shape is insufficient.
- Keep icons visually consistent with the storyboard and accompanying labels in separate editable text objects.

## Animation

- Use no animation by default.
- Add simple appear, fade, or wipe effects only when the approved design or narrative requires a sequence, build, or state transition.
- Animate logical groups, not individual words or decorative objects.
- Keep the final slide understandable when printed or exported to PDF.
