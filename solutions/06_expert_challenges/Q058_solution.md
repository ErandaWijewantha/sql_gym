# Reasoning

## 1. Interpret the Business Question

Supply chain wants a rough, defensible estimate of revenue left on the
table due to stockouts — built from each product's own typical sales
rate when it *was* available, applied to the days it wasn't.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

`in_stock_day` = an inventory row where `opening_stock +
received_quantity > 0` (some stock was actually available to sell that
day). `stockout_day` = a row where `opening_stock + received_quantity =
0` (nothing at all was available). `avg_daily_units_in_stock` =
average `sold_quantity` across in-stock days only. `estimated_lost_units
= stockout_days * avg_daily_units_in_stock`. `estimated_lost_revenue =
estimated_lost_units * products.selling_price`.

## 4. Required Data

`inventory`: store_id, product_id, inventory_date, opening_stock,
received_quantity, sold_quantity, closing_stock.
`products`: product_id, selling_price.

## 5. Logical Decomposition

    Step 1 → classify every inventory row as in-stock or stockout
    Step 2 → per product (across all stores), compute avg daily units
              sold on in-stock days, and count stockout days
    Step 3 → estimated_lost_revenue = stockout_days * avg_daily_units *
              selling_price

## 6. SQL

```sql
WITH classified AS (
    SELECT
        product_id,
        inventory_date,
        sold_quantity,
        CASE WHEN opening_stock + received_quantity > 0 THEN 1 ELSE 0 END AS in_stock
    FROM inventory
),
product_stats AS (
    SELECT
        product_id,
        SUM(CASE WHEN in_stock = 1 THEN sold_quantity ELSE 0 END) AS units_sold_in_stock,
        SUM(CASE WHEN in_stock = 1 THEN 1 ELSE 0 END) AS in_stock_days,
        SUM(CASE WHEN in_stock = 0 THEN 1 ELSE 0 END) AS stockout_days
    FROM classified
    GROUP BY product_id
)
SELECT
    ps.product_id,
    p.product_name,
    ps.in_stock_days,
    ps.stockout_days,
    ROUND(ps.units_sold_in_stock / NULLIF(ps.in_stock_days, 0), 3) AS avg_daily_units_in_stock,
    ROUND(
        ps.stockout_days * (ps.units_sold_in_stock / NULLIF(ps.in_stock_days, 0)) * p.selling_price,
        2
    ) AS estimated_lost_revenue
FROM product_stats ps
JOIN products p ON p.product_id = ps.product_id
WHERE ps.stockout_days > 0
ORDER BY estimated_lost_revenue DESC;
```

## 7. Walkthrough

`classified` labels every inventory row using
`opening_stock + received_quantity` — this is the total stock actually
available that day, *before* any sales happen, which is the correct
basis for "was there anything to sell" (as opposed to `closing_stock`,
which is already *after* the day's sales and would be zero on a
perfectly-sold-out-but-not-stocked-out day too). `product_stats`
aggregates across all stores a product is carried in, computing the
average daily sales rate only over in-stock days (`NULLIF` guards
against a product with zero in-stock days, though that would be an
unusual edge case). The final estimate multiplies the stockout day
count by that in-stock sales rate and the product's selling price.

## 8. Validation

- Pick one product and manually verify `in_stock_days + stockout_days`
  equals its total row count in `inventory`.
- Confirm `avg_daily_units_in_stock` is a small, plausible number (this
  dataset's demand model produces low single-digit average daily units
  per store-product), not something wildly large that would suggest a
  units/aggregation error.
- Products with zero stockout days are correctly excluded via the
  `WHERE ps.stockout_days > 0` filter — there's nothing to estimate for
  them.

## 9. Edge Cases

- This assumes demand during stockout days would have looked *exactly*
  like demand on in-stock days — in reality, a stockout might also
  suppress demand indirectly (customers who see "out of stock" and
  don't come back later), which this simple estimate doesn't capture;
  it's a lower-bound-style estimate of *direct* lost sales, not total
  business impact.
- A product stocked at only 1-2 stores will have a much smaller sample
  of in-stock days to estimate its daily rate from than a
  widely-carried product — the resulting average is noisier for
  low-distribution products, worth flagging when presenting results.
- `selling_price` (not a discounted realized price) is used for the
  estimate — a product that's typically sold at a discount would have
  its lost revenue somewhat overstated by this simplification.

## 10. Alternative Approach

Computing this per (store, product) instead of aggregating across all
of a product's stores would let supply chain target specific
underperforming locations rather than treating the issue as
product-wide — a natural refinement if the stockout pattern turns out
to be concentrated in a few specific stores rather than spread evenly.

## 11. Trade-offs

The product-wide (all-stores) version used here gives supply chain a
prioritized product list quickly; the per-store version is more
actionable operationally (which store needs the restock) but produces
a much longer, more granular report — worth having both, used for
different purposes.

## 12. Business Interpretation

This gives supply chain a defensible, if approximate, dollar figure to
justify investment in better replenishment forecasting — framed
honestly as an estimate based on typical in-stock demand, not a
precise accounting figure.
