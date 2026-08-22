# Reasoning

## 1. Interpret the Business Question

Marketing wants a stage-by-stage funnel per channel: how many unique
customers reached each stage, and what fraction was lost moving to the
next one.

## 2. Output Grain

One row = one campaign channel.

## 3. Metric Definition

Per channel: `customers_impressed`, `customers_clicked`,
`customers_converted` — each a **distinct customer count**, not a raw
interaction count (a customer could generate multiple impressions for
campaigns in the same channel; the funnel should count people, not
events). `impression_to_click_dropoff = 1 - customers_clicked /
customers_impressed`; `click_to_conversion_dropoff = 1 -
customers_converted / customers_clicked`.

## 4. Required Data

`campaigns`: campaign_id, channel.
`customer_campaigns`: customer_id, campaign_id, interaction_type.

## 5. Logical Decomposition

    Step 1 → join customer_campaigns to campaigns to get channel
    Step 2 → per channel, count DISTINCT customers with each interaction_type
    Step 3 → compute drop-off rates between consecutive stages

## 6. Pattern Recognition

"Stage counts, then drop-off between stages" → conditional aggregation
with `COUNT(DISTINCT ...)` per stage (not a fan-out-prone join across
stages), since a customer's presence at a later stage doesn't remove
their row at an earlier one — they need to be counted independently at
each stage from the same joined table.

## 7. SQL

```sql
WITH interactions AS (
    SELECT
        c.channel,
        cc.customer_id,
        cc.interaction_type
    FROM customer_campaigns cc
    JOIN campaigns c ON c.campaign_id = cc.campaign_id
),
stage_counts AS (
    SELECT
        channel,
        COUNT(DISTINCT CASE WHEN interaction_type = 'impression' THEN customer_id END) AS customers_impressed,
        COUNT(DISTINCT CASE WHEN interaction_type = 'click'      THEN customer_id END) AS customers_clicked,
        COUNT(DISTINCT CASE WHEN interaction_type = 'conversion' THEN customer_id END) AS customers_converted
    FROM interactions
    GROUP BY channel
)
SELECT
    channel,
    customers_impressed,
    customers_clicked,
    customers_converted,
    ROUND((1 - customers_clicked * 1.0 / NULLIF(customers_impressed, 0)) * 100, 1) AS impression_to_click_dropoff_pct,
    ROUND((1 - customers_converted * 1.0 / NULLIF(customers_clicked, 0)) * 100, 1) AS click_to_conversion_dropoff_pct
FROM stage_counts
ORDER BY impression_to_click_dropoff_pct DESC;
```

## 8. Walkthrough

`interactions` attaches `channel` to every raw interaction row.
`stage_counts` then uses `COUNT(DISTINCT CASE WHEN interaction_type = X
THEN customer_id END)` for each stage independently — this counts *how
many distinct customers* reached each stage, without requiring any
join between stages (a customer who both clicked and converted is
correctly counted in both `customers_clicked` and
`customers_converted`, since these are independent conditional counts
over the same joined table, not a chain of joins that would fan out).
The drop-off percentages are then simple ratios between consecutive
stage counts.

## 9. Validation

- `customers_converted <= customers_clicked <= customers_impressed`
  should hold for every channel, since the data generator's funnel
  logic only allows a click after an impression and a conversion after
  a click for the same customer-campaign pair — worth confirming
  directly as a sanity check rather than assuming.
- Manually verify one channel's `customers_clicked` by running
  `SELECT COUNT(DISTINCT customer_id) FROM customer_campaigns cc JOIN
  campaigns c ON ... WHERE c.channel = '<channel>' AND
  interaction_type='click'` directly.

## 10. Edge Cases

- If a channel has zero clicks, `click_to_conversion_dropoff_pct`
  would divide by zero — `NULLIF(customers_clicked, 0)` guards against
  a hard error, returning `NULL` instead, which correctly signals "not
  computable" rather than a misleading 0% or 100%.
- This counts a customer once per stage even if they interacted with
  *multiple different campaigns* within the same channel — appropriate
  for a channel-level funnel view, but worth noting if the business
  actually wanted a per-campaign funnel instead (a simple change: add
  `campaign_id` to the `GROUP BY` and drop the channel-level rollup).

## 11. Alternative Approach

A version using `LEFT JOIN`s between three separately pre-aggregated
per-stage customer lists (rather than conditional aggregation) would
produce the same result and might be clearer to someone unfamiliar with
`COUNT(DISTINCT CASE WHEN ...)`, at the cost of more verbose SQL for no
real benefit here.

## 12. Trade-offs

Not applicable — conditional aggregation is the concise, idiomatic
choice for this shape.

## 13. Business Interpretation

A channel with heavy impression-to-click drop-off has a
messaging/creative problem (people see it but don't engage); a channel
with heavy click-to-conversion drop-off has a landing-page or
offer problem (people engage but don't buy) — the fix differs
completely depending on which stage is actually leaking, which is
exactly why this needs to be broken out by stage rather than reported
as one overall conversion rate.
