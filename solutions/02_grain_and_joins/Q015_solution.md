# Reasoning

## 1. Interpret the Business Question

Supply chain needs net units sold per product. The diagnostic half of
the task is showing why joining `order_items` straight to `returns` on
`product_id` alone is a fan-out trap, structurally identical to Q011
but between two child tables instead of a child and its parent's
sibling.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

Net units sold = total quantity sold (from order_items) minus total
quantity returned (from returns), computed independently per side.

## 4. Required Data

`order_items`: product_id, quantity.
`returns`: product_id, quantity.

## 5. Logical Decomposition

    Step 1 → aggregate order_items by product_id → units_sold
    Step 2 → aggregate returns by product_id → units_returned
    Step 3 → LEFT JOIN units_sold to units_returned on product_id
    Step 4 → COALESCE missing returns to 0
    Step 5 → net = units_sold - units_returned

## 6. Pattern Recognition

"Combine two independent 'many' tables that share a dimension key, but
aren't directly related to each other" → pre-aggregate each side to the
shared grain *first*, then join the two summaries. Never join the two
raw fact tables directly on just the shared key.

## 7. SQL

```sql
WITH sold AS (
    SELECT product_id, SUM(quantity) AS units_sold
    FROM order_items
    GROUP BY product_id
),
returned AS (
    SELECT product_id, SUM(quantity) AS units_returned
    FROM returns
    GROUP BY product_id
)
SELECT
    s.product_id,
    s.units_sold,
    COALESCE(r.units_returned, 0) AS units_returned,
    s.units_sold - COALESCE(r.units_returned, 0) AS net_units_sold
FROM sold s
LEFT JOIN returned r ON r.product_id = s.product_id
ORDER BY net_units_sold DESC;
```

## 8. Walkthrough

Both `sold` and `returned` collapse their source table down to one row
per `product_id` *before* any join happens — at that point, joining
them on `product_id` is a clean one-to-one (or one-to-zero) join, since
each side now has at most one row per product. `LEFT JOIN` (not `JOIN`)
from `sold` preserves products with sales but zero returns; `COALESCE`
turns the resulting NULL into 0 so the subtraction works.

## 9. Validation

- Compare against the naive fan-out version
  (`SELECT product_id, SUM(oi.quantity) FROM order_items oi JOIN returns
  r ON r.product_id = oi.product_id GROUP BY product_id`) for one
  popular product — the naive version's sum will be inflated roughly by
  a factor equal to that product's return-row count, proving the bug.
- `net_units_sold` should never exceed `units_sold`, and should be
  non-negative for every product (validated separately by
  `05_validation.sql`'s `returns_exceeding_purchased_qty` check, which
  operates at the correct order+product grain rather than just
  product-level).

## 10. Edge Cases

- Products with sales but zero returns must still appear with
  `units_returned = 0`, not be silently dropped — this is exactly what
  the `LEFT JOIN` + `COALESCE` combination guarantees.
- Products that were never sold at all (the data generator's
  deliberate ~5% "never sold" set) don't appear in `sold` and therefore
  don't appear in this result at all — correct, since "net units sold"
  is undefined for a product with zero sales.
- Note this product-level net figure is coarser than the
  order+product-level check in `05_validation.sql` — a product could
  show a healthy net total here while still having one specific
  over-returned order line hiding underneath it.

## 11. Alternative Approach

A single query using two independent scalar-subquery-style aggregates
in the SELECT list (`(SELECT SUM(quantity) FROM returns r WHERE
r.product_id = p.product_id)`) driven off a `products` or `DISTINCT
product_id` base achieves the same result without CTEs, at the cost of
re-scanning `returns` once per product row — the CTE version is
preferred for both clarity and performance at this data volume.

## 12. Trade-offs

The CTE version is more verbose but scales cleanly and is easy to
extend (e.g., adding a third independent fact like `inventory` follows
the same "aggregate first, then join" recipe). The correlated-subquery
version is more compact for a one-off check but doesn't generalize well.

## 13. Business Interpretation

This gives supply chain a trustworthy net-sales figure per product to
feed replenishment — critically, one that isn't silently inflated by
however many return records happen to exist for popular items.
