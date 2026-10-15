# Code Style V2.1 Plan

## Current position

- Status: planning only. No Skill file is changed in this run.
- Base revision: `26ed4e7` on `feature/code-style-v2`.
- Target: [code-style](../../skills/coding/16.code-style/SKILL.md) after the
  first real trial of `apply` on the agv-tools frontend (2026-10-14).
- Next: independent review of this plan, then one implementation run that
  follows the segments below. Deployment happens only after review and commit.
- Source of decisions: the user's decisions D1-D8 of 2026-10-14, quoted in
  short under [Decisions](#decisions). Where they leave a detail open, this plan
  states its choice under [Interpretations](#interpretations).

## Goal

Make `apply` cheaper and its comments leaner, based on measured trial evidence:
batch by source size in KB of the files that need documentation work, edit
with targeted replacements, write fewer and shorter TypeScript and JavaScript
comments, and fix two template gaps (EditorConfig indentation for CSS and HTML,
comment wrapping).

Design claim for the implementation run: "Every decision fits in edits to six
existing files of the `code-style` Skill plus its `SKILL.md` Apply and
Completion text; no new file, Skill, intent, description change, or deployment
change is needed." Cheap disproof check: after the edits, `git status` lists only
the files under [File changes](#file-changes), the frontmatter is unchanged, and
`Deploy-Skills.ps1 -ListOnly` still lists `code-style` from its current folder.

## Trial evidence

Measured by the Orchestrator from subagent transcripts (agv-tools frontend):

| Measure | Subagent A | Subagent B |
|---|---|---|
| Files | 25 | 21 |
| Source size | ~197 KB (~49k tokens) | ~121 KB (~30k tokens) |
| First-call context | 53k | 53k |
| Peak context | 188k | 151k |
| API calls | 28 | 19 |
| Input tokens processed | 3.33M (94% cache read) | 1.86M |

- Whole frontend tracked code: ~985 KB (~246k tokens by bytes / 4), of which
  ~166k tokens are tests and e2e that need formatting only. Documentation scope:
  46 source files, 319 KB (~80k tokens).
- Fixed overhead is ~53k tokens per subagent. Context grew to ~2.8x the source
  size because subagents read files with `cat` and rewrote whole files with
  `Write`.
- Result: +1474 comment lines on 46 files (~32 per file); build, lint, and 391
  unit tests passed. The only code change was 5-6 component signatures
  reflowed by Prettier, because field comments were added inside inline props
  types.
- Over-commenting: in `AppLogo.tsx`, an accurate one-line JSDoc became a
  separate module header, the same summary again, and an `@param size` tag. The
  same pattern appeared in the module headers of `main.tsx` and `clientId.ts`.
- `assets/editorconfig.template` sets `indent_size = 2` only for
  `ts,tsx,js,jsx,json,yml,yaml`. Prettier reads `indent_size` from
  `.editorconfig` when `.prettierrc` has no `tabWidth`, so existing 2-space CSS
  and HTML would be reformatted to 4. The Orchestrator added `css` and `html` by
  hand.
- Prettier does not wrap comments, so JSDoc lines exceeded `printWidth` 100. No
  rule says whether comments wrap.
- Prettier's Markdown formatter collapsed the inline code span with a space,
  an asterisk, and a space to a bare asterisk inside a rule sentence. The
  current frontend reference contains exactly such a span.

## Decisions

| ID | Decision (short) |
|---|---|
| D1 | Documentation subagents edit with targeted replacements (`Edit`), never whole-file `Write`; read each file once |
| D2 | Batch by KB of source content; default budget about 100 KB per subagent; a file larger than the budget gets its own subagent; the orchestrator works alone only when the documentation scope fits one budget; at most 5 concurrent, then waves; ask to narrow above a stated cap; record actual KB, peak context, and calls |
| D3 | The estimate counts only files that need documentation work; test code and tool configuration are excluded once the formatter has run |
| D4 | TS/JS comment volume: (a) deletion test; (b) one primary export: its JSDoc is the header, no module header; module headers only for boundary modules; entry files none; (c) full `@param`/`@returns`/`@throws` only on exports used across a module or package boundary, others a one-line summary plus `@param` only when unit, range, or null meaning is unclear; AppLogo as a "Do not write" counter-example |
| D5 | React component JSDoc: summary, no `@param props`; props fields documented only on a named `<Component>Props` type; inline props type gets no field comments |
| D6 | `editorconfig.template` gives `indent_size = 2` to `css`, `scss`, `less`, `html` too |
| D7 | Comments wrap at the project's print width like code; state who wraps |
| D8 | C# keeps full XML docs on public, internal, and key private members; the deletion test only decides which private members are key; no C# tag is loosened |

## Interpretations

The decisions leave these details open. The plan chooses the simplest reading;
the reviewer may challenge any of them.

1. **Cap for asking the user (D2).** 500 KB of documentation scope, which is
   five full budgets, so one full wave. This keeps the old shape: waves happen
   only after the user confirms a scope above the cap.
2. **Packing (D2).** Files larger than the budget get one subagent each. For
   the rest, `n = ceil(rest KB / 100)`; fill batches in folder order to about
   `rest KB / n` each, never above 100 KB; add a batch when a file does not fit.
   Batches stay grouped by language and folder, as today.
3. **"Within one budget" (D2)** means a documentation scope of at most 100 KB.
4. **D1 applies to the orchestrator too** when it does the work itself, because
   the same context growth applies. D1 is written tool-neutrally: "targeted
   replacement edits (the `Edit` tool or an equivalent patch), never a
   whole-file write". Reading a file with a shell command such as `cat` counts
   as a read; a file is not read again after the agent's own edit.
5. **Documentation scope (D3).** In-scope files of a confirmed language whose
   style section sets comment or documentation rules. Excluded after the
   formatter run: test code (identified from the project's test configuration
   and naming, for example `*.test.*`, `*.spec.*`, `e2e/`, `tests/`,
   `__tests__/`), tool configuration (package, build, lint, format, and test
   configuration and lockfiles), and data or style files with no comment rules
   (JSON, YAML, CSS unless the style file sets comment rules for them). Test
   code gets the formatter pass only, consistent with the profile's test-code
   exemption.
6. **Telemetry (D2).** Peak context and API calls are recorded per subagent when
   the platform reports them; otherwise the report says "not available". Never
   estimate them.
7. **Deletion test scope (D4a, D8).** It is a cross-language rule in the default
   profile. It decides whether to write a comment or documentation block that
   no language default requires, including `Step n:` comments. It never removes
   documentation a language Owner Default requires: C# public and internal XML
   docs (D8), Python docstrings, and the SQL header stay required as today.
8. **Primary export (D4b).** A file has one primary export when it exports one
   runtime unit (function, component, class, or constant); its own props type
   and other type-only exports that serve it do not count. A multi-export module
   has two or more independent runtime exports. A package entry is the module a
   `package.json` `main` or `exports` field names, or a library folder's barrel
   `index.ts`. An application entry that mounts the app, such as `main.tsx`,
   gets no module header.
9. **"Used across a module or package boundary" (D4c).** A module here is a
   source area defined by the Architecture Design or, without one, by a
   top-level source folder (for example `src/api/`, `src/state/`, a feature
   folder), not a single file. An export crosses the boundary when a file
   outside its area imports it; the agent confirms this with an import search.
   Exports of a boundary module (D4b) cross by definition. "Full" means
   `@param` per parameter, `@returns` when not void, and `@throws` only for an
   observable error.
10. **One-line JSDoc form (D4c, D5).** A summary-only JSDoc uses
    `/** Summary. */` on one line when it fits the print width; otherwise the
    multi-line form, wrapped (D7).
11. **Props comments (D5).** Field comments on a named `<Component>Props` type
    also pass the deletion test; the type itself needs no JSDoc of its own.
    `apply` never extracts a named props type only to hold comments; a field
    whose unit, range, or null meaning is unclear in an inline props type is
    reported as an unsure item.
12. **Wrapping (D7).** It applies to every language with a print width set by
    project configuration (`printWidth`, `max_line_length`, Ruff
    `line-length`) or by the language Owner Default (TS/JS: 100). The author of
    the comment, agent or person, wraps it; formatters such as Prettier do not.
    An unbreakable token such as a URL may exceed the width. Where no width is
    set, none is imposed.
13. **Where the subagent sees the rules.** `apply` follows only rules
    established in the project's style files, and a subagent reads those, not
    the Skill references. The deletion test and wrapping rule land in the
    cross-language `Comments` section of a refreshed style file, so the brief
    carries the project's own `Comments` and `Documentation` sections (root
    file) and the matching language section (root or project file), and states
    that these project rules win over anything else in the brief. The
    reference's `Do Not Write` section (about 20 lines) is added to a TS/JS
    brief only when the project's language section adopts the D4 rules, that
    is, it limits module headers to boundary modules and sets the export
    documentation depth, for example after a `define` refresh. Otherwise the
    counter-example is omitted, so `apply` never introduces documentation
    policy the project has not adopted. The same holds for wrapping: the brief
    asks for it only through the carried rules.
14. **Verification of D5.** The verify step adds the formatter's check mode on
    the scope and a diff review: a documentation diff shows only comment lines
    and formatter output; any reflowed or changed code line is reported.
15. **Markdown wording hazard.** No new rule is added. The one affected rule
    sentence is reworded so it holds no inline code span that starts or ends
    with a space, and acceptance check 5 searches for such spans.
16. **D6 scope.** Only the EditorConfig template changes. CSS and HTML print
    width stays Prettier's default unless project configuration sets one. The
    VS Code templates are unchanged: built-in CSS and HTML formatting follows
    the tab size the EditorConfig extension sets.
17. **Existing projects.** `apply` uses the project's style file, so a project
    written with the old defaults (agv-tools) gets D4, D5, and D7 only after a
    `define` refresh. That refresh is outside this change.

## File changes

All paths are under `skills/coding/16.code-style/`. Decision IDs say why.

### `SKILL.md` (edit Apply and Completion only)

- **Apply step 3, sub-step 3:** replace "estimate the scope size" with
  "estimate the documentation scope in KB: in-scope files that need comment or
  documentation work, excluding test code and tool configuration once the
  formatter has run". (D2, D3)
- **Apply step 3, sub-step 4:** replace with "fix the remaining deviations
  yourself when that scope fits one batch budget, otherwise in subagent batches
  by size; read each file once and edit with targeted replacements, never by
  rewriting a whole file". (D1, D2)
- **Completion, `apply` sentence:** "the batch plan used (self or N subagents,
  and waves) with actual counts" becomes "the batch plan used (self or N
  subagents, and waves) with the actual KB of each batch, and peak context and
  API calls per subagent when the platform reports them". (D2,
  Interpretation 6)
