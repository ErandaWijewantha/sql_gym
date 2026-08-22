# Reasoning

## 1. Interpret the Business Question

Finance wants to know whether tenure (how long someone's been a
customer) correlates with lifetime value — computed per customer, then
summarized per tenure bucket.

## 2. Output Grain

The intermediate grain is one row per customer; the final output grain
is one row per tenure bucket.

## 3. Metric Definition

`lifetime_net_spend` = `SUM(quantity*unit_price - discount_amount)`
across a customer's completed orders. `tenure_months` =
`PERIOD_DIFF` (or `TIMESTAMPDIFF(MONTH, ...)`) between
`registration_date` and the fixed reference date 2025-12-31. Tenure
buckets: "0-6 months," "6-12 months," "12-24 months," "24+ months".

## 4. Required Data

`customers`: customer_id, registration_date.
`orders`: order_id, customer_id, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute lifetime net spend per customer (completed orders)
    Step 2 → compute tenure_months per customer from registration_date
    Step 3 → CASE-bucket tenure_months
    Step 4 → GROUP BY bucket, AVG(lifetime_net_spend)

## 6. Pattern Recognition

Two ideas combined: a customer-grain aggregation (same shape as Q005's
revenue join, applied per customer instead of per channel) and a
CASE-bucketing step (same shape as Q003's price tiers), computed
together and then summarized.

## 7. SQL

```sql
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.registration_date,
        COALESCE(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 0) AS lifetime_net_spend
    FROM customers c
    JOIN orders o        ON o.customer_id = c.customer_id AND o.order_status = 'completed'
    JOIN order_items oi  ON oi.order_id   = o.order_id
    GROUP BY c.customer_id, c.registration_date
),
tenure_bucketed AS (
    SELECT
        customer_id,
        lifetime_net_spend,
        TIMESTAMPDIFF(MONTH, registration_date, '2025-12-31') AS tenure_months,
        CASE
            WHEN TIMESTAMPDIFF(MONTH, registration_date, '2025-12-31') < 6  THEN '0-6 months'
            WHEN TIMESTAMPDIFF(MONTH, registration_date, '2025-12-31') < 12 THEN '6-12 months'
            WHEN TIMESTAMPDIFF(MONTH, registration_date, '2025-12-31') < 24 THEN '12-24 months'
            ELSE '24+ months'
        END AS tenure_bucket
    FROM customer_spend
)
SELECT
    tenure_bucket,
    COUNT(*) AS customer_count,
    ROUND(AVG(lifetime_net_spend), 2) AS avg_lifetime_spend
FROM tenure_bucketed
GROUP BY tenure_bucket
ORDER BY FIELD(tenure_bucket, '0-6 months', '6-12 months', '12-24 months', '24+ months');
```

## 8. Walkthrough

`customer_spend` restricts to *purchasing* customers (the `JOIN` to
`orders`/`order_items` naturally excludes customers with zero orders,
consistent with "purchasing customer" in the question). `tenure_months`
uses `TIMESTAMPDIFF(MONTH, ...)` against the fixed reference date,
never `NOW()`. The `CASE` bucketing mirrors Q003's tier pattern exactly.
The final `GROUP BY tenure_bucket` then computes average lifetime spend
per bucket, with `ORDER BY FIELD(...)` forcing a logical (not
alphabetical) bucket order.

## 9. Validation

- `customer_count` summed across all four buckets should equal the
  total number of customers with >= 1 completed order.
- Spot check one customer: independently compute their
  `lifetime_net_spend` and `tenure_months`, and confirm both match this
  query's intermediate values.
- The "24+ months" bucket should be non-empty, since the dataset allows
  registration dates back to 2021-01-01, comfortably exceeding 24
  months before the 2025-12-31 reference date.

## 10. Edge Cases

- This restricts to *completed* orders for the spend figure (a genuine
  lifetime-value number shouldn't include cancelled/refunded activity),
  but is agnostic about *lifecycle* activity — a customer whose only
  orders were cancelled would have `lifetime_net_spend = 0` and would
  not even appear in this result at all, since the `JOIN` to `orders`
  filters on `order_status = 'completed'` directly. If finance wants
  those customers included with a $0 spend value rather than excluded
  entirely, a `LEFT JOIN` with a status condition moved into the `ON`
  clause (not `WHERE`) would be needed instead.
- **Survivorship caution**: the "24+ months" bucket is, by construction,
  made up entirely of customers who registered a long time ago *and*
  are still being counted at all — it says nothing about customers who
  registered 24+ months ago and then churned so completely they have
  zero completed orders (those are excluded here entirely, per the
  point above). A higher average spend in this bucket could partly
  reflect "customers who survive this long tend to be the more engaged
  ones," not necessarily "tenure itself increases value" — a
  distinction worth raising explicitly with finance rather than letting
  the chart imply causation it can't support.

## 11. Alternative Approach

Computing `tenure_months` via `PERIOD_DIFF(DATE_FORMAT('2025-12-31',
'%Y%m'), DATE_FORMAT(registration_date, '%Y%m'))` is a common
alternative to `TIMESTAMPDIFF(MONTH, ...)` and produces a very similar
(sometimes off-by-one at month boundaries, depending on day-of-month)
result — worth being aware both exist, and picking one consistently
rather than mixing them across a codebase.

## 12. Trade-offs

Not applicable beyond the join-type consideration noted in Edge Cases.

## 13. Business Interpretation

If average lifetime spend rises with tenure, that supports investing
more in retention (each additional month of tenure is worth more,
compounding); if it plateaus early, retention efforts might yield
better ROI focused on the first 6-12 months specifically — but either
conclusion should be reported alongside the survivorship caveat above,
not as a clean causal story.
