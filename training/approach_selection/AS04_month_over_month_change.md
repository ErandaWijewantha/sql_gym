# AS04 — Approach Selection: Month-over-Month Revenue Change

## Business Question

For each calendar month, show that month's revenue and its change
compared to the previous month.

## Data Available

orders
order_items

## Your Task

Sketch three different SQL structures:

- **A — LAG Window Function**: compute monthly revenue, then
  `LAG(revenue) OVER (ORDER BY month)`.
- **B — Self-Join on Shifted Month**: join a monthly-revenue result to
  itself, matching each row to the row exactly one calendar month
  earlier.
- **C — Correlated Subquery**: for each month, a subquery looks up the
  revenue for `DATE_SUB(month, INTERVAL 1 MONTH)`.

For each approach, answer:

1. What happens to each approach if a calendar month has zero revenue
   and therefore doesn't appear as a row at all in the monthly-revenue
   result? Does "previous month" still mean "the actual prior calendar
   month," or does it silently mean "whatever row happens to be
   previous in the result set"?
2. Which approach(es) are naturally robust to that gap-month issue, and
   which would need extra work (like a full calendar grid) to fix it?

Then pick your production choice and write down why, before checking
`solutions/approach_selection/AS04_solution.md`.
