# Reasoning

## 1. Interpret the Business Question

Category planning wants to know which categories cleared a specific
revenue bar in a specific quarter — a threshold question, not a
top-N or ranking question.

## 2. Output Grain

One row = one category (but only categories that clear the threshold).

## 3. Metric Definition

Gross sales, same definition as Q005: `quantity * unit_price`, from
completed orders only. The time window is explicit: 2025-10-01 through
2025-12-31 inclusive. Threshold: LKR 50,000,000.

## 4. Required Data

`orders`: order_id, order_date, order_status.
`order_items`: order_id, product_id, quantity, unit_price.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → filter orders to completed and order_date in [2025-10-01, 2025-12-31]
    Step 2 → join to order_items, then to products, then to categories
    Step 3 → GROUP BY category_name, SUM gross revenue
    Step 4 → HAVING SUM > 5,000,000

## 6. Pattern Recognition

"Categories that generated more than X" → aggregate first, *then*
filter on the aggregate → `HAVING`, not `WHERE`. This is the canonical
example from `CLAUDE.md` itself: filtering is HAVING, since the
condition is on `SUM(...)`, a value that only exists after grouping.

## 7. SQL

```sql
SELECT
    c.category_name,
    SUM(oi.quantity * oi.unit_price) AS q4_gross_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p      ON p.product_id = oi.product_id
JOIN categories c     ON c.category_id = p.category_id
WHERE o.order_status = 'completed'
  AND o.order_date >= '2025-10-01'
  AND o.order_date <  '2026-01-01'
GROUP BY c.category_name
HAVING SUM(oi.quantity * oi.unit_price) > 50000000
ORDER BY q4_gross_revenue DESC;
```

## 8. Walkthrough

The date filter uses a half-open range (`>= '2025-10-01' AND <
'2026-01-01'`) rather than `<= '2025-12-31'`, because `order_date` is a
`DATETIME` — a literal `'2025-12-31'` comparison would silently exclude
any order placed after midnight on that day (e.g., `2025-12-31 14:30`
is *not* `<= '2025-12-31 00:00:00'`). This is exactly the kind of
boundary bug the question's "Think Before SQL" step 10 was pointing at.
Three joins walk from the fact table up through two dimension levels
(product → category) without changing grain, since each join is
many-to-one. `GROUP BY` then collapses to one row per category, and
`HAVING` discards any category that didn't clear LKR 5,000,000.

## 9. Validation

- Run the same query without the `HAVING` clause first, to see every
  category's Q4 revenue — confirm the ones that disappear with
  `HAVING` are genuinely below the threshold, not victims of a filter
  bug elsewhere. In this dataset, all 24 categories have some completed
  Q4 revenue, but only 8 clear LKR 50,000,000 (led by Mobile Phones and
  Home Appliances) — the other 16 (e.g. Beverages, Beauty & Cosmetics,
  Books & Stationery at the low end) fall short and are correctly
  dropped by `HAVING`.
- Spot-check that no order with `order_date` on 2025-12-31 late in the
  day was excluded, by testing the date boundary explicitly.
- Category count in the output should be well below the full 24
  categories, since 50,000,000 is a meaningful bar — if nearly every
  category passes, the threshold is too low to be useful and the
  `HAVING` clause isn't really doing any filtering work.

## 10. Edge Cases

- Using `<= '2025-12-31'` instead of `< '2026-01-01'` is the single
  most common mistake here, and it fails silently (no error, just a
  slightly smaller number) — exactly the kind of bug `docs/common_mistakes.md`
  calls out under "incorrect date boundaries."
- A category with zero completed Q4 orders never appears at all — not
  because of `HAVING`, but because an INNER JOIN chain requires at
  least one matching order_item to produce a row in the first place.
- Using `WHERE SUM(...) > 5000000` instead of `HAVING` is a syntax
  error in MySQL — aggregates aren't allowed in `WHERE`.

## 11. Alternative Approach

A CTE that computes each category's Q4 revenue first, with the
threshold applied as a plain `WHERE` in the outer query, is equivalent
and arguably clearer once the aggregation logic itself grows more
complex than a single SUM.

## 12. Trade-offs

The direct `HAVING` version is idiomatic SQL for this exact shape and
is what most engineers would write and expect to read; a CTE adds a
layer of indirection only worth it if the aggregation step is reused
elsewhere in the same query.

## 13. Business Interpretation

This surfaces exactly which categories are pulling their weight for the
upcoming season, under one concrete definition of "generated" (gross,
completed-orders-only, this specific date range) — a different
definition (net of discounts, or including refunded orders as negative
revenue) could plausibly change which categories clear the bar.
