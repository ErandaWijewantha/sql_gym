# Q052 — Spend Tier Journey

## Business Context

Account management wants to spot customers whose spending tier rose
and then fell again — a pattern that might indicate a customer who was
briefly won over by a promotion or a big-ticket purchase, but didn't
stick at the higher tier.

## Business Question

Classify each customer's net spend into a tier ("Low," "Mid," "High")
for each calendar quarter of the dataset. Identify customers whose tier
went up for at least one quarter and then dropped back down in a later
quarter.

## Data Available

orders
order_items

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What does one output row represent, at the intermediate stage, before
  you get to the final customer list?
- What would "tier" mean here, and does it need to be defined relative
  to all customers, or per customer over time?
- What counts as "went up, then came back down" — does it need to be
  consecutive quarters, or can there be a gap?

[space for learner]
