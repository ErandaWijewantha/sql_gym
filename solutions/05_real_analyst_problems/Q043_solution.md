# Reasoning

## 1. Interpret the Business Question

"Did it work?" implies a clean causal answer that this data cannot
fully deliver — there's no randomized control group. The professional
answer is to present multiple honest cuts with their weaknesses stated,
not a single false-confidence number.

**Chosen approach for this solution**: compare average order value and
order rate for customers who *converted* on the campaign (per
`customer_campaigns.interaction_type = 'conversion'`) against customers
who were merely *impressed* but never clicked or converted, in the 30
days following each customer's interaction — while explicitly flagging
that this is a correlational comparison, not a causal one, since
campaigns may have targeted or naturally attracted higher-intent
customers to begin with.

## 2. Output Grain

One summary row per comparison group ("converted" vs. "impression
only").

## 3. Metric Definition

For each group: average net spend (completed orders) in the 30 days
following the customer's last interaction with the chosen campaign.

## 4. Required Data

`campaigns`: campaign_id, campaign_name, start_date, end_date.
`customer_campaigns`: customer_id, campaign_id, interaction_date,
interaction_type.
`orders`, `order_items`: for post-interaction spend.

## 5. Logical Decomposition

    Step 1 → pick one campaign_id
    Step 2 → for each customer, find their interaction_type and the date
              of their last interaction with it
    Step 3 → split customers into "converted" vs "impression only"
    Step 4 → compute each group's average net spend in the 30 days after
              their interaction date
    Step 5 → compare, with caveats

## 6. SQL

```sql
WITH campaign_interactions AS (
    SELECT
        customer_id,
        MAX(interaction_date) AS last_interaction_date,
        MAX(CASE WHEN interaction_type = 'conversion' THEN 1 ELSE 0 END) AS converted
    FROM customer_campaigns
    WHERE campaign_id = 1
    GROUP BY customer_id
),
post_interaction_spend AS (
    SELECT
        ci.customer_id,
        ci.converted,
        COALESCE(SUM(oi.quantity * oi.unit_price - oi.discount_amount), 0) AS spend_30d_after
    FROM campaign_interactions ci
    LEFT JOIN orders o
        ON o.customer_id = ci.customer_id
       AND o.order_status = 'completed'
       AND o.order_date >= ci.last_interaction_date
       AND o.order_date <  DATE_ADD(ci.last_interaction_date, INTERVAL 30 DAY)
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY ci.customer_id, ci.converted
)
SELECT
    CASE WHEN converted = 1 THEN 'converted' ELSE 'impression/click only' END AS group_label,
    COUNT(*) AS customer_count,
    ROUND(AVG(spend_30d_after), 2) AS avg_30d_spend
FROM post_interaction_spend
GROUP BY converted;
```

## 7. Walkthrough

`campaign_interactions` collapses each customer's activity on the
chosen campaign to a single row, flagging whether they ever converted.
`post_interaction_spend` then measures completed-order net spend in the
30 days immediately following their last interaction (using a `LEFT
JOIN` so customers with zero subsequent orders correctly contribute
`$0`, not disappear). The final query compares average spend between
the "converted" and "impression/click only" groups.

## 8. Validation

- Confirm `customer_count` in each group sums to the total distinct
  customers reached by the campaign.
- Sanity check that "converted" customers show meaningfully higher
  30-day spend than "impression only" customers — if a conversion
  event (by definition, often tied to placing an order) doesn't show
  elevated near-term spend, something in the join logic is likely
  wrong.
- Cross-check one customer's 30-day post-interaction spend manually.

## 9. Edge Cases and the Core Caveat

- **This comparison cannot separate correlation from causation.**
  Customers who converted may simply have been more likely to buy
  *regardless* of the campaign — the campaign's `EXISTS` interaction
  doesn't prove it changed their behavior. A stronger (though still
  imperfect) design would compare a campaign-reached group against a
  demographically similar *unreached* group — this dataset doesn't
  provide an experimentally clean control, only an ability to
  approximate one.
- The 30-day attribution window is a judgment call — a shorter window
  understates delayed purchases; a longer one risks attributing
  unrelated, coincidental purchases to the campaign.
- Seasonality is not controlled for: if the campaign ran in November
  (a `holiday_peak` season for some categories per the data generator),
  elevated spend afterward could partly reflect the season, not the
  campaign.

## 10. Alternative Approach

A before/after comparison (each converted customer's own spend in the
30 days before vs. after their interaction) at least controls for
individual customer baseline, though it still can't rule out
seasonality or a pre-existing upward trend unrelated to the campaign.

## 11. Trade-offs

The converted-vs-impression-only comparison used here is simple and
uses data actually available, but conflates "the campaign worked" with
"the kind of customer who converts also happens to spend more." The
before/after alternative controls for individual baseline but not for
external trends. Neither alone constitutes proof of causation — the
honest answer to the Marketing Director should present the numbers
alongside this limitation explicitly, not paper over it.

## 12. Business Interpretation

Report something like: "customers who converted on this campaign spent
X more per person in the following 30 days than those who saw it but
didn't act — but we can't rule out that these customers would have
spent more anyway. If you want a cleaner answer next time, we'd need a
proper holdout group before the campaign launches."
