# Q050 — Build a Churn Early-Warning List

## Business Context

The retention team wants a single, prioritized list of customers most
likely to churn soon — not customers who are already gone (too late),
but ones showing early warning signs while there's still time to act.

## Business Question

Build an early-warning list of customers at risk of churning, combining
recency, frequency, and monetary trend signals.

## Data Available

customers
orders
order_items

## Think Before SQL

This is the level's capstone — it deliberately requires combining
several patterns from earlier in the gym rather than introducing a new
one.

1. Why is recency alone (Q032/Q039) insufficient to distinguish "early
   warning" from "already gone" or "just naturally infrequent but
   fine"?
2. What frequency signal would help — has their typical time-between-
   orders (recall Q024) recently gotten *longer* than their own
   historical average?
3. What monetary trend signal would help — is their recent monthly
   spend trending down (recall the LAG-based comparisons from Q023,
   or the decline-streak logic from Q038, applied to a customer instead
   of a product)?
4. Should "early warning" require *all three* signals to agree, or is a
   weighted combination (e.g., 2 out of 3) more realistic? What's the
   trade-off between a strict definition (fewer, higher-confidence
   flags) and a loose one (more coverage, more false positives)?
5. How would you handle a customer with too little history to compute
   a meaningful trend (e.g., only 2 total orders)? Should they be
   excluded from this analysis, or handled with a different, simpler
   rule?
6. Is a VIP-archetype customer who's merely "less active than their own
   extremely high baseline" a more urgent flag than a naturally
   occasional customer showing the same relative slowdown? How might
   you weight signals by a customer's historical value?
7. What would the *final* output need to look like for retention to
   actually act on it — a single risk score, or the underlying signals
   shown separately so they can see *why* someone was flagged?
8. Given this combines several earlier patterns, what's a reasonable
   way to structure the query — one giant query, or several CTEs each
   computing one signal, combined at the end?
9. How would you validate this list isn't dominated by one signal alone
   (e.g., check that customers are being flagged for genuinely
   different reasons, not all failing the same single check)?
10. What would you tell the retention team about this list's
    limitations — is it a precise prediction, or a reasonable,
    imperfect heuristic?

## Attempt

Design your own weighting/combination rule, document it explicitly,
and then implement it.

[space for learner]
