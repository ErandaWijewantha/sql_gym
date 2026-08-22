# RS03 — Solution

## Grain
One row = one product category.

## What is being computed
Total gross revenue (completed orders) per category, keeping only
categories above LKR 50,000,000.

## Pattern
`GROUP BY` + `HAVING` — filtering on an aggregate value, not a raw row
attribute.

## Likely business question
"Which product categories generated more than LKR 50,000,000 in
sales?" — this is exactly Q006 from Level 1.

## Notes
`HAVING` (not `WHERE`) is required here because the filter condition
(`SUM(...) > 50000000`) depends on the aggregated value, which doesn't
exist until after `GROUP BY` has collapsed the rows.

## Verification query

```sql
SELECT
    c.category_name,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p      ON p.product_id = oi.product_id
JOIN categories c     ON c.category_id = p.category_id
WHERE o.order_status = 'completed'
GROUP BY c.category_name
HAVING SUM(oi.quantity * oi.unit_price) > 50000000
ORDER BY total_revenue DESC;
```
