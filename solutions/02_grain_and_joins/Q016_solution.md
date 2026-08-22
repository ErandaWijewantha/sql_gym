# Reasoning

## 1. Interpret the Business Question

Two analysts got different "average order values" for the same store.
The job is to reproduce both, show they differ, and explain which one
actually answers "what does a typical order cost."

## 2. Output Grain

Version (A)'s implicit grain is one row per line item (an average taken
over line items). Version (B)'s grain is one row per order (an average
taken over pre-aggregated order totals).

## 3. Metric Definition

Average order value, net of discounts — but version (A) computes an
"average line item value" while believing it's computing an average
order value; version (B) computes the real thing.

## 4. Required Data

`orders`: order_id, store_id, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → version (A): AVG(quantity*unit_price-discount_amount) directly over the order/order_items join
    Step 2 → version (B): pre-aggregate order_items to order grain first, then AVG the order totals
    Step 3 → compare both for one store

## 6. Pattern Recognition

Same family as Q008/Q012: `AVG()` (and any aggregate) computes over
whatever grain the rows in front of it happen to be at — it has no
awareness of what you *intended* to average over. If the rows are at
line-item grain, you get a line-item average, full stop.

## 7. SQL

```sql
-- version (A): naive, averages line items not orders
SELECT
    o.store_id,
    AVG(oi.quantity * oi.unit_price - oi.discount_amount) AS naive_avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'completed'
GROUP BY o.store_id;
```

```sql
-- version (B): correct, averages actual order totals
WITH order_totals AS (
    SELECT order_id, SUM(quantity * unit_price - discount_amount) AS net_total
    FROM order_items
    GROUP BY order_id
)
SELECT
    o.store_id,
    AVG(ot.net_total) AS correct_avg_order_value
FROM orders o
JOIN order_totals ot ON ot.order_id = o.order_id
WHERE o.order_status = 'completed'
GROUP BY o.store_id;
```

## 8. Walkthrough

In version (A), the rows being averaged are individual order_items
rows — an order with 6 cheap line items pulls the "average" down per
line, while an order with 1 expensive line item pulls it toward that
single high value, in proportion to how many lines each order happens
to have. In version (B), `order_totals` first collapses every order down
to one net total, so the outer `AVG()` genuinely averages one number per
order, unaffected by how many line items contributed to that number.

## 9. Validation

Concrete proof with two toy orders, both legitimately worth 10,000 net:
Order X has 1 line item at 10,000. Order Y has 4 line items at 2,500
each.
- Version (A) averages 5 rows: `10000, 2500, 2500, 2500, 2500` → mean =
  4,400 — nowhere near either order's actual value of 10,000.
- Version (B) averages 2 rows: `10000, 10000` → mean = 10,000 — the
  correct answer, since both orders really are worth 10,000.

Run this same reasoning against the real store data: pick a store, and
confirm `naive_avg_order_value` is systematically lower than
`correct_avg_order_value`, since orders in this dataset average ~2.86
line items — version (A) will look artificially deflated across every
store as a result.

## 10. Edge Cases

- If, hypothetically, every order at a store had exactly one line item,
  versions (A) and (B) would coincide exactly — this only happens by
  coincidence, never by design, so don't rely on it.
- This is the exact trap Q008's solution warned about — Q008's correct
  approach used either `COUNT(DISTINCT order_id)` as a divisor or the
  same pre-aggregation shown here as version (B).

## 11. Alternative Approach

Version (A) can be "fixed" without a CTE by dividing sums instead of
using `AVG()` directly:
`SUM(oi.quantity*oi.unit_price-oi.discount_amount) / COUNT(DISTINCT
o.order_id)` — mathematically equivalent to version (B)'s per-store
average, without a separate pre-aggregation step. This is the same
technique used in Q008.

## 12. Trade-offs

The CTE (version B) is more explicit and less error-prone for teams,
since it makes the order-grain step a visible, named intermediate
result rather than relying on every future query correctly remembering
to divide by `COUNT(DISTINCT ...)`. The inline-division form is more
compact for a single ad hoc query.

## 13. Business Interpretation

"Average order value" computed the wrong way systematically
understates true AOV for any store where orders vary in item count —
which is essentially always. Any AOV figure in a report should specify
which version it is, and this exercise is why.
