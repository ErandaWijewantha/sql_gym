# Reasoning

## 1. Interpret the Business Question

Finance wants a cumulative revenue curve across the whole dataset —
monthly revenue plus a running total from the start of the window.

## 2. Output Grain

One row = one calendar month.

## 3. Metric Definition

Monthly gross revenue, plus `running_total = SUM(monthly revenue) from
the first month through the current month, inclusive`.

## 4. Required Data

`orders`: order_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price.

## 5. Logical Decomposition

    Step 1 → compute gross revenue per month (completed orders)
    Step 2 → SUM(revenue) OVER (ORDER BY month), accumulating

## 6. Pattern Recognition

"Cumulative total over time" → running-total window aggregation:
`SUM(x) OVER (ORDER BY time_column)`. No `PARTITION BY` is needed when
there's a single overall series (contrast with Q026's per-store moving
average, which does need one).

## 7. SQL

```sql
WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m-01')
)
SELECT
    month_start,
    revenue,
    SUM(revenue) OVER (ORDER BY month_start) AS running_total_revenue
FROM monthly_revenue
ORDER BY month_start;
```

## 8. Walkthrough

`monthly_revenue` collapses the dataset to one row per month. The outer
`SUM(revenue) OVER (ORDER BY month_start)` uses the default window
frame for an `ORDER BY`-only window (`RANGE BETWEEN UNBOUNDED
PRECEDING AND CURRENT ROW`), meaning each row's running total includes
every month from the earliest one up through the current one,
inclusive. No `PARTITION BY` is used because the whole point is one
continuous series across the entire dataset, not per-group totals.

## 9. Validation

- The final row's `running_total_revenue` should exactly equal
  `SELECT SUM(quantity*unit_price) FROM order_items oi JOIN orders o ON
  ... WHERE o.order_status='completed'` computed directly (the same
  total from Q005, restricted to completed orders across the full
  window).
- `running_total_revenue` should be non-decreasing from row to row,
  since every month's revenue is non-negative.
- The first row's `running_total_revenue` should exactly equal that
  month's own `revenue`.

## 10. Edge Cases

- A per-store running total would require adding
  `PARTITION BY store_id` to the window (and including `store_id` in
  `monthly_revenue`'s GROUP BY) — each store's running total would then
  restart independently from its own first month, not from a shared
  start.
- Because this window uses the default `RANGE` frame (not an explicit
  `ROWS` frame), two months with an identical `month_start` value would
  be treated as peers within the same frame boundary — not a practical
  concern here since `month_start` is unique per row by construction
  (one row per month from the GROUP BY), but worth knowing the
  difference exists (see Q026 for where `ROWS` framing becomes
  essential).

## 11. Alternative Approach

A correlated subquery (`SELECT SUM(revenue) FROM monthly_revenue m2
WHERE m2.month_start <= m1.month_start`) produces an identical result
without a window function, but re-scans `monthly_revenue` once per row
— fine at 24 rows, but the window-function version is the standard,
scalable idiom and should be the default habit.

## 12. Trade-offs

Not applicable at this data volume — the window-function version is
strictly preferable in both clarity and performance.

## 13. Business Interpretation

This running total is exactly what a "progress toward annual target"
chart needs — finance can overlay a straight-line target trajectory
against this actual cumulative curve to see if the business is ahead
or behind pace at any point in the year.
