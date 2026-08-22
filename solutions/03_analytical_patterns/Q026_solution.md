# Reasoning

## 1. Interpret the Business Question

Store operations wants a smoothed, per-store trend line: each month's
raw order count alongside a trailing 3-month average, to make genuine
shifts easier to spot than the raw noisy counts alone.

## 2. Output Grain

One row = one (store, month) pair.

## 3. Metric Definition

Monthly completed order count per store, plus a trailing 3-month
average (current month + 2 preceding months) of that count.

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.

## 5. Logical Decomposition

    Step 1 → compute completed order count per (store, month)
    Step 2 → AVG(order_count) OVER (PARTITION BY store_id ORDER BY month
              ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)

## 6. Pattern Recognition

"Smoothed trend over a fixed recent window, per group" → moving average
via an explicit `ROWS BETWEEN ... AND ...` frame, partitioned by the
group. The key difference from Q025's running total: a moving average
uses a *bounded* frame (a fixed number of preceding rows), not
`UNBOUNDED PRECEDING`.

## 7. SQL

```sql
WITH monthly_store_orders AS (
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
    AVG(order_count) OVER (
        PARTITION BY store_id
        ORDER BY month_start
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3mo
FROM monthly_store_orders
ORDER BY store_id, month_start;
```

## 8. Walkthrough

`monthly_store_orders` collapses orders to one row per (store, month).
`PARTITION BY store_id` keeps each store's series independent — the
window never blends rows from a different store. `ORDER BY month_start`
establishes chronological sequence within each store. `ROWS BETWEEN 2
PRECEDING AND CURRENT ROW` explicitly bounds the frame to exactly 3
rows counting backward from (and including) the current one: the
current month plus the two immediately preceding rows in that store's
partition — hence "3-month" despite the number 2 appearing in the
syntax.

## 9. Validation

- For a store's 3rd chronological month, manually average its months 1,
  2, and 3 order counts and confirm it matches `moving_avg_3mo` on that
  3rd row.
- For a store's 1st month, `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`
  has no preceding rows available, so MySQL simply averages over
  whatever rows do exist within the frame bound (just the 1 row) —
  `moving_avg_3mo` on that first row equals `order_count` itself, not
  an error and not NULL.
- On a store's 2nd month, the moving average is the average of exactly
  2 rows (months 1 and 2).

## 10. Edge Cases

- If a store has a gap month (zero completed orders, hence no row at
  all for that month in `monthly_store_orders`), the window's "2
  PRECEDING" counts *rows*, not calendar months — so the moving average
  after a gap silently spans a wider calendar range than 3 actual
  months, without any error or warning. Whether that's acceptable
  depends on how gap-prone the data is; for genuinely continuous
  monthly reporting, you may need to first generate a full store x
  month calendar (via a numbers table or recursive CTE) and `LEFT JOIN`
  order counts onto it (defaulting missing months to 0) before applying
  the window.
- Using `RANGE BETWEEN INTERVAL 2 MONTH PRECEDING AND CURRENT ROW`
  instead of `ROWS` would (in engines that support date-based RANGE
  framing) correctly account for calendar gaps — MySQL 8's `RANGE`
  frame support for non-numeric ordering columns is limited, so the
  gap-filling calendar approach is the more portable fix.

## 11. Alternative Approach

A self-join of `monthly_store_orders` to itself, matching rows within
the same store where the month is within a 2-month range, then
averaging in an outer `GROUP BY`, achieves the same result and can more
naturally use true calendar-month arithmetic (`month_start BETWEEN
DATE_SUB(current, INTERVAL 2 MONTH) AND current`) instead of a
row-count-based frame — directly solving the gap-month issue above at
the cost of a more verbose query.

## 12. Trade-offs

The window-function version is simpler and faster, and is entirely
correct as long as the underlying monthly series has no gaps (verified
per store, if that assumption matters for the business use case); the
self-join version is more robust to gaps but noticeably more complex to
write and read.

## 13. Business Interpretation

The smoothed trend line lets store operations distinguish a genuine
multi-month decline (moving average trending down) from a single noisy
bad month (raw count dips but the moving average barely moves) —
exactly the distinction a raw monthly chart alone can't make clearly.
