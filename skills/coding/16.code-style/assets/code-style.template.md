# <Project> Code Style

Every code-style rule for this repository lives here. `AGENTS.md` routes to this
file and holds no code-style rule itself.

Rules below are binding instructions. A rule that configured tooling already
enforces is not restated here; the table routes to that tooling instead.

## Enforced By Tooling

| Concern | Authoritative surface | Verified command |
|---|---|---|
| Formatting | `<.editorconfig, Prettier, dotnet format, ruff format>` | `<verified command>` |
| Lint and analyzers | `<ESLint, analyzers, ruff>` | `<verified command>` |
| Types and warnings | `<tsconfig, MSBuild properties, mypy>` | `<verified command>` |

Do not restate what these tools enforce. When a tool and this file disagree, the
tool wins and this file is wrong; report it.

## Module Boundaries

Keep the rules the project actually adopted; delete the rest.

- Give each module one responsibility statable in one sentence. Split a module
  whose name needs "and".
- Depend on `<direction, for example: UI -> application -> domain; domain
  depends on nothing>`. Do not add a dependency that reverses or short-circuits
  it.
- Keep a type, function, or field private until a second caller outside the
  module needs it. Widening visibility is a deliberate contract change.
- Put shared behavior in `<location>` only when at least two modules use it.
  Do not create a shared layer for a single caller.
- Never reach into another module's internals to avoid extending its public
  contract.

## Structure

- One primary public type or exported unit per file; name the file after it.
- Order a file `<for example: imports, public contract, primary logic, private
  helpers>`, consistently across the repository.
- Keep a function to one level of abstraction. When a function mixes
  orchestration with detail, extract the detail and name it.
- Extract a named unit at `<threshold, for example: a function past about 40
  lines or 3 nesting levels>`, unless the extraction obscures the logic.
- Return early on invalid or exceptional input; keep the primary path
  unindented.

## Comments

Comments carry intent. Code already carries mechanics.

- Explain why, not what. Delete a comment that restates the line below it.
- Record the reason for a non-obvious choice: a constraint, a workaround, a
  performance trade-off, an upstream defect, or a deliberate deviation from the
  rules in this file. Link the issue or source when one exists.
- Explain a key step or algorithm before the block that implements it: the
  approach, why it was chosen over the obvious alternative, and its complexity
  or cost when that drove the choice.
- State every non-obvious precondition, invariant, unit, ownership rule, and
  thread-safety expectation the signature cannot express.
- Mark an intentional omission explicitly, for example an empty catch or an
  unhandled case, with the reason it is safe.
- Do not leave commented-out code; version control holds it.
- Update a comment in the same change as the code it describes. A stale comment
  is a defect.

## Documentation

- Document every public API in `<format, for example: XML doc comments,
  docstrings, TSDoc>` with its contract, not a restatement of its name:
  parameters and their valid ranges, return value, observable errors, and side
  effects.
- Document units, encodings, time zones, and coordinate or currency conventions
  wherever a value carries one.
- Give each module or package a short entry point comment or README stating what
  it owns and what it deliberately does not.
- `<Additional project documentation rule.>`

## <Language one, for example C#>

- `<A binding rule the tooling does not enforce.>`

## <Language two, for example TypeScript>

- `<A binding rule the tooling does not enforce.>`

## Tests

- Use `<framework>`; do not introduce another test framework or assertion
  library.
- Name and locate tests as `<pattern>`.
- Separate happy-path and failure-path tests as `<for example:
  *HappyPathTests and *FailurePathTests>`.
- A test name states the scenario and the expected observable result.
