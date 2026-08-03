# Fidelity Rules

The recurring failure in wireframing is not too little detail — it is detail at
the wrong altitude. A deck of forty diagrams, one per dropdown, is unreviewable
and is obsolete the day a control moves. This document fixes the altitude.

## The unit of drawing

Draw **screens**, not controls. A screen is anything a user perceives as "where
they are": a route, a full-page modal, a wizard step, a handheld task view.

Everything smaller than a screen is a **row in a table** belonging to that
screen.

## Decision table

| Candidate | Draw it? | Where it goes instead |
|-----------|----------|-----------------------|
| New route or screen | Yes, L1 | — |
| Existing screen whose layout materially changes | Yes, L1 | — |
| Wizard step with a different layout | Yes, L1 | — |
| Full-page modal or takeover | Yes, L1 | — |
| Multi-screen flow with a branch | Yes, L3 | — |
| Multi-screen flow that is strictly linear | No | Named as a sequence in prose |
| Dropdown, select, combobox | No | Control table row |
| Text input, number input, date picker | No | Control table row |
| Checkbox, radio group, toggle | No | Control table row |
| Tooltip, helper text, inline validation | No | Control table row |
| Confirmation dialog using an established pattern | No | State table row |
| Confirmation dialog with a novel layout or impact preview | Yes, L1 | — |
| Loading, empty, error, offline variants | No | State table rows |
| Sort, filter, or pagination that changes data in place | No | Control table row |
| Filter panel that occupies its own screen on mobile | Yes, L1 | — |
| Toast, banner, snackbar | No | State table row |
| Tab that swaps the entire content region | Yes, L1 per tab | — |
| Tab that swaps a small panel | No | Control table row |

## The escalation test

A control earns its own L1 skeleton only if interacting with it either:

1. navigates the user somewhere else, or
2. reveals a layout the reader cannot predict from the parent skeleton.

A dropdown that filters a list fails both tests — it is a control row. A dropdown
whose selection replaces the form below it with a different set of fields passes
test 2 — draw the resulting variant.

## Worked judgements

**"Should I draw the context selector dropdown?"**
No. One control table row: type `dropdown`, options source `allowed contexts for
the current user`, default `last active context`, on select `reloads the result
list`, disabled when only one context is available.

**"Should I draw a privileged mismatch override?"**
Yes, L3. It spans the input screen, an authorization prompt, and two outcomes,
and it branches. The branch condition on each edge must be named.

**"Should I draw the offline state of the input screen?"**
No separate skeleton. One state table row describing the persistent banner and
that operations continue and queue locally. Draw it only if going offline changes
the layout rather than adding an indicator.

**"Should I draw all six columns of the results table?"**
Not as six things. One L1 showing the table region with two representative rows
and `...`, plus a control table row per interactive column header.

## Size limits

- An L1 skeleton stays under 25 lines. Longer means the screen is doing too much;
  report it and ask whether the feature should be split.
- A feature that produces more than eight L1 skeletons is almost certainly too
  large for one feature-specification cycle. Report it against the roadmap's
  feature-boundary rules rather than quietly drawing all of them.
- A product-mode screen inventory lists every screen but draws only the global
  shell.

## What never appears at any level

Color, hex values, font family, font size, spacing values, pixel dimensions,
component library names, CSS class names, framework names, animation timing, and
icon sets. These belong to technical planning and detailed design. A wireframe
that names a component library has already made a technical decision that the
plan was supposed to own.

Copy that is legally or operationally mandated — regulatory disclosures, exact
error text required by policy — is the exception. Quote it, and cite the product
requirement that mandates it.