- **Unchanged:** frontmatter (`name`, `description`), Intent, Output, Language
  Coverage, Define, Consistency Check. The decisions change no trigger,
  exclusion, output file, or `define` step.

Size limit: `skill-authoring` sets no numeric line cap; this plan keeps
`SKILL.md` at or below 200 lines (195 today) and the `description` unchanged at
1000 characters, below the 1024 limit. Numbers, the brief, and examples stay in
the references, per `skill-authoring` step 5.

### `references/apply-batching.md` (rewrite the procedure and worked numbers)

Procedure after the edit:

1. Formatter first: unchanged.
2. Scope: unchanged.
3. Documentation scope and size (D3, Interpretation 5): after the formatter
   run, drop test code, tool configuration, and files with no comment rules.
   Sum the remaining bytes / 1024 as KB and list each file's KB for packing. A
   PowerShell 5.1-compatible shape, with the scope's file list built as today:

   ```powershell
   $files = @(git diff --name-only --diff-filter=ACMR <commit> -- <path>) + @(git ls-files --others --exclude-standard -- <path>)
   $doc = @($files | Where-Object { $_ -match '<source pattern>' -and $_ -notmatch '<test and configuration pattern>' -and (Test-Path -LiteralPath $_) } | Get-Item)
   [math]::Round(($doc | Measure-Object Length -Sum).Sum / 1KB)
   ```

   For a named folder, `$files` is `git ls-files` plus untracked files of that
   folder. Frontend example patterns: source `\.(ts|tsx|js|jsx)$`; excluded
   `(^|/)(e2e|tests?|__tests__)/|\.(test|spec)\.[cm]?[jt]sx?$|\.config\.[cm]?[jt]s$`.
