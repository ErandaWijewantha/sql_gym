# Reasoning

## 1. Interpret the Business Question

Compare regions by repeat-purchase rate — the fraction of a region's
purchasing customers who placed more than one order — independent of
each region's raw customer count or revenue.

## 2. Output Grain

One row = one region.

## 3. Metric Definition

`repeat_rate = customers with >= 2 orders / customers with >= 1 order`,
per region.

## 4. Required Data

`customers`: customer_id, region.
`orders`: customer_id.

## 5. SQL

```sql
WITH customer_order_counts AS (
    SELECT c.customer_id, c.region, COUNT(o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_id, c.region
)
SELECT
    region,
    COUNT(*) AS purchasing_customers,
    SUM(order_count >= 2) AS repeat_customers,
    ROUND(SUM(order_count >= 2) * 100.0 / COUNT(*), 1) AS repeat_rate_pct
FROM customer_order_counts
WHERE region IS NOT NULL
GROUP BY region
ORDER BY repeat_rate_pct DESC;
```

## 6. Walkthrough

`customer_order_counts` collapses to one row per purchasing customer
with their order count and region (an inner `JOIN` naturally excludes
zero-order customers, appropriate since the rate's denominator is
"purchasing customers," not the whole customer base). The final query
computes, per region, what fraction of purchasing customers have 2 or
more orders.

## 7. Validation

- `repeat_customers <= purchasing_customers` for every region.
- Compare against the global repeat rate from Q033 — regional rates
  should scatter around it, not diverge wildly unless a real regional
  effect exists.

## 8. Edge Cases

- Customers with `NULL` region are excluded — a deliberate choice
  (there's no "region" to attribute their repeat/one-time status to);
  worth stating rather than letting them silently vanish unnoticed.
- A region with very few purchasing customers produces a noisier
  percentage — worth showing `purchasing_customers` alongside the rate
  so a reader doesn't over-trust a rate based on a tiny sample.

## 9. Alternative Approach

A window-function version (`COUNT(*) OVER (PARTITION BY region)` etc.)
could avoid an explicit second GROUP BY level, but the two-step
CTE-then-GROUP-BY version here is clearer for this shape.

## 10. Trade-offs

Not applicable beyond the above.

## 11. Business Interpretation

The highest-repeat-rate region represents the strongest organic
loyalty pattern — useful context before assuming a region's high
revenue is only a function of population size or store count rather
than genuine customer stickiness.
