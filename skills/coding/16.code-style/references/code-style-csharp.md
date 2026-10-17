# C# Code-Style Decisions

Read this reference only when C# is a confirmed language for the project.

## Evidence

Inspect only what is needed to separate enforced from unenforced rules:

- solution and project files: `.sln`, `.slnx`, and `.csproj`;
- SDK selection in `global.json`;
- shared MSBuild policy in `Directory.Build.props` and
  `Directory.Build.targets`;
- applicable `.editorconfig` files;
- analyzer packages, rulesets, and analyzer settings;
- CI workflows, tasks, and scripts that establish commands;
- test projects and their package references.

All of these are read-only, except that `define` may create a missing
`.editorconfig` or `.vscode/` file from the Skill templates as described in
[formatting configuration](formatting-config.md). Never change existing
code-style configuration, MSBuild policy, or analyzer packages; report each
difference instead.

## Precedence And Compatibility

Prefer explicit user direction, then an approved project document, then existing
configuration, then the [owner default](#owner-default) for an unenforced rule.
Use
modern C# syntax only when the configured `LangVersion` and the lowest target
framework support it. Report a conflict between these signals rather than
picking one.

## Enforced By Tooling

| Concern | Authoritative surface |
|---|---|
| Naming and formatting | `.editorconfig` and the configured formatter |
| Nullable, implicit usings, warnings as errors, documentation generation, analysis level | MSBuild properties |
| Additional diagnostics | Analyzer packages and severity settings |
| Format, build, and test commands | CI, tasks, scripts, solution, and project files |

Route to these in the style file's tooling table. Treat `dotnet format`,
`dotnet build`, and `dotnet test` as command candidates, not defaults; include a
command only when its path and arguments are verified.

## Rules To Decide And Write

Tooling does not enforce these. Settle each one with the user and write it into
the C# section, or omit it deliberately:

- public API minimality and what widening visibility requires;
- async and cancellation behavior, including `ConfigureAwait` policy and whether
  an async method must accept a `CancellationToken`;
- resource ownership and disposal, including who disposes an injected
  dependency;
- input validation placement and the exception contract for invalid input;
- null, empty, and default-value behavior at public boundaries;
- units, time zones, and encodings carried in contract names or documented;
- cross-platform constraints.

Dependency boundaries between projects in the solution belong to the
Architecture Design; link them instead of writing them here.

A consistently observed source pattern is a proposal to confirm, not policy.

## XML Documentation

Write the C# documentation rule with these element meanings:

- `summary` states the contract, not the member name restated;
- `param` for every parameter and `typeparam` for every type parameter;
- `returns` for non-void members, and `value` when a property needs it;
- `exception` only for observable, documented exceptions;
- `remarks` for thread safety, performance, units, side effects, and edge cases
  when they matter;
- `inheritdoc` when the inherited contract is still accurate.

## Owner Default

Use these unless the user or a project document says otherwise:

- Full XML documentation on public and internal members, and on key private
  members: `summary`, `param`, `typeparam`, `returns`, `exception`, and
  `remarks` for important reminders. A private member is key when its
  documentation passes the deletion test of the
  [default profile](default-profile.md#cross-language-defaults).
- Record positional parameters need no `param` tag; add one only where a unit,
  a valid range, or the meaning of `null` is unclear from the name and type.
- Layout: an element whose content is one sentence and whose whole line, with
  its indentation, fits 100 characters stays on one line, such as
  `/// <summary>Seconds since the run started.</summary>`. Any longer element
  sits on its own lines, with its content indented four spaces after `///` and
  wrapped at 100 characters.
- `Step n:` comments as in the [default profile](default-profile.md).
- Test code is exempt from XML documentation.

```csharp
/// <summary>Builds the parameterized SELECT that reads one export window.</summary>
/// <param name="start">Window start, inclusive.</param>
/// <param name="end">
///     Window end, exclusive. Example: 01:00-05:00 reads rows with time >= 01:00 and < 05:00.
/// </param>
```

## Tests

Detect the existing profile before writing a test rule: xUnit, NUnit, or MSTest;
assertion and mocking libraries; naming pattern; parameterization style; and
integration-test markers or categories. Write the detected profile as binding,
and never impose a framework or library the repository does not use.

## Placement

| Finding | Destination |
|---|---|
| Formatting, naming, or diagnostic enforcement | Tooling table route; configuration stays read-only |
| A decided semantic, structural, or documentation rule | The C# section of `docs/code-style.md`, or of a project file when only that project uses the rule |
| A rule that applies to every language | The cross-language sections of `docs/code-style.md` |
| Unknown or conflicting evidence | Ask, or omit and report |
