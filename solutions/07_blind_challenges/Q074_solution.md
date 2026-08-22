# Reasoning

## 1. Interpret the Business Question

Compare campaigns by a rough return-on-spend proxy: net spend generated
by converting customers within 14 days of their conversion, divided by
the campaign's budget.

## 2. Output Grain

One row = one campaign.

## 3. Metric Definition

`attributed_revenue` = sum of net spend (completed orders) placed by
each converting customer within 14 days after their conversion date.
`roas_proxy = attributed_revenue / campaigns.budget`.

## 4. Required Data

`campaigns`: campaign_id, budget.
`customer_campaigns`: customer_id, campaign_id, interaction_type,
interaction_date.
`orders`, `order_items`: for attributed spend.

## 5. SQL

```sql
WITH conversions AS (
    SELECT customer_id, campaign_id, interaction_date AS conversion_date
    FROM customer_campaigns
    WHERE interaction_type = 'conversion'
),
attributed_spend AS (
    SELECT
        cv.campaign_id,
        cv.customer_id,
        cv.conversion_date,
        COALESCE(SUM(
            CASE WHEN o.order_date >= cv.conversion_date
                  AND o.order_date < DATE_ADD(cv.conversion_date, INTERVAL 14 DAY)
                  AND o.order_status = 'completed'
                 THEN oi.quantity * oi.unit_price - oi.discount_amount ELSE 0 END
        ), 0) AS spend_14d
    FROM conversions cv
    LEFT JOIN orders o ON o.customer_id = cv.customer_id
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY cv.campaign_id, cv.customer_id, cv.conversion_date
)
SELECT
    c.campaign_id,
    c.campaign_name,
    c.budget,
    ROUND(SUM(a.spend_14d), 2) AS attributed_revenue,
    ROUND(SUM(a.spend_14d) / c.budget, 3) AS roas_proxy
FROM attributed_spend a
JOIN campaigns c ON c.campaign_id = a.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.budget
ORDER BY roas_proxy DESC;
```

## 6. Walkthrough

`conversions` extracts each customer's conversion event(s) per
campaign. `attributed_spend` then computes, per (campaign, customer,
conversion), how much that customer spent in the 14 days starting at
their conversion date — using `LEFT JOIN` so a converting customer with
no subsequent orders correctly contributes `0`, not disappearing. The
final query sums this across all conversions per campaign and divides
by the stated budget.

## 7. Validation

- Manually verify one customer's attributed 14-day spend against their
  raw orders.
- Confirm `roas_proxy` values are all non-negative (spend and budget
  are both non-negative by construction).

## 8. Edge Cases and Core Caveat

- **This is explicitly a proxy, not a rigorous ROAS calculation.** It
  attributes *all* of a converting customer's spend in the window to
  the campaign, even though some of that spend might have happened
  anyway — the same causal-attribution limitation flagged in Q043.
- A customer who converted on two different campaigns close together
  in time could have the same order attributed to both — this isn't
  corrected for here, and would need a de-duplication or attribution
  rule (e.g., "credit only the most recent campaign") in a more
  rigorous version.
- Campaigns with zero conversions produce no rows at all in this
  result (there's nothing in `conversions` to attribute from) — worth
  surfacing separately as "zero measurable return" rather than letting
  them silently disappear from the ranking.

## 9. Alternative Approach

A stricter version could require the order to contain the *specific
product or category the campaign promoted* (if that were tracked),
rather than crediting all subsequent spend — this schema doesn't link
campaigns to specific products, so that refinement isn't possible here
without additional data.

## 10. Trade-offs

The all-subsequent-spend proxy used here is simple and directionally
useful for a rough budget comparison; a more rigorous multi-touch
attribution model would be more accurate but requires data and
methodology this schema doesn't support.

## 11. Business Interpretation

Present this ranking with the caveat spelled out explicitly: "this
compares campaigns by a rough spend-after-conversion proxy, not a
true incremental-revenue ROAS — useful for spotting which campaigns are
clearly punching above or below their budget, not for precise dollar
attribution."
