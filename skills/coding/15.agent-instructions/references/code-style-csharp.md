# C# Code-Style Decisions

## Trigger And Evidence

Read this reference only when repository evidence includes C# or .NET. Inspect
only the relevant surfaces:

- solution and project files: `.sln`, `.slnx`, and `.csproj`;
- SDK selection in `global.json`;
- shared MSBuild policy in `Directory.Build.props` and
  `Directory.Build.targets`;
- applicable `.editorconfig` files;
- analyzer packages, rulesets, and analyzer settings;
- repository CI, tasks, and scripts that establish commands;
- test projects and their package references.

These files are read-only evidence for this Skill. Do not create or update
code-style configuration, MSBuild policy, or analyzer packages.

## Precedence And Compatibility

Prefer explicit user direction, approved project documents, existing
configuration, and consistent repository patterns over generic advice. Use
modern C# syntax only when the configured `LangVersion` and the lowest target
framework support it. When those signals conflict or are absent, report or omit
the rule rather than guessing.

## Mechanical Enforcement

| Concern | Authoritative surface | Audit action |
|---|---|---|
| Naming and formatting | `.editorconfig` and configured formatter | Read and route; do not restate a large rule set |
| Nullable, implicit usings, warnings as errors, documentation generation, analysis level | MSBuild properties | Record only verified policy |
| Additional diagnostics | Analyzer packages and settings | Preserve package and severity choices |
| Format, build, and test commands | CI, tasks, scripts, solution, and project files | Keep exact verified commands and arguments |

Treat `dotnet format`, `dotnet build`, and `dotnet test` as command candidates,
not defaults. Include a command only when repository automation or an observed
successful run verifies its path and arguments.

## Semantic Candidates

Put a semantic rule in `AGENTS.md` only when explicit user direction, a
governing document, or configuration approves it and it is short enough to
apply across the project. A consistently observed source pattern is evidence
to report, not authority to establish policy. Candidates include:

- public API minimality and compatibility expectations;
- async and cancellation behavior;
- resource ownership and disposal;
- input validation and exception contracts;
- null, empty, and default-value behavior;
- cross-platform constraints;
- dependency boundaries;
- required test scope and categories.

Do not turn this list into project policy without evidence.

## XML Documentation

When the repository requires XML documentation, apply it to public APIs with
meaningful content rather than restating names:

- use `summary` to describe the contract;
- use `param` for each parameter and `typeparam` for each type parameter;
- use `returns` for non-void methods and `value` when a property convention
  needs explanation;
- use `exception` only for observable, documented exceptions;
- use `remarks` for thread safety, performance, units, side effects, or edge
  cases when they matter;
- use `inheritdoc` when the contract is inherited and remains accurate.

## Test Profile

Detect the existing test profile before writing guidance: xUnit, NUnit, or
MSTest; assertion and mocking libraries; naming patterns; theory or other
parameterization conventions; and integration-test markers or categories.
Never impose a framework, library, or convention that is not present or
approved.

## Output Placement

| Finding | Destination |
|---|---|
| Mechanical formatting, naming, or diagnostic enforcement | Existing configuration; read-only for this Skill |
| Short universal semantic rule | `AGENTS.md` |
| Detailed examples or specialized workflow | Existing project docs or scoped instructions |
| Unknown, absent, or conflicting evidence | Omit or report |

Do not create or update `.editorconfig`, `Directory.Build.props`,
`Directory.Build.targets`, analyzer settings, or analyzer package references.
