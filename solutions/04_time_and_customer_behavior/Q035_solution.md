# Reasoning

## 1. Interpret the Business Question

Marketing suspects a post-New-Year drop-off and wants the exact list of
customers who ordered in January 2025 but went silent in February 2025
— a time-windowed anti-join.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

No numeric metric — a set-difference condition between two
independently defined time-windowed populations.

## 4. Required Data

`orders`: customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → build the set of customers who ordered in January 2025
    Step 2 → build the set of customers who ordered in February 2025
    Step 3 → keep customers in the first set but not the second

## 6. Pattern Recognition

Same anti-join shape as Q013 (never ordered) and Q029 (never bought a
category) — here the "excluding" condition is a *different time
window* rather than "no match at all" or "a different category."

## 7. SQL

```sql
SELECT DISTINCT o1.customer_id
FROM orders o1
WHERE o1.order_date >= '2025-01-01' AND o1.order_date < '2025-02-01'
  AND NOT EXISTS (
      SELECT 1 FROM orders o2
      WHERE o2.customer_id = o1.customer_id
        AND o2.order_date >= '2025-02-01' AND o2.order_date < '2025-03-01'
  );
```

## 8. Walkthrough

The outer query scans `orders` restricted to January 2025 — this is
"customers who ordered in January," though a customer could appear
multiple times here if they placed several January orders, which is
why `DISTINCT` (or an outer `GROUP BY`) is needed. The correlated
`NOT EXISTS` subquery then checks, per customer, whether *any* February
2025 order exists for them; if none does, the anti-join condition holds
and that customer survives the filter.

## 9. Validation

- Pick one resulting customer_id and confirm directly:
  `SELECT order_date FROM orders WHERE customer_id = <id> AND order_date
  >= '2025-01-01' AND order_date < '2025-03-01'` should show at least
  one January row and zero February rows.
- The half-open date ranges (`>= ... AND < ...`) avoid the classic
  boundary bug from Q006 — double check no January 31st late-night
  order or February 28th order is mishandled.

## 10. Edge Cases

- Order status isn't filtered here — a cancelled January order still
  counts as "activity" for this investigation, consistent with the
  lifecycle framing used in Q031/Q033. If marketing specifically wanted
  "placed a *completed* order in January," add
  `AND o1.order_status = 'completed'` (and the equivalent inside the
  subquery for February, if February completed orders specifically
  should count as "still active").
- A customer who ordered in January, *and* December, and *not* February
  is still included — this question only cares about January and
  February, not the customer's broader history.

## 11. Alternative Approach

```sql
WITH jan_customers AS (
    SELECT DISTINCT customer_id FROM orders
    WHERE order_date >= '2025-01-01' AND order_date < '2025-02-01'
),
feb_customers AS (
    SELECT DISTINCT customer_id FROM orders
    WHERE order_date >= '2025-02-01' AND order_date < '2025-03-01'
)
SELECT j.customer_id
FROM jan_customers j
LEFT JOIN feb_customers f ON f.customer_id = j.customer_id
WHERE f.customer_id IS NULL;
```

This builds both populations as explicit named CTEs first, then
anti-joins them via `LEFT JOIN`/`IS NULL` — functionally identical to
the `NOT EXISTS` version, and arguably clearer about the "two sets,
then subtract" structure of the question.

## 12. Trade-offs

The `NOT EXISTS` version is more compact; the two-CTE version makes the
"population A minus population B" framing explicit, which can help
when explaining the query to a non-technical stakeholder. Both perform
comparably at this data volume.

## 13. Business Interpretation

This is the exact list marketing needs for a targeted "we miss you"
follow-up — critically, it's scoped to people who were *just* active,
making a reactivation message far more timely and relevant than a
generic win-back campaign aimed at long-dormant customers.
