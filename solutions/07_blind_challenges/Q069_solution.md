# Reasoning

## 1. Interpret the Business Question

Find employees present (by hire_date) during a period when their
store's revenue declined, comparing the most recent 3 months to the 3
months before that.

## 2. Output Grain

One row = one employee (at a store meeting the decline condition,
restricted to employees hired early enough to have been present
throughout).

## 3. Metric Definition

Store-level: `recent_3mo_revenue` (2025-10-01 to 2025-12-31) vs.
`prior_3mo_revenue` (2025-07-01 to 2025-09-30), completed orders.
Employee eligibility: `hire_date < '2025-07-01'`.

## 4. Required Data

`employees`: employee_id, store_id, hire_date.
`orders`: order_id, store_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. SQL

```sql
WITH store_period_revenue AS (
    SELECT
        o.store_id,
        SUM(CASE WHEN o.order_date >= '2025-10-01' THEN oi.quantity*oi.unit_price-oi.discount_amount ELSE 0 END) AS recent_3mo_revenue,
        SUM(CASE WHEN o.order_date >= '2025-07-01' AND o.order_date < '2025-10-01' THEN oi.quantity*oi.unit_price-oi.discount_amount ELSE 0 END) AS prior_3mo_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
      AND o.order_date >= '2025-07-01' AND o.order_date < '2026-01-01'
    GROUP BY o.store_id
)
SELECT
    e.employee_id, e.store_id, e.hire_date,
    spr.recent_3mo_revenue, spr.prior_3mo_revenue
FROM employees e
JOIN store_period_revenue spr ON spr.store_id = e.store_id
WHERE e.hire_date < '2025-07-01'
  AND spr.recent_3mo_revenue < spr.prior_3mo_revenue
ORDER BY (spr.prior_3mo_revenue - spr.recent_3mo_revenue) DESC;
```

## 6. Walkthrough

`store_period_revenue` computes both quarters' revenue per store in
one pass (the same conditional-aggregation idiom as Q042, without the
peer-median step since this question only needs a store's own
before/after comparison). Joining `employees` to this store-grain result
is safe (no fan-out, since `store_period_revenue` is already one row
per store) — filtering to employees hired before the comparison
window began ensures every included employee was actually present for
the "before" period being measured.

## 7. Validation

- Confirm every result's `hire_date < '2025-07-01'`.
- Confirm every result's `recent_3mo_revenue < prior_3mo_revenue`.
- Spot-check one store's two quarterly figures directly.

## 8. Edge Cases

- An employee hired exactly on `2025-07-01` is excluded (`<`, not
  `<=`) — they weren't present for any part of the "prior" 3-month
  window, so including them would misrepresent "during the decline."
- Multiple employees at the same declining store all appear as separate
  rows — expected, since the grain is employee, not store.

## 9. Alternative Approach

Restricting to a longer comparison window (6 months vs 6 months) would
be less sensitive to a single unusually slow month, at the cost of
being less specific about "recent" decline.

## 10. Trade-offs

Not applicable beyond the window-length choice above.

## 11. Business Interpretation

This is a tenure-filtered list HR can use to identify long-enough-
serving staff at stores currently trending down — useful context for a
conversation about whether store-level issues (not individual
performance) explain a broader pattern across multiple employees at
the same location.
