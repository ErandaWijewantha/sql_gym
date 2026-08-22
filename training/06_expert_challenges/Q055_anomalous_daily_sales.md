# Q055 — Unusual Days

## Business Context

A store manager mentioned offhand that "some days just feel off" —
either way busier or way quieter than normal — and asked whether the
data could confirm which days actually were unusual, rather than relying
on gut feel.

## Business Question

For each store, identify days where completed-order revenue was
unusually high or unusually low compared to that store's typical daily
revenue.

## Data Available

orders
order_items
stores

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What does "typical" mean for a store's daily revenue — a single
  number, or something that captures how much daily revenue normally
  varies?
- What statistical building blocks would let you express "unusually
  far from typical" as a concrete, computable condition?
- Should "typical" be computed once for the whole 24 months, or would a
  store's typical daily revenue plausibly have shifted over that time?

[space for learner]
