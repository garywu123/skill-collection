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
- Deletion test: do not write a comment whose removal loses nothing a reader
  gets from the signature in a few seconds. It applies to every comment and
  documentation block a language Owner Default does not require, including
  `Step n:` comments; it never removes required documentation.
- Wrapping: wrap comments at the print width the project or the language Owner
  Default sets, like code. The author of the comment wraps it; formatters such
  as Prettier do not. An unbreakable token such as a URL may exceed the width.
  Where no width is set, none is imposed.
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
