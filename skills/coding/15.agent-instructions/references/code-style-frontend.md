# Frontend Code-Style Decisions

## Trigger And Evidence

Read this reference only when repository evidence includes HTML, CSS,
JavaScript, TypeScript, or a frontend framework. Inspect only the relevant
surfaces:

- `package.json`, including scripts, dependencies, and the `packageManager`
  field;
- the selected package manager lockfile;
- applicable `tsconfig.json`, `jsconfig.json`, and extended configurations;
- ESLint, Prettier, Biome, Stylelint, and Browserslist configuration;
- Vite, Webpack, Next.js, Angular, Vue, and Svelte configuration when present;
- unit, component, integration, and end-to-end test configuration;
- source, component, style, and test layout;
- CI workflows, repository tasks, and scripts that establish commands.

These surfaces are read-only evidence. For cross-language indentation and file
hygiene, consult the
[EditorConfig comparison baseline](editorconfig-baseline.md) without duplicating
it here.

## Precedence And Compatibility

Prefer explicit user direction, approved project documents, current
configuration, and consistent repository evidence, in that order. Honor
declared browser and runtime targets, the module system, configured TypeScript
or JavaScript language level, and the installed framework version. Do not infer
policy from globally installed or latest tools.

## Environment And Dependencies

Preserve npm, pnpm, Yarn, or Bun as selected by the lockfile and
`packageManager` field. Report conflicts between those signals. Record only
exact verified commands for dependency installation, build, development, lint,
formatting, type checking, and tests. Verify them from package scripts, CI,
tasks, configuration, or a successful run. Never switch package managers or
add dependencies automatically.

## Mechanical Enforcement

| Concern | Authoritative surface | Audit action |
|---|---|---|
| Indentation and file hygiene | Applicable `.editorconfig` and configured formatter | Compare with `editorconfig-baseline.md`; preserve repository policy |
| Formatting | Prettier, Biome, or another configured formatter | Preserve current ownership and scope |
| JavaScript, TypeScript, and CSS linting | ESLint, Biome, Stylelint, or framework tooling | Preserve configured rules, scope, and severity |
| Type checking | `tsconfig.json`, extended configurations, and package scripts | Record only configured language level, strictness, scope, and command |
| Compatibility and transforms | Browserslist, framework, and bundler configuration | Honor declared targets and module behavior |

Do not assign the same concern to overlapping tools unless repository evidence
shows that the overlap is intentional.

## Semantic Candidates

Put a short semantic rule in `AGENTS.md` only when explicit user direction, a
governing document, or configuration approves it across the applicable project
surface. A consistently observed source pattern is evidence to report, not
authority to establish policy. Candidates include:

- TypeScript contracts and avoiding unbounded `any`;
- component and module boundaries;
- state management and data-fetching conventions;
- error, loading, and empty states;
- semantic HTML, accessibility, labels, focus, and keyboard behavior;
- responsive support and browser compatibility;
- security, privacy, and client/server trust boundaries;
- testing levels and ownership.

Do not turn this list into policy without evidence, impose a framework or design
aesthetic, or copy detailed workflows into `AGENTS.md`.

## Framework And Markup Decisions

Detect React, Vue, Angular, Svelte, or another framework only when present, and
preserve its established patterns. Use React-specific modern features only when
the installed version and team guidance support them.

For HTML and CSS, record semantic structure, labels, focus and keyboard
behavior, reduced-motion behavior where relevant, and CSS architecture or token
usage only when repository evidence supports them. Do not invent a design
system.

## Test Profile

Detect Vitest, Jest, Playwright, Cypress, or other test tooling from current
configuration and dependencies. Preserve its naming, layout, test levels, and
exact verified commands. Never invent a test framework or command.

## Output Placement

| Finding | Destination |
|---|---|
| Mechanical formatting, linting, typing, or compatibility enforcement | Existing configuration; read-only for this Skill |
| Short universal semantic rule | `AGENTS.md` |
| Detailed UX, design, accessibility, or testing workflow | Existing project docs or scoped instructions |
| Unknown, absent, or conflicting evidence | Omit or report |

## Read-Only Boundary

Do not create or update frontend configs, package files, lockfiles,
dependencies, framework choices, or design systems. Read those surfaces only
to route verified project rules and commands.
