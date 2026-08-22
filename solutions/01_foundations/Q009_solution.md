# Reasoning

## 1. Interpret the Business Question

Pricing wants to find products that are almost never sold at full
price — a signal that a promotional discount has effectively become
the "real" price, and a straight price cut might be cleaner.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

Discount frequency = (number of line items with discount_amount > 0)
divided by (total number of line items) for that product, expressed as
a percentage — restricted to products with a minimum sample size of 5
line items so a single discounted sale doesn't look like "100%
discounted."

## 4. Required Data

`order_items`: product_id, discount_amount.

## 5. Logical Decomposition

    Step 1 → for each order_item row, flag whether discount_amount > 0
    Step 2 → GROUP BY product_id
    Step 3 → compute AVG(flag) as the discount percentage (or SUM(flag)/COUNT(*))
    Step 4 → HAVING COUNT(*) >= 5
    Step 5 → ORDER BY the percentage descending, LIMIT 15

## 6. Pattern Recognition

"What fraction of rows meet a condition" → conditional aggregation.
`AVG(CASE WHEN condition THEN 1 ELSE 0 END)` (or equivalently
`SUM(CASE WHEN condition THEN 1 ELSE 0 END) / COUNT(*)`) is the standard
idiom for turning a per-row boolean into a per-group rate.

## 7. SQL

```sql
SELECT
    product_id,
    COUNT(*) AS line_item_count,
    ROUND(
        AVG(CASE WHEN discount_amount > 0 THEN 1 ELSE 0 END) * 100,
        1
    ) AS pct_discounted_lines
FROM order_items
GROUP BY product_id
HAVING COUNT(*) >= 5
ORDER BY pct_discounted_lines DESC, line_item_count DESC
LIMIT 15;
```

## 8. Walkthrough

The `CASE` expression evaluates to `1` or `0` per row; `AVG()` over a
column of 1s and 0s is exactly the fraction of rows where the condition
was true, since `AVG = SUM/COUNT`. Multiplying by 100 and rounding
turns that fraction into a readable percentage. `HAVING COUNT(*) >= 5`
excludes low-volume products *after* grouping, since the row count
itself is only known post-aggregation.

## 9. Validation

- Manually check one product: run
  `SELECT discount_amount FROM order_items WHERE product_id = <id>`
  and confirm the fraction of positive values matches the computed
  percentage.
- Confirm every `pct_discounted_lines` value is between 0 and 100.
- Confirm no product with fewer than 5 line items appears in the
  output.

## 10. Edge Cases

- A product could legitimately show 100% (deliberately never sold at
  full price by the generator's discount logic) — not a bug.
- Products with the popularity weight set to zero (deliberately
  "never sold," ~5% of the catalog) will have zero rows in
  `order_items` and are correctly absent from this result entirely —
  don't mistake their absence for a query bug; see Q013/Q029 for how to
  surface never-sold products explicitly via an anti-join instead.
- `AVG()` over an empty group can't happen here because `HAVING COUNT(*)
  >= 5` guarantees at least 5 rows per surviving group.

## 11. Alternative Approach

`SUM(CASE WHEN discount_amount > 0 THEN 1 ELSE 0 END) / COUNT(*)` is
arithmetically identical to the `AVG(CASE ...)` form and some engineers
prefer it for explicitness about numerator/denominator — purely a style
choice here.

## 12. Trade-offs

Not applicable — the two forms are equivalent in cost and clarity;
pick whichever reads more naturally to your team.

## 13. Business Interpretation

Products at or near 100% discount frequency are candidates for pricing
to review: either lower the list price to match the "effective" selling
price, or investigate whether the discount is being over-applied by
promotions that no longer need to run.
