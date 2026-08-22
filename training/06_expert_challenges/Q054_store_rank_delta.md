# Q054 — Store Rank Movement

## Business Context

Regional leadership doesn't just want to know which stores rank where
this month — they want to know which stores are *moving*, up or down,
month over month, since a store climbing the rankings tells a different
story than one that's always been near the top.

## Business Question

For each store, for each month, show its revenue rank among all stores
that month, and how much that rank changed compared to the previous
month.

## Data Available

orders
order_items
stores

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What do you need to compute per store, per month, before any ranking
  is possible?
- Once every store has a rank for every month, how is "comparing a
  rank to last month's rank for the same store" different from
  anything you've ranked before?
- Could you end up needing two different window functions stacked on
  top of each other?

[space for learner]
