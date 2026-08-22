# RS10 — Solution

## Grain
One row = one customer.

## What is being computed
Every customer whose total net spend (completed orders) exceeds the
*overall average* total spend across *all* purchasing customers — a
single global benchmark, not a per-region or per-segment one.

## Pattern
Non-correlated subquery against a global aggregate — the inner
`all_totals` subquery computes one single number (the average of every
customer's total spend) completely independently of the outer query's
rows, then the outer query filters against that one fixed value.

## Likely business question
"Which customers spend more than the average customer?" — a simpler,
ungrouped cousin of Q028's "spend above their *regional* average"
question. The key structural difference: Q028's comparison value
depends on which region a given customer belongs to (a *correlated*
comparison), while this query's comparison value is the same single
number for every customer (a *non-correlated* one).

## Notes
Because the inner subquery here doesn't reference anything from the
outer query (no correlation), MySQL can compute it exactly once and
reuse the result for every row's comparison — a materially cheaper
operation than a correlated subquery that must be re-evaluated (at
least conceptually) once per outer row.

## Verification query

```sql
SELECT customer_id, total_spend
FROM (
    SELECT
        c.customer_id,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS total_spend
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id
) customer_totals
WHERE total_spend > (
    SELECT AVG(total_spend) FROM (
        SELECT SUM(oi2.quantity * oi2.unit_price - oi2.discount_amount) AS total_spend
        FROM customers c2
        JOIN orders o2 ON o2.customer_id = c2.customer_id AND o2.order_status = 'completed'
        JOIN order_items oi2 ON oi2.order_id = o2.order_id
        GROUP BY c2.customer_id
    ) all_totals
);
```
