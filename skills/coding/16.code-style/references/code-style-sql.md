# SQL Code-Style Decisions

Read this reference only when SQL is a confirmed language for the project.

## Evidence

- the SQL dialect and database engine;
- the migration tool, its folder, and its file naming;
- any configured SQL formatter or linter;
- scripts, jobs, and application code that run the SQL.

All of these are read-only. Never change existing SQL tooling or migration
configuration; report each difference instead.

## Owner Default

Use these unless the user or a project document says otherwise:

- Each script starts with a header comment block: script, purpose, input, and
  output.
- A `Step n:` comment precedes each main step, as in the
  [default profile](default-profile.md).
- A complex step adds a concrete example below its `Step n:` line.

```sql
/*
Script:  export_window.sql
Purpose: Reads one export window of vehicle events.
Input:   @start, @end (end is exclusive)
Output:  One row per event, with Seq per key.
*/
-- Step 1: Keep rows inside the window.
-- Step 2: Number rows per key in time order.
--     Example: ROW_NUMBER adds a Seq column: key on rows 12 and 40 -> Seq 1 and 2.
```

## Rules To Decide And Write

Write these only when the user or a project document settles them; otherwise
omit them and report the gap:

- keyword case;
- naming of tables, columns, parameters, and scripts;
- parameterization at call sites.

## Placement

| Finding | Destination |
|---|---|
| Formatting or lint enforcement | Tooling table route; configuration stays read-only |
| A decided semantic, structural, or documentation rule | The SQL section of `docs/code-style.md`, or of a project file when only that project uses the rule |
| A rule that applies to every language | The cross-language sections of `docs/code-style.md` |
| Unknown or conflicting evidence | Ask, or omit and report |
