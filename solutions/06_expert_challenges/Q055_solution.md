# Reasoning

## 1. Interpret the Business Question

The store manager wants statistical confirmation of "off" days —
formalizing "typical" as a mean and a measure of normal variation, then
flagging days that fall far outside that range.

## 2. Output Grain

One row = one (store, day) pair, restricted to days flagged as
anomalous.

## 3. Metric Definition

Per store: `mean_daily_revenue` and `stddev_daily_revenue` computed
across every day in the dataset (including true zero-revenue days — a
day with no completed orders is a real, meaningful data point for
"typical," not a gap to ignore). A day is anomalous if its revenue is
more than 2 standard deviations above or below that store's mean.

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → build a full store x calendar-day grid (2024-01-01 through
              2025-12-31), so zero-revenue days are explicit rows
    Step 2 → compute daily net revenue per (store, day), defaulting to 0
    Step 3 → compute each store's mean and stddev of daily revenue across
              all 730 days
    Step 4 → flag days more than 2 stddev away from that store's mean

## 6. Pattern Recognition

"Unusually far from typical" → mean and standard deviation, computed
per group via window functions (`AVG(...) OVER (PARTITION BY store_id)`
and `STDDEV(...) OVER (PARTITION BY store_id)`), then a per-row
distance-from-mean check — the same "compute a group statistic
alongside each row" idea as Q027's percentage-of-total, applied to a
statistical measure instead of a sum.

## 7. SQL

```sql
WITH RECURSIVE days AS (
    SELECT DATE('2024-01-01') AS day_date
    UNION ALL
    SELECT DATE_ADD(day_date, INTERVAL 1 DAY)
    FROM days
    WHERE day_date < '2025-12-31'
),
daily_revenue AS (
    SELECT
        o.store_id,
        DATE(o.order_date) AS day_date,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.store_id, DATE(o.order_date)
),
full_series AS (
    SELECT
        s.store_id,
        d.day_date,
        COALESCE(dr.net_revenue, 0) AS net_revenue
    FROM stores s
    CROSS JOIN days d
    LEFT JOIN daily_revenue dr ON dr.store_id = s.store_id AND dr.day_date = d.day_date
),
with_stats AS (
    SELECT
        store_id,
        day_date,
        net_revenue,
        AVG(net_revenue)    OVER (PARTITION BY store_id) AS mean_daily_revenue,
        STDDEV(net_revenue) OVER (PARTITION BY store_id) AS stddev_daily_revenue
    FROM full_series
)
SELECT
    store_id, day_date, net_revenue,
    ROUND(mean_daily_revenue, 2) AS mean_daily_revenue,
    ROUND(stddev_daily_revenue, 2) AS stddev_daily_revenue,
    CASE WHEN net_revenue > mean_daily_revenue THEN 'unusually high' ELSE 'unusually low' END AS anomaly_type
FROM with_stats
WHERE ABS(net_revenue - mean_daily_revenue) > 2 * stddev_daily_revenue
ORDER BY store_id, day_date;
```

## 8. Walkthrough

The full `days` x `stores` grid guarantees every store has exactly 730
rows, one per calendar day, with genuine zero-revenue days explicitly
present (via `COALESCE(dr.net_revenue, 0)`) — critical, since excluding
zero-order days from the mean/stddev calculation would understate how
much a store's daily revenue actually varies, and would make truly
"unusually low" days invisible (there'd be no row for a day with
literally zero sales to even flag). `AVG(...) OVER (PARTITION BY
store_id)` and `STDDEV(...) OVER (PARTITION BY store_id)` compute each
store's own mean and standard deviation *alongside every one of its
daily rows*, without collapsing the grain — the same window-function
technique as Q027. The final filter flags any day more than 2 standard
deviations from that store's own mean, in either direction.

## 9. Validation

- For one store, manually verify its `mean_daily_revenue` and
  `stddev_daily_revenue` are constant across all 730 of its rows (a
  quick way to confirm the window function computed a true per-store
  statistic, not something varying incorrectly by row).
- Confirm the number of flagged days per store is small relative to
  730 — under a normal-ish distribution, roughly 4-5% of days should
  fall outside 2 standard deviations; a store with a much larger
  fraction flagged suggests its daily revenue isn't well-approximated
  by a simple mean/stddev model (e.g., it might be strongly bimodal or
  seasonal) rather than a query bug.

## 10. Edge Cases

- A store with many consecutive zero-revenue days (e.g., a genuinely
  very low-traffic outlet) will have a mean pulled toward zero and a
  moderate stddev — a single big sales day there could easily register
  as "unusually high" even if the absolute revenue is modest compared
  to a flagship store; this method flags relative anomalies per store,
  not absolute outliers across the whole chain.
- Category seasonality (built into this dataset's data generator) means
  some "unusually high" days might simply reflect a predictable
  seasonal peak, not a true anomaly — a more refined version would
  detrend for day-of-week or month-of-year seasonality before flagging,
  which this simple mean/stddev approach does not do.
- `STDDEV()` here is the population standard deviation (`STDDEV` is an
  alias for `STDDEV_POP` in MySQL); using `STDDEV_SAMP` instead would
  give a very slightly different (and, for large day-counts like 730,
  practically negligible) result.

## 11. Alternative Approach

A more sophisticated version would first compute a day-of-week or
month-specific baseline (e.g., "unusual relative to other Saturdays,"
or detrended by the category seasonality shapes from the data
generator) before applying the same mean/stddev anomaly check — a
meaningfully more accurate but also more complex approach, appropriate
if the simple version flags too many "anomalies" that are actually just
predictable patterns.

## 12. Trade-offs

The simple whole-series mean/stddev approach is easy to compute and
explain, but conflates genuine anomalies with predictable seasonal or
weekly patterns; a seasonally-adjusted version is more accurate but
requires meaningfully more modeling effort to build and to explain to
a non-technical store manager.

## 13. Business Interpretation

This gives the store manager exactly what they asked for — statistical
confirmation of which specific days were genuinely unusual for their
store — while the caveats above (seasonality, day-of-week effects) are
worth mentioning so the manager doesn't over-interpret a predictable
Saturday peak as a mystery worth investigating.
