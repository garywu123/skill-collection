# <ID> <Batch Name> Findings

Current position: <questions pending | decisions pending | reviewed; next action>

## Scope and answers

Scope: <entry points, callers and documents read>. Plan: [review plan](00.review-plan.md).

- <question in plain words> -> <user's answer> (<date>)

## Checklist

The checklist is the only status. Checked means done in code, or a final
`retain` or rejected decision. Status words: `open`, `accepted`, `rejected`,
`after <ID>`, `done in <commit>`.

- [ ] <ID>-01 `decide` - <short title> - open
- [ ] <ID>-02 `simplify` - <short title> - after <ID>-01
- [x] <ID>-03 `retain` - <short title>

## Items

<!-- Use level-three headings only for items; the budget check counts each one. -->

### <ID>-01 <Short title>

**What happens now:** <plain-language scenario: what the user or consumer sees>

**Why it is more than needed:** <the confirmed constraint it exceeds, linked>

**Proposal:** <smallest change>

**Must stay the same:** <only the essentials>

**Evidence:** `<path>` `<Symbol>` (<source-read | reproduced | measured>)

### <ID>-03 <Short title>

<One sentence: the scenario inside the confirmed constraints that needs it.>
Evidence: `<path>` `<Symbol>`.

<!-- A `defect` item states what is wrong, the correction and its evidence. -->
