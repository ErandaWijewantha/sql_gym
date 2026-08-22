# Reasoning

## 1. Interpret the Business Question

Growth wants to reallocate acquisition budget by channel quality, which
means comparing average lifetime spend per channel, while being honest
about the tenure-bias risk called out in the question itself.

## 2. Output Grain

One row = one acquisition_channel.

## 3. Metric Definition

Average lifetime net spend (completed orders) among customers acquired
through that channel — computed two ways: (a) across all customers
acquired via the channel (including zero-order customers, which
measures true channel ROI), and (b) restricted to customers who
converted at least once (measuring "value given conversion").

## 4. Required Data

`customers`: customer_id, acquisition_channel.
`orders`, `order_items`.

## 5. Logical Decomposition

    Step 1 → compute lifetime net spend per customer (0 if no completed orders)
    Step 2 → GROUP BY acquisition_channel: AVG including zero-spend customers,
              AVG excluding them, plus customer counts for both

## 6. SQL

```sql
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.acquisition_channel,
        COALESCE(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 0) AS lifetime_net_spend
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    WHERE c.acquisition_channel IS NOT NULL
    GROUP BY c.customer_id, c.acquisition_channel
)
SELECT
    acquisition_channel,
    COUNT(*) AS total_acquired,
    SUM(lifetime_net_spend > 0) AS converted_count,
    ROUND(AVG(lifetime_net_spend), 2) AS avg_spend_all_acquired,
    ROUND(AVG(CASE WHEN lifetime_net_spend > 0 THEN lifetime_net_spend END), 2) AS avg_spend_given_converted
FROM customer_spend
GROUP BY acquisition_channel
ORDER BY avg_spend_all_acquired DESC;
```

## 7. Walkthrough

The `LEFT JOIN` chain from `customers` guarantees every acquired
customer appears in `customer_spend`, even those with zero orders
(`COALESCE(..., 0)`), which is essential for the "true channel ROI"
measure — excluding them would silently only measure "value of people
who convert," ignoring the channel's actual conversion rate.
`avg_spend_all_acquired` divides by every acquired customer;
`avg_spend_given_converted` uses a `CASE` inside `AVG` to only average
over customers with `lifetime_net_spend > 0`, since `AVG()` ignores
NULL rows automatically.

## 8. Validation

- `converted_count <= total_acquired` for every channel.
- `avg_spend_given_converted >= avg_spend_all_acquired` should always
  hold for the same channel (removing zero-spend customers from an
  average can only raise or maintain it, never lower it).
- Compare channel rankings under both measures — a channel could rank
  well on one and poorly on the other (e.g., low conversion rate but
  high value once converted), which is itself the useful finding.

## 9. Edge Cases

- **The tenure-bias risk flagged in the question is real but not fully
  corrected here** — a channel that only recently started acquiring
  customers will show lower average lifetime spend simply because
  those customers have had less *time* to spend, not because they're
  lower quality. A more rigorous version would restrict to customers
  with tenure above some minimum (e.g., only customers registered
  before a cutoff date, giving everyone compared a fair amount of time
  to have spent) — worth flagging to Growth as a caveat on this result
  rather than silently ignoring it.
- Customers with `NULL` acquisition_channel are excluded entirely
  (~3% of the base) — worth noting rather than letting them silently
  vanish from the analysis.

## 10. Alternative Approach

Restricting the whole analysis to customers registered before, say,
2025-01-01 (giving everyone at least 12 months to transact) would
directly address the tenure-bias caveat, at the cost of throwing away
information about more recently-acquired customers — a reasonable
trade-off specifically because this is a *quality* comparison, not a
volume one.

## 11. Trade-offs

Including zero-spend customers (measuring true ROI) vs. excluding them
(measuring value-given-conversion) answer different budget-allocation
questions: the former is what you want if you're deciding where to
spend the next acquisition dollar; the latter is more useful for
understanding what happens once someone is already in the funnel.

## 12. Business Interpretation

Report both numbers together, plus the tenure caveat: "channel A has
the highest average value once someone converts, but channel B
converts more people overall — and both numbers for any recently-
ramped-up channel should be read with the caveat that its customers
haven't had as much time to spend yet."
