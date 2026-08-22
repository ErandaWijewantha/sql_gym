# Reasoning

## 1. Interpret the Business Question

"Which products need investigating" bundles at least four unrelated
signals. Rather than forcing them into one score (which would hide
*why* a product was flagged), this solution computes each
independently and shows where they overlap.

**Chosen signals**: (a) return rate by unit (with a minimum-volume
guard, as in Q009), (b) frequency of stockouts (`closing_stock = 0`
days), (c) a 3-consecutive-month sales decline (reusing Q038 exactly),
and (d) products sold at a loss after typical discounting.

## 2. Output Grain

One row = one product, with independent flag columns per signal.

## 3. Metric Definition

- Return rate: `SUM(returns.quantity) / SUM(order_items.quantity)`, only
  for products with >= 20 units sold.
- Stockout frequency: count of `inventory` rows with `closing_stock = 0`
  for that product, across all stores.
- Decline streak: reuse of Q038's flag (has >= 1 three-month decline
  streak).
- Loss-making: average realized unit price after discount
  (`SUM(quantity*unit_price - discount_amount)/SUM(quantity)`) below
  `products.cost`.

## 4. Required Data

`products`, `order_items`, `orders`, `returns`, `inventory`.

## 5. Logical Decomposition

    Step 1 → compute each signal independently, at product grain
    Step 2 → LEFT JOIN all four onto the product list
    Step 3 → present all flags side by side (no forced single score)

## 6. SQL

```sql
WITH sales_summary AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'completed'
    GROUP BY oi.product_id
),
return_summary AS (
    SELECT product_id, SUM(quantity) AS units_returned
    FROM returns
    GROUP BY product_id
),
stockout_summary AS (
    SELECT product_id, SUM(CASE WHEN closing_stock = 0 THEN 1 ELSE 0 END) AS stockout_days
    FROM inventory
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_name,
    ss.units_sold,
    ROUND(COALESCE(rs.units_returned, 0) / NULLIF(ss.units_sold, 0) * 100, 1) AS return_rate_pct,
    COALESCE(so.stockout_days, 0) AS stockout_days,
    ROUND(ss.net_revenue / NULLIF(ss.units_sold, 0), 2) AS avg_realized_unit_price,
    p.cost,
    (ss.net_revenue / NULLIF(ss.units_sold, 0)) < p.cost AS is_loss_making
FROM products p
JOIN sales_summary ss ON ss.product_id = p.product_id
LEFT JOIN return_summary rs ON rs.product_id = p.product_id
LEFT JOIN stockout_summary so ON so.product_id = p.product_id
WHERE ss.units_sold >= 20
  AND (
      COALESCE(rs.units_returned, 0) / NULLIF(ss.units_sold, 0) > 0.10
      OR COALESCE(so.stockout_days, 0) > 30
      OR (ss.net_revenue / NULLIF(ss.units_sold, 0)) < p.cost
  )
ORDER BY is_loss_making DESC, return_rate_pct DESC;
```

## 7. Walkthrough

`sales_summary`, `return_summary`, and `stockout_summary` each
independently pre-aggregate their source table to product grain — a
direct application of Level 2's core lesson, especially important here
since three separate one-to-many tables (`order_items`, `returns`,
`inventory`) all hang off `products`. `LEFT JOIN`s (not inner joins)
onto `sales_summary` (already filtered to products with real sales via
the base `JOIN`) mean a product with no returns or no stockout days
correctly shows `0`, not disappearing. The final `WHERE` requires *any*
of the three numeric signals to breach its threshold, deliberately
using `OR` rather than forcing all conditions — the point is triage
coverage, not a single strict AND.

## 8. Validation

- Confirm every returned row triggers at least one of the three
  threshold conditions when inspected individually.
- Spot check one flagged "loss-making" product: independently compute
  `net_revenue/units_sold` and compare to `cost`.
- Confirm the never-sold products (excluded via the inner join to
  `sales_summary`) don't appear at all — they have no sales to
  investigate in this particular sense (though they might deserve a
  *different* kind of investigation, e.g., "why has this never sold,"
  which is outside this query's scope).

## 9. Edge Cases

- The decline-streak signal (Q038) isn't included in this particular
  query for brevity, since it requires the full recursive-CTE machinery
  — in practice you'd union its result in as a fourth boolean column,
  exactly as the other three are joined.
- The 10% return-rate and 30-stockout-day thresholds are judgment
  calls, not universal constants — worth stating explicitly to
  Operations, same as every other threshold in this level.
- A product could be flagged for multiple reasons simultaneously (e.g.,
  both loss-making and high-return) — that's a legitimate higher-
  priority signal, not a bug.

## 10. Alternative Approach

A single weighted composite score (e.g., normalize each of the four
signals to 0-1 and sum them) would produce one ranked list instead of
independent flags — easier to sort by "worst overall," but hides *why*
a product ranks where it does, which matters more for an Operations
team that needs to decide *what kind* of action to take (a stockout
problem needs a different fix than a margin problem).

## 11. Trade-offs

Independent flags (this solution) support better triage and root-cause
clarity; a composite score supports easier prioritization at a glance.
For an Operations audience specifically, independent flags are usually
more actionable.

## 12. Business Interpretation

Operations gets a short, explainable list where each row shows *which*
problem(s) apply — a product flagged only for stockouts needs a supply
chain fix, one flagged only for margin needs a pricing review, and one
flagged for both needs both, in that priority order.
