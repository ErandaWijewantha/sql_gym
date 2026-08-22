# Q059 — Revenue Curve by Customer Age

## Business Context

Finance wants to model expected lifetime revenue for a new customer,
based on how past cohorts actually generated revenue over their first
year, month by month since their first purchase.

## Business Question

Group customers by the calendar month of their *first* purchase.
For each cohort, show cumulative average revenue per customer at each
number of months since that first purchase (month 0, month 1, month 2,
...).

## Data Available

orders
order_items

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What's the difference between "calendar month" and "months since
  first purchase" as a way of organizing time here? Which one does
  this question actually need?
- What does one output row represent — and how many different
  "clocks" (calendar time vs. customer-relative time) does this
  question need you to track at once?
- Would you need to compute something per customer first, before you
  can compute anything per cohort?

[space for learner]
