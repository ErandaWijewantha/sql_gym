# Q046 — What Is Our Return Rate?

## Business Context

A board member asks, in a review meeting: "What's our return rate?"
Everyone in the room nods as if this is a simple, well-defined number.
It isn't.

## Business Question

What is the company's overall return rate?

## Data Available

order_items
returns
orders

## Think Before SQL

1. List at least three different valid denominators for "return rate":
   (a) returned units / units sold, (b) orders with at least one return
   / total orders, (c) returned revenue / gross revenue.
2. Do these three definitions produce numbers of similar magnitude, or
   could they differ substantially? Why might a board member be
   misled if you don't specify which one you're reporting?
3. For definition (a): does "units sold" include cancelled orders'
   items? Should it?
4. For definition (b): does a customer returning 1 of 5 items in an
   order count the *whole order* as "returned," or only that fraction?
5. For definition (c): is "returned revenue" the original sale value of
   the returned units, or does it need to account for whatever
   discount was applied to those specific units at the time of sale?
6. Should refunded/cancelled orders be included in either the numerator
   or denominator of any of these definitions, or do they double-count
   against the `returns` table (which already tracks explicit returns
   separately from order-level refund status)?
7. Is there a "right" time window — return rate over the full 24
   months, or a trailing period (since return behavior might shift
   seasonally)?
8. If you had to report just *one* number to the board, which
   definition would you pick, and what one-sentence caveat would you
   attach to it?
9. Would you ever report all three side by side instead of picking one?
   What's the cost (board members may find multiple numbers confusing)
   versus the benefit (nobody is misled about what's being measured)?
10. How would you validate your chosen definition's number against a
    completely independent hand-calculation for a tiny slice of the
    data (e.g., one product, one month)?

## Attempt

Compute all three candidate definitions and compare their resulting
percentages.

[space for learner]
