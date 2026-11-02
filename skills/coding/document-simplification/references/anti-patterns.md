# Common Anti-patterns

Language models drift toward these because they look careful. Each one makes
the reader work harder without telling them what to do.

## Certainty commentary instead of the rule

The text explains how sure the author is rather than stating the rule.

Bad:

```markdown
Pickup progress and drop progress remain separate from the Order outcome.
The recorded type must be read from the source; the recovery purpose is not
a substitute for Order Type. This counting rule is a proposal, not an
accepted rule.
```

Good:

```markdown
Read `order_type` from the Order. A recovery destination does not change it.
```

If the page is a draft, say so once under the title.

## Process history

Dates, discovery IDs, who confirmed what, check records, "assistant
proposal", "checked on". The reader needs the current rule, not its
biography.

Bad:

```markdown
The user confirmed on 2026-10-13 that Order Type `Tasks` identifies Task
Orders (S14). Proposed 2026-10-16; not accepted and not checked against data.
```

Good:

```markdown
`Tasks` Orders are customer Tasks.
```

## Defensive non-claims

Lists of what the example or rule does not prove.

Bad:

```markdown
Limits: the example does not establish delivery to the originally requested
destination, request-to-completion time, or v1 behavior.
```

Good: state what the example shows. Add a limit only when a reader would
otherwise make that exact mistake, and phrase it as an instruction.

## Self-description and routing prose

Opening paragraphs that explain what the page covers, owns, and does not
cover. A title and one sentence of purpose are enough; ownership rules
belong in the project's guidance.

## Concept columns instead of real columns

Output described as ideas ("pickup location and progress", "outcome
context") instead of actual column names with values. Name the column and
say how its value is computed.

## Rules scattered through narrative

A rule the reader must follow is buried in an explanation, an example's
caption, or an "open decisions" list. Put each rule once, in the step where
it is applied.

## Additive revision

Each update appends a clarification instead of rewriting the section, so the
page grows and contradicts itself. Rewrite the section so it reads as if
written once.
