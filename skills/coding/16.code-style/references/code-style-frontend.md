# Frontend Code-Style Decisions

Read this reference only when HTML, CSS, JavaScript, TypeScript, or a frontend
framework is a confirmed surface for the project.

## Evidence

- `package.json`, including scripts, dependencies, and `packageManager`;
- the selected package manager lockfile;
- applicable `tsconfig.json`, `jsconfig.json`, and extended configurations;
- ESLint, Prettier, Biome, Stylelint, and Browserslist configuration;
- Vite, Webpack, Next.js, Angular, Vue, and Svelte configuration when present;
- unit, component, integration, and end-to-end test configuration;
- source, component, style, and test layout;
- CI workflows, repository tasks, and scripts that establish commands.

All of these are read-only, except that `define` may create a missing
`.editorconfig` or `.vscode/` file from the Skill templates as described in
[formatting configuration](formatting-config.md). Never change existing
frontend configuration, package files, lockfiles, dependencies, framework
choices, or design systems; report each difference instead.

## Precedence And Compatibility

Prefer explicit user direction, then an approved project document, then current
configuration, then the [owner default](#owner-default) for an unenforced rule.
Honor the
declared browser and runtime targets, the module system, the configured
TypeScript or JavaScript language level, and the installed framework version.
Do not infer policy from a globally installed or newer tool.

## Environment And Dependencies

Preserve npm, pnpm, Yarn, or Bun as selected by the lockfile and
`packageManager`, and report a conflict between those signals. Record only exact
verified commands for install, build, development, lint, format, type check, and
tests. Never switch package managers or add a dependency.

## Enforced By Tooling

| Concern | Authoritative surface |
|---|---|
| Indentation and file hygiene | Applicable `.editorconfig` and the configured formatter |
| Formatting | Prettier, Biome, or another configured formatter |
| JavaScript, TypeScript, and CSS linting | ESLint, Biome, Stylelint, or framework tooling |
| Type checking | `tsconfig.json`, extended configurations, and package scripts |
| Compatibility and transforms | Browserslist, framework, and bundler configuration |

Do not assign one concern to overlapping tools unless the repository shows the
overlap is intentional.

## Rules To Decide And Write

Tooling does not enforce these. Settle each one with the user and write it into
the frontend section, or omit it deliberately:

- TypeScript contract strictness at boundaries and where `any` is forbidden;
- local component and module organization, including what may hold state;
- state management and data-fetching conventions;
- required error, loading, and empty states;
- semantic HTML, accessibility, labels, focus, and keyboard behavior;
- responsive support and browser compatibility expectations;
- code-level handling of secrets, private data, and untrusted input;
- which behavior is tested at which level.

The client/server trust boundary, application boundaries, and dependency
direction belong to the Architecture Design; link them instead of writing them
here. A consistently observed source pattern is a proposal to confirm, not
policy.

## Owner Default

Use these for TypeScript and JavaScript unless the user, a project document, or
existing configuration says otherwise:

- The deletion test and the wrapping rule of the
  [default profile](default-profile.md#cross-language-defaults) apply.
- Module headers: a file with one primary export uses that export's JSDoc as
  its header and gets no separate module header. A primary export is the one
  runtime unit a file exports - a function, component, class, or constant; its
  own props type and other type-only exports that serve it do not count. Write
  a module header stating what the module owns and does not own only for a
  boundary module: a package entry (the module a `package.json` `main` or
  `exports` field names, or a library folder's barrel `index.ts`), an API
  client, a state model, or a module with two or more independent runtime
  exports. An application entry that mounts the app, such as `main.tsx`, gets
  none.
- Functions: full JSDoc - `@param` per parameter, `@returns` when not void, and
  `@throws` only for an observable error - only on an exported function used
  across a module or package boundary. A module here is a source area the
  Architecture Design defines or, without one, a top-level source folder such
  as `src/api/`, `src/state/`, or a feature folder. An export crosses the
  boundary when a file outside its area imports it, which an import search
  confirms; every export of a boundary module crosses it. Other exports get a
  one-line summary; add `@param` only where a unit, a range, or the meaning of
  `null` or `undefined` is unclear from the signature.
- React components: the JSDoc holds the summary and no `@param props` tag.
  Document props fields only on a named `<Component>Props` type; each field
  comment passes the deletion test, and the type needs no JSDoc of its own. An
  inline props type gets no field comments, so the signature stays on one
  line. Do not extract a named props type only to hold comments; report an
  inline field whose unit, range, or null meaning is unclear instead.
- Layout: a summary-only JSDoc uses the one-line form `/** Summary. */` when it
  fits the print width; otherwise the multi-line form, wrapped. In a
  multi-line JSDoc, each tag sits on its own line and its content on the
  following lines, indented four spaces past the leading asterisk.
- `Step n:` comments as in the [default profile](default-profile.md).
- 2-space indentation, including CSS, SCSS, Less, and HTML, and print width
  100, unless project configuration sets other values.

Full JSDoc, for an API client export used across a module boundary:

```ts
/**
 * Loads one export window from the API.
 *
 * @param end
 *     Window end, exclusive.
 * @returns
 *     Rows ordered by time.
 * @throws
 *     ApiError when the server rejects the window.
 */
```

A summary-only export and a named props type:

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

## Do Not Write

This section illustrates the Owner Default rules above and goes into an `apply`
brief only when the project's style file adopts them. The summary is from a
real `AppLogo.tsx`; the same pattern also appeared in the module headers of
`main.tsx` and `clientId.ts`.

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

## Framework And Markup

Detect React, Vue, Angular, Svelte, or another framework only when present and
preserve its established patterns; use a version-specific feature only when the
installed version supports it. For HTML and CSS, write rules for semantic
structure, labels, focus and keyboard behavior, reduced-motion behavior, and CSS
architecture or design tokens only when the repository or the user supports
them. Do not invent a design system or impose an aesthetic.

## Tests

Detect Vitest, Jest, Playwright, Cypress, or other tooling from configuration
and dependencies. Preserve its naming, layout, levels, and exact verified
commands; never invent a framework or command.

## Placement

| Finding | Destination |
|---|---|
| Formatting, linting, typing, or compatibility enforcement | Tooling table route; configuration stays read-only |
| A decided semantic, structural, or documentation rule | The frontend section of `docs/code-style.md`, or of a project file when only that project uses the rule |
| A rule that applies to every language | The cross-language sections of `docs/code-style.md` |
| A detailed UX, design, or accessibility workflow | An existing project document, routed from the style file |
| Unknown or conflicting evidence | Ask, or omit and report |
