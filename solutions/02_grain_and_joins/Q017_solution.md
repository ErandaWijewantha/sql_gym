# Reasoning

## 1. Interpret the Business Question

Finance wants confirmed-collected revenue per store, immune to the
retry-payment duplication built into the data generator (~5% of
completed orders carry both a `failed` and a `success` payment row).

## 2. Output Grain

One row = one store.

## 3. Metric Definition

Sum of `payments.amount` where `payment_status = 'success'`, with each
order contributing at most once even if it has multiple rows in
`payments`.

## 4. Required Data

`orders`: order_id, store_id.
`payments`: order_id, amount, payment_status.

## 5. Logical Decomposition

    Step 1 → filter payments to payment_status = 'success'
    Step 2 → collapse to one confirmed amount per order_id (defensive dedup)
    Step 3 → join to orders to attach store_id
    Step 4 → GROUP BY store_id, SUM

## 6. Pattern Recognition

Filtering `payment_status = 'success'` already removes the `failed`
attempt row for the 5% of orders with a retry (only the `success` row
survives), so in *this specific dataset* the filter alone prevents
duplication. But relying on that being true by construction is fragile
— the safe pattern is to defensively collapse to one row per order
*before* aggregating by store, exactly as in Q015: never assume a
child table has at most one qualifying row per parent without
guarding for it explicitly.

## 7. SQL

```sql
WITH confirmed_payment AS (
    SELECT order_id, MAX(amount) AS amount
    FROM payments
    WHERE payment_status = 'success'
    GROUP BY order_id
)
SELECT
    o.store_id,
    SUM(cp.amount) AS confirmed_revenue
FROM orders o
JOIN confirmed_payment cp ON cp.order_id = o.order_id
GROUP BY o.store_id
ORDER BY confirmed_revenue DESC;
```

## 8. Walkthrough

`confirmed_payment` groups `payments` by `order_id` *after* filtering to
successful payments, using `MAX(amount)` as a defensive collapse in
case an order somehow had more than one successful payment row (not
constructed by this generator, but not something the query should
silently assume away either). This guarantees at most one row per
order before the join to `orders`, so the subsequent `GROUP BY
store_id` + `SUM` cannot double count any order.

## 9. Validation

- Confirm `SELECT order_id, COUNT(*) FROM payments WHERE payment_status
  = 'success' GROUP BY order_id HAVING COUNT(*) > 1` returns zero rows
  in this dataset — proving the `MAX()` collapse wasn't strictly
  necessary here, but was cheap insurance against the assumption being
  wrong.
- Total `confirmed_revenue` across all stores should be noticeably
  less than Q005's gross revenue figure (which included all completed
  orders' full item totals) — since some completed orders' payments
  are still `pending` rather than `success` in edge cases, and this
  query only counts confirmed collections.

## 10. Edge Cases

- An order with a `failed` payment and no successful retry (i.e., it
  ended up `cancelled`) contributes nothing here — correctly, since
  nothing was actually collected.
- If a future data change ever introduced a genuine duplicate
  successful payment for one order (e.g., a reconciliation bug
  upstream), the `MAX(amount)` collapse means this query would silently
  keep the larger amount rather than double-count both — arguably still
  worth flagging separately as a data-quality issue rather than quietly
  absorbing it, but at least it won't corrupt the revenue total.

## 11. Alternative Approach

Skipping the `confirmed_payment` CTE and joining `orders` directly to
`payments` filtered by `WHERE payment_status='success'`, then using
`SUM(DISTINCT ...)` is *not* a safe alternative — `SUM(DISTINCT
amount)` would incorrectly collapse two *different* orders that
happen to have the identical payment amount into one contribution,
which is a different and worse bug than the one it's trying to avoid.

## 12. Trade-offs

The pre-aggregation CTE costs one extra step but removes any reliance
on an assumption about the data ("payments never has >1 success row
per order") that happens to be true today but isn't guaranteed by the
schema itself — worth the extra step for a finance-facing number.

## 13. Business Interpretation

This is the number finance should actually reconcile against bank
deposits — gross line-item revenue (Q005) and confirmed payment
revenue (this query) will diverge whenever payments are still pending,
failed without a retry, or refunded, and finance needs to know which of
the two they're looking at.
