# Q038 — Products in a Three-Month Sales Decline

## Business Context

Category management wants an early-warning list of products whose
sales have been dropping for three consecutive months, before they
become a bigger inventory problem.

## Business Question

Identify products that had at least one stretch of three consecutive
calendar months where each month's unit sales were strictly lower than
the previous month's.

## Data Available

orders
order_items

## Think Before SQL

1. What does one output row represent?
2. How is this question structurally identical to Q037, just applied
   to a different entity and the opposite direction of change?
3. What intermediate result do you need first — one row per what two
   dimensions?
4. What comparison (via LAG) flags a month as a "decline" relative to
   its predecessor?
5. What's different, if anything, about detecting a *decline* streak
   versus Q037's *growth* streak — is it the same gaps-and-islands
   technique with one comparison operator flipped?
6. A product with only 2 months of any sales history at all can never
   satisfy "three consecutive declining months" — why not, mechanically
   (how many LAG-comparisons are even possible)?
7. Would a product's very first recorded month of sales ever count as
   part of a decline streak? Why or why not (think about what LAG
   returns for the first row in a partition)?
8. Does a month with zero sales even produce a row in your intermediate
   result, if you're building it via a simple GROUP BY on order data
   only? What would that mean for detecting a decline into zero?
9. If a product actually went to *zero* sales in some month, would your
   query still detect a preceding decline into that low point, or would
   the missing row silently break the streak detection?
10. How would you validate one flagged product by listing its monthly
    unit sales directly and confirming three consecutive decreases by
    eye?

## Attempt

[space for learner]
