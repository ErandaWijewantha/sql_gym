# Reasoning

## 1. Interpret the Business Question

"Underperforming" needs a benchmark before it means anything. This
dataset has no explicit budget/target table, so the two realistic
options are: compare against peer stores of the same `store_type`, or
compare a store against its own recent trend. **Chosen definition**:
a store is "underperforming" if its trailing-3-month net revenue is
both (a) below the median of same-type peer stores, and (b) declining
relative to its own prior 3 months — requiring both makes this a
meaningfully stricter, more defensible flag than either signal alone.

## 2. Output Grain

One row = one store.

## 3. Metric Definition

`recent_3mo_revenue` = net revenue (completed orders) for
2025-10-01 through 2025-12-31. `prior_3mo_revenue` = the same measure
for 2025-07-01 through 2025-09-30. "Peer median" = median
`recent_3mo_revenue` among stores sharing the same `store_type`.

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.
`stores`: store_id, store_name, store_type.

## 5. Logical Decomposition

    Step 1 → compute recent_3mo_revenue and prior_3mo_revenue per store
    Step 2 → compute each store_type's peer median of recent_3mo_revenue
    Step 3 → flag stores below their peer median AND declining vs. prior period

## 6. Pattern Recognition

This combines a peer-benchmark comparison (window function, similar to
Q028's regional-average pattern) with a period-over-period comparison
(similar to Q023's month-over-month LAG, collapsed here to two fixed
quarters instead of a rolling series).

## 7. SQL

```sql
WITH store_period_revenue AS (
    SELECT
        s.store_id,
        s.store_name,
        s.store_type,
        SUM(CASE
            WHEN o.order_date >= '2025-10-01' AND o.order_date < '2026-01-01'
            THEN oi.quantity * oi.unit_price - oi.discount_amount ELSE 0
        END) AS recent_3mo_revenue,
        SUM(CASE
            WHEN o.order_date >= '2025-07-01' AND o.order_date < '2025-10-01'
            THEN oi.quantity * oi.unit_price - oi.discount_amount ELSE 0
        END) AS prior_3mo_revenue
    FROM stores s
    JOIN orders o ON o.store_id = s.store_id AND o.order_status = 'completed'
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_date >= '2025-07-01' AND o.order_date < '2026-01-01'
    GROUP BY s.store_id, s.store_name, s.store_type
),
ranked_by_type AS (
    SELECT
        store_id, store_name, store_type, recent_3mo_revenue, prior_3mo_revenue,
        ROW_NUMBER() OVER (PARTITION BY store_type ORDER BY recent_3mo_revenue) AS rn,
        COUNT(*)     OVER (PARTITION BY store_type) AS peer_count
    FROM store_period_revenue
),
peer_median AS (
    SELECT store_type, AVG(recent_3mo_revenue) AS median_revenue
    FROM ranked_by_type
    WHERE rn IN ((peer_count + 1) DIV 2, (peer_count + 2) DIV 2)
    GROUP BY store_type
)
SELECT
    r.store_id, r.store_name, r.store_type,
    r.recent_3mo_revenue, r.prior_3mo_revenue, pm.median_revenue,
    (r.recent_3mo_revenue < r.prior_3mo_revenue) AS declining_vs_prior
FROM ranked_by_type r
JOIN peer_median pm ON pm.store_type = r.store_type
WHERE r.recent_3mo_revenue < pm.median_revenue
  AND r.recent_3mo_revenue < r.prior_3mo_revenue
ORDER BY r.store_type, r.recent_3mo_revenue;
```

## 8. Walkthrough

`store_period_revenue` computes both quarters' revenue per store in
one pass using conditional aggregation (two `SUM(CASE WHEN ...)`
expressions), restricted up front by the outer `WHERE` to only scan the
6 months actually needed. MySQL 8 has no built-in `MEDIAN()` aggregate,
so `ranked_by_type` numbers each store within its `store_type` peer
group by revenue, and `peer_median` picks the middle row — using
`(peer_count + 1) DIV 2` and `(peer_count + 2) DIV 2` as the two
candidate positions handles both odd-sized groups (both expressions
land on the same middle row, so `AVG` of one value is just that value)
and even-sized groups (the two expressions land on the two middle rows,
and `AVG` correctly averages them). The final query joins each store
back to its peer group's median and requires *both* conditions: below
peer median, and declining versus the store's own prior quarter.

## 9. Validation

- Manually compute the peer median for one `store_type` group by
  listing all its `recent_3mo_revenue` values sorted, and confirm the
  computed median matches.
- Confirm every flagged store's `recent_3mo_revenue` really is less
  than both its peer median and its own prior-quarter figure.
- Compare against a simpler, single-signal version (just "below peer
  median," no trend requirement) to see how much smaller and more
  targeted the combined-condition list is.

## 10. Edge Cases

- Online stores (only 2 in this dataset) form a peer group of just 2 —
  a "median of 2" is really just their average, and any comparison
  within such a small peer group is statistically thin; worth
  footnoting rather than treating with the same confidence as the
  35-store-wide standard/outlet/flagship groups.
- A store that's simply smaller by design (e.g., an outlet store) isn't
  unfairly penalized here, since it's only compared against other
  outlet stores, not flagships.
- This entirely sidesteps "compare against a target/budget" because
  this dataset has no such table — worth being explicit with the VP
  that this is a peer-and-trend-based proxy, not a comparison against
  an actual company target.

## 11. Alternative Approach

A simpler, single-signal version — just "bottom quartile of revenue
within store_type, full 24-month total, no trend requirement" — is
easier to compute (no median subquery, no period split) and easier to
explain, at the cost of potentially flagging a store that's always
been modest-but-stable (not actually "under-performing" in any dynamic
sense) rather than one that's actively declining.

## 12. Trade-offs

The combined peer + trend definition used here is stricter and more
defensible for a quarterly review (it answers "who's getting worse,
relative to peers," not just "who's small") but is more complex to
compute and communicate. A simpler one-signal version trades precision
for ease of explanation — reasonable if the VP just wants a quick
starting list to discuss, not a rigorous statistical flag.

## 13. Business Interpretation

Bringing this to the VP should come with the explicit statement: "I
defined underperforming as below-peer-median AND declining vs. last
quarter, since we don't have a stored budget/target to compare against
— here's the list under that definition, and here's how it would
change under a looser one."
