# Reasoning

## 1. Interpret the Business Question

A useful early-warning list needs to catch a *slowdown*, not just
silence — combining three independent signals so retention sees why
each customer was flagged, and requiring at least two of three to
agree (rather than any single noisy signal) before flagging anyone.

**Chosen design**: (1) their current gap since last order exceeds 1.5x
their own historical average gap — a personalized recency signal, so a
VIP who normally orders weekly is flagged much sooner than an
occasional buyer with the same absolute day-count; (2) their order
count in the last 90 days is lower than the prior 90 days; (3) their
net spend in the last 90 days is lower than the prior 90 days. A
customer needs at least 4 total completed orders (3 measurable gaps) to
even be eligible, since a trend requires enough history to establish
one.

## 2. Output Grain

One row = one customer, with each of the three signals shown
independently plus a combined count.

## 3. Metric Definition

See design above — `recency_flag`, `frequency_flag`, `monetary_flag`,
each boolean; `signal_count = ` sum of the three.

## 4. Required Data

`orders`: customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute each customer's gap history and its average (LAG-based)
    Step 2 → compute their current gap since last order, compare to 1.5x average
    Step 3 → compute order count and net spend for the last 90 days vs the
              prior 90 days
    Step 4 → combine all three signals, require history depth and >= 2 flags

## 6. SQL

```sql
WITH order_gaps AS (
    SELECT
        customer_id,
        order_date,
        DATEDIFF(
            order_date,
            LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)
        ) AS gap_days
    FROM orders
    WHERE order_status = 'completed'
),
avg_gap AS (
    SELECT customer_id, AVG(gap_days) AS avg_gap_days, COUNT(*) AS gap_count
    FROM order_gaps
    WHERE gap_days IS NOT NULL
    GROUP BY customer_id
),
last_order AS (
    SELECT customer_id, MAX(order_date) AS last_order_date
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id
),
recency_check AS (
    SELECT
        lo.customer_id,
        DATEDIFF('2025-12-31', lo.last_order_date) AS current_gap_days,
        ag.avg_gap_days,
        ag.gap_count,
        (DATEDIFF('2025-12-31', lo.last_order_date) > 1.5 * ag.avg_gap_days) AS recency_flag
    FROM last_order lo
    JOIN avg_gap ag ON ag.customer_id = lo.customer_id
),
period_orders AS (
    SELECT
        customer_id,
        SUM(CASE WHEN order_date >= '2025-10-02' THEN 1 ELSE 0 END) AS recent_90d_orders,
        SUM(CASE WHEN order_date >= '2025-07-04' AND order_date < '2025-10-02' THEN 1 ELSE 0 END) AS prior_90d_orders
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id
),
period_spend AS (
    SELECT
        o.customer_id,
        SUM(CASE WHEN o.order_date >= '2025-10-02' THEN oi.quantity*oi.unit_price - oi.discount_amount ELSE 0 END) AS recent_90d_spend,
        SUM(CASE WHEN o.order_date >= '2025-07-04' AND o.order_date < '2025-10-02' THEN oi.quantity*oi.unit_price - oi.discount_amount ELSE 0 END) AS prior_90d_spend
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.customer_id
)
SELECT
    rc.customer_id,
    rc.current_gap_days,
    ROUND(rc.avg_gap_days, 1) AS avg_gap_days,
    rc.recency_flag,
    po.recent_90d_orders, po.prior_90d_orders,
    (po.recent_90d_orders < po.prior_90d_orders) AS frequency_flag,
    ROUND(ps.recent_90d_spend, 2) AS recent_90d_spend,
    ROUND(ps.prior_90d_spend, 2) AS prior_90d_spend,
    (ps.recent_90d_spend < ps.prior_90d_spend) AS monetary_flag,
    (rc.recency_flag
        + (po.recent_90d_orders < po.prior_90d_orders)
        + (ps.recent_90d_spend < ps.prior_90d_spend)) AS signal_count
FROM recency_check rc
JOIN period_orders po ON po.customer_id = rc.customer_id
JOIN period_spend ps  ON ps.customer_id = rc.customer_id
WHERE rc.gap_count >= 3
  AND (rc.recency_flag
        + (po.recent_90d_orders < po.prior_90d_orders)
        + (ps.recent_90d_spend < ps.prior_90d_spend)) >= 2
ORDER BY signal_count DESC, rc.current_gap_days DESC;
```

## 7. Walkthrough

`order_gaps` uses `LAG` to compute the day-gap between each of a
customer's consecutive completed orders; `avg_gap` then averages those
gaps per customer (requiring `gap_days IS NOT NULL`, which naturally
excludes each customer's first order). `recency_check` compares the
customer's *current* silence (since their last order, against the
fixed reference date) to 1.5x their own historical average gap — a
personalized threshold rather than one fixed number for everyone.
`period_orders` and `period_spend` independently compute 90-day
before/after windows via conditional aggregation. The final query joins
all three (already at customer grain, so no fan-out risk) and requires
`gap_count >= 3` (at least 4 total orders) before requiring at least 2
of the 3 boolean signals to hold.

## 8. Validation

- Pick one flagged customer and manually verify at least 2 of the 3
  `_flag` columns are genuinely true from the raw numbers shown
  alongside them.
- Confirm no customer with fewer than 4 total completed orders appears
  in the result (the `gap_count >= 3` filter should guarantee this).
- Check the distribution of `signal_count` across the result — if
  every single flagged customer has all 3 signals (never just 2), the
  "require >= 2" threshold isn't doing meaningful work and could be
  tightened or loosened depending on what retention actually wants.

## 9. Edge Cases

- A brand-new VIP with only 4 orders very close together has a very
  small `avg_gap_days`, making the 1.5x recency threshold easy to trip
  even with a moderate pause — arguably correct (a customer who
  normally orders every 5 days going quiet for 20 is a meaningful
  change), but worth being aware the recency_flag is much more
  sensitive for high-frequency customers than for naturally sporadic
  ones.
- The 1.5x multiplier and the "2 of 3 signals" threshold are both
  judgment calls, exactly like every other threshold in this level —
  they should be revisited with retention based on how the resulting
  list size and precision feel in practice, not treated as fixed
  constants.
- A customer whose recent decline is due to one large one-off order in
  the "prior" window (rather than a genuine ongoing pattern) could
  trigger `monetary_flag` on a fluke — this is exactly why the query
  requires agreement across multiple independent signals rather than
  trusting any single one.

## 10. Alternative Approach

A single weighted risk score (e.g., a linear combination of normalized
recency, frequency, and monetary signals) would produce a smooth
ranking instead of a binary "2 of 3" cutoff — more nuanced for
prioritizing a long list, but harder to explain to the retention team
in a sentence, and requires choosing weights that are just as arbitrary
as this solution's thresholds.

## 11. Trade-offs

The 3-signal-agreement approach used here is transparent (retention can
see exactly why someone was flagged) and conservative (fewer false
positives than any single signal alone), at the cost of missing
customers who show a very strong signal on just one dimension (e.g.,
a severe recency lapse but with only 2 flags total because their
frequency/monetary numbers are still borderline).

## 12. Business Interpretation

This is a **starting list for triage, not a certain prediction** — hand
it to retention with the three underlying numbers visible per customer
(not just a pass/fail flag), so they can weigh which signal matters
most for a given customer's outreach message, and revisit the
thresholds after seeing how the list performs over the next quarter.
