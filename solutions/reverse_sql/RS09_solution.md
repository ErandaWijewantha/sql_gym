# RS09 — Solution

## Grain
One row = one product category.

## What is being computed
Return rate per category, defined here as: distinct orders containing
a return for that category's products, divided by distinct orders
containing any completed line item from that category.

## Pattern
`COUNT(DISTINCT ...)` with a `LEFT JOIN` to an optional child table
(`returns`) — computing a rate where the denominator is "all matching
orders" and the numerator is "the subset that also had a return,"
without letting the `LEFT JOIN` inflate the denominator (since the join
is on the specific (order_id, product_id) pair, not just order_id
alone).

## Likely business question
"What is our return rate, broken down by category?" — related to
Q046's return-rate-definition exercise, here specifically using the
"orders affected" denominator (one of the three definitions Q046
contrasts), applied per category rather than company-wide.

## Notes
This is definition (b) from Q046 ("order return rate"), not (a) (unit
return rate) or (c) (revenue return rate) — reproducing this query with
`SUM(oi.quantity)` and `SUM(r.quantity)` instead of `COUNT(DISTINCT
...order_id)` would compute the unit-based definition instead, a
meaningfully different number.

## Verification query

```sql
SELECT
    p.category_id,
    COUNT(DISTINCT r.order_id) AS orders_with_return,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(
        COUNT(DISTINCT r.order_id) * 100.0 / COUNT(DISTINCT oi.order_id),
        2
    ) AS return_rate_pct
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
LEFT JOIN returns r ON r.order_id = oi.order_id AND r.product_id = oi.product_id
WHERE o.order_status = 'completed'
GROUP BY p.category_id;
```
