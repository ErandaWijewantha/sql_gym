# Reasoning

## 1. Interpret the Business Question

For each category, measure how often a customer who buys from it once
comes back to buy from that *same category* again at some later point —
a category-level repeat-purchase habit measure.

## 2. Output Grain

One row = one category.

## 3. Metric Definition

`repeat_rate = customers who bought from the category in >= 2 distinct
calendar months / customers who bought from the category in >= 1
calendar month`.

## 4. Required Data

`orders`: order_id, customer_id, order_date, order_status.
`order_items`: order_id, product_id.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. SQL

```sql
WITH customer_category_months AS (
    SELECT DISTINCT
        cat.category_name,
        o.customer_id,
        DATE_FORMAT(o.order_date, '%Y-%m-01') AS purchase_month
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    JOIN categories cat ON cat.category_id = p.category_id
    WHERE o.order_status = 'completed'
),
customer_category_month_counts AS (
    SELECT category_name, customer_id, COUNT(*) AS distinct_months_purchased
    FROM customer_category_months
    GROUP BY category_name, customer_id
)
SELECT
    category_name,
    COUNT(*) AS category_customers,
    SUM(distinct_months_purchased >= 2) AS repeat_month_customers,
    ROUND(SUM(distinct_months_purchased >= 2) * 100.0 / COUNT(*), 1) AS repeat_rate_pct
FROM customer_category_month_counts
GROUP BY category_name
ORDER BY repeat_rate_pct DESC;
```

## 6. Walkthrough

`customer_category_months` uses `DISTINCT` to collapse each
(category, customer, month) combination to a single row, regardless of
how many individual orders or line items contributed to it in that
month. `customer_category_month_counts` then counts, per (category,
customer), how many *distinct months* they bought from that category —
this is the key measure: buying twice in the same month doesn't count
as "coming back," since that's likely one shopping trip's related
items, not a renewed, separate purchase occasion. The final query
computes what fraction of each category's customers reached 2 or more
distinct purchase months.

## 7. Validation

- Pick one category and manually verify one customer's distinct month
  count directly against their orders in that category.
- Confirm `repeat_month_customers <= category_customers` for every
  category.

## 8. Edge Cases

- A customer who bought 10 units of a category's products all within
  the same calendar month counts as only 1 "month" here, not a repeat —
  this deliberately measures *renewed occasions* over time, not order
  or unit volume.
- A category bought by very few customers overall produces a noisier
  rate — worth checking `category_customers` (already shown) before
  reading too much into an extreme percentage from a small base.
- This uses calendar month as the "occasion" granularity — a category
  bought twice in adjacent months (e.g., Jan 30 and Feb 1) counts as
  2 separate occasions here even though the purchases were only 2 days
  apart; a stricter version might require a minimum gap between
  purchases instead of a hard calendar-month boundary.

## 9. Alternative Approach

Using a minimum day-gap (e.g., >= 14 days between any two orders
touching the category) instead of "different calendar month" would
avoid the January-30/February-1 edge case above, at the cost of a
noticeably more complex query (requiring a LAG-based gap check per
customer-category, similar to Q034's reactivation logic).

## 10. Trade-offs

The calendar-month approach is simple and matches the same granularity
used throughout this gym's cohort questions (Q036); the day-gap
approach is more precise about "genuinely separate occasions" but adds
real complexity — reasonable to start with the simpler version and
upgrade only if the boundary cases turn out to matter for the specific
decision being made.

## 11. Business Interpretation

A category with a high repeat-month rate creates a genuine ongoing
habit (e.g., consumables like Groceries or Personal Care would
plausibly show this), while a low rate suggests a category is more
often a one-and-done purchase (e.g., Furniture or Jewelry & Watches,
where repeat purchases are naturally much rarer) — useful context for
deciding where a subscription or replenishment-reminder feature would
actually add value.
