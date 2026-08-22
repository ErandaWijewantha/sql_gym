# Reasoning

## 1. Interpret the Business Question

"Most valuable" needs a metric before it means anything, and different
metrics can legitimately disagree. This solution computes three side by
side — total revenue, average revenue per customer, and average margin
per customer — rather than committing to one.

## 2. Output Grain

One row = one customer_segment.

## 3. Metric Definition

- Total net revenue (completed orders) per segment.
- Average net revenue per customer within the segment.
- Average gross margin per customer (`SUM((selling_price - cost) *
  quantity) - discount_amount`, roughly — see caveat below on
  discount allocation) within the segment.

## 4. Required Data

`customers`: customer_id, customer_segment.
`orders`, `order_items`, `products` (for cost and selling_price).

## 5. Logical Decomposition

    Step 1 → compute each customer's total net revenue and total margin
    Step 2 → GROUP BY customer_segment: SUM(revenue), AVG(revenue),
              AVG(margin), COUNT(customers)

## 6. SQL

```sql
WITH customer_value AS (
    SELECT
        c.customer_id,
        c.customer_segment,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue,
        SUM(oi.quantity * (p.selling_price - p.cost)) - SUM(oi.discount_amount) AS approx_margin
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY c.customer_id, c.customer_segment
)
SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(net_revenue), 2) AS total_segment_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_revenue_per_customer,
    ROUND(AVG(approx_margin), 2) AS avg_margin_per_customer
FROM customer_value
GROUP BY customer_segment
ORDER BY avg_revenue_per_customer DESC;
```

## 7. Walkthrough

`customer_value` computes, per purchasing customer, both net revenue
and an approximate margin (`quantity * (selling_price - cost)`, summed
across their line items, less total discounts — an approximation,
since discounts are subtracted from total margin rather than allocated
proportionally to each unit's specific margin, which this schema
doesn't support precisely). The outer query then produces three
independent rankings in one result: total (which reflects segment
*size* as much as value), and two per-customer averages (which control
for segment size and better answer "customer for customer, which
segment is worth more").

## 8. Validation

- Confirm `customer_count` across all four segments sums to the total
  number of purchasing customers.
- Compare the ranking under `total_segment_revenue` against the ranking
  under `avg_revenue_per_customer` — if they disagree (a strong
  possibility, since segment sizes are deliberately skewed by the data
  generator, with "Standard" being the largest), that disagreement
  *is* the key finding to bring to the CFO, not a problem to resolve
  away.
- Spot check one customer's margin calculation against
  `products.cost`/`selling_price` directly.

## 9. Edge Cases

- `customer_segment` is, by this dataset's own design, an independent
  marketing-assigned tier that does **not** derive from actual
  purchase behavior (see `data_generation/README.md`) — so before
  presenting any ranking as meaningful, it's worth explicitly checking
  whether the segments actually separate customers by value at all, or
  whether the spread across segments is statistically indistinguishable
  from noise. Reporting a ranking without this check risks over-reading
  a real business signal into what might be an artifact of how tiers
  happen to have been assigned.
- The margin approximation understates precision where discounts are
  heavy — a more precise version would need per-unit discount
  allocation, which this schema doesn't store explicitly (only an
  order-item-level total `discount_amount`).

## 10. Alternative Approach

A pure profitability ranking omitting revenue and reporting only
`avg_margin_per_customer` would answer "which segment contributes most
to the bottom line, customer for customer" most directly — arguably
the single best answer if forced to pick just one, since it accounts
for both selling price *and* cost, unlike raw revenue.

## 11. Trade-offs

Reporting all three numbers costs a moment of the CFO's attention but
avoids the risk of a misleading single-number answer (e.g., "Standard"
might lead on total revenue purely because it's the largest segment by
customer count, while "Premium" leads decisively on a per-customer
basis) — in a CFO-facing context, that nuance is usually worth the
extra column.

## 12. Business Interpretation

The honest answer is rarely a single segment name — it's "Standard
drives the most total revenue because it's the largest segment, but
Premium customers are worth roughly Nx more individually; which of
those matters more depends on whether you're deciding where to spend
retention budget (favor per-customer value) or reporting overall
revenue mix (favor total)."
