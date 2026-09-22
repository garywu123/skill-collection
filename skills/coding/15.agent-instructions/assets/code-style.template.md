# <Project> Code Style

Every code-style rule for this repository lives here. `AGENTS.md` routes to
this file and holds no code-style rule itself. Each rule below is verified by
project configuration, automation, or an observed successful run; delete a
section whose language the repository does not use.

## Enforced by tooling

| Concern | Authoritative surface | Command |
|---|---|---|
| Formatting | `<.editorconfig, Prettier, dotnet format, ruff format>` | `<verified command>` |
| Lint and analyzers | `<ESLint, analyzers, ruff>` | `<verified command>` |
| Types and warnings | `<tsconfig, MSBuild properties, mypy>` | `<verified command>` |

Do not restate rules those tools enforce; route to the configuration.

## <Language one, for example C#>

- <A verified rule the tooling does not enforce: file layout, naming, nullable
  truthfulness, units in contract names, documentation expectations.>

## <Language two, for example TypeScript>

- <A verified rule the tooling does not enforce.>

## Tests

- <Framework, file naming, and split such as `*HappyPathTests` and
  `*FailurePathTests`; libraries not to introduce.>
