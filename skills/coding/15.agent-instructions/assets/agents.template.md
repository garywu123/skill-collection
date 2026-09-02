# <Project> Agent Instructions

<One or two sentences: what this project is and who it serves.>

## Documents

| Need | Read |
|---|---|
| Product purpose, users, MVP boundary | `docs/product-brief.md` |
| Features, dependencies, technical direction, architecture | `docs/feature-map.md` |
| One feature's implementation, tests, and real results | `docs/features/<feature-id>-<slug>.md` |
| One UI feature's visible states and transitions | `docs/storyboards/<feature-id>-<slug>.html` |

Read only the route the current task needs. Do not load unrelated Feature Plans
or reconstruct project state from conversation history. Delete a row whose
document this project does not keep.

## Precedence

Resolve conflicts in this order: the current explicit user instruction, the
Product Brief, the Feature Map, the selected Feature Plan, then repository
evidence. Report a conflict instead of promoting current code behavior into
intended behavior.

## Commands

- Setup: `<verified command>`
- Run: `<verified command>`
- Focused test: `<verified command>`
- Full check: `<verified command>`

<Keep only commands verified by a manifest, CI configuration, or an observed
successful run. Delete this whole section when none is verified yet.>

## Conventions

- <A verified repository convention: directory layout, naming, formatting, or
  tooling. Delete this section when the repository shows none.>

## Communication Style

- State facts, results, and decisions in plain, direct language. Avoid
  metaphors, slogans, clever phrasing, and anthropomorphic descriptions.
- Use familiar words and complete phrases. Do not invent abbreviations,
  compressed labels, or abstract terms merely to shorten a response.
- Lead with the result, recommendation, or decision that requires attention.
  Add the explanation needed to understand or act on it.
- Keep each sentence focused on one idea, but use enough words to make the
  meaning natural and unambiguous.
- Explain an unfamiliar or project-specific term the first time it appears in
  a reply.
- Prefer clarity over token savings. Be concise, but include details required
  for correctness, risk assessment, verification, or the user's decision.

## Working rules

1. Make the smallest change that satisfies the named feature. Stay inside its
   boundary and avoid unrelated refactors or dependency bumps.
2. Before adding code, check reuse/delete/change of existing code, repository
   facilities, standard library/framework/native platform, installed
   dependencies, then use the minimum new code. Defer abstractions without a
   current need or observed constraint.
3. Add or update tests for changed behavior.
4. Record only results that actually ran.
5. Report unknowns, conflicts, assumptions, and remaining risk.
6. Never commit secrets or real production data.
