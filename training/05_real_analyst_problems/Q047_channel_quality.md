# Q047 — Which Acquisition Channel Brings the Best Customers?

## Business Context

The Growth Lead wants to reallocate next quarter's acquisition budget
toward whichever channel brings in the highest-quality customers, not
just the most of them.

## Business Question

For each acquisition_channel, what is the average lifetime net spend of
the customers it brought in?

## Data Available

customers
orders
order_items

## Think Before SQL

1. What does one output row represent?
2. What per-customer measure do you need first, before any per-channel
   comparison is meaningful?
3. Is "lifetime net spend" the same definition used in Q040? Should it
   be, for consistency across the gym's exercises?
4. A channel that acquired customers mostly in the last 2 months of the
   dataset hasn't had as much *time* to accumulate spend as a channel
   that's been acquiring since month 1. Does comparing raw average
   lifetime spend across channels risk penalizing newer cohorts of
   acquisition unfairly? How might you account for this (hint: think
   about normalizing by tenure, or restricting to customers past a
   minimum tenure)?
5. Should customers with zero orders be included in a channel's average
   (dragging it toward zero), or excluded (measuring only "value given
   that they converted at all")? Which better answers "best customers,"
   and which better answers "best channel ROI"?
6. Would a channel with very few total customers but a high average
   deserve the same confidence as a channel with thousands of customers
   and a similar average? What additional column would help judge that?
7. What table and join gets you from a channel to its customers' spend?
8. Does `acquisition_channel` have any NULL values, and how should they
   be handled?
9. How would you present this so growth can act on it — a simple
   ranked list, or something that also shows customer count and
   variability per channel?
10. How would you validate the average for one channel by manually
    checking a handful of its customers' spend?

## Attempt

[space for learner]
