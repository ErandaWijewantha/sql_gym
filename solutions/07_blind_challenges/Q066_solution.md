# Reasoning

## 1. Interpret the Business Question

"Top 5 products per region" for Q4 2025 — but this dataset has *two*
plausible sources of "region": the store where an order was placed, or
the customer's home region. These are genuinely different questions
(where to stock the display vs. who to market to), and the question as
posed doesn't disambiguate — the correct first move, as in Level 5, is
noticing the ambiguity rather than silently picking one.

**Chosen interpretation for this solution**: "region" means the
*store's* region — since the business context ("plan window displays")
is explicitly about physical merchandising at a location, which only
makes sense tied to where the order was fulfilled, not where the
customer happens to live.

## 2. Output Grain

One row = one (region, product) pair, top 5 per region.

## 3. Metric Definition

Gross revenue per (store region, product), completed orders, 2025 Q4.

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.
`order_items`: order_id, product_id, quantity, unit_price.
`stores`: store_id, region.
`products`: product_id, product_name.

## 5. SQL

```sql
WITH region_product_revenue AS (
    SELECT
        s.region,
        p.product_id,
        p.product_name,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN stores s        ON s.store_id = o.store_id
    JOIN order_items oi  ON oi.order_id = o.order_id
    JOIN products p      ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
      AND o.order_date >= '2025-10-01' AND o.order_date < '2026-01-01'
    GROUP BY s.region, p.product_id, p.product_name
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY revenue DESC) AS rn
    FROM region_product_revenue
)
SELECT region, product_name, revenue
FROM ranked
WHERE rn <= 5
ORDER BY region, rn;
```

## 6. Walkthrough

This is the same "top N per group" ranking pattern as Q021, just keyed
on `store.region` instead of `product.category_id`. All four tables are
joined many-to-one throughout (order→store, order→order_items,
order_item→product), so no fan-out risk exists before the
pre-aggregation in `region_product_revenue`.

## 7. Validation

- Confirm each region has at most 5 rows (fewer only if a region has
  fewer than 5 distinct products sold that quarter).
- For one region, manually list its top products sorted by revenue and
  confirm the top 5 match.

## 8. Edge Cases

- Under the *customer*-region interpretation instead, a customer could
  place an order at any store regardless of their home region, so the
  join path would go through `customers.region` instead of
  `stores.region` — and the resulting top-5 lists could differ
  meaningfully from this solution's store-region version, especially
  for regions with a lot of cross-region shopping.
- Online orders are attributed to whichever store record represents
  the online storefront (recall: `store_type = 'online'`), which has
  its own `region` value (Western, per the data generator) — worth
  noting that "region" for online orders may not correspond to where
  the actual customer or shipment is.

## 9. Alternative Approach

The customer-region version simply swaps `JOIN stores s ON s.store_id =
o.store_id` for `JOIN customers c ON c.customer_id = o.customer_id`
and groups by `c.region` instead — structurally identical query, wholly
different business meaning.

## 10. Trade-offs

Not applicable — the two interpretations aren't a stylistic trade-off,
they're two different valid business questions that happen to share
the same surface wording.

## 11. Business Interpretation

Before handing this list to regional merchandising teams, the analyst
should confirm which "region" was intended — a store-region list
supports in-store display decisions directly; a customer-region list
would instead support region-targeted marketing, which is a materially
different use case.
