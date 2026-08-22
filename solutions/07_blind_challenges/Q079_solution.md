# Reasoning

## 1. Interpret the Business Question

Find customers whose chronologically most recent order ended badly
(cancelled or refunded) — a "last impression" signal, distinct from
overall cancellation rate.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

For each customer, identify their single most recent order (by
`order_date`) and check whether its `order_status` is `cancelled` or
`refunded`.

## 4. Required Data

`orders`: customer_id, order_date, order_status.

## 5. SQL

```sql
WITH ranked AS (
    SELECT
        customer_id,
        order_date,
        order_status,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
    FROM orders
)
SELECT customer_id, order_date AS most_recent_order_date, order_status
FROM ranked
WHERE rn = 1
  AND order_status IN ('cancelled', 'refunded');
```

## 6. Walkthrough

`ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC)`
numbers each customer's orders from most recent (1) backward — the
same technique used in Q034's reactivation query. Filtering to `rn = 1`
isolates exactly the single most recent order per customer, and the
final `WHERE` checks its status.

## 7. Validation

- Pick one resulting customer and manually confirm their true most
  recent order (by directly querying and sorting) has the shown status.
- Confirm no customer appears more than once in the result (guaranteed
  by `rn = 1` selecting exactly one row per customer).

## 8. Edge Cases

- A customer whose most recent order was cancelled but who has *other*,
  earlier successful orders is still included — this question is
  specifically about the *last* impression, not overall order history.
- A customer with only one order ever, which happens to be cancelled
  or refunded, is included — `rn=1` works correctly even with a single
  row per partition.
- Two orders on the exact same `order_date` (down to the second) for
  one customer would be a genuine tie for "most recent" — `ROW_NUMBER()`
  breaks it arbitrarily; add a secondary `ORDER BY order_id DESC` if a
  deterministic tiebreak matters.

## 9. Alternative Approach

A `GROUP BY customer_id` with `MAX(order_date)` joined back to `orders`
to recover that specific order's status would produce the same result,
but requires an extra join step; the window-function version is more
direct.

## 10. Trade-offs

Not applicable — the window-function version is the clear, idiomatic
choice for "the most recent row per group, with its full row detail."

## 11. Business Interpretation

This is a precise, low-noise outreach list for customer success — these
customers' last interaction with the company was negative, making them
a meaningfully higher churn risk than someone whose last order simply
completed normally a while ago.
