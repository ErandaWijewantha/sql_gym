# RS08 — Solution

## Grain
One row = one unordered pair of distinct products.

## What is being computed
The 10 pairs of products most frequently found together in the same
completed order, via a self-join on `order_items`.

## Pattern
Self-join for pairwise comparison within the same parent entity (here,
the same order) — the same technique as Q014 (employee pairs) and Q057
(market basket pairs), with `product_id_1 < product_id_2` preventing
both self-pairs and double-counted reverse pairs.

## Likely business question
"Which products are most frequently bought together?" — this is Q057
from Level 6, intended to power a "customers also bought" feature.

## Notes
`COUNT(DISTINCT oi1.order_id)` (rather than plain `COUNT(*)`) guards
against a pair being counted more than once for a single order, which
could otherwise happen if either product appeared as more than one
separate line item within that order.

## Verification query

```sql
SELECT
    oi1.product_id AS product_a,
    oi2.product_id AS product_b,
    COUNT(DISTINCT oi1.order_id) AS co_occurrence_count
FROM order_items oi1
JOIN order_items oi2
    ON oi1.order_id = oi2.order_id
   AND oi1.product_id < oi2.product_id
JOIN orders o ON o.order_id = oi1.order_id
WHERE o.order_status = 'completed'
GROUP BY oi1.product_id, oi2.product_id
ORDER BY co_occurrence_count DESC
LIMIT 10;
```
