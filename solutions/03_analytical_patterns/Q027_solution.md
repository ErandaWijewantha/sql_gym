# Reasoning

## 1. Interpret the Business Question

Category managers want to see product-level revenue concentration:
does one or two hero SKUs dominate a category's revenue, or is it
spread broadly?

## 2. Output Grain

One row = one product.

## 3. Metric Definition

`pct_of_category_revenue = product_revenue / category_total_revenue *
100`, both numerator and denominator computed from completed orders'
gross revenue.

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id, product_id, quantity, unit_price.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → compute gross revenue per product
    Step 2 → compute SUM(revenue) OVER (PARTITION BY category_id) alongside
              each product row, without collapsing the product grain
    Step 3 → divide product revenue by that category total

## 6. Pattern Recognition

"Percentage of total, at a finer grain than the total itself" → window
`SUM(...) OVER (PARTITION BY group)`. The critical property: unlike a
`GROUP BY` aggregate, a window function's `SUM` doesn't collapse rows —
every product row keeps its own identity while also seeing its
category's total sitting right alongside it.

## 7. SQL

```sql
WITH product_revenue AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category_id,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.product_name, p.category_id
)
SELECT
    c.category_name,
    pr.product_name,
    pr.revenue,
    SUM(pr.revenue) OVER (PARTITION BY pr.category_id) AS category_total_revenue,
    ROUND(
        pr.revenue / SUM(pr.revenue) OVER (PARTITION BY pr.category_id) * 100,
        2
    ) AS pct_of_category_revenue
FROM product_revenue pr
JOIN categories c ON c.category_id = pr.category_id
ORDER BY c.category_name, pct_of_category_revenue DESC;
```

## 8. Walkthrough

`product_revenue` first collapses to one row per product (the usual
pre-aggregation step). `SUM(pr.revenue) OVER (PARTITION BY
pr.category_id)` then computes, on *every product row*, the total
revenue of all products sharing that same `category_id` — without
reducing the number of rows. Dividing each product's own revenue by
that category-level total (visible on the same row) gives the
percentage directly, with no separate join or subquery needed for the
denominator.

## 9. Validation

- Pick one category and sum `pct_of_category_revenue` across all its
  products — it should total to (approximately, allowing for rounding)
  100.
- `category_total_revenue` should be identical across every row sharing
  the same `category_name` — a quick way to confirm the window function
  computed the group total correctly rather than something per-row.
- Cross-check the category total here against Q006's per-category
  revenue figure (same underlying definition, computed a different way)
  for any overlapping time-unrestricted total.

## 10. Edge Cases

- A never-sold product doesn't appear in `product_revenue` at all, so
  it can't distort any category's percentage totals — correctly
  excluded.
- A category with only one product sold will show that product at
  100% — not a bug, just an accurate reflection of total concentration.
- Rounding to 2 decimal places means the percentages might sum to
  99.98% or 100.02% for a category with many products — expected
  floating-point/rounding behavior, not a calculation error.

## 11. Alternative Approach

```sql
WITH product_revenue AS (
    SELECT p.product_id, p.category_id,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.category_id
),
category_totals AS (
    SELECT category_id, SUM(revenue) AS category_total_revenue
    FROM product_revenue
    GROUP BY category_id
)
SELECT
    pr.product_id, pr.revenue, ct.category_total_revenue,
    ROUND(pr.revenue / ct.category_total_revenue * 100, 2) AS pct_of_category_revenue
FROM product_revenue pr
JOIN category_totals ct ON ct.category_id = pr.category_id;
```

This CTE + JOIN version computes the exact same result without a
window function, by explicitly building the category totals as their
own aggregated step and joining them back.

## 12. Trade-offs

The window-function version is more compact (one fewer CTE, no join
needed for the denominator) and is the idiomatic choice for "percentage
of total" once a team is comfortable with window functions. The CTE +
JOIN version is more explicit about what's happening and may be easier
for a SQL beginner to follow step by step — a good example of the same
underlying arithmetic expressed two structurally different ways (see
`training/approach_selection/` for more of this contrast).

## 13. Business Interpretation

A category where one product holds, say, 70%+ of revenue is a
concentration risk (a single discontinued or out-of-stock SKU could
tank the whole category's numbers), while a category with revenue
spread evenly across many products is more resilient — this output
directly supports that kind of category-health conversation.