4. At most 100 KB: the orchestrating session does the work itself, batch by
   batch, under the same edit rules as a subagent. (D2, Interpretations 3-4)
5. Above 100 KB: documentation subagents on a strong model (Sonnet class),
   packed as in Interpretation 2; at most 5 running; start the next wave only
   after the current wave returns. Above 500 KB, ask the user to narrow the
   scope; continue above it only on the user's confirmation.
   (D2, Interpretation 1)
6. Subagent brief (D1, Interpretation 13): the project's own `Comments` and
   `Documentation` sections and the matching language section, with the
   statement that these project rules win; the reference's `Do Not Write`
   section only for a TS/JS batch whose project language section adopts the
   D4 rules; and the batch's file list with KB per file. Instructions: follow
   only the carried rules, including any wrapping rule they set (the formatter
   will not wrap comments); read each file once; edit with targeted
   replacements (the `Edit` tool or an equivalent patch), never a whole-file
   write; start no subagents; return at most 10 lines: the changed files and
   at most 3 unsure
   items as `file:line` plus one sentence; no diffs or file contents. For
   `audit`, files with gaps and rule names instead of changed files.
7. Cheap model for mechanical leftovers: unchanged.
8. Verify: `git diff --stat`; the formatter's check mode on the scope; the
   verified build and tests; 2-3 spot-checked diffs. A documentation diff shows
   only comment lines and formatter output; report any reflowed or changed code
   line. (Interpretation 14)
