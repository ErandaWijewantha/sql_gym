# Reasoning

## 1. Interpret the Business Question

Marketing wants customers who outspend their own region's average — a
"compare to group benchmark" question, which is exactly the shape
covered in depth by `training/approach_selection/AS01.md`. This
solution presents the same three approaches side by side.

## 2. Output Grain

One row = one customer (restricted to those above their region's
average).

## 3. Metric Definition

Per-customer total net spend (completed orders) compared against the
average of that same per-customer total, computed across all customers
sharing the same region.

## 4. Required Data

`customers`: customer_id, region.
`orders`: order_id, customer_id, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute total net spend per customer (completed orders)
    Step 2 → compute the average of that spend, per region
    Step 3 → keep customers whose own spend exceeds their region's average

## 6. Pattern Recognition

"Compare an entity to its own group's benchmark" → three equally valid
structures: CTE + JOIN, window function `AVG(...) OVER (PARTITION BY
...)`, or a correlated subquery. None is universally "the" right
answer — see `docs/approach_selection.md`.

## 7. SQL — Approach A: CTE + JOIN

```sql
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.region,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o        ON o.customer_id = c.customer_id
    JOIN order_items oi  ON oi.order_id   = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY c.customer_id, c.region
),
region_avg AS (
    SELECT region, AVG(total_spend) AS avg_spend
    FROM customer_spend
    GROUP BY region
)
SELECT cs.customer_id, cs.region, cs.total_spend, ra.avg_spend
FROM customer_spend cs
JOIN region_avg ra ON ra.region = cs.region
WHERE cs.total_spend > ra.avg_spend
ORDER BY cs.region, cs.total_spend DESC;
```

## Approach B: Window Function

```sql
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.region,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o        ON o.customer_id = c.customer_id
    JOIN order_items oi  ON oi.order_id   = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY c.customer_id, c.region
)
SELECT customer_id, region, total_spend, region_avg_spend
FROM (
    SELECT
        customer_id, region, total_spend,
        AVG(total_spend) OVER (PARTITION BY region) AS region_avg_spend
    FROM customer_spend
) t
WHERE total_spend > region_avg_spend
ORDER BY region, total_spend DESC;
```

## Approach C: Correlated Subquery

```sql
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.region,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o        ON o.customer_id = c.customer_id
    JOIN order_items oi  ON oi.order_id   = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY c.customer_id, c.region
)
SELECT cs.customer_id, cs.region, cs.total_spend
FROM customer_spend cs
WHERE cs.total_spend > (
    SELECT AVG(cs2.total_spend)
    FROM customer_spend cs2
    WHERE cs2.region = cs.region
)
ORDER BY cs.region, cs.total_spend DESC;
```

## 8. Walkthrough

All three approaches share the same first step: `customer_spend` must
exist as a customer-grain pre-aggregation before any regional
comparison is meaningful (skipping this and comparing raw order_items
rows would repeat Q016's grain mistake). From there:
- **A** computes the regional averages as their own named result and
  joins them back — the most explicit, step-by-step version.
- **B** computes the same average as a window function sitting
  alongside each customer row, avoiding a second aggregation pass; it's
  wrapped in an outer query because a window function's result can't be
  referenced directly in the same-level `WHERE`.
- **C** recomputes the region's average once per customer row via a
  subquery correlated on `region` — conceptually the most "obvious"
  translation of the English sentence ("their spend is more than average
  spend in their region"), at the cost of re-scanning `customer_spend`
  once per outer row.

## 9. Validation

All three approaches must return the *identical* set of customer_ids —
run any two side by side and confirm output parity (e.g., an outer
`EXCEPT`/anti-join between the two result sets should be empty). Pick
one region, compute its average manually, and confirm the count of
customers above it looks like a minority of that region's customers
(by definition, an average splits a population roughly in half only for
symmetric distributions — with skewed spend, expect meaningfully more
or less than half above average).

## 10. Edge Cases

- Customers with a `NULL` region are excluded from every version here
  (since `GROUP BY region` and `PARTITION BY region` both treat NULL
  as its own group, and the comparison would be "above the average of
  other NULL-region customers," which is a legitimate but probably
  unintended reading) — worth flagging explicitly if marketing didn't
  anticipate a NULL-region bucket.
- A customer with zero completed orders never appears in
  `customer_spend`, and is correctly excluded from all three versions.

## 11. Alternative Approach

See section 7 above — this question's entire point is presenting three
alternatives together rather than one primary solution with
alternatives appended.

## 12. Trade-offs

- **CTE + JOIN**: most readable for someone unfamiliar with window
  functions; requires two aggregation passes conceptually, though the
  optimizer may handle this efficiently.
- **Window function**: most compact, avoids a second explicit
  aggregation step, and is the natural choice once a team is
  comfortable with window syntax; the outer-query wrapper (to filter on
  the window result) adds a small amount of nesting.
- **Correlated subquery**: reads closest to the original English
  sentence, but is the least efficient of the three at scale, since the
  subquery conceptually re-runs per outer row (MySQL's optimizer may
  partially mitigate this, but it's not guaranteed).

In production, the window-function version (B) is the most common
choice for this exact shape once a team has the SQL maturity for it;
the CTE+JOIN version (A) is a reasonable default otherwise.

## 13. Business Interpretation

This identifies over-indexed spenders relative to their own regional
peer group — useful for a loyalty-tier upgrade offer specifically
because it's *relative*, not absolute: a customer in a lower-spending
region who's still a standout there may be just as valuable to retain
as a high-absolute-spender in a wealthier region.
