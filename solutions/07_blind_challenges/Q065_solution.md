# Reasoning

## 1. Interpret the Business Question

Find customers who clicked >= 2 times on a given campaign but never
converted on it — an engaged-but-not-converting audience per campaign.

## 2. Output Grain

One row = one (customer, campaign) pair.

## 3. Metric Definition

`click_count >= 2` and `conversion_count = 0`, both computed per
(customer_id, campaign_id) from `customer_campaigns`.

## 4. Required Data

`customer_campaigns`: customer_id, campaign_id, interaction_type.

## 5. SQL

```sql
SELECT
    customer_id,
    campaign_id,
    SUM(interaction_type = 'click') AS click_count,
    SUM(interaction_type = 'conversion') AS conversion_count
FROM customer_campaigns
GROUP BY customer_id, campaign_id
HAVING SUM(interaction_type = 'click') >= 2
   AND SUM(interaction_type = 'conversion') = 0;
```

## 6. Walkthrough

`SUM(interaction_type = 'click')` relies on MySQL evaluating the
boolean comparison to `1`/`0`, summed directly — the same idiom as
Q009's conditional aggregation, just without an explicit `CASE`.
`GROUP BY (customer_id, campaign_id)` establishes the correct grain
(a customer's activity on *one specific campaign*, not across all
campaigns combined), and `HAVING` applies both conditions on the
aggregated counts.

## 7. Validation

- Pick one resulting (customer_id, campaign_id) pair and manually list
  its raw `customer_campaigns` rows to confirm >= 2 clicks and 0
  conversions.
- Confirm no row in the result has `conversion_count > 0`.

## 8. Edge Cases

- A customer who clicked 5 times across 3 *different* campaigns, never
  converting on any single one, correctly produces up to 3 separate
  rows here (one per campaign) rather than being collapsed into one —
  this question is about engagement with *a* specific campaign, not
  overall click volume.
- A customer with clicks on a campaign that has since ended is still
  included — this query doesn't filter by campaign date range.

## 9. Alternative Approach

`COUNT(CASE WHEN interaction_type='click' THEN 1 END)` is an equivalent,
more traditional way to write the same conditional count if a reader
finds the direct-boolean-sum idiom less familiar.

## 10. Trade-offs

Not applicable — purely a style choice between the two conditional
counting idioms.

## 11. Business Interpretation

This is a clear "interested but not convinced" audience per campaign —
worth investigating whether the offer, price point, or landing
experience for that specific campaign is the barrier, since the
engagement (repeated clicking) already proves the messaging caught
their attention.
