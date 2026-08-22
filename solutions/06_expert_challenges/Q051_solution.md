# Reasoning

## 1. Interpret the Business Question

Loyalty design wants the longest run of consecutive active months per
customer — not just whether one exists (that would be closer to a
"did they ever have a streak >= N" question), but the actual maximum
length, per customer.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

`longest_active_streak_months` = the length, in months, of the longest
run of consecutive calendar months (2024-01 through 2025-12) in which
the customer placed at least one completed order.

## 4. Required Data

`orders`: customer_id, order_date, order_status.

## 5. Logical Decomposition

    Step 1 → build a full customer x calendar-month grid (so "no order
              that month" is an explicit gap, not a missing row)
    Step 2 → flag each month as active (1) or inactive (0)
    Step 3 → group consecutive active months into islands (gaps and
              islands, same mechanism as Q037/Q038)
    Step 4 → per customer, take the MAX island length among active islands

## 6. Pattern Recognition

Gaps and islands, extended one step further than Q037/Q038: instead of
just checking "does a streak of length >= K exist," this question asks
for the single longest streak's actual length — which means the
groups-by-island step must be followed by a `MAX(COUNT(*))` rather than
a `HAVING COUNT(*) >= K` filter.

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
    SELECT DISTINCT customer_id FROM orders WHERE order_status = 'completed'
),
calendar AS (
    SELECT ac.customer_id, m.month_start
    FROM active_customers ac
    CROSS JOIN months m
),
monthly_activity AS (
    SELECT customer_id, DATE_FORMAT(order_date, '%Y-%m-01') AS month_start
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id, DATE_FORMAT(order_date, '%Y-%m-01')
),
full_series AS (
    SELECT
        c.customer_id,
        c.month_start,
        CASE WHEN ma.month_start IS NOT NULL THEN 1 ELSE 0 END AS is_active
    FROM calendar c
    LEFT JOIN monthly_activity ma
        ON ma.customer_id = c.customer_id AND ma.month_start = c.month_start
),
islands AS (
    SELECT
        customer_id,
        is_active,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY month_start)
        - ROW_NUMBER() OVER (PARTITION BY customer_id, is_active ORDER BY month_start) AS grp
    FROM full_series
)
SELECT
    customer_id,
    MAX(streak_len) AS longest_active_streak_months
FROM (
    SELECT customer_id, grp, COUNT(*) AS streak_len
    FROM islands
    WHERE is_active = 1
    GROUP BY customer_id, grp
) island_lengths
GROUP BY customer_id
ORDER BY longest_active_streak_months DESC;
```

## 8. Walkthrough

The full calendar grid (`months` x `active_customers`) guarantees every
customer has exactly one row per month for the full 24-month window,
with `is_active` explicitly `0` for months with no completed order —
without this, a customer active in Jan and Mar but not Feb would
otherwise have no Feb row at all, and a naive row-adjacency check would
wrongly treat Jan and Mar as consecutive. `islands` applies the
standard row-number-minus-row-number trick to group consecutive
same-`is_active` months. The final aggregation counts each island's
length, keeps only islands where `is_active = 1`, and takes the
`MAX()` per customer — the longest active streak, specifically.

## 9. Validation

- Pick one customer and manually lay out their 24-month activity
  sequence (active/inactive per month); count the longest run of 1s by
  eye and confirm it matches.
- The maximum possible value across the whole result is 24 (a customer
  active in every single month) — confirm no value exceeds that.
- A `one_time` archetype customer should show `longest_active_streak_months
  = 1` (a single active month, however many orders happened within it).

## 10. Edge Cases

- A customer with zero completed orders never appears in
  `active_customers` and is correctly absent from the entire result.
- Two separate streaks of different lengths for the same customer
  (e.g., 3 active months, a gap, then 5 active months) correctly
  produce `MAX() = 5`, not a sum or an average of the two.
- This uses only `completed` orders as the activity definition —
  restricting to a narrower/broader status set would change which
  months count as "active," a judgment call worth stating explicitly
  as in Level 5.

## 11. Alternative Approach

A pure `LAG`-based approach without the full calendar grid would
mistakenly treat non-adjacent active months (with a gap month in
between) as part of the same streak, since it would only ever look at
"the previous row in the result," not "the previous calendar month" —
this is exactly why the calendar-grid step is not optional here.

## 12. Trade-offs

The calendar-grid approach costs a cross join (customers x 24 months,
a modest ~276K rows for ~11,500 active customers) but is the only
version that correctly respects true calendar adjacency rather than
"whatever row happened to come next in a filtered result."

## 13. Business Interpretation

A customer with a long, sustained active streak represents a
fundamentally different retention profile than one with the same total
order count scattered unpredictably — the former is a strong loyalty
program candidate precisely because their engagement has already
proven durable, not just frequent.
