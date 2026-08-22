# Q035 — Active in January, Silent in February

## Business Context

Marketing is investigating a suspected drop-off after the New Year
promotional period ended, and wants to see exactly who stopped
ordering.

## Business Question

Which customers placed at least one order in January 2025 but placed
no order at all in February 2025?

## Data Available

orders

## Think Before SQL

1. What does one output row represent?
2. This question involves two separate time windows compared against
   each other for the same customer. What are the two populations
   being compared (name them precisely as sets)?
3. Is this fundamentally the same shape as Q013's "customers who never
   ordered," or Q029's "customers who never bought category X" —
   just with a time window standing in for the category filter?
4. How would you construct "customers who ordered in January 2025" as
   its own intermediate result?
5. How would you construct "customers who ordered in February 2025" as
   a second, independent intermediate result?
6. What set operation or anti-join pattern combines these two:
   customers in the first set but *not* in the second?
7. Would `WHERE order_date BETWEEN '2025-01-01' AND '2025-02-28' AND
   NOT (order_date BETWEEN ...)` on a single pass over `orders` ever
   correctly express this? Why is trying to do it in one WHERE clause
   over one table scan fundamentally the wrong shape?
8. What's the risk of forgetting that a customer could appear multiple
   times in the January result (multiple January orders) — does your
   chosen structure already handle that, or do you need an explicit
   DISTINCT/GROUP BY?
9. Does this question care about order_status, or should cancelled
   orders still count as "activity" for this specific investigation?
10. How would you validate one resulting customer by directly listing
    all their orders in Jan–Feb 2025?

## Attempt

[space for learner]
