# AS01 — Solution

This exact comparison is worked through in full in
`solutions/03_analytical_patterns/Q028_solution.md` — that file
contains all three approaches' complete, tested SQL. This page adds the
production-recommendation discussion the training file asked for.

## Approach A — CTE + JOIN

```sql
WITH customer_spend AS (
    SELECT c.customer_id, c.region,
           SUM(oi.quantity*oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.region
),
region_avg AS (
    SELECT region, AVG(total_spend) AS avg_spend
    FROM customer_spend GROUP BY region
)
SELECT cs.customer_id, cs.region, cs.total_spend, ra.avg_spend
FROM customer_spend cs
JOIN region_avg ra ON ra.region = cs.region
WHERE cs.total_spend > ra.avg_spend;
```

## Approach B — Window Function

```sql
WITH customer_spend AS (
    SELECT c.customer_id, c.region,
           SUM(oi.quantity*oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.region
)
SELECT customer_id, region, total_spend, region_avg_spend
FROM (
    SELECT customer_id, region, total_spend,
           AVG(total_spend) OVER (PARTITION BY region) AS region_avg_spend
    FROM customer_spend
) t
WHERE total_spend > region_avg_spend;
```

## Approach C — Correlated Subquery

```sql
WITH customer_spend AS (
    SELECT c.customer_id, c.region,
           SUM(oi.quantity*oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.region
)
SELECT cs.customer_id, cs.region, cs.total_spend
FROM customer_spend cs
WHERE cs.total_spend > (
    SELECT AVG(cs2.total_spend) FROM customer_spend cs2 WHERE cs2.region = cs.region
);
```

## Comparison

| | Intermediate results needed | Conceptual scans of spend data | Readability without window-function familiarity |
|---|---|---|---|
| A (CTE+JOIN) | 2 (spend, then regional avg) | 2 | Highest — every step is a named, ordinary aggregation |
| B (Window) | 1 | 1 | Lower — requires understanding PARTITION BY semantics |
| C (Correlated subquery) | 1 (but re-evaluated per row) | 1 + N (re-scanned per customer, conceptually) | Medium — reads closest to the English sentence, but performance isn't obvious from the syntax |

## Recommendation

**Approach B (window function)** is the standard production choice once
a team is comfortable with window syntax — it avoids the second
aggregation pass of Approach A and avoids the per-row re-evaluation risk
of Approach C, while still being fully declarative and index-friendly.
**Approach A** is the right choice for a team or a specific report
where window-function unfamiliarity would make B harder to maintain
than the extra verbosity of A is worth. **Approach C** is rarely the
best production choice for this shape — it exists here mainly to make
the performance cost of correlated subqueries concrete, and to motivate
learning B.
