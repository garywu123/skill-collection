# Crown Light Layout Catalog

## Selection sequence

1. Write the slide assertion.
2. Identify the evidence form: narrative, comparison, table, process, image, or decision.
3. Choose the narrowest Crown layout that supports that evidence without forcing small text.
4. Add native editable objects inside the inherited content region.
5. Split the content when it exceeds the selected layout's natural capacity.

## Opening and navigation

| Layout | Use for | Avoid for |
|---|---|---|
| `Cover_Light` | Deck title, project, reporting period, presenter | Agenda or normal content |
| `Section_Light` | Category opening or major transition | Detailed evidence |
| `Agenda_Light` | Agenda, objectives, presentation roadmap | Project status details |

## Content Option 1: clean evidence pages

| Layout | Use for | Content pattern |
|---|---|---|
| `Content Option 1_Light_Blank` | Highly custom native diagram | One focal visual system |
| `Content Option 1_Light_Title Only` | Full-width table, timeline, architecture, chart | Assertion + one large evidence object |
| `Content Option 1_Light_1 Column` | Executive narrative, detailed case, code explanation | Assertion + structured vertical story |
| `Content Option 1_Light_2 Column` | Evidence/implication, issue/response, comparison | Two regions with distinct jobs |
| `Content Option 1_Light_3 Column` | Three workstreams, states, or capabilities | Three parallel concepts of similar depth |
| `Content Option 1_Light_Image Right` | Tool or product explanation | Explanation left, screenshot right |
| `Content Option 1_Light_Image Left` | Case evidence or product context | Evidence image left, findings right |

## Content Option 2: stronger brand presence

| Layout | Use for | Content pattern |
|---|---|---|
| `Content Option 2_Light_1 Column` | Executive summary or short branded narrative | One concise message block |
| `Content Option 2_Light_2 Column` | Paired themes or senior-level comparison | Two concise columns |
| `Content Option 2_Light_1/3 Left` | Metric or status plus explanation | Narrow feature left, narrative right |
| `Content Option 2_Light_1/3 Right` | Analysis plus decision or callout | Narrative left, narrow action right |

## Content Option 3: asymmetric feature pages

| Layout | Use for | Content pattern |
|---|---|---|
| `Content Option 3_Light_1 Column` | General content with light brand rail | One structured content field |
| `Content Option 3_Light_2 Column` | Balanced comparison | Two related groups |
| `Content Option 3_Light_Image Right` | Product screenshot or case image | Explanation left, evidence right |
| `Content Option 3_Light_1/3 Left` | Case study or product feature | Feature/image left, detail right |
| `Content Option 3_Light_1/3 Right` | Detailed analysis plus summary | Detail left, summary/decision right |

## Closing

| Layout | Use for | Avoid for |
|---|---|---|
| `Sign-Off` | Final action, discussion prompt, contact | Empty generic thank-you page |

## Common mappings

| Content | First choice | Alternative |
|---|---|---|
| Recent outage evidence | `Content Option 1_Light_Title Only` | `Content Option 1_Light_1 Column` |
| Support operating model | `Content Option 1_Light_3 Column` | `Content Option 1_Light_Title Only` |
| Project status by workstream | `Content Option 1_Light_1 Column` | `Content Option 1_Light_3 Column` |
| Tool logic plus screenshot | `Content Option 1_Light_Image Right` | `Content Option 3_Light_Image Right` |
| Case study | `Content Option 3_Light_1/3 Left` | `Content Option 1_Light_Image Left` |
| Product introduction | `Content Option 1_Light_Image Right` | `Content Option 3_Light_1/3 Left` |
| Executive decision | `Content Option 2_Light_1/3 Right` | `Content Option 1_Light_2 Column` |

## Capacity guardrails

- Use one column for one large object or one detailed story.
- Use two columns only when the regions have different semantic roles.
- Use three columns only for genuinely parallel concepts.
- Use 1/3 layouts when the narrow region is a metric, summary, image, risk, or decision.
- Use an image layout only when the image is evidence.
- Do not place a full-width dense table into a two-column placeholder system.

