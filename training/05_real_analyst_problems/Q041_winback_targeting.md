# Q041 — Who Should Marketing Target for Win-Back?

## Business Context

The Head of Marketing walks over and says: "We have budget for a
win-back campaign. Give me the list of customers we're at risk of
losing."

## Business Question

Which customers should Marketing target for a win-back campaign?

## Data Available

customers
orders
order_items

## Think Before SQL

This question is **deliberately underspecified**. Do not write SQL
yet — the correct first move is naming what's missing.

1. What does "at risk of losing" actually mean? List at least three
   different reasonable definitions (e.g., recency-based, frequency-
   decline-based, a combination).
2. Does "at risk" mean "already gone quiet" (recency threshold, like
   Q039) or "showing early signs of slowing down while still active"
   (a trend-based signal)? These are different populations.
3. What recency threshold would you propose, and how would you justify
   it rather than just picking a round number?
4. Should this only include customers with meaningful historical value
   (why target a $50 lifetime customer the same as a $50,000 one)? If
   so, what threshold, and why?
5. Does "at risk" implicitly exclude customers who never really
   engaged much to begin with (one-time, low-value)? Is a one-time
   customer from 200 days ago "at risk," or were they never really
   "at" anything to begin with?
6. What time-bounded population should you even be looking at — does
   someone who registered last week but hasn't ordered yet count?
7. Is there a budget or list-size constraint implied by "we have
   budget"? Does that change whether you want a strict definition (few,
   high-confidence targets) or a loose one (many, lower-confidence
   targets)?
8. Once you've picked one concrete, defensible definition, what tables
   and columns does it require?
9. What would you say back to the Head of Marketing *before* running
   any query, to confirm your assumption is the one they actually want?
10. How would this answer change if "losing" meant "losing revenue"
    specifically, versus "losing the relationship" more broadly?

## Attempt

First, write down the specific definition you're choosing to answer
with, and why. Only then write the SQL for *that* definition.

[space for learner]
