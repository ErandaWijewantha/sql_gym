# AS03 — Solution

## Approach A — Ranking Window Function

```sql
WITH product_revenue AS (
    SELECT p.product_id, p.product_name, p.category_id,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.product_name, p.category_id
)
SELECT product_id, product_name, category_id, revenue
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY revenue DESC) AS rn
    FROM product_revenue
) t
WHERE rn = 1;
```

## Approach B — Correlated Subquery with MAX

```sql
WITH product_revenue AS (
    SELECT p.product_id, p.product_name, p.category_id,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.product_name, p.category_id
)
SELECT pr.product_id, pr.product_name, pr.category_id, pr.revenue
FROM product_revenue pr
WHERE pr.revenue = (
    SELECT MAX(pr2.revenue) FROM product_revenue pr2 WHERE pr2.category_id = pr.category_id
);
```

## Comparison

1. **Under Approach B with a tie**: `WHERE pr.revenue = (SELECT
   MAX(...))` returns **every** product whose revenue equals the
   category maximum — if two products in "Mobile Phones" are tied for
   #1, Approach B correctly returns both of them.
2. **Under Approach A with `ROW_NUMBER()` and that same tie**:
   `ROW_NUMBER()` still only ever returns exactly one row per category
   at `rn = 1` — it arbitrarily picks one of the two tied products (by
   whatever order MySQL happens to break the tie, unless a secondary
   `ORDER BY` key like `product_id` is added) and silently drops the
   other, even though it's equally "the top product."
3. **RANK() vs ROW_NUMBER()**: `RANK()` would behave like Approach B in
   this respect — both tied products would receive rank 1, and filtering
   to `rnk = 1` would return both. If a stakeholder asks for "the" top
   product expecting exactly one answer, `ROW_NUMBER()` guarantees
   that (at the cost of arbitrarily resolving real ties); if they want
   to see every product that's genuinely tied for the top, `RANK()` (or
   Approach B) is correct instead.

## Recommendation

Use **`RANK()`** (a small variant of Approach A) as the default —
it's exactly as efficient as `ROW_NUMBER()` but doesn't silently hide a
genuine tie the way `ROW_NUMBER()` does. Reserve plain **`ROW_NUMBER()`**
for when the business has explicitly said they want exactly one row no
matter what (with an agreed tiebreak rule). Approach B (correlated
`MAX` subquery) is a reasonable alternative for a single ad hoc check,
but scales worse than a window function and is less idiomatic once
window functions are available (MySQL 8+, which this project targets).
