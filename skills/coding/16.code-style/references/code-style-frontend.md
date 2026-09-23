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

All of these are read-only. Never create or modify frontend configuration,
package files, lockfiles, dependencies, framework choices, or design systems.
For cross-language indentation and file hygiene, consult the
[EditorConfig baseline](editorconfig-baseline.md) without repeating it here.

## Precedence And Compatibility

Prefer explicit user direction, then an approved project document, then current
configuration, then a consistent repository pattern the user confirms. Honor the
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
- component and module boundaries, including what may hold state;
- state management and data-fetching conventions;
- required error, loading, and empty states;
- semantic HTML, accessibility, labels, focus, and keyboard behavior;
- responsive support and browser compatibility expectations;
- security, privacy, and the client/server trust boundary;
- which behavior is tested at which level.

A consistently observed source pattern is a proposal to confirm, not policy.

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
| A decided semantic, structural, or documentation rule | The frontend section of `docs/code-style.md` |
| A rule that applies to every language | The cross-language sections of `docs/code-style.md` |
| A detailed UX, design, or accessibility workflow | An existing project document, routed from the style file |
| Unknown or conflicting evidence | Ask, or omit and report |
