# Reasoning

## 1. Interpret the Business Question

Find customers whose average order value rose while their order
frequency fell, 2025 vs. 2024 — a "fewer but bigger" purchasing shift.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

`aov_2024 = net_spend_2024 / order_count_2024` (and analogously for
2025), computed only for customers with >= 1 completed order in both
years.

## 4. Required Data

`orders`: order_id, customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. SQL

```sql
WITH yearly AS (
    SELECT
        o.customer_id,
        YEAR(o.order_date) AS yr,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_spend
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
      AND YEAR(o.order_date) IN (2024, 2025)
    GROUP BY o.customer_id, YEAR(o.order_date)
),
pivoted AS (
    SELECT
        customer_id,
        MAX(CASE WHEN yr = 2024 THEN order_count END) AS orders_2024,
        MAX(CASE WHEN yr = 2024 THEN net_spend / order_count END) AS aov_2024,
        MAX(CASE WHEN yr = 2025 THEN order_count END) AS orders_2025,
        MAX(CASE WHEN yr = 2025 THEN net_spend / order_count END) AS aov_2025
    FROM yearly
    GROUP BY customer_id
)
SELECT customer_id, orders_2024, aov_2024, orders_2025, aov_2025
FROM pivoted
WHERE orders_2024 IS NOT NULL AND orders_2025 IS NOT NULL
  AND orders_2025 < orders_2024
  AND aov_2025 > aov_2024
ORDER BY aov_2025 - aov_2024 DESC;
```

## 6. Walkthrough

`yearly` computes per (customer, year) order count and net spend
(using `COUNT(DISTINCT order_id)` since it's joined to `order_items`,
avoiding the Q012 fan-out trap). `pivoted` reshapes the two years from
separate rows into separate columns per customer via `MAX(CASE WHEN yr
= X THEN ... END)` — a standard pivot idiom. The final filter requires
both years present (a real comparison needs both), fewer 2025 orders,
and higher 2025 AOV.

## 7. Validation

- Pick one flagged customer and manually verify their per-year order
  count and AOV.
- Confirm no result has `orders_2024 IS NULL` or `orders_2025 IS NULL`.

## 8. Edge Cases

- A customer with exactly 1 order in each year can still qualify (AOV
  is just that single order's value) — "frequency decreased" only
  requires strictly fewer orders, not a minimum count on either side.
- This uses `COUNT(DISTINCT order_id)` inside `yearly`'s aggregation,
  necessary because that CTE is joined through `order_items` — using
  plain `COUNT(*)` there would silently count line items instead of
  orders, repeating Q012's mistake.

## 9. Alternative Approach

Two separate CTEs (one per year) joined together instead of a single
pivoted CTE would avoid the `MAX(CASE WHEN ...)` idiom, at the cost of
near-duplicated code for each year.

## 10. Trade-offs

The pivot approach is more compact for exactly two comparison periods;
with more than two periods, a long/tall format with window functions
(`LAG` per year) would scale better than repeating pivot columns.

## 11. Business Interpretation

This pattern (fewer, bigger orders) could reflect a customer
consolidating purchases (buying more per trip) or shifting toward
higher-value items — worth a closer look at *what* they're buying
differently before assuming it's purely positive.
