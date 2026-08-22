# AS05 — Approach Selection: Running Total of Revenue

## Business Question

Show cumulative revenue from the start of the dataset through each
calendar month.

## Data Available

orders
order_items

## Your Task

Sketch three different ways to compute this:

- **A — Window SUM OVER**: `SUM(revenue) OVER (ORDER BY month)`.
- **B — Correlated Subquery**: for each month, a subquery sums all
  months up to and including it.
- **C — Session Variable Accumulator**: a pre-8.0-style pattern using
  user-defined variables (`SET @running := 0` and `@running :=
  @running + revenue` inside a `SELECT`) to accumulate a running total
  row by row.

For each approach, answer:

1. Which of these is guaranteed reliable row-processing order in
   modern MySQL, and which historically depended on undocumented,
   version-specific evaluation order that could silently break on an
   engine upgrade?
2. Why is approach C generally considered a legacy anti-pattern now
   that window functions exist (MySQL 8.0+)?
3. Would you ever still choose B over A? Under what circumstance?

Then pick your production choice and write down why, before checking
`solutions/approach_selection/AS05_solution.md`.
