# Reasoning

## 1. Interpret the Business Question

This is a diagnostic exercise: demonstrate exactly why `COUNT(*)` after
a one-to-many join overcounts, and why `COUNT(DISTINCT order_id)` fixes
it.

## 2. Output Grain

The comparison query's grain is a single summary row with three
numbers side by side.

## 3. Metric Definition

Three counts: raw joined-row count, distinct-order count from the join,
and the true order count from `orders` alone.

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id.

## 5. Logical Decomposition

    Step 1 → join orders to order_items for completed orders
    Step 2 → COUNT(*) over the joined rows
    Step 3 → COUNT(DISTINCT order_id) over the same joined rows
    Step 4 → compare both to a plain COUNT(*) from orders alone

## 6. Pattern Recognition

"Counting after a fan-out join" → always ask "what is one row of this
JOIN's result, and is that the same thing I want to count?" `COUNT(*)`
counts *rows of the join result* (here, line items); `COUNT(DISTINCT
order_id)` counts *distinct values of a key*, which is what "how many
orders" actually means once you're no longer at order grain.

## 7. SQL

```sql
SELECT
    COUNT(*)                    AS joined_row_count,
    COUNT(DISTINCT o.order_id)  AS distinct_order_count
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'completed';
```

```sql
SELECT COUNT(*) AS true_order_count
FROM orders
WHERE order_status = 'completed';
```

## 8. Walkthrough

The first query's `COUNT(*)` counts every (order, line item) pair —
this is the number of order_items rows belonging to completed orders,
not the number of orders. `COUNT(DISTINCT o.order_id)` instead counts
how many *unique* order_id values appear in that same joined result —
since every completed order has at least one order_items row (INNER
JOIN requires a match), this distinct count recovers exactly the number
of completed orders. The second query confirms that directly from
`orders`, with no join involved at all.

## 9. Validation

`distinct_order_count` from the first query must exactly equal
`true_order_count` from the second. `joined_row_count` will be larger
(by a factor equal to the average number of line items per order,
~2.8x in this dataset) unless every completed order happens to have
exactly one line item, which is not the case here.

## 10. Edge Cases

- If some completed order somehow had *zero* order_items rows, an
  INNER JOIN would silently exclude it, and `COUNT(DISTINCT
  o.order_id)` would then be *less* than the true order count — this
  dataset's validation checks (`orders_without_items` in
  `05_validation.sql`) confirm this never happens, but it's exactly the
  kind of assumption worth checking rather than trusting blindly.
- `SUM()` has the analogous but *not* identical issue: there's no
  "SUM(DISTINCT ...)" equivalent fix, because summing a duplicated
  *measure* (like revenue) produces a wrong total that dropping
  duplicate values can't repair — you have to avoid the fan-out
  altogether (pre-aggregate, as in Q011/Q020), not just count distinct
  keys.

## 11. Alternative Approach

Not applicable — this is the canonical diagnostic for this exact
mistake.

## 12. Trade-offs

Not applicable.

## 13. Business Interpretation

Any dashboard metric labeled "orders" that was actually computed as
`COUNT(*)` after joining in a child table is silently reporting line
items, not orders — a one-line rule (`COUNT(DISTINCT order_id)`, or
better, don't join at all if you don't need the child table) prevents
a very common class of dashboard bug.
