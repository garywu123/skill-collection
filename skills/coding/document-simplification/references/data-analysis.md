# Data Analysis Documents

For pages that explain how source data becomes a report and how to read the
result. The reader is an engineer who writes or checks the query next. These
are the shapes that usually work; adapt them when a scenario needs more.

## Report manual

One page per report, shared by all customers.

1. What the report shows and what one output row is.
2. Source tables and the fields used from each.
3. Parsing steps, numbered, in processing order. Put missing-data and
   cancellation handling in the step where it applies.
4. Output columns: name and value or calculation.
5. A small invented input and the rows it produces.

## Customer page

Applies a report manual to one customer. Read after the manual; never repeat
its rules.

1. One sentence on what is special for this customer.
2. Customer value mappings: types, operations, states, as tables.
3. Customer-specific parsing steps.
4. Column notes only where the customer changes a value.
5. Example rows for the customer's typical and exceptional cases.

A good customer page reads like this:

```markdown
## Parsing

1. For a normal Tasks Order, Part 1 is Pick. Part 2 starts as DropDecision at
   the source and changes to Drop at the destination. This remains one Order
   with two Parts.
2. Set `pick_location` to the latest recorded Pick location. Set
   `drop_location` to the latest recorded Drop target. Do not use
   DropDecision's source location as the drop target.
```

The same rule written badly:

```markdown
| Part | Initial operation | What happens | Reporting role |
|---|---|---|---|
| 2 | DropDecision | Obtains the destination, then the same Part is rewritten to Drop. | Delivery context. The initial DropDecision location is the source, not the final destination. |

Reporting consequences:

- The DropDecision-to-Drop change is an operation change within Part 2. It is
  not a new Part or a new Order.
```

The bad version explains the mechanism; the good version tells the reader
what to put in which column.

## Source and reference data

Describe each table by what one row is, its key, its clock, and the fields
reports use. Decode values in tables. Keep environment names, check dates, and
version provenance in the environment record, not here.

## Investigations

An investigation page states its question, the reports and measures it uses,
the current answer, and what is still unknown. It is not a log of queries run.
