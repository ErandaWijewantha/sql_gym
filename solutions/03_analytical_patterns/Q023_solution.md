# Reasoning

## 1. Interpret the Business Question

Category planning wants a month-over-month trend view per category:
current revenue, previous revenue, and both absolute and percentage
change.

## 2. Output Grain

One row = one (category, month) pair.

## 3. Metric Definition

Gross monthly revenue per category, plus:
`change = current_month_revenue - previous_month_revenue`
`pct_change = change / previous_month_revenue * 100`

## 4. Required Data

`orders`: order_id, order_date, order_status.
`order_items`: order_id, product_id, quantity, unit_price.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → compute gross revenue per (category, month)
    Step 2 → LAG(revenue) partitioned by category, ordered by month
    Step 3 → compute absolute and percentage change

## 6. Pattern Recognition

"Compare to the previous period, per group" → `LAG()` partitioned by
the group (category) and ordered by the time dimension (month). This is
the canonical use case for `LAG` — Q024 explores its forward-looking
counterpart, `LEAD`.

## 7. SQL

```sql
WITH monthly_category_revenue AS (
    SELECT
        c.category_id,
        c.category_name,
        DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p      ON p.product_id = oi.product_id
    JOIN categories c    ON c.category_id = p.category_id
    WHERE o.order_status = 'completed'
    GROUP BY c.category_id, c.category_name, DATE_FORMAT(o.order_date, '%Y-%m-01')
)
SELECT
    category_name,
    month_start,
    revenue AS current_month_revenue,
    LAG(revenue) OVER (PARTITION BY category_id ORDER BY month_start) AS prev_month_revenue,
    revenue - LAG(revenue) OVER (PARTITION BY category_id ORDER BY month_start) AS absolute_change,
    ROUND(
        (revenue - LAG(revenue) OVER (PARTITION BY category_id ORDER BY month_start))
        / NULLIF(LAG(revenue) OVER (PARTITION BY category_id ORDER BY month_start), 0) * 100,
        1
    ) AS pct_change
FROM monthly_category_revenue
ORDER BY category_name, month_start;
```

## 8. Walkthrough

`monthly_category_revenue` first collapses everything to one row per
(category, month_start), using `DATE_FORMAT(..., '%Y-%m-01')` to bucket
every order into its calendar month regardless of the day it fell on.
`LAG(revenue) OVER (PARTITION BY category_id ORDER BY month_start)`
then looks at the *previous row within the same category's own
partition*, ordered chronologically — for the first month a category
appears, there is no previous row, so `LAG` returns `NULL`, which
correctly propagates into `NULL` absolute and percentage change for
that first month. `NULLIF(..., 0)` guards the percentage-change
division against a division-by-zero error if a category had exactly
zero revenue in the prior month.

## 9. Validation

- Every category's first appearing month should show `NULL` for
  `prev_month_revenue`, `absolute_change`, and `pct_change`.
- Pick one category and one month pair, manually look up both months'
  revenue from `monthly_category_revenue`, and confirm the computed
  change matches.
- `current_month_revenue - absolute_change` should always equal
  `prev_month_revenue` (an algebraic identity worth spot-checking).

## 10. Edge Cases

- A category with a gap month (zero completed orders in some calendar
  month) simply has no row for that month in
  `monthly_category_revenue` — `LAG()` would then skip straight to the
  next month that *does* have data, silently treating it as "previous,"
  which understates the real gap. If gap months must be represented
  explicitly (e.g., as zero-revenue rows), you'd need to first generate
  a full category x month calendar and `LEFT JOIN` revenue onto it
  before applying `LAG`.
- `NULLIF(prev_month_revenue, 0)` prevents a hard division error, but a
  `NULL` percentage change for "previous month had zero revenue" is
  itself worth flagging distinctly from "no previous month exists at
  all" if a report needs to distinguish the two.

## 11. Alternative Approach

A self-join of `monthly_category_revenue` to itself, matching
`t2.category_id = t1.category_id AND t2.month_start =
DATE_ADD(t1.month_start, INTERVAL -1 MONTH)`, achieves the same result
without a window function — this version is actually more robust
against the gap-month issue above, since it explicitly looks for "the
row exactly one calendar month earlier" rather than "whatever row
happens to be previous in sort order."

## 12. Trade-offs

`LAG()` is simpler to write and reads more naturally for continuous
time series with no gaps; the self-join is more verbose but correctly
distinguishes "previous calendar month had zero revenue" from "no data
exists for the previous calendar month" — worth the extra complexity
whenever gap months are a real possibility, which they are here (a
category could plausibly have a slow month with literally zero
completed orders).

## 13. Business Interpretation

This is the base table for a month-over-month trend chart per
category — but the gap-month caveat above means category planning
should not treat "no data shown" as automatically meaning "no change,"
especially for smaller or seasonal categories.
