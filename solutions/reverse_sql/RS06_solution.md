# RS06 — Solution

## Grain
One row = one (region, product) pair, limited to the top 3 per region.

## What is being computed
Each store region's top 3 products by gross revenue (completed
orders), using `RANK()` partitioned by region.

## Pattern
Top-N-per-group ranking window function — the same shape as Q021
(top 3 products per category), here partitioned by region instead of
category, and using `RANK()` (which preserves ties, possibly yielding
more than 3 rows for a region with a tie at the 3rd position) rather
than `ROW_NUMBER()`.

## Likely business question
"What are the top 3 best-selling products in each region?" — very
close to Q066's blind-challenge framing, using store region
specifically (note: a different query joining through `customers`
instead of `stores` would answer the customer-region version of the
same question — the ambiguity Q066 highlights explicitly).

## Notes
Because `RANK()` is used (not `ROW_NUMBER()`), a region with a 3-way
tie for 2nd place would show 4 rows (two counted as "2", then the next
distinct value as "4," but the `rnk <= 3` filter would actually admit
all rows tied at rank <= 3) — worth checking whether that matches what
was intended.

## Verification query

```sql
WITH region_revenue AS (
    SELECT
        s.region,
        p.product_id,
        p.product_name,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN stores s ON s.store_id = o.store_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'completed'
    GROUP BY s.region, p.product_id, p.product_name
)
SELECT region, product_name, revenue
FROM (
    SELECT *, RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS rnk
    FROM region_revenue
) t
WHERE rnk <= 3;
```
