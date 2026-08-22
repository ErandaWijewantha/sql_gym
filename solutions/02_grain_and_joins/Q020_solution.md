# Reasoning

## 1. Interpret the Business Question

This is the level's capstone: build one reusable, order-grain
intermediate result, then show it correctly answers two different
questions (total revenue per store, average order value per store)
without repeating any of the grain mistakes from Q011–Q019.

## 2. Output Grain

The intermediate result: one row = one completed order. The two final
answers each collapse further to one row = one store.

## 3. Metric Definition

`net_order_value` per order = `SUM(quantity * unit_price -
discount_amount)` across that order's line items. `item_count` = number
of order_items rows for that order (not the sum of quantities — a
distinct, smaller number).

## 4. Required Data

`orders`: order_id, customer_id, store_id, order_date, sales_channel,
order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → aggregate order_items by order_id → net_order_value, item_count
    Step 2 → join that to orders (filtered to completed) → one row per order,
              carrying customer_id/store_id/order_date/sales_channel
    Step 3 → from this order-grain result: GROUP BY store_id for total revenue
    Step 4 → from the same result: GROUP BY store_id, AVG(net_order_value) for AOV

## 6. Pattern Recognition

Every prior "wrong grain" question in this level (Q011 fan-out, Q015
fan-out, Q016 average-of-line-items, Q017 payment duplication, Q019
double fan-out) traces back to the same root cause: aggregating a child
table only *after* joining it to something else that changes its
effective grain. The fix is always the same shape — pre-aggregate the
child to the grain you actually want, first, in isolation.

## 7. SQL

```sql
CREATE OR REPLACE VIEW v_order_grain_completed AS
SELECT
    o.order_id,
    o.customer_id,
    o.store_id,
    o.order_date,
    o.sales_channel,
    agg.net_order_value,
    agg.item_count
FROM orders o
JOIN (
    SELECT
        order_id,
        SUM(quantity * unit_price - discount_amount) AS net_order_value,
        COUNT(*) AS item_count
    FROM order_items
    GROUP BY order_id
) agg ON agg.order_id = o.order_id
WHERE o.order_status = 'completed';
```

```sql
SELECT
    store_id,
    SUM(net_order_value) AS total_net_revenue,
    AVG(net_order_value) AS avg_order_value,
    COUNT(*) AS completed_order_count
FROM v_order_grain_completed
GROUP BY store_id
ORDER BY total_net_revenue DESC;
```

## 8. Walkthrough

The subquery `agg` collapses `order_items` to order grain *before* it
ever touches `orders`, so the join to `orders` is a clean one-to-one
(each completed order matches exactly one `agg` row). The resulting
view is genuinely at order grain: every downstream aggregate
(`SUM`, `AVG`, plain `COUNT(*)`) behaves correctly with no special-casing
needed, because there's no fan-out left to guard against — that work
was already done once, upstream.

## 9. Validation

- `SUM(net_order_value)` from this view, grouped by store, should
  exactly equal Q005's per-store revenue figure restricted to completed
  orders (same underlying computation, different route).
- `AVG(net_order_value)` here should exactly equal Q016's "version (B)"
  result — both pre-aggregate to order grain before averaging.
- `COUNT(*)` on this view (no GROUP BY) should equal
  `SELECT COUNT(*) FROM orders WHERE order_status='completed'`.

## 10. Edge Cases

- To extend this to cancelled orders too, drop the `WHERE order_status
  = 'completed'` filter (or parameterize it) — but recompute
  `net_order_value`'s meaning carefully, since a cancelled order's
  "value" may not represent real revenue at all; this is exactly the
  kind of definitional question Level 5 trains explicitly.
- `item_count` is a `COUNT(*)` over order_items rows, not
  `SUM(quantity)` — an order with 2 line items of quantity 3 each has
  `item_count = 2`, not 6. Confusing the two would misrepresent basket
  size.

## 11. Alternative Approach

A CTE (`WITH v AS (...)`) instead of a real `VIEW` avoids persisting
anything in the schema and is preferable for one-off analysis; a real
view is preferable when multiple people/reports need the same
order-grain base repeatedly, since it centralizes the logic in one
place rather than pasting the same subquery into every report.

## 12. Trade-offs

A materialized view (if the engine supported one, MySQL doesn't
natively) would trade freshness for query speed on a large dataset; a
plain view recomputes on every query but always reflects current data —
the right choice for a training/reporting base that changes as new
orders arrive.

## 13. Business Interpretation

This is the artifact a team should actually build once and reuse,
rather than letting every analyst reinvent (and risk re-breaking) the
same order-revenue logic independently — the entire point of Level 2.
