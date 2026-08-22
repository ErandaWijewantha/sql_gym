# Reasoning

## 1. Interpret the Business Question

Per store, find the single worst day by total returned value (original
sale value of the returned units).

## 2. Output Grain

One row = one store (its single worst day).

## 3. Metric Definition

`returned_value = SUM(returns.quantity * order_items.unit_price)` for
the matching (order_id, product_id), grouped by (store, return_date).

## 4. Required Data

`returns`: order_id, product_id, return_date, quantity.
`order_items`: order_id, product_id, unit_price.
`orders`: order_id, store_id.

## 5. Logical Decomposition

    Step 1 → join returns to order_items to recover each returned unit's
              original sale price, and to orders for store_id
    Step 2 → sum returned_value per (store_id, return_date)
    Step 3 → per store, keep the single highest-value day

## 6. SQL

```sql
WITH daily_store_returns AS (
    SELECT
        o.store_id,
        r.return_date,
        SUM(r.quantity * oi.unit_price) AS returned_value
    FROM returns r
    JOIN order_items oi ON oi.order_id = r.order_id AND oi.product_id = r.product_id
    JOIN orders o ON o.order_id = r.order_id
    GROUP BY o.store_id, r.return_date
),
ranked AS (
    SELECT
        store_id, return_date, returned_value,
        ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY returned_value DESC) AS rn
    FROM daily_store_returns
)
SELECT store_id, return_date, returned_value
FROM ranked
WHERE rn = 1
ORDER BY returned_value DESC;
```

## 7. Walkthrough

Joining `returns` to `order_items` on the matching (order_id,
product_id) pair recovers the specific `unit_price` each returned unit
was actually sold at — a return row alone doesn't carry price
information. `orders` supplies `store_id`. `daily_store_returns`
collapses to one row per (store, day); `ROW_NUMBER()` then picks the
single top day per store.

## 8. Validation

- Confirm exactly one row per store in the final result.
- Manually verify one store's top day by listing its
  `daily_store_returns` rows sorted descending.

## 9. Edge Cases

- A store with only a handful of total returns still gets a "worst
  day" — it's just whichever day (possibly a very small value) happens
  to be its maximum; worth pairing this with the store's overall return
  volume for context.
- Ties for the top day within a store both would need `RANK()` instead
  of `ROW_NUMBER()` if the business wants to see every tied top day
  rather than an arbitrary one.

## 10. Alternative Approach

A correlated subquery (`WHERE returned_value = (SELECT MAX(returned_value)
FROM daily_store_returns d2 WHERE d2.store_id = daily_store_returns.store_id)`)
achieves the same result, correctly showing all ties, at the cost of a
per-row subquery re-scan.

## 11. Trade-offs

`ROW_NUMBER()` guarantees exactly one row per store (arbitrary tiebreak)
and is simpler; the correlated-subquery/`RANK()` alternative correctly
surfaces ties, which matters if the business cares about seeing every
day that shares the maximum.

## 12. Business Interpretation

This gives operations a specific date per store to investigate — cross-
referencing against `return_reason` for that day could reveal a
systemic issue (e.g., a bad batch of a specific product) rather than
routine background returns.
