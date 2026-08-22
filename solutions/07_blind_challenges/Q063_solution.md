# Reasoning

## 1. Interpret the Business Question

Compare each product's discounted-line-item share between 2024 (first
half of the dataset) and 2025 (second half), flagging products where
it rose meaningfully.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

`discount_share_2024`, `discount_share_2025` = fraction of that year's
line items with `discount_amount > 0`, using conditional aggregation
(same idiom as Q009).

## 4. Required Data

`order_items`: product_id, discount_amount.
`orders`: order_id, order_date.

## 5. SQL

```sql
WITH product_year_stats AS (
    SELECT
        oi.product_id,
        SUM(CASE WHEN YEAR(o.order_date) = 2024 THEN 1 ELSE 0 END) AS lines_2024,
        SUM(CASE WHEN YEAR(o.order_date) = 2024 AND oi.discount_amount > 0 THEN 1 ELSE 0 END) AS discounted_2024,
        SUM(CASE WHEN YEAR(o.order_date) = 2025 THEN 1 ELSE 0 END) AS lines_2025,
        SUM(CASE WHEN YEAR(o.order_date) = 2025 AND oi.discount_amount > 0 THEN 1 ELSE 0 END) AS discounted_2025
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    GROUP BY oi.product_id
)
SELECT
    product_id,
    ROUND(discounted_2024 / NULLIF(lines_2024, 0) * 100, 1) AS discount_share_2024_pct,
    ROUND(discounted_2025 / NULLIF(lines_2025, 0) * 100, 1) AS discount_share_2025_pct
FROM product_year_stats
WHERE lines_2024 >= 5 AND lines_2025 >= 5
  AND (discounted_2025 / NULLIF(lines_2025, 0)) - (discounted_2024 / NULLIF(lines_2024, 0)) > 0.15
ORDER BY discount_share_2025_pct - discount_share_2024_pct DESC;
```

## 6. Walkthrough

Conditional aggregation computes four numbers per product in one pass:
line-item count and discounted-line-item count, split by year.
`NULLIF` guards each ratio's denominator against zero. A minimum
sample size (`>= 5` lines in each year, echoing Q009's guard) prevents
a product with only 1-2 sales in either year from producing a
misleadingly extreme percentage swing. The final filter requires a
meaningful rise (> 15 percentage points) rather than any positive
difference, avoiding noise from tiny fluctuations.

## 7. Validation

- Manually verify one flagged product's line counts and discounted
  counts per year directly from `order_items`/`orders`.
- Confirm every result satisfies both minimum-sample-size conditions.

## 8. Edge Cases

- A product only introduced partway through 2024 or 2025 (via
  `launch_date`) may have very few lines in one year, which the
  minimum-sample-size filter should catch — but it's worth checking a
  flagged product's `launch_date` isn't itself explaining a lopsided
  comparison.
- The 15-percentage-point threshold is a judgment call, not a fixed
  rule — smaller shifts might still be meaningful for a very
  high-volume product.

## 9. Alternative Approach

Restricting to quarters instead of full-year halves would give a more
granular trend view (rising steadily vs. a single anomalous quarter)
at the cost of more complexity.

## 10. Trade-offs

The year-over-year split is simple and directly matches "second half vs
first half" as literally asked; a finer time grain trades simplicity
for more diagnostic detail.

## 11. Business Interpretation

A rising discount share on a product that wasn't discounted much before
suggests either a deliberate new promotional strategy or an unplanned
pricing/margin creep — worth a conversation with whoever owns that
product's promotions calendar.
