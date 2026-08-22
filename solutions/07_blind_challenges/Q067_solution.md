# Reasoning

## 1. Interpret the Business Question

Find products that chronically run low (not just hit zero once) —
defined here as closing stock <= 5 on more than 10% of the days they
appear in inventory.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

`low_stock_day = closing_stock <= 5`. `low_stock_rate = low_stock_days
/ total_inventory_days`, per product (aggregated across all stores
carrying it).

## 4. Required Data

`inventory`: product_id, closing_stock.
`products`: product_id, product_name.

## 5. SQL

```sql
SELECT
    p.product_id,
    p.product_name,
    COUNT(*) AS total_inventory_days,
    SUM(i.closing_stock <= 5) AS low_stock_days,
    ROUND(SUM(i.closing_stock <= 5) * 100.0 / COUNT(*), 1) AS low_stock_rate_pct
FROM inventory i
JOIN products p ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name
HAVING SUM(i.closing_stock <= 5) * 1.0 / COUNT(*) > 0.10
ORDER BY low_stock_rate_pct DESC;
```

## 6. Walkthrough

`inventory` is already at (store, product, day) grain; grouping by
product alone aggregates across every store-day combination that
product appears in. `SUM(i.closing_stock <= 5)` sums the boolean
condition directly (1 per qualifying day), giving a low-stock day
count; dividing by the total day count gives the rate. `HAVING`
filters on that computed rate.

## 7. Validation

- Manually verify one flagged product's day count and low-stock-day
  count directly against its `inventory` rows.
- Confirm the rate calculation in `HAVING` matches the displayed
  `low_stock_rate_pct` column exactly (same formula, just not rounded).

## 8. Edge Cases

- This aggregates across *all* stores carrying the product — a product
  chronically low at one store but well-stocked everywhere else could
  still clear the 10% threshold if that one store represents a large
  share of its total inventory-days; a per-(store, product) version
  would be needed to localize the problem to specific locations.
- A product carried at very few stores for a short window has fewer
  total inventory-days, making its rate noisier — worth pairing this
  rate with `total_inventory_days` (already shown) so a reader can
  judge sample size.

## 9. Alternative Approach

Computing this per (store, product) instead of product-wide would let
inventory planning target specific store-level restocking issues rather
than treating it as a product-wide problem.

## 10. Trade-offs

The product-wide version is a good first-pass triage list; the
per-store version is more operationally actionable but produces a
longer, more granular report.

## 11. Business Interpretation

Products on this list are chronic near-stockout risks — worth reviewing
reorder point and lead time assumptions specifically for them, rather
than the more common but less useful "did it ever hit zero" framing.