9. No subagents available: unchanged.
10. Budget and cap are defaults; a run may pass a temporary override. Record per
    batch the actual KB and file count, and per subagent the peak context and
    API calls when the platform reports them; otherwise "not available".
    (D2, Interpretation 6)

New worked-numbers table (budget 100 KB, cap 500 KB, 5 running):

| Documentation scope | Plan |
|---|---|
| 80 KB | The orchestrating session does the work itself |
| 100 KB | The orchestrating session does the work itself; the scope fits one budget |
| 140 KB | 2 subagents of about 70 KB, one wave |
| 260 KB including one 130 KB file | 3 subagents: the large file alone, then two of about 65 KB; one wave |
| 319 KB, 46 files (agv-tools trial; 985 KB tracked before tests and configuration were excluded) | 4 subagents of about 80 KB, one wave |
| 480 KB | 5 subagents of about 96 KB, one wave |
| 520 KB | Ask the user to narrow the scope |
| 750 KB, confirmed by the user | 8 subagents of about 94 KB, waves of 5 and 3 |

Closing note in the reference: about 100 KB of source is roughly 25-30k
tokens; with ~53k fixed overhead per subagent, the trial's 197 KB batch peaked
at 188k context with whole-file rewrites. The budget is a default to tune from
recorded runs. Delete the old note that waves occur only above 300k.

### `references/default-profile.md` (edit Cross-Language Defaults)

Add two bullets after "Comments carry intent":

- Deletion test (D4a, D8, Interpretation 7): do not write a comment whose
  removal loses nothing a reader gets from the signature in a few seconds. It
  applies to every comment and documentation block a language Owner Default
  does not require, including `Step n:` comments; it never removes required
  documentation.
- Wrapping (D7, Interpretation 12): wrap comments at the print width the
  project or the language Owner Default sets, like code. The author of the
  comment wraps it; formatters such as Prettier do not. An unbreakable token
  such as a URL may exceed the width.

### `references/code-style-frontend.md` (rewrite Owner Default; add Do Not Write)

`Owner Default` bullets after the edit:

- The deletion test and wrapping rule of the default profile apply.
- Module headers (D4b, Interpretation 8): a file with one primary export uses
  that export's JSDoc as its header and gets no separate module header. Write a
  module header stating what the module owns and does not own only for a
  boundary module: a package entry, an API client, a state model, or a module
  with several independent exports. An application entry such as `main.tsx`
  gets none.
- Functions (D4c, Interpretation 9): full JSDoc only on an exported function
  used across a module or package boundary. Other exports get a one-line
  summary; add `@param` only where a unit, a range, or the meaning of `null` or
  `undefined` is unclear from the signature.
- React components (D5, Interpretation 11): the JSDoc holds the summary and no
  `@param props` tag. Document props fields only on a named `<Component>Props`
  type. An inline props type gets no field comments, so the signature stays on
  one line.
- Layout (Interpretations 10, 15): a summary-only JSDoc uses the one-line form
  when it fits the print width. In a multi-line JSDoc, each tag sits on its own
  line and its content on the following lines, indented four spaces past the
  leading asterisk. This replaces the current sentence that ends in an inline
  code span of a space, an asterisk, and a space.
- `Step n:` comments: unchanged.
- 2-space indentation, including CSS, SCSS, Less, and HTML, and print width 100,
  unless project configuration sets other values. (D6, D7)

Examples: keep the current full JSDoc example, labeled as an API client export
that crosses a module boundary. Add two short examples, a summary-only export
and a named props type:

```tsx
/** Formats a duration in seconds as m:ss. */
export function formatDuration(seconds: number): string;
```

