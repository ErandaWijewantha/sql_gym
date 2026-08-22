# Reasoning

## 1. Interpret the Business Question

Store operations wants two things per store, for the busiest 10 stores:
(a) confirmation they're in the top 10 by completed order volume, and
(b) their average order value. The subtlety is that "average order
value" must be computed at the *order* grain, not the line-item grain.

## 2. Output Grain

One row = one store (limited to the 10 with the most completed orders).

## 3. Metric Definition

Average order value (AOV), net of discounts:
`SUM(quantity * unit_price - discount_amount) / COUNT(DISTINCT order_id)`
— i.e., total net revenue divided by number of orders, *not* an average
taken directly over order_items rows.

## 4. Required Data

`orders`: order_id, store_id, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.
`stores`: store_id, store_name (for readability).

## 5. Logical Decomposition

    Step 1 → filter to completed orders
    Step 2 → join to order_items
    Step 3 → per store: SUM(net line amount) and COUNT(DISTINCT order_id)
    Step 4 → AOV = net revenue / distinct order count
    Step 5 → order by order count descending, limit 10

## 6. Pattern Recognition

This is the first place in the gym where "average" needs care: a naive
`AVG(quantity*unit_price-discount_amount)` computed directly over the
joined (store, order, order_item) rows would average *line items*, not
*orders* — an order with 5 line items would be counted 5 times, biasing
the "average" toward orders with more items. The fix is to compute the
numerator and denominator explicitly rather than reaching for `AVG()`
naively. (Level 2's Q016 examines this trap in depth.)

## 7. SQL

```sql
SELECT
    s.store_id,
    s.store_name,
    COUNT(DISTINCT o.order_id)  AS completed_order_count,
    SUM(oi.quantity * oi.unit_price - oi.discount_amount)
        / COUNT(DISTINCT o.order_id) AS avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN stores s        ON s.store_id  = o.store_id
WHERE o.order_status = 'completed'
GROUP BY s.store_id, s.store_name
ORDER BY completed_order_count DESC
LIMIT 10;
```

## 8. Walkthrough

The join to `order_items` puts us at line-item grain, so
`COUNT(DISTINCT o.order_id)` is essential — it counts *distinct orders*
represented in that store's line items, not the number of line-item
rows. The numerator sums net line-item value across all of a store's
completed orders. Dividing the two gives a true per-order average.
`ORDER BY completed_order_count DESC LIMIT 10` selects the 10
busiest stores by order volume (as the question specifies — this is a
*different* ranking than "highest AOV").

## 9. Validation

- Pick one store from the result and independently compute its AOV via
  a separate query that pre-aggregates order_items to order grain first
  (see Alternative Approach) — the two numbers must match exactly.
- `completed_order_count` should be a plausible fraction of that
  store's total orders (roughly ~90%, matching the overall completed
  rate).
- If you'd (incorrectly) used plain `AVG()` over the joined rows, you'd
  get a *different, wrong* number for stores whose orders vary a lot in
  item count — comparing the two is a good way to feel the bug.

## 10. Edge Cases

- A store with zero completed orders wouldn't appear here at all (inner
  joins require a match) — correctly excluded, since AOV is undefined
  for zero orders anyway.
- If a store has completed orders with wildly different item counts,
  the naive-`AVG()` version and the correct version can diverge
  substantially — this is exactly the scenario the data generator
  creates (order item counts range 1-8 with a long right tail).

## 11. Alternative Approach

Pre-aggregate order_items to order-grain first, then join to orders/stores:

```sql
WITH order_totals AS (
    SELECT order_id, SUM(quantity * unit_price - discount_amount) AS net_total
    FROM order_items
    GROUP BY order_id
)
SELECT
    s.store_id,
    s.store_name,
    COUNT(*) AS completed_order_count,
    AVG(ot.net_total) AS avg_order_value
FROM orders o
JOIN order_totals ot ON ot.order_id = o.order_id
JOIN stores s ON s.store_id = o.store_id
WHERE o.order_status = 'completed'
GROUP BY s.store_id, s.store_name
ORDER BY completed_order_count DESC
LIMIT 10;
```

Here, `order_totals` is already at order grain, so a plain `AVG()` in
the outer query is correct without needing `COUNT(DISTINCT ...)`.

## 12. Trade-offs

The CTE version is arguably more readable and less error-prone (it
makes the order-grain intermediate result explicit, and a plain `AVG()`
"just works"), at the cost of an extra query stage. The single-query
`COUNT(DISTINCT)` version is more compact but relies on the reader
correctly recognizing why `COUNT(DISTINCT ...)` is necessary — a subtle
enough point that the CTE version is the safer default in production.

## 13. Business Interpretation

This tells store operations which busy stores also carry high-value
baskets versus high volume of smaller orders — two stores with
identical order counts but very different AOV likely need different
merchandising or upsell strategies.
