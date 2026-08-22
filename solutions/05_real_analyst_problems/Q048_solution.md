# Reasoning

## 1. Interpret the Business Question

Finance's worry is precise: a product might show positive revenue on
paper but actually lose money once discounts and returns are both
accounted for. The chosen framing: compare net revenue collected on
*kept* (non-returned) units against the cost of *all* units sold
(including ones later returned, since the company paid/committed COGS
for every unit shipped, whether or not it came back).

## 2. Output Grain

One row = one product (restricted to those failing the test).

## 3. Metric Definition

    units_sold        = SUM(order_items.quantity), completed orders
    units_returned     = SUM(returns.quantity) for those orders
    units_kept         = units_sold - units_returned
    net_revenue_kept   = SUM(quantity*unit_price - discount_amount) for
                          completed orders, prorated to units_kept
                          (approximated here as a simple ratio, since
                          this schema doesn't track which specific
                          units within a line item were returned)
    cogs_all_sold      = units_sold * products.cost
    is_losing_money    = net_revenue_kept < cogs_all_sold

## 4. Required Data

`products`: product_id, cost.
`order_items`: product_id, quantity, unit_price, discount_amount.
`returns`: product_id, quantity.

## 5. SQL

```sql
WITH sales AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'completed'
    GROUP BY oi.product_id
),
returned AS (
    SELECT product_id, SUM(quantity) AS units_returned
    FROM returns
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_name,
    s.units_sold,
    COALESCE(r.units_returned, 0) AS units_returned,
    s.units_sold - COALESCE(r.units_returned, 0) AS units_kept,
    ROUND(s.net_revenue * (s.units_sold - COALESCE(r.units_returned, 0)) / s.units_sold, 2) AS approx_net_revenue_kept,
    ROUND(s.units_sold * p.cost, 2) AS cogs_all_units_sold
FROM products p
JOIN sales s ON s.product_id = p.product_id
LEFT JOIN returned r ON r.product_id = p.product_id
WHERE (s.net_revenue * (s.units_sold - COALESCE(r.units_returned, 0)) / s.units_sold)
      < (s.units_sold * p.cost)
ORDER BY approx_net_revenue_kept - cogs_all_units_sold ASC;
```

## 6. Walkthrough

`sales` and `returned` are pre-aggregated independently to product
grain (the Level 2 lesson, reused). `approx_net_revenue_kept` prorates
total net revenue by the fraction of units kept (`units_kept /
units_sold`) — an approximation, since this schema records only a
line-item-level `discount_amount`, not which individual units within a
multi-unit line item were the ones later returned; a returned unit
could plausibly have been discounted differently than a kept one, which
this proration can't distinguish. `cogs_all_units_sold` charges the
full cost against every unit sold, on the reasoning that the company
incurred that cost regardless of what was later returned. The `WHERE`
clause flags products where kept revenue doesn't cover total COGS.

## 7. Validation

- Manually reconstruct one flagged product's numbers: pull its raw
  `cost`, `selling_price`, total units sold, total discount applied,
  and units returned, and confirm the flagged inequality actually holds
  by hand.
- Confirm no product with zero returns is ever flagged purely from
  discounting alone unless its *average* realized price (after
  discount) already falls below cost on its own — a useful secondary
  check that separates "returns are the problem" from "discounting
  alone is the problem" (worth computing as a follow-up, similar to
  Q044's independent-signals approach).

## 8. Edge Cases

- The proration in `approx_net_revenue_kept` is a simplification, not
  an exact allocation — flag this explicitly to finance rather than
  presenting it as precise. An exact version would need order-item-
  level knowledge of exactly which units within a line were returned,
  which this schema doesn't capture.
- A product with `units_sold` very close to zero returns entirely
  (`units_kept ≈ units_sold`) is unaffected by the return side of this
  calculation — if it's still flagged, the problem is pure margin/
  discounting, not returns.
- Products with zero sales don't appear (excluded by the inner join to
  `sales`) — correctly, since "losing money on returns" doesn't apply
  to something that was never sold.

## 9. Alternative Approach

A stricter, order-item-level version (if the schema tracked which
specific units were returned) would avoid the proration approximation
entirely — worth recommending as a data-capture improvement if this
kind of analysis becomes a recurring finance need.

## 10. Trade-offs

The proration approach is workable with the data actually available
and catches the general pattern finance is worried about, at the cost
of some precision on any individual product's exact number — acceptable
for triage, not for a precise per-product P&L statement.

## 11. Business Interpretation

Any product surfaced here genuinely warrants finance's attention — the
combination of margin, discount depth, and return rate has crossed
from "acceptable cost of doing business" into "net money-losing" even
before accounting for fixed costs like shipping and handling, which
would only make the picture worse.
