# Reasoning

## 1. Interpret the Business Question

Compare average discount amount per line item, by category, between
2024 and 2025.

## 2. Output Grain

One row = one category.

## 3. Metric Definition

`avg_discount_2024`, `avg_discount_2025` = `AVG(discount_amount)` per
category per year, over all line items (not just discounted ones —
zeros pull the average down proportionally, which is the correct
behavior for "average discount amount," distinct from Q009's
"percentage of lines discounted at all").

## 4. Required Data

`order_items`: product_id, discount_amount.
`orders`: order_id, order_date.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. SQL

```sql
WITH category_year_discount AS (
    SELECT
        cat.category_name,
        YEAR(o.order_date) AS yr,
        AVG(oi.discount_amount) AS avg_discount
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    JOIN categories cat ON cat.category_id = p.category_id
    WHERE YEAR(o.order_date) IN (2024, 2025)
    GROUP BY cat.category_name, YEAR(o.order_date)
)
SELECT
    category_name,
    MAX(CASE WHEN yr = 2024 THEN avg_discount END) AS avg_discount_2024,
    MAX(CASE WHEN yr = 2025 THEN avg_discount END) AS avg_discount_2025,
    MAX(CASE WHEN yr = 2025 THEN avg_discount END)
        > MAX(CASE WHEN yr = 2024 THEN avg_discount END) AS discount_rising
FROM category_year_discount
GROUP BY category_name
ORDER BY category_name;
```

## 6. Walkthrough

`category_year_discount` computes each category's average discount per
year. The outer query pivots the two years into columns (same idiom as
Q068/Q072) and flags whether 2025's average exceeds 2024's.

## 7. Validation

- Manually verify one category's 2024 and 2025 average discount amounts
  directly.
- Confirm `discount_rising` is `1` exactly when `avg_discount_2025 >
  avg_discount_2024`.

## 8. Edge Cases

- A category that didn't exist or had no sales in one of the two years
  would show `NULL` for that year's average, and `discount_rising`
  would also evaluate to `NULL` (any comparison involving `NULL` is
  `NULL`, not `TRUE`/`FALSE`) — worth explicitly filtering these out or
  flagging them as "insufficient data" rather than silently treating a
  NULL as "false."
- This computes the average over *all* line items, including those
  with zero discount — a category could show a rising average purely
  because a larger *share* of its lines are discounted, purely because
  the *depth* of discounts on already-discounted lines increased, or
  both; this single number doesn't distinguish those two mechanisms.

## 9. Alternative Approach

Splitting this into two separate numbers — average discount rate
(Q009/Q063's style) and average discount depth *among discounted lines
only* — would separate "more things are on sale" from "sales are
deeper," a genuinely different diagnostic than one blended average.

## 10. Trade-offs

The single blended average is simpler to report; the two-number
decomposition is more diagnostic for deciding *what* pricing lever
changed.

## 11. Business Interpretation

A category with a rising blended average discount is spending more on
promotions per unit sold, on average — worth decomposing further (as
above) before deciding whether that's a deliberate, working strategy or
unplanned margin erosion.
