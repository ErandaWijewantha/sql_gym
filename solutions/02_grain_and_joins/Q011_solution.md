# Reasoning

## 1. Interpret the Business Question

The task is diagnostic: reproduce a buggy query, prove it's wrong, and
fix it. The bug is a classic join fan-out caused by joining two
independent "many" tables (`order_items` and `payments`) directly to a
shared "one" table (`orders`) in the same query.

## 2. Output Grain

The naive query's *actual* grain is "one row per (order_item x
payment) combination" — not orders, not line items, not payments, but
their cross product within each order. The corrected query's grain is
one row per line item (order_items), which is what a gross-revenue SUM
should be based on.

## 3. Metric Definition

Gross revenue = `SUM(quantity * unit_price)` over completed orders'
line items — same definition as Q005.

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id, quantity, unit_price.
`payments`: order_id (only to demonstrate the bug — not needed for the
correct answer).

## 5. Logical Decomposition

    Step 1 → reproduce the naive 3-table join and its inflated total
    Step 2 → pick one order with >1 order_items row and >1 payments row
    Step 3 → show the row count that join produces for that one order
    Step 4 → write the corrected 2-table query (orders + order_items only)
    Step 5 → compare totals

## 6. Pattern Recognition

"Joining two independent 'many' tables through a shared 'one' table
multiplies rows" — the fan-out pattern. Whenever a query joins Fact A
and Fact B that both reference the same Dimension/parent, and A:parent
and B:parent are both one-to-many, the combined join is many-to-many
in effect, even though no single JOIN clause looks wrong in isolation.

## 7. SQL

```sql
-- (a) naive, buggy version --------------------------------------
SELECT SUM(oi.quantity * oi.unit_price) AS naive_gross_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN payments p      ON p.order_id  = o.order_id
WHERE o.order_status = 'completed';
```

```sql
-- (b) demonstrate the fan-out on one concrete order --------------
SELECT
    o.order_id,
    (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.order_id) AS n_items,
    (SELECT COUNT(*) FROM payments p WHERE p.order_id = o.order_id)      AS n_payments
FROM orders o
WHERE o.order_status = 'completed'
  AND (SELECT COUNT(*) FROM payments p WHERE p.order_id = o.order_id) > 1
LIMIT 1;
```

```sql
-- (c) correct version ---------------------------------------------
SELECT SUM(oi.quantity * oi.unit_price) AS correct_gross_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'completed';
```

## 8. Walkthrough

In query (a), joining `payments` into a query that's already at
order_items grain means every line item of an order gets repeated once
per payment row for that order. An order with 3 line items and 2
payment rows (1 failed + 1 successful retry) contributes 3 x 2 = 6 rows
to the join, and `SUM(quantity * unit_price)` counts each line item's
value twice. Query (b) isolates one such order and shows the item/payment
counts directly, proving the fan-out is real. Query (c) drops `payments`
entirely — it was never needed for a revenue total — and gets the
correct, unduplicated sum.

## 9. Validation

- `naive_gross_revenue` should be noticeably higher than
  `correct_gross_revenue` (roughly proportional to how many orders have
  2 payment rows — about 5% of completed orders, so expect the naive
  total to be inflated by a few percent, not doubled outright).
- `correct_gross_revenue` should exactly equal Q005's completed-orders
  gross revenue total (same query, in fact).
- For the one order surfaced in query (b), manually verify: sum its
  order_items 3 times over (once) vs however many payment rows it has,
  and confirm the naive query's contribution for that order is
  `(true line total) * n_payments`.

## 10. Edge Cases

- An order with exactly 1 payment row and 1 order_items row is *not*
  affected by the bug at all — the fan-out only shows up once either
  side has more than one row, which is why the naive total's inflation
  is proportional (not universal).
- Cancelled orders with a `failed` payment attempt are excluded from
  both queries here by the `order_status = 'completed'` filter, so
  they're irrelevant to this specific comparison.

## 11. Alternative Approach

If you truly needed a per-order view that includes both item detail
and payment detail without fan-out, the correct structure is two
independent pre-aggregations (order_items summed to order grain,
payments summed/deduped to order grain) joined to each other on
`order_id` — never a direct 3-way fact join. See Q020.

## 12. Trade-offs

There's no legitimate version of the naive 3-table join that's ever
"good enough" — it's not a stylistic trade-off, it's simply incorrect.
The lesson is structural: know each table's grain *before* deciding how
many tables belong in one JOIN chain.

## 13. Business Interpretation

Any revenue figure computed by directly joining multiple fact tables
that each fan out from `orders` should be treated as suspect until
proven otherwise — this is one of the most common ways a real
dashboard silently overstates revenue.
