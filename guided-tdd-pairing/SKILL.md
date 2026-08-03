---
name: guided-tdd-pairing
description: Coach a user who explicitly wants to write implementation code themselves through small test-driven steps, hints, or negotiated pair programming. Use for clear learning or pairing intent, not as an automatic lifecycle phase and not when the user simply wants the feature implemented.
---

# Guided TDD Pairing

This is an optional collaboration mode, not a lifecycle skill. It may help with
an already-authorized implementation task but never authorizes or advances it.

## Context and ownership

- Confirm the current task and who writes tests, core logic, and boilerplate.
  Default to the agent writing failing tests/fixtures and the user writing core
  logic; honor changes at any step.
- In a spec-driven repository, read `.specify/flow-state.yaml`, then locate the
  active feature/task with
  `python <this-skill-dir>/../flow-state/scripts/flow_state.py --root . resolve --id <ID>`.
  Never load the complete index into semantic context. Read that task, the
  smallest applicable spec section, existing code, and the targeted tests; do
  not load the whole roadmap or unrelated feature artifacts.
- Keep each opened semantic/code slice at or below 8 KiB and the initial target
  payload at or below 24 KiB. Narrow large changes by task and path. This
  interactive context may span several red/green loops for the same authorized
  implementation, but it must stop before any lifecycle review or gate; that
  gate begins in a new minimal context the user explicitly authorizes.
- Write only files the user assigns within the already-authorized implementation
  scope. Do not create or modify lifecycle artifacts, pointer/index YAML,
  approvals, roadmap status, or release state.
- Never invoke another skill or phase. Report a missing prerequisite or scope
  conflict and wait for the user.

## One-step loop

1. State one behavior and the smallest test that proves it.
2. Write and run that test when assigned to the agent. Confirm it fails for the
   intended reason; fix an invalid test before proceeding.
3. Give one minimal hint or function-level example for the current behavior.
   Do not pre-implement later behavior or dump the full solution.
4. Hand the implementation step to the user and stop. Do not continue until the
   user supplies or saves their change.
5. Run the targeted test, explain the result, and make only the agreed cleanup.
6. Repeat with the next behavior. Run broader relevant validation only after the
   focused loops pass.

Use short teaching comments only while explaining unfamiliar syntax or an
idiom. Remove instructional scaffolding from production code once understood.
If the user asks for speed, switch the agreed writer instead of enforcing the
default division.

## Completion

Report behaviors completed, files changed by each participant, focused and
broader test results, and remaining implementation work. Leave lifecycle state
unchanged and return control to the user.