```tsx
type RouteMapProps = {
  /** Zoom factor; 1 shows the whole map. */
  zoom: number;
  onSelect: (nodeId: string) => void;
};
```

New `## Do Not Write` section after `Owner Default` (D4). It opens with one
sentence saying it illustrates the Owner Default rules and goes into an `apply`
brief only when the project's style file adopts them (Interpretation 13), and
one sentence saying the pattern also appeared in `main.tsx` and `clientId.ts`
module headers. The summary text is the trial's; the signature is
illustrative:

```tsx
// Do not write: a module header, the same summary again, and a props tag.
/**
 * Owns the App logo graphic. Does not own where or at what size it is shown.
 */

/**
 * Decorative App logo, a route through three Nodes, coloured by theme variables only.
 *
 * @param size
 *     Width and height in pixels.
 */
export function AppLogo({ size }: { size: number }) {
```

```tsx
// Write instead: the one-line summary is the file's header.
/** Decorative App logo, a route through three Nodes, coloured by theme variables only. */
export function AppLogo({ size }: { size: number }) {
```

The one-line form is 90 characters, within print width 100.

### `references/code-style-csharp.md` (edit Owner Default, one bullet)

"and on key private members" becomes "and on key private members; a private member
is key when its documentation passes the deletion test of the default profile".
Every listed element, the layout, and the example stay unchanged. (D8)

### `references/formatting-config.md` (one sentence)

After "The Skill ships no `.prettierrc`; ...", add: "Prettier reads
`indent_size` from `.editorconfig` when no `tabWidth` is set, so the EditorConfig
template covers every extension Prettier formats in a frontend project,
including CSS, SCSS, Less, and HTML." Why: D6; keeps a future edit from
dropping those extensions, and makes the existing-file difference report name
them.

### `assets/editorconfig.template` (one line)

```ini
[*.{ts,tsx,js,jsx,json,yml,yaml,css,scss,less,html}]
indent_size = 2
```

The `max_line_length = 100` section for `ts,tsx,js,jsx` is unchanged. (D6,
Interpretation 16)

### `assets/code-style.template.md` (edit Comments and Documentation)

The rendered root file is what agents follow, and its current Documentation
bullet "Give each module or package a short entry point comment or README"
contradicts D4b.

- `Comments`: add the deletion test and the wrapping rule as two bullets, in
  the default profile's words. (D4a, D7)
- `Documentation`: "Document every public API in `<format>` with its contract"
  becomes "Document public APIs in `<format>` to the depth the language section
  sets, with their contract". "Give each module or package a short entry point
  comment or README" becomes "Give each package, and each module its language
  section names as a boundary module, a short entry point comment or README
  stating what it owns and what it deliberately does not; a file with one
  primary export documents that export instead." (D4b, D4c, Interpretation 7)

## Files read and left unchanged

| File | Reason |
|---|---|
| `SKILL.md` frontmatter and sections other than Apply and Completion | No trigger, exclusion, output, or `define` step changes |
| `references/code-style-python.md` | Decisions cover TS/JS and C# only; its required module docstring stays (Interpretation 7). Same over-commenting risk is a follow-up |
| `references/code-style-sql.md`, `references/code-style-xaml.md` | Not affected |
| `assets/vscode-settings.template.json`, `assets/vscode-extensions.template.json` | D6 is EditorConfig only (Interpretation 16) |
| `assets/code-style.project.template.md` | Holds only the inheritance line and local rules |
| [Coding collection README](../../skills/coding/README.md) | Its `code-style` row ("按大小分批") stays accurate; no public capability change |
| [skill-authoring](../../skills/coding/skill-authoring/SKILL.md) | Source of authoring limits |
| [Previous plan](code-style-v2.md) | Historical record; its token thresholds stay as written there |
| `docs/review-backlog.md` | Excluded by the request; it holds an unrelated local change |
| `scripts/deploy-skill/deploy-skills.json` | `code-style` is already mapped; the folder does not move |

## Implementation segments

1. References and assets: `apply-batching.md`, `default-profile.md`,
   `code-style-frontend.md`, `code-style-csharp.md`, `formatting-config.md`,
   `editorconfig.template`, `code-style.template.md`. Checks: acceptance checks
   3-7.
2. `SKILL.md` Apply and Completion. Checks: acceptance checks 1-2, then the full
   list.

Work is serial: the files share wording for the deletion test, wrapping, and
batching, so parallel subagents would add merge cost.

## Acceptance checks

Run in the implementation run; record command, exit code, and short result.

