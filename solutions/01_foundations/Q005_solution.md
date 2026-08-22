# Reasoning

## 1. Interpret the Business Question

Leadership wants a channel-level revenue comparison. This is the first
question in the gym where "revenue" itself needs a definition before
writing SQL — see `docs/business_metrics.md`.

## 2. Output Grain

One row = one sales_channel value.

## 3. Metric Definition

"Gross revenue" is explicitly defined in the question as
`quantity * unit_price`, deliberately *before* subtracting
`discount_amount`. This is one legitimate definition of "revenue" among
several (see Q046 for the return-rate denominator ambiguity, and
`docs/business_metrics.md` generally) — the point here is that the
question pins the definition down instead of leaving it to guesswork.

The question also restricts to completed orders: cancelled orders never
fulfilled, refunded orders were reversed, and pending orders haven't
resolved yet — none of those represent revenue that actually landed.

## 4. Required Data

`orders`: order_id, sales_channel, order_status.
`order_items`: order_id, quantity, unit_price.

## 5. Logical Decomposition

    Step 1 → filter orders to order_status = 'completed'
    Step 2 → join to order_items on order_id
    Step 3 → compute quantity * unit_price per line item
    Step 4 → GROUP BY sales_channel, SUM the line-item amounts

## 6. Pattern Recognition

"Total X by category" → `JOIN` + `GROUP BY` + `SUM`. The extra
ingredient versus Q004 is that the measure being summed
(`quantity * unit_price`) lives on the *child* table (`order_items`)
while the grouping column (`sales_channel`) lives on the *parent*
(`orders`) — a shape that will reappear constantly.

## 7. SQL

```sql
SELECT
    o.sales_channel,
    SUM(oi.quantity * oi.unit_price) AS gross_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'completed'
GROUP BY o.sales_channel
ORDER BY gross_revenue DESC;
```

## 8. Walkthrough

The JOIN expands to one row per order line item (the natural grain of
`order_items`), carrying `sales_channel` along from the parent order.
`WHERE` filters out non-completed orders *before* aggregation, so their
line items never enter the sum. `GROUP BY sales_channel` then collapses
everything down to two rows (`online`, `in_store`), with `SUM` adding up
every qualifying line item's contribution.

## 9. Validation

- This JOIN does *not* duplicate revenue: each `order_items` row is a
  distinct line item, and joining it to its one parent order via
  `order_id` doesn't multiply anything (orders is the "one" side).
  Contrast this with joining in `payments` as well, which *would* be a
  problem (see Q017).
- Sanity-check magnitude: ~118K orders x ~75% completed x a few
  thousand LKR average order value should land in the tens of billions
  of LKR total across both channels — if the number is off by several
  orders of magnitude, suspect a missing filter or unit confusion.
- Cross-check: `online` should be the smaller of the two totals in row
  count (constructed as ~25% of orders) but potentially not proportionally
  smaller in revenue if online average order value differs.

## 10. Edge Cases

- If `WHERE o.order_status = 'completed'` were dropped, cancelled and
  refunded orders would inflate the number with revenue that was never
  actually realized — the resulting figure would no longer mean
  "revenue," despite still being labeled that way in the column alias.
- This is *gross* revenue: it does not net out `discount_amount`,
  returns, or COGS. Don't casually reuse this number where "net sales"
  or "profit" is actually meant — see `docs/business_metrics.md` for
  the full family of related-but-distinct metrics.

## 11. Alternative Approach

Pre-aggregating `order_items` by `order_id` in a CTE before joining to
`orders` would be equivalent here (since we're not counting orders,
just summing amounts) and becomes necessary once you *do* need an
order-level measure like average order value (see Q008, Q016).

## 12. Trade-offs

The direct JOIN is simplest and correct for a pure SUM like this one;
reach for pre-aggregation only when the question requires something
that depends on the *number of orders* rather than just the sum of
line items.

## 13. Business Interpretation

This tells leadership the split of gross sales between channels under
one specific, stated definition of revenue. Before using this number in
a board deck, be ready to answer "gross or net?" and "does this include
cancelled orders?" — this exercise exists precisely so that answer is
never a guess.
