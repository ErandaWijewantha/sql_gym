# Reasoning

## 1. Interpret the Business Question

Marketing wants customers on a genuine 3-consecutive-calendar-month
upward spend trajectory — not just "spent more this month than last,"
but two increases in a row, forming a real streak.

## 2. Output Grain

One row = one customer (those with >= 1 qualifying streak anywhere in
their history).

## 3. Metric Definition

Monthly net spend (completed orders) per customer. An "increase" month
is one whose spend is strictly greater than the *immediately preceding
calendar month's* spend. A qualifying streak is 2 consecutive increase
months in a row (which together with the baseline month before them
spans 3 months total).

## 4. Required Data

`orders`: order_id, customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → build a full customer x calendar-month grid (so "no orders
              that month" becomes an explicit 0, not a missing row)
    Step 2 → compute net spend per (customer, month), defaulting to 0
    Step 3 → flag each month as an increase (1) or not (0) vs. the
              previous calendar month, via LAG
    Step 4 → group consecutive increase-flags into "islands" (gaps and
              islands technique)
    Step 5 → keep customers with an island of size >= 2 increase-months

## 6. Pattern Recognition

"A run of N consecutive qualifying periods" → gaps and islands. The
standard trick: number rows within a partition (`ROW_NUMBER` by month),
separately number rows within the same partition *and same flag value*
(`ROW_NUMBER` by month, partitioned additionally by the flag); the
difference between the two row numbers is constant across a contiguous
run of the same flag value, which lets a single `GROUP BY` collapse
each run into one group.

## 7. SQL

```sql
WITH RECURSIVE months AS (
    SELECT DATE('2024-01-01') AS month_start
    UNION ALL
    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH)
    FROM months
    WHERE month_start < '2025-12-01'
),
active_customers AS (
    SELECT DISTINCT customer_id FROM orders
),
calendar AS (
    SELECT ac.customer_id, m.month_start
    FROM active_customers ac
    CROSS JOIN months m
),
monthly_spend AS (
    SELECT
        o.customer_id,
        DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_spend
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.customer_id, DATE_FORMAT(o.order_date, '%Y-%m-01')
),
full_series AS (
    SELECT
        c.customer_id,
        c.month_start,
        COALESCE(ms.net_spend, 0) AS net_spend
    FROM calendar c
    LEFT JOIN monthly_spend ms
        ON ms.customer_id = c.customer_id AND ms.month_start = c.month_start
),
flagged AS (
    SELECT
        customer_id,
        month_start,
        CASE
            WHEN net_spend > LAG(net_spend) OVER (PARTITION BY customer_id ORDER BY month_start)
            THEN 1 ELSE 0
        END AS is_increase
    FROM full_series
),
islands AS (
    SELECT
        customer_id,
        month_start,
        is_increase,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY month_start)
        - ROW_NUMBER() OVER (PARTITION BY customer_id, is_increase ORDER BY month_start) AS grp
    FROM flagged
)
SELECT DISTINCT customer_id
FROM islands
WHERE is_increase = 1
GROUP BY customer_id, grp
HAVING COUNT(*) >= 2;
```

## 8. Walkthrough

`months` recursively generates every calendar month from 2024-01 to
2025-12; crossed with every customer who has ever ordered, `calendar`
gives a complete grid with no gaps. `monthly_spend` computes actual net
spend only where orders exist; the `LEFT JOIN` plus `COALESCE(...,0)`
in `full_series` makes every customer-month explicit, including
zero-spend months — this is what makes the later `LAG` comparison
calendar-correct rather than silently skipping over gap months (the
exact trap Q023/Q026 warned about). `flagged` then marks each month as
an increase relative to the *actual previous calendar month* (now
guaranteed to exist as a row). `islands` applies the row-number-minus-
row-number trick: within a customer's series, consecutive rows sharing
the same `is_increase` value get the same `grp` value. Filtering to
`is_increase = 1` and grouping by `(customer_id, grp)` with `HAVING
COUNT(*) >= 2` finds any run of 2+ consecutive increase-months — which,
together with the non-increase baseline month right before the run
began, spans 3 consecutive months of genuine growth.

## 9. Validation

- Pick one flagged customer and list their full 24-month `full_series`
  spend sequence; manually verify at least one place has 3 consecutive
  strictly-increasing values.
- Confirm every customer in the final result has `order_status =
  'completed'` orders spanning enough distinct months to even make a
  3-month streak possible (fewer than 3 months of any activity can
  never qualify).
- Spot-check that a customer with a single isolated 2-month increase
  surrounded by flat/declining months elsewhere is correctly included
  (only one streak is required, not a sustained pattern throughout
  their whole history).

## 10. Edge Cases

- This is precisely why the full calendar grid matters: without it,
  `LAG` would compare a month to whatever row happened to be previous
  *in the result set*, which might actually be 2 or 3 calendar months
  earlier if the customer had a gap month — silently fabricating a
  "streak" out of two non-adjacent months, or missing a real one that
  crossed a zero-spend month.
- A customer whose first-ever active month happens to be an "increase"
  relative to `LAG`'s `NULL` result: `net_spend > NULL` evaluates to
  `NULL` in SQL (not `TRUE`), which the `CASE` correctly treats as `0`
  (not an increase) — so the very first month of a customer's grid can
  never itself start a counted streak, which is the right behavior
  (there's no prior month to have grown from).

## 11. Alternative Approach

A purely procedural approach (iterating month by month in application
code, tracking a running streak counter per customer) would avoid the
gaps-and-islands SQL entirely, at the cost of pulling all the data out
of the database to process row by row — reasonable for a one-off
analysis in a notebook, but not idiomatic SQL, and not something that
scales as a reusable query or view.

## 12. Trade-offs

The full-calendar-grid approach costs an extra recursive CTE and a
cross join, but is the only way to make the "3 *consecutive calendar*
months" requirement actually correct rather than "3 consecutive rows
that happened to survive an implicit filter." Skipping the calendar
grid is a common shortcut that silently produces wrong answers exactly
when gap months exist — which, in this dataset, they sometimes do.

## 13. Business Interpretation

Customers surfaced here are showing sustained, multi-month momentum —
a meaningfully stronger signal than a single good month, and a
reasonable basis for proactively extending a loyalty-tier upgrade
before a competitor has a chance to capture that growing wallet share.