1. Frontmatter: `git diff 26ed4e7 -- skills/coding/16.code-style/SKILL.md`
   shows no change in lines 1-5; `name` is `code-style`; the `description` is
   at or below 1024 characters (1000 today).
2. `SKILL.md` is at or below 200 lines.
3. Stale batching rules: a search of `skills/coding/` (excluding `_obsolete/`)
   and `docs/` (excluding `docs/plans/`) for
   `\b(60|80|120|290|300|320|450)k\b|ceil\(tokens|Estimate tokens|bytes / 4`
   finds nothing.
4. Stale comment rules: no match for "Each module starts with a comment",
   "Exported functions get JSDoc with", or "Give each module or package a short
   entry point" under `skills/coding/16.code-style/`.
5. Markdown hazard: no inline code span of a space, an asterisk, and a space
   under `skills/coding/16.code-style/`; review every changed rule sentence for
   a code span that starts or ends with a space.
6. Template: the 2-space section of `assets/editorconfig.template` lists
   `ts,tsx,js,jsx,json,yml,yaml,css,scss,less,html`.
7. Links: `powershell -ExecutionPolicy Bypass -File skills/coding/15.coding-agent-instructions/scripts/Test-DocLinks.ps1 -Path skills/coding/16.code-style`
   exits 0; the same for `-Path docs/plans`.
8. Estimate command: run the step 3 command shape in Windows PowerShell 5.1 on
   `scripts/` with source pattern `\.ps1$`; it returns a number without error.
9. Walkthrough in the run report: recompute every worked-numbers row with
   Interpretation 2, and the agv-tools trial row from 985 KB tracked to 319 KB
   documentation scope. Also walk the brief for two TS/JS projects: one whose
   style file adopts the D4 rules (the brief includes `Do Not Write`) and one
   written with the old defaults (it omits `Do Not Write` and carries only that
   project's rules).
10. `git diff --check` reports nothing.
11. `powershell -ExecutionPolicy Bypass -File scripts/deploy-skill/Deploy-Skills.ps1 -ListOnly`
    lists `code-style` from `skills/coding/16.code-style`.
12. `git status --short` lists only the files under
    [File changes](#file-changes) plus the pre-existing `docs/review-backlog.md`
    change, which stays untouched.

Limits: these checks show structure and wording. They cannot show that a model
applies the deletion test well, or that 100 KB batches with targeted edits keep
peak context in budget; that needs the next real run and its recorded KB, peak
context, and calls.

## Implementation notes

Deviations from the file changes above, made in the implementation run:

- `apply-batching.md` step 5 derives waves as `ceil(batches / 5)` from the
  packed batch count, independent of the 500 KB cap (Orchestrator note R1-002).
  The worked-numbers table states that its totals assume the files pack into
  100 KB batches, and adds the row "480 KB as six 80 KB files": six batches,
  waves of 5 and 1.
- `apply-batching.md` states the edit rules once in step 4, for the session and
  every subagent, and the brief in step 6 refers to them.
- `code-style-csharp.md`: the key-private-member clause is a separate sentence
  after the element list, because inserting it before the list's colon breaks
  the sentence. The meaning is unchanged.
- `code-style.template.md` `Comments`: the two bullets use "language section"
  where the default profile says "language Owner Default", because a rendered
  style file has language sections, not Owner Defaults.
- `code-style-frontend.md` `Owner Default` carries the definitions of
  Interpretations 8, 9, and 11 (primary export, boundary module, module
  boundary, props-type extraction), so `define` can write them as followable
  rules.

## Out of scope

- Any change to the `description`, intents, `define`, or other Skills.
- A `define` refresh or `apply` run in agv-tools or any other project.
- Python, SQL, or XAML comment-volume rules; Markdown formatting rules for style
  files; CSS or HTML print width; VS Code template changes.
- A gap-scan or size-estimate script.
- Deployment before review and commit.

## Risks

- The 100 KB budget and 500 KB cap rest on one trial that used whole-file
  rewrites. Peak context with targeted edits is unmeasured until the next run.
- Peak context and call counts may be unavailable on some platforms; the report
  then says so and the budget cannot be tuned from that run.
- The deletion test and "used across a boundary" are judgment rules. The import
  search makes the second checkable; the first is checked only by spot review.
- Projects written with the old defaults keep module headers on every file
  until a `define` refresh (Interpretation 17).
- Python's required module docstring may produce the same over-commenting
  pattern seen in TS/JS.
