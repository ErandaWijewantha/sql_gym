# Reasoning

## 1. Interpret the Business Question

Customer success wants evidence, not just intuition, that slow support
resolution correlates with reduced subsequent purchasing — while being
honest that correlation here cannot prove causation (a theme carried
over from Q043).

**Chosen design**: for each customer, take their *most recent resolved*
support ticket. Split customers into "fast resolution" (below the
median resolution time across all resolved tickets) and "slow
resolution" (at or above the median). Compare the fraction of each
group who placed at least one completed order in the 60 days following
that ticket's resolution.

## 2. Output Grain

One row per group ("fast" / "slow").

## 3. Metric Definition

`resolution_hours = TIMESTAMPDIFF(HOUR, created_at, resolved_at)` for
each resolved ticket. `placed_order_within_60d` = whether the customer
has >= 1 completed order in the 60 days after `resolved_at`.

## 4. Required Data

`support_tickets`: ticket_id, customer_id, created_at, resolved_at.
`orders`: customer_id, order_date, order_status.

## 5. Logical Decomposition

    Step 1 → for each customer, find their most recent resolved ticket
    Step 2 → compute its resolution_hours
    Step 3 → split into fast/slow using the overall median resolution time
    Step 4 → for each customer, check for a completed order within 60 days
              after that ticket's resolved_at
    Step 5 → compare the "placed order" rate between the two groups

## 6. SQL

```sql
WITH resolved_tickets AS (
    SELECT
        ticket_id, customer_id, created_at, resolved_at,
        TIMESTAMPDIFF(HOUR, created_at, resolved_at) AS resolution_hours,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY resolved_at DESC) AS rn
    FROM support_tickets
    WHERE resolved_at IS NOT NULL
),
latest_ticket AS (
    SELECT customer_id, resolved_at, resolution_hours
    FROM resolved_tickets
    WHERE rn = 1
),
ranked_for_median AS (
    SELECT
        resolution_hours,
        ROW_NUMBER() OVER (ORDER BY resolution_hours) AS rn,
        COUNT(*) OVER () AS total_n
    FROM latest_ticket
),
median_calc AS (
    SELECT AVG(resolution_hours) AS median_hours
    FROM ranked_for_median
    WHERE rn IN ((total_n + 1) DIV 2, (total_n + 2) DIV 2)
),
grouped AS (
    SELECT
        lt.customer_id,
        lt.resolved_at,
        lt.resolution_hours,
        CASE WHEN lt.resolution_hours < mc.median_hours THEN 'fast' ELSE 'slow' END AS speed_group,
        EXISTS (
            SELECT 1 FROM orders o
            WHERE o.customer_id = lt.customer_id
              AND o.order_status = 'completed'
              AND o.order_date > lt.resolved_at
              AND o.order_date <= DATE_ADD(lt.resolved_at, INTERVAL 60 DAY)
        ) AS ordered_within_60d
    FROM latest_ticket lt
    CROSS JOIN median_calc mc
)
SELECT
    speed_group,
    COUNT(*) AS customer_count,
    SUM(ordered_within_60d) AS ordered_within_60d_count,
    ROUND(SUM(ordered_within_60d) * 100.0 / COUNT(*), 1) AS pct_ordered_within_60d
FROM grouped
GROUP BY speed_group;
```

## 7. Walkthrough

`resolved_tickets` computes resolution time for every resolved ticket
and numbers each customer's tickets from most-recent-resolved backward;
`latest_ticket` keeps only `rn = 1` — one row per customer, their most
recently resolved ticket. `median_calc` uses the same row-number-based
median trick as Q042. `grouped` classifies each customer as fast/slow
relative to that overall median, then uses a correlated `EXISTS` to
check for a completed order strictly after `resolved_at` and within the
following 60 days. The final aggregation compares the "ordered within
60 days" rate between the two groups.

## 8. Validation

- Confirm the median split roughly divides customers into two
  comparably-sized groups (by construction, close to 50/50, since it's
  literally the median).
- Manually verify one customer's `ordered_within_60d` flag by directly
  checking their orders against their ticket's `resolved_at` date.
- Compare `pct_ordered_within_60d` between groups — a meaningfully
  lower rate in the "slow" group is suggestive, but see the caveat
  below before calling it conclusive.

## 9. Edge Cases and the Core Caveat

- **This cannot separate "slow support caused reduced buying" from
  "customers who were already about to churn happened to also file
  tickets that took longer to resolve"** (e.g., a low-priority,
  low-urgency ticket from a disengaged customer might simply sit longer
  in a queue than an urgent one from an actively engaged customer) —
  ticket priority itself might be a confound driving both resolution
  time and subsequent purchasing.
- Customers with *no* resolved ticket at all are excluded entirely —
  this analysis only speaks to customers who *did* file and get a
  resolution, not the broader customer base.
- Using each customer's *most recent* ticket (rather than, say, their
  *first* or *average across all* tickets) is a specific, debatable
  choice — a customer with one fast early ticket and one slow recent
  one would be classified by the recent one only.

## 10. Alternative Approach

Controlling for ticket `priority` (comparing fast vs. slow resolution
*within* the same priority level, rather than across the whole
customer base) would partially address the confound above — a
meaningfully more rigorous version worth pursuing if this initial
comparison shows a notable gap.

## 11. Trade-offs

The simple median-split comparison used here is easy to compute and
explain, but is vulnerable to the priority-level confound described
above; a priority-stratified version is more defensible but requires
enough sample size within each priority x speed combination to remain
statistically meaningful.

## 12. Business Interpretation

If the gap is large, it's a reasonable data point to include in a case
for more support headcount — but it should be presented as
correlational evidence alongside the priority-confound caveat, not as
proof that faster resolution *causes* more purchasing. The honest
framing: "customers whose last ticket was slow to resolve buy less
afterward than those whose ticket was fast — this is suggestive, but
we haven't ruled out that already-disengaged customers both file
lower-priority tickets and buy less, regardless of resolution speed."
