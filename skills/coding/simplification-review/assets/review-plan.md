# <Project> Simplification Review Plan

Current position: <stage or batch in progress, next action>

## Business profile

<Three to five sentences: what the software is, who consumes it, what "correct
enough" means.>

Recorded constraints: [<Functional Specification or Product Brief section>](<relative link>)

## Answers

- <question in plain words> -> <answer, with units> (<confirmed | open>)

## Modules

| Module | Code | Size |
|---|---|---|
| <name> | `<path>` | <lines> |

## Batches

| ID | Kind | Scope (entry points) | Scenario | Status |
|---|---|---|---|---|
| R10 | cross-module | `<Caller.Method>` -> `<Callee.Method>` | <user scenario> | planned |
| R20 | module | `<path/or/namespace>` | <user scenario> | planned |

Status values: `planned`, `in-review`, `reviewed`.

## Batch notes

### R10 <name>

- Questions to ask first: <draft questions specific to this batch>
- Exclusions: <what this batch does not read or judge>
