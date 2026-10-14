# Owner Default Profile

Read this reference for every `define` run, and for `audit` or `apply` when a
style file states that it uses these defaults.

## Precedence

Use these defaults for an unenforced rule unless the user or an approved project
document says otherwise. Do not ask about a rule this profile settles; ask only
where neither the user, a project document, nor this profile decides it.
Formatting values in existing configuration win over the profile; report each
difference instead of changing that configuration.

## Cross-Language Defaults

- Comments carry intent. Never restate one line of code.
- Before every important step, write a `Step n:` comment that states what the
  step achieves. Other comments explain why: a constraint, a workaround, a
  trade-off, or a deliberate deviation.
- A complex step adds a concrete example below its `Step n:` line:

  ```csharp
  // Step 2: Number the rows of each key in time order.
  //     Example: key A on rows 12 and 40 -> Seq 1 and 2.
  ```

## Test Code

- No API documentation is required in test code.
- Formatting rules still apply.
- Test names describe the behavior under test and its expected result.

## Language Defaults

Read only the sections for confirmed languages:

- C#: [Owner Default](code-style-csharp.md#owner-default)
- TypeScript and JavaScript: [Owner Default](code-style-frontend.md#owner-default)
- Python: [Owner Default](code-style-python.md#owner-default)
- SQL: [Owner Default](code-style-sql.md#owner-default)
- XAML: [Owner Default](code-style-xaml.md#owner-default)
