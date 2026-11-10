# How the engine works

Everything below describes the code in `src/velocity_analytics/`. All examples use synthetic data.

## 1. One row per ticket (`worksheet.py`)

Input is the status change history. For each ticket:

- **In progress date** is the last time it moved to `In Progress`.
- **Done date** is the last time it moved to `Done`.
- A ticket that never reached `In Progress` is dropped.

So a ticket that was reopened is measured from its final restart, not its first start.

## 2. Working days (`workdays.py`)

```
Working Days = number of business days from the in progress timestamp to the done timestamp
```

The engine lists one date per business day starting at the in progress timestamp (same time of day)
and counts the dates that are not after the done timestamp. Two examples with weekends skipped:

| In progress | Done | Working days |
|---|---|---|
| Monday 09:00 | next Monday 00:30 | 5 |
| Monday 09:00 | next Monday 17:00 | 6 |

Holidays: `us_federal` skips weekends and US federal holidays, `weekdays` skips weekends only.

## 3. Delivery stage (`stages.py`)

For every ticket row the engine builds these columns in order. Each lookup table is a sheet in
`lookup_tables.xlsx`.

| Step | Column | How |
|---|---|---|
| 1 | `Role` | from the `roles` table by assignee, else `Not Known` |
| 2 | `Main Stage` | first keyword of the `stages` table found in the title, else `Not Found` |
| 3 | `Sub Stage` | first keyword of the `keywords` table found in the title |
| 3b | `Sub Stage` | if still empty: `keywords2` (keyword and role) |
| 3c | `Sub Stage` | if still empty: `mainstage_role` (main stage and role) |
| 4 | `Data Enablement Stage` | looked up from (`Main Stage`, `Sub Stage`) in the `mapping` table |

Keyword matching is a lower case substring match and the first keyword in table order wins.

Example: "Purchase Orders - Raw Vault ETL" by a Data Engineer. Main stage `Raw Vault` (keyword `raw`),
sub stage `ETL` (keyword `etl`), stage `Raw Vault ETL`.

Example with the fallbacks: "Purchase Orders - Raw Vault Prod Release" by a Data Engineer. The keyword
`prod` has no sub stage of its own, so `keywords2` says a Data Engineer doing a `prod` task is doing `ETL`.

A blank sub stage matches a `mapping` row whose sub stage is also blank (for example Business Requirements).
The original prototype never matched such a row because of how it compared missing values. This engine
matches it, which is what the table was written to do. The synthetic data does not contain this case, so
the golden test is unaffected.

## 4. Averages (`velocity.py`)

1. **Refine.** Keep rows that have a stage and at most `max_working_days` (default 20) working days.
2. **Average.** For each row of the `summary_sequence` table, take the refined rows of that stage:
   the mean of `Working Days` overall and for each team. A stage with no rows is blank.
3. **Average row.** The last row is the mean of the column above it. Blank stages are skipped, and every
   stage counts once whatever its number of tickets. It is not a ticket weighted average.

## 5. Outputs

| Sheet | Contents |
|---|---|
| `average_velocity` | the table from step 4 |
| `worksheet_refined` | the rows that count towards the averages |
| `worksheet` | every ticket row with all intermediate columns |
