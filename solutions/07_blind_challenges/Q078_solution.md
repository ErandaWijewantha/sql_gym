# Reasoning

## 1. Interpret the Business Question

Find the store whose monthly net revenue varies the least — the most
"predictable" store, measured by relative variability rather than
absolute size (since a naturally smaller store would trivially have a
smaller absolute standard deviation).

## 2. Output Grain

One row per store, then take the single most consistent one.

## 3. Metric Definition

Coefficient of variation: `stddev_monthly_revenue / mean_monthly_revenue`,
computed across the store's 24 monthly revenue figures (including
zero-revenue months as real data points, following the same reasoning
as Q055).

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.
`stores`: store_id, store_name.

## 5. SQL

```sql
WITH RECURSIVE months AS (
    SELECT DATE('2024-01-01') AS month_start
    UNION ALL SELECT DATE_ADD(month_start, INTERVAL 1 MONTH) FROM months WHERE month_start < '2025-12-01'
),
calendar AS (
    SELECT s.store_id, m.month_start FROM stores s CROSS JOIN months m
),
monthly_revenue AS (
    SELECT o.store_id, DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
           SUM(oi.quantity*oi.unit_price - oi.discount_amount) AS net_revenue
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.store_id, DATE_FORMAT(o.order_date, '%Y-%m-01')
),
full_series AS (
    SELECT c.store_id, c.month_start, COALESCE(mr.net_revenue, 0) AS net_revenue
    FROM calendar c
    LEFT JOIN monthly_revenue mr ON mr.store_id = c.store_id AND mr.month_start = c.month_start
),
store_stats AS (
    SELECT store_id, AVG(net_revenue) AS mean_revenue, STDDEV(net_revenue) AS stddev_revenue
    FROM full_series
    GROUP BY store_id
)
SELECT
    s.store_id, s.store_name, ss.mean_revenue, ss.stddev_revenue,
    ROUND(ss.stddev_revenue / NULLIF(ss.mean_revenue, 0), 3) AS coefficient_of_variation
FROM store_stats ss
JOIN stores s ON s.store_id = ss.store_id
ORDER BY coefficient_of_variation ASC
LIMIT 1;
```

## 6. Walkthrough

The full calendar grid (store x 24 months) guarantees every store has
exactly 24 monthly revenue figures, including explicit zeros for any
quiet month — necessary so `AVG`/`STDDEV` reflect true variability
rather than only variability among active months. `store_stats`
computes both statistics per store in one `GROUP BY` pass; the final
query computes coefficient of variation (stddev relative to mean, which
normalizes for store size) and takes the single lowest value.

## 7. Validation

- Manually list one store's 24 monthly revenue figures and independently
  compute mean/stddev to confirm the aggregate matches.
- Confirm the winning store's coefficient of variation is genuinely the
  smallest among all 35 — check the full ranked list, not just the top
  row, to make sure it isn't a near-tie worth mentioning.

## 8. Edge Cases

- Using coefficient of variation (relative) rather than raw standard
  deviation (absolute) is a deliberate choice — a large flagship store
  could have a bigger absolute standard deviation than a tiny outlet
  purely due to scale, while still being *proportionally* more stable;
  raw stddev alone would likely just crown whichever store has the
  smallest overall revenue.
- A store with `mean_revenue = 0` (never had any completed order,
  hypothetically) would produce a division-by-zero, guarded here by
  `NULLIF` — not expected to occur given every store in this dataset
  has real order volume.

## 9. Alternative Approach

Ranking by raw standard deviation instead of coefficient of variation
would answer a different, size-biased question ("which store has the
smallest absolute swing"), which is why the relative measure is the
more meaningful choice for "most predictable" in a comparison across
stores of different sizes.

## 10. Trade-offs

Coefficient of variation is the right normalization for comparing
consistency across differently-sized stores; if leadership specifically
wants "which store is easiest to forecast in absolute LKR terms"
(e.g., for staffing headcount purposes), raw standard deviation would
actually be the more relevant measure instead.

## 11. Business Interpretation

The most consistent store is a good case study for what stable,
predictable operations looks like — worth examining what's different
about its customer base, product mix, or local market compared to more
volatile stores, as a template other locations might learn from.
