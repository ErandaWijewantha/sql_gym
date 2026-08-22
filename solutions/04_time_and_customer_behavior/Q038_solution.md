# Reasoning

## 1. Interpret the Business Question

Category management wants an early-warning list: products whose unit
sales dropped for three consecutive calendar months in a row —
structurally the mirror image of Q037, applied to products instead of
customers, unit quantity instead of spend, and decline instead of
growth.

## 2. Output Grain

One row = one product (those with >= 1 qualifying decline streak).

## 3. Metric Definition

Monthly unit sales (`SUM(quantity)` from completed orders) per product.
A "decline" month is strictly lower than the immediately preceding
calendar month. A qualifying streak is 2 consecutive decline months in
a row (spanning 3 months total together with the baseline month
before).

## 4. Required Data

`orders`: order_id, order_status, order_date.
`order_items`: order_id, product_id, quantity.

## 5. Logical Decomposition

    Step 1 → build a full product x calendar-month grid
    Step 2 → compute unit sales per (product, month), defaulting to 0
    Step 3 → flag each month as a decline (1) or not (0) vs. the previous
              calendar month, via LAG
    Step 4 → group consecutive decline-flags into islands
    Step 5 → keep products with an island of size >= 2 decline-months

## 6. Pattern Recognition

Identical gaps-and-islands technique to Q037: the only changes are the
entity (product instead of customer), the measure (unit quantity
instead of net spend), and the comparison direction (`<` instead of
`>`).

## 7. SQL

```sql
WITH RECURSIVE months AS (
    SELECT DATE('2024-01-01') AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH)
    FROM months
    WHERE month_start < '2025-12-01'
),
sold_products AS (
    SELECT DISTINCT oi.product_id
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'completed'
),
calendar AS (
    SELECT sp.product_id, m.month_start
    FROM sold_products sp
    CROSS JOIN months m
),
monthly_units AS (
    SELECT
        oi.product_id,
        DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
        SUM(oi.quantity) AS units_sold
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'completed'
    GROUP BY oi.product_id, DATE_FORMAT(o.order_date, '%Y-%m-01')
),
full_series AS (
    SELECT
        c.product_id,
        c.month_start,
        COALESCE(mu.units_sold, 0) AS units_sold
    FROM calendar c
    LEFT JOIN monthly_units mu
        ON mu.product_id = c.product_id AND mu.month_start = c.month_start
),
flagged AS (
    SELECT
        product_id,
        month_start,
        CASE
            WHEN units_sold < LAG(units_sold) OVER (PARTITION BY product_id ORDER BY month_start)
            THEN 1 ELSE 0
        END AS is_decline
    FROM full_series
),
islands AS (
    SELECT
        product_id,
        month_start,
        is_decline,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY month_start)
        - ROW_NUMBER() OVER (PARTITION BY product_id, is_decline ORDER BY month_start) AS grp
    FROM flagged
)
SELECT DISTINCT product_id
FROM islands
WHERE is_decline = 1
GROUP BY product_id, grp
HAVING COUNT(*) >= 2;
```

## 8. Walkthrough

Same structure as Q037: `months` generates the full calendar; `calendar`
crosses it with every product that has ever sold at least one unit
(never-sold products are excluded up front via `sold_products`, since a
product with zero sales across the board can't meaningfully "decline").
`full_series` guarantees zero-sales months appear explicitly rather
than being silently absent, which is what makes the `LAG`-based decline
flag calendar-correct. The `islands` step is identical in mechanism to
Q037, just applied to `is_decline` instead of `is_increase`.

## 9. Validation

- Pick one flagged product and list its full 24-month `units_sold`
  sequence; confirm 3 consecutive strictly-decreasing values appear
  somewhere.
- Confirm no never-sold product (the data generator's deliberate ~5%
  set with zero orders at all) appears in the result — `sold_products`
  should exclude them entirely from the calendar grid.
- Products that declined all the way to zero and then had a later
  resurgence should still correctly show the decline streak leading up
  to the zero point.

## 10. Edge Cases

- A product's first-ever month in the grid can't start a decline
  streak (`LAG` returns `NULL`, and `units_sold < NULL` evaluates to
  `NULL`, treated as `0`/not-a-decline by the `CASE`) — same reasoning
  as Q037's growth case.
- A product could have multiple separate decline streaks across its
  24-month history (e.g., a dip, a recovery, then another dip) — this
  query only requires *at least one* qualifying streak to flag the
  product, not that the decline be sustained throughout its whole
  history.
- If a product declines to a genuine stockout (recall `inventory`'s
  stockout mechanic), unit sales could hit zero not because demand
  vanished but because there was nothing left to sell — this query
  can't distinguish a demand-driven decline from a supply-constrained
  one; that distinction is exactly what Level 6's Q058 (stockout
  impact) investigates separately.

## 11. Alternative Approach

Same alternative as Q037: a procedural month-by-month scan in
application code would sidestep the SQL gaps-and-islands machinery
entirely, at the cost of leaving the database and losing the
reusability of a pure-SQL view.

## 12. Trade-offs

Identical trade-off discussion to Q037 — the calendar-grid approach is
more verbose but is the only version immune to gap-month
miscounting.

## 13. Business Interpretation

This is a genuine early-warning list — three consecutive months of
declining unit sales is a much stronger signal than a single slow
month, and category management can act on it before the product
becomes a bigger write-off or inventory problem.
