# Q045 — Which Customer Segment Is Most Valuable?

## Business Context

The CFO asks: "Which of our customer segments is actually most
valuable to the business?"

## Business Question

Which customer_segment (Premium, Standard, Budget, Corporate) is most
valuable?

## Data Available

customers
orders
order_items
returns

## Think Before SQL

This question is **deliberately underspecified** — "valuable" has
several legitimate, non-equivalent definitions.

1. List at least four different metrics "valuable" could mean here:
   total revenue, average revenue per customer, gross margin (using
   `cost` vs `selling_price`), and return-adjusted net value.
2. Would ranking segments by *total* revenue unfairly favor whichever
   segment simply has more customers in it (recall the
   `CUSTOMER_SEGMENT_WEIGHTS` skew from the data generator — Standard
   is deliberately the largest segment)? Is total revenue a fair
   segment-level comparison, or does it need to be normalized per
   customer?
3. If you compute *average* revenue per customer instead, does that
   better answer "which segment, customer-for-customer, is worth
   more"? What does it lose compared to total revenue (e.g., overall
   business impact)?
4. Does "valuable" mean revenue, or profit? What would you need from
   `products.cost` vs `products.selling_price` to compute margin
   instead of just top-line revenue?
5. Should returns reduce a segment's "value"? If Corporate customers
   have high revenue but also a high return rate, does that change
   the ranking under a net-value definition?
6. Is `customer_segment` (recall: an independent marketing-assigned
   tier, not derived from actual behavior) even a good proxy for real
   value, or might the real answer be "this labeling scheme doesn't
   actually separate high- and low-value customers well" — and how
   would you check that possibility before trusting any ranking at all?
7. Would you rather report multiple metrics side by side (total
   revenue, per-customer average, margin) and let the CFO weigh them,
   or commit to one composite number?
8. What time window should this be measured over — all 24 months, or
   something more recent?
9. Does segment size itself matter to the CFO's decision (e.g., a
   small but extremely high-value segment might warrant a different
   strategic response than a large, modestly valuable one)?
10. How would you present the caveat that `customer_segment` might not
    strongly predict actual spend, if that turns out to be the case in
    this data?

## Attempt

Compute at least two different "valuable" definitions and compare
whether they agree on the ranking.

[space for learner]
