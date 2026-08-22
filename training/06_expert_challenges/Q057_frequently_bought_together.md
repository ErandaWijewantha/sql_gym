# Q057 — Frequently Bought Together

## Business Context

Merchandising wants to build a "customers also bought" feature for the
online store, based on actual co-purchase patterns rather than guesses.

## Business Question

Find the 10 pairs of products most frequently purchased together in the
same completed order.

## Data Available

orders
order_items
products

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What does one output row represent?
- You need to compare line items *within the same order* to each
  other. What's the general technique for comparing rows of a table to
  other rows of the same table?
- If an order has 4 different products in it, how many distinct pairs
  does that single order contribute? Would your query accidentally
  count each pair twice (A-B and B-A)?

[space for learner]
