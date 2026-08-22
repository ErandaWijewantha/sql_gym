# RS05 — Solution

## Grain
One row = one calendar month.

## What is being computed
Monthly gross revenue, plus a cumulative running total from the start
of the dataset through each month.

## Pattern
Running total via window aggregation: `SUM(x) OVER (ORDER BY
time_column)`, using the default frame (`RANGE BETWEEN UNBOUNDED
PRECEDING AND CURRENT ROW`).

## Likely business question
"What is our cumulative revenue over time?" — this is Q025 from
Level 3, likely feeding a progress-against-annual-target chart.

## Notes
No `PARTITION BY` appears because this is a single overall series; a
per-store or per-category running total (as in a variant of this
pattern) would need `PARTITION BY store_id` or similar, restarting the
cumulative sum independently for each group.

## Verification query

```sql
WITH monthly AS (
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
    SUM(revenue) OVER (ORDER BY month_start) AS cumulative_total
FROM monthly
ORDER BY month_start;
```
