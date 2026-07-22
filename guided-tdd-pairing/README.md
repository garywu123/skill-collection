# Guided TDD Pairing

A coaching skill for when you want to *learn* by writing the code yourself — with the AI acting as your pair programmer rather than doing it all for you.

**Full skill instructions:** [SKILL.md](SKILL.md)

---

## What it does

Runs a TDD red → green loop where **you write the core logic** and the AI writes the tests and boilerplate. At each step you get:

- A failing test (written and run by the AI) that defines exactly one behaviour.
- A worked example with inline teaching comments showing *what each line does and why*.
- Space to implement it yourself, then run the test to green.
- Clean production comments replacing the teaching scaffolding once you're done.

Who writes what is negotiable at any step — you can always say "you write this one" or "I'll take this one" and the AI adapts without friction.

---

## When to use

- You want to learn a new language, library, or pattern by doing, not reading.
- You said "give me hints, not the whole thing" or "coach me through this."
- You want to stay in control of the implementation but need direction at each step.
- You are pair-programming on a feature and want TDD discipline enforced.

**When NOT to use:** you just want the feature done quickly — ask the AI to implement it directly instead.

**Position in the overall workflow:** this skill is used *during implementation*, after a feature spec and task list exist. See [spec-driven-flow.md](../spec-driven-flow.md) for context.

---

## Example

### Scenario

You are learning TypeScript and want to implement a `ShoppingCart` class. You have a task that says:

> Implement `ShoppingCart` with `addItem(name, price, qty)`, `total()`, and `removeItem(name)`.

Instead of asking the AI to write it, you invoke the skill and learn by doing.

### Step 1 — Invoke the skill

```
/guided-tdd-pairing

I want to implement a ShoppingCart class in TypeScript.
Methods: addItem(name, price, qty), total(), removeItem(name).
Guide me — I'll write the logic, you write the tests.
```

### Step 2 — AI writes the first failing test (RED)

The AI writes one test and runs it:

```typescript
// cart.test.ts
import { ShoppingCart } from './cart';

test('total() returns 0 for an empty cart', () => {
  const cart = new ShoppingCart();
  expect(cart.total()).toBe(0);
});
```

```
✗  total() returns 0 for an empty cart
   Cannot find module './cart'   ← correct failure reason
```

### Step 3 — AI hands off with a worked example (GREEN)

```
Your turn. Make this test pass.

Here's a minimal example with teaching comments:

  export class ShoppingCart {
    // private field: TypeScript convention for internal state
    private items: { name: string; price: number; qty: number }[] = [];
    //                                                              ^^^ initialise to empty array

    total(): number {
      // Array.reduce accumulates a running sum across all items
      return this.items.reduce(
        (sum, item) => sum + item.price * item.qty,
        0   // ← starting value
      );
    }
  }

Write your version in cart.ts, then run the test.
```

### Step 4 — You implement, run to green

You write your version of `ShoppingCart` (retyping and adapting the example). The test passes.

### Step 5 — Next RED

The AI writes the next failing test — `addItem` — and the loop repeats. After you pass all tests, the AI replaces teaching comments with clean production docstrings.

### Final output

By the end you have a working, tested `ShoppingCart` implementation that *you* typed — and you understand every line.

---

## Labor division (default)

| Piece | Who writes it |
|-------|--------------|
| Failing tests + fixtures | AI |
| Core / design logic | You |
| Boilerplate & scaffolding | AI |
| Final docstrings / comments | AI |

You can flip any row at any step — just say so.
