# Reasoning

## 1. Interpret the Business Question

Compare, per acquisition channel, how long it takes a new customer to
come back for their second order.

## 2. Output Grain

One row = one acquisition_channel.

## 3. Metric Definition

Per customer (with >= 2 orders): `days_to_second_order = DATEDIFF(2nd
order date, 1st order date)`. Then averaged per channel.

## 4. Required Data

`customers`: customer_id, acquisition_channel.
`orders`: customer_id, order_date.

## 5. SQL

```sql
WITH ranked_orders AS (
    SELECT
        customer_id,
        order_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_seq
    FROM orders
),
first_two AS (
    SELECT
        customer_id,
        MAX(CASE WHEN order_seq = 1 THEN order_date END) AS first_order_date,
        MAX(CASE WHEN order_seq = 2 THEN order_date END) AS second_order_date
    FROM ranked_orders
    WHERE order_seq IN (1, 2)
    GROUP BY customer_id
    HAVING second_order_date IS NOT NULL
)
SELECT
    c.acquisition_channel,
    COUNT(*) AS customers_with_2plus_orders,
    ROUND(AVG(DATEDIFF(ft.second_order_date, ft.first_order_date)), 1) AS avg_days_to_second_order
FROM first_two ft
JOIN customers c ON c.customer_id = ft.customer_id
WHERE c.acquisition_channel IS NOT NULL
GROUP BY c.acquisition_channel
ORDER BY avg_days_to_second_order;
```

## 6. Walkthrough

`ranked_orders` numbers each customer's orders chronologically.
`first_two` pivots orders 1 and 2 into columns per customer (the same
`MAX(CASE WHEN ...)` idiom as Q068), keeping only customers who have a
second order at all (`HAVING second_order_date IS NOT NULL`). The final
query joins to `customers` for channel and averages the day-gap per
channel.

## 7. Validation

- Manually verify one customer's first/second order dates and the
  resulting gap.
- Confirm `customers_with_2plus_orders` per channel is consistent with
  what you'd expect given each channel's rough share of repeat
  customers.

## 8. Edge Cases

- One-time customers are naturally excluded (`second_order_date IS
  NULL` for them) — this metric can only be computed for repeat
  customers, which is worth stating whenever it's reported (a channel
  with very few repeat customers has a noisier, less trustworthy
  average).
- Customers with `NULL` acquisition_channel are excluded from the final
  grouping.

## 9. Alternative Approach

Using `LEAD(order_date)` from a customer's first order (looking only at
`order_seq = 1` rows and taking `LEAD` to peek at `order_seq = 2`)
achieves the same result via a different window function — the pivot
approach here and a LEAD-based approach are roughly equivalent in
complexity for this specific two-event case.

## 10. Trade-offs

Not applicable — a matter of preference between the two window-
function idioms.

## 11. Business Interpretation

A channel with a notably longer average time-to-second-order might
benefit from a more deliberate post-purchase nurture sequence (email,
retargeting) to shorten that gap, while a channel that's already fast
might indicate strong product-market fit for whoever it attracts.
