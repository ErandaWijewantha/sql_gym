# Reasoning

## 1. Interpret the Business Question

A year-over-year comparison per customer: 2025 net spend vs. 2024 net
spend, flagging a drop of more than 30%.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

`spend_2024`, `spend_2025` = net revenue (completed orders) within each
calendar year. Flagged if `spend_2025 < spend_2024 * 0.7`.

## 4. Required Data

`orders`: order_id, customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute net spend per (customer, year) via conditional aggregation
    Step 2 → require both years to have a value (a customer must have
              existed and possibly bought in both years to have a
              meaningful YoY comparison)
    Step 3 → filter to spend_2025 < spend_2024 * 0.7

## 6. SQL

```sql
WITH yearly_spend AS (
    SELECT
        o.customer_id,
        SUM(CASE WHEN YEAR(o.order_date) = 2024 THEN oi.quantity*oi.unit_price - oi.discount_amount ELSE 0 END) AS spend_2024,
        SUM(CASE WHEN YEAR(o.order_date) = 2025 THEN oi.quantity*oi.unit_price - oi.discount_amount ELSE 0 END) AS spend_2025
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.customer_id
)
SELECT customer_id, spend_2024, spend_2025,
       ROUND((spend_2024 - spend_2025) / spend_2024 * 100, 1) AS pct_decline
FROM yearly_spend
WHERE spend_2024 > 0
  AND spend_2025 < spend_2024 * 0.7
ORDER BY pct_decline DESC;
```

## 7. Walkthrough

Conditional `SUM(CASE WHEN YEAR(...) = X ...)` computes both years'
spend in a single pass over `order_items`, avoiding two separate scans
or a self-join. `WHERE spend_2024 > 0` excludes customers with no 2024
spend at all (a decline percentage is undefined/meaningless without a
positive baseline — a customer who only started buying in 2025 hasn't
"declined" from anything).

## 8. Validation

- Spot check one customer's `spend_2024`/`spend_2025` against a direct
  per-year query.
- Confirm every result row has `spend_2025 < spend_2024 * 0.7` and
  `spend_2024 > 0`.

## 9. Edge Cases

- A customer with `spend_2025 = 0` (bought in 2024, nothing since) is
  correctly included — a 100% decline clears the 30% bar easily.
- A customer who bought only in 2025 (no 2024 orders) is excluded by
  `spend_2024 > 0` — correctly, since there's no prior-year baseline to
  decline from.

## 10. Alternative Approach

Two separate CTEs (one per year) joined together would produce the
same result with more verbosity; conditional aggregation in one pass is
more concise here.

## 11. Trade-offs

Not applicable beyond the above.

## 12. Business Interpretation

This flags meaningful year-over-year contraction specifically among
customers with an established 2024 baseline — useful for a retention
review focused on existing, not brand-new, customers.
