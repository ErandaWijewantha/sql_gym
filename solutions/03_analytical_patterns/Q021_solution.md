# Reasoning

## 1. Interpret the Business Question

Every category manager wants their *own* top-3 list simultaneously — 24
independent rankings computed in one pass, not one global top-3.

## 2. Output Grain

One row = one (category, product) pair, restricted to rank <= 3 within
its category.

## 3. Metric Definition

Gross revenue per product = `SUM(quantity * unit_price)` from completed
orders, same definition as prior revenue questions.

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id, product_id, quantity, unit_price.
`products`: product_id, product_name, category_id.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → compute gross revenue per product (completed orders only)
    Step 2 → attach category_name to each product
    Step 3 → within each category, rank products by revenue descending
    Step 4 → keep only rank <= 3

## 6. Pattern Recognition

"Top N *within each group*, simultaneously for every group" → a ranking
window function (`ROW_NUMBER()`, `RANK()`, or `DENSE_RANK()`)
partitioned by the group column. This is the single most important
pattern distinction from Q002's plain `LIMIT`: `LIMIT` only ever
produces one global cutoff, never one cutoff per group.

## 7. SQL

```sql
WITH product_revenue AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category_id,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN orders o    ON o.order_id = oi.order_id
    JOIN products p  ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY p.product_id, p.product_name, p.category_id
),
ranked AS (
    SELECT
        pr.*,
        c.category_name,
        ROW_NUMBER() OVER (PARTITION BY pr.category_id ORDER BY pr.revenue DESC) AS rn
    FROM product_revenue pr
    JOIN categories c ON c.category_id = pr.category_id
)
SELECT category_name, product_name, revenue, rn AS rank_in_category
FROM ranked
WHERE rn <= 3
ORDER BY category_name, rank_in_category;
```

## 8. Walkthrough

`product_revenue` first collapses order_items down to one row per
product (a necessary pre-aggregation, same lesson as Level 2).
`ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY revenue DESC)`
then assigns a fresh 1, 2, 3, ... sequence *independently within each
category* — the `PARTITION BY` is what makes this "top 3 per group"
rather than "top 3 overall." Window functions are only allowed in the
`SELECT` list (or an outer query), never directly in `WHERE`, which is
exactly why the filter `rn <= 3` lives in an outer query against the
CTE rather than in the same `SELECT` that computes `rn`.

## 9. Validation

- Every category_name in the output should appear at most 3 times.
- For one category, independently query all its products' revenue,
  sort descending by hand, and confirm the top 3 match.
- Total distinct categories represented should equal the number of
  categories that have any completed-order revenue at all (some
  categories could have fewer than 3 products sold, in which case they
  contribute fewer than 3 rows — not a bug).

## 10. Edge Cases

- A category with only 2 products sold produces only 2 rows, not 3 —
  correct, not a bug.
- `ROW_NUMBER()` breaks exact revenue ties arbitrarily (by whatever
  order MySQL happens to process rows in, unless a secondary ORDER BY
  key is added) — if the business cares about ties being visible, use
  `RANK()` instead (see Q022 for the full ties discussion), which would
  let two tied products both show rank 2, with the next product
  jumping to rank 4.
- Never-sold products don't appear in `product_revenue` (no
  order_items rows to aggregate) and are correctly absent throughout.

## 11. Alternative Approach

A correlated subquery counting "how many products in this product's
category have strictly higher revenue" (and keeping rows where that
count is < 3) can express the same idea without a window function, but
it's less efficient (it re-scans per row) and less idiomatic — the
window-function CTE is clearly preferred here.

## 12. Trade-offs

`ROW_NUMBER()` guarantees exactly 3 rows per category (assuming at
least 3 exist) but arbitrarily breaks ties; `RANK()` respects ties but
can return more than 3 rows for a category if there's a tie at the
boundary. Which one is "correct" depends entirely on what the category
managers actually want — this is worth clarifying with them rather than
guessing.

## 13. Business Interpretation

Each category manager now has their own definitive hero-SKU list,
computed consistently across all 24 categories in one query — exactly
the kind of report that should live as a saved view/dashboard rather
than be recomputed ad hoc each time.
