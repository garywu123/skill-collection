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

Use these unless the user or a project document says otherwise. These SQL
forms specialize the [default profile](default-profile.md):

- File header: use a star-bordered banner block for script, purpose, input and
  output. Reserve this decoration for the file header; its exact width is not
  prescribed.
- Main steps: use an ordinary `/* ... */` block beginning with `Step n:`.
  State the business action and output. Put key rules and, for complex steps,
  a small fictional input/output example in that block, with example content
  indented four spaces. Use actual field names and state row meaning when it
  changes.
- Within a step: use `--` line comments beside expressions or subqueries for
  local reasons and exceptions. Do not repeat the header or Step explanation.

```sql
/***************************************
Script:  order_observations.sql
Purpose: Counts observations for each Order.
Input:   #scoped_history, already bounded by customer and UTC period.
Output:  One row per customer and Order, with observation_count.
***************************************/

/*
Step 1: Summarize how much history supports each Order.
    Example: Five observations for customer A, Order 7 -> one row with count 5.
*/
SELECT customer_id, order_id, COUNT_BIG(*) AS observation_count
FROM #scoped_history
-- Different customers can reuse the same Order ID.
GROUP BY customer_id, order_id;
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
