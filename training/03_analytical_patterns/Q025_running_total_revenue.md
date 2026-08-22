# Q025 — Cumulative Revenue Over Time

## Business Context

Finance wants a cumulative revenue curve across the whole dataset
window, to track progress against an annual target month by month.

## Business Question

For each calendar month, show that month's gross revenue and the
cumulative (running total) revenue from the start of the dataset up
through that month.

## Data Available

orders
order_items

## Think Before SQL

1. What does one output row represent?
2. What intermediate result do you need first — one row per what?
3. Does computing a running total require GROUP BY at all once you
   already have one row per month, or does it require something else
   entirely?
4. What window function accumulates a SUM as you move through ordered
   rows?
5. What must the ORDER BY inside that window function be, and why does
   getting this wrong (e.g., ordering by revenue instead of by month)
   produce a "running total" that means nothing?
6. Does this running total need a PARTITION BY? What would partitioning
   even mean here, given there's only one overall revenue stream (not
   one per category or store)?
7. By default, does `SUM(...) OVER (ORDER BY month)` accumulate from
   the beginning up to and including the current row, or something
   else? What's the (usually implicit) frame clause doing?
8. How would the query change if finance instead wanted a *separate*
   running total per store, restarting at zero for each store?
9. What should the running total equal on the very last month of the
   dataset — what other, independently computed number should it match
   exactly?
10. How would you sanity check that the running total never decreases
    from one month to the next (assuming no negative-revenue months)?

## Attempt

[space for learner]
