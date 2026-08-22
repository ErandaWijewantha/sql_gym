# Reasoning

## 1. Interpret the Business Question

Category managers already know the #1 product per (brand, category);
they want the runner-up — the product most likely to become the next
hero SKU.

## 2. Output Grain

One row = one (brand, category) combination with >= 2 distinct products
sold, showing its second-highest-revenue product.

## 3. Metric Definition

Gross revenue per product (completed orders), ranked within each
(brand, category) group; "second highest" uses `DENSE_RANK()` so that
if two products are exactly tied for #1, there is still a well-defined
#2 (the next *distinct* revenue value), rather than `ROW_NUMBER()`
arbitrarily picking one of the tied products as "#1" and the other as
"#2."

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id, product_id, quantity, unit_price.
`products`: product_id, category_id, brand_id.

## 5. Logical Decomposition

    Step 1 → compute gross revenue per product
    Step 2 → DENSE_RANK products within each (brand_id, category_id) group,
              ordered by revenue descending
    Step 3 → keep rank = 2

## 6. Pattern Recognition

"The Nth highest, not just the highest" → the naive trap is something
like `MAX(revenue) WHERE revenue != (SELECT MAX(revenue) ...)`, which
silently breaks the moment there's a tie for first place (it would
exclude *all* products tied for #1, then return the actual 3rd-highest
value as if it were 2nd). The robust fix is a ranking window function
with an explicit tie-handling choice.

## 7. SQL

```sql
WITH product_revenue AS (
    SELECT
        p.product_id,
        p.product_name,
        p.brand_id,
        p.category_id,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.product_name, p.brand_id, p.category_id
),
ranked AS (
    SELECT
        *,
        DENSE_RANK() OVER (PARTITION BY brand_id, category_id ORDER BY revenue DESC) AS rnk
    FROM product_revenue
)
SELECT brand_id, category_id, product_id, product_name, revenue
FROM ranked
WHERE rnk = 2
ORDER BY brand_id, category_id;
```

## 8. Walkthrough

`product_revenue` pre-aggregates to product grain (standard
pre-aggregation, per Level 2). `DENSE_RANK() OVER (PARTITION BY
brand_id, category_id ORDER BY revenue DESC)` assigns rank 1 to the
highest-revenue product(s) in each brand-category group, and — because
`DENSE_RANK` never skips numbers after a tie — rank 2 always refers to
the product(s) at the *next distinct revenue value* below the top,
regardless of how many products tied for #1. Filtering to `rnk = 2`
directly answers "the runner-up."

## 9. Validation

- Pick one (brand_id, category_id) group with no ties, list its
  products' revenue sorted descending by hand, and confirm the query's
  #2 matches the actual second-highest value.
- Deliberately construct (or find, if one exists) a group with two
  products tied for #1 and confirm the query correctly returns the
  *3rd*-highest distinct value's product as rank 2 in that case, not an
  arbitrary pick between the two tied products.
- Confirm no (brand_id, category_id) group with only 1 product sold
  appears in the output — there's no "second" for it.

## 10. Edge Cases

- If two products tie for the *second*-highest revenue value, both
  will appear in the output (both get `rnk = 2` under `DENSE_RANK`) —
  arguably correct ("here are your #2 candidates"), though it means the
  output isn't guaranteed to be exactly one row per group; if category
  managers specifically want exactly one runner-up regardless of ties,
  `ROW_NUMBER()` with a deterministic tiebreak (e.g., `ORDER BY revenue
  DESC, product_id`) would be needed instead — a different, and
  arguably less honest, answer to "who's really in second place."
- A (brand, category) combination with only 1 product ever sold
  correctly produces no rank-2 row at all (there's nothing to rank
  against).

## 11. Alternative Approach

A correlated subquery counting, for each product, "how many distinct
revenue values in its brand-category group are strictly higher than
its own," keeping products where that count equals exactly 1, achieves
the same tie-safe result without `DENSE_RANK` — more verbose, and
re-scans the group per product, but a useful way to understand what
`DENSE_RANK` is doing under the hood.

## 12. Trade-offs

`DENSE_RANK()` is the clear preferred tool here — it directly encodes
"the next distinct value down" without any manual correlated-count
logic, and its behavior under ties is exactly what "the #2 product"
should mean when ties are possible.

## 13. Business Interpretation

The runner-up product per brand-category combination is a natural
candidate for additional marketing push — it's already proven
demand within that specific brand-category niche, just slightly behind
the current leader, making it a lower-risk bet than trying to launch an
entirely new SKU from zero.
