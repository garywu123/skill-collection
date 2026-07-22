---
name: guided-tdd-pairing
description: Use when the user wants to implement code themselves with step-by-step coaching instead of having you write it — pair-programming or learning-oriented sessions (often with TDD) where the user asks for hints rather than a finished solution, says they are learning, or wants to control who writes what per step.
---

# Guided TDD Pairing

## Overview

Coach the user through implementation one small step at a time on a TDD red→green loop. The user writes the core logic (to learn); you write the tests and the rote parts. **Who writes each piece is negotiable per step** — the user can always say "I'll write this" or "you write this," and you adapt without friction.

## When to Use

- The user says "I'll write the code, guide me", "give me hints not the whole thing", "I'm using this to learn", or asks you to coach rather than implement.
- Any task where the user wants to type the implementation themselves but wants direction.

**When NOT to use:** the user just wants the feature done fast, or it's throwaway/mechanical work — write it yourself.

## The Loop

1. **Ideas first.** For core/design logic, give the approach and reasoning before any code.
2. **RED.** Write the failing test yourself, run it, and confirm it fails for the right reason. One behavior per loop.
3. **Hand off GREEN.** Give the user the minimal step to make it pass.
4. **User implements**, then runs the test to green.
5. **Comments after.** Once they save it, replace any teaching comments with production docstrings/comments.
6. **Next RED.** Repeat.

## Labor Division (default — override per step)

| Piece | Default writer |
|---|---|
| Failing tests + fixtures | You |
| Core / design logic | User (by imitation) |
| Boilerplate, established idioms, scaffolding | You |
| Final docstrings / comments | You |

The user flips any cell on request. If a step is slow and the user wants speed, offer to write it — don't force hand-writing.

## Teaching by Imitation

When the user implements a step, give a **worked, function-level code example with inline comments** that explain *what each line does, why, and the language idiom in play* — so the user learns by retyping and adapting it, not from prose alone.

- Keep the example **minimal for the current RED step** — never pre-implement behavior that has no failing test yet (TDD discipline).
- The teaching comments are scaffolding; after the user writes it, swap them for clean production comments.

## Common Mistakes

- **Dumping the whole solution** when the user wanted to learn — give one step, commented for understanding.
- **Forcing hand-writing** when the user wants speed — let them flip the step to you.
- **Code before a failing test** — always RED first, even in teaching mode.
- **Pre-implementing untested behavior** in the worked example — only what the current test demands.
