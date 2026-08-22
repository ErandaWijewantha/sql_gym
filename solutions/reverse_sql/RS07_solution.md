# RS07 — Solution

## Grain
One row = one (store, month) pair.

## What is being computed
Monthly completed order count per store, the previous month's count
(via `LAG`), and the percentage change between them.

## Pattern
Month-over-month comparison via `LAG()`, partitioned by store and
ordered by month — the same pattern as Q023, applied to order *count*
rather than revenue.

## Likely business question
"How is each store's order volume trending month over month?" —
closely related to Q026's moving-average question but showing raw
period-over-period change instead of a smoothed trend.

## Notes
The first month for any given store will show `NULL` for
`prev_order_count` and `pct_change`, since `LAG` has no prior row to
look at within that store's partition — correct behavior, not a bug.
`NULLIF` guards the percentage calculation against a division by zero
if a store had exactly 0 orders in the prior month.

## Verification query

```sql
WITH monthly AS (
    SELECT
        store_id,
        DATE_FORMAT(order_date, '%Y-%m-01') AS month_start,
        COUNT(*) AS order_count
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY store_id, DATE_FORMAT(order_date, '%Y-%m-01')
)
SELECT
    store_id,
    month_start,
    order_count,
    LAG(order_count) OVER (PARTITION BY store_id ORDER BY month_start) AS prev_order_count,
    ROUND(
        (order_count - LAG(order_count) OVER (PARTITION BY store_id ORDER BY month_start))
        / NULLIF(LAG(order_count) OVER (PARTITION BY store_id ORDER BY month_start), 0) * 100,
        1
    ) AS pct_change
FROM monthly
ORDER BY store_id, month_start;
```
