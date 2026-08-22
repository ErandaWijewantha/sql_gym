# Q024 — Days Until a Customer's Next Order

## Business Context

The retention team wants to understand typical re-purchase timing: for
every order a customer places, how many days until their *next* order
(if they place one at all)?

## Business Question

For every order, show the customer's next order date (chronologically)
and the number of days between this order and that next one. Orders
with no subsequent order should show NULL for both.

## Data Available

orders

## Think Before SQL

1. What does one output row represent?
2. Q010 and Q032-style questions look *backward* (previous/most recent
   event). This question looks *forward*. What window function is the
   forward-looking counterpart to LAG?
3. What must the PARTITION BY be, so you're only ever comparing a
   customer's orders to their own other orders?
4. What must the ORDER BY be, and does its direction matter as much
   here as it did for a backward-looking window function?
5. For a customer's most recent (last) order, what does LEAD return,
   and does that match what "no next order" should look like?
6. Once you have the next order's date in the same row, what function
   computes the day gap?
7. Does a customer with only one order ever produce a non-NULL "next
   order date"? Walk through why or why not.
8. Would this same LEAD-based structure work if you instead wanted
   "days since the *previous* order" for every order? What single word
   would you change?
9. What aggregate could you build on top of this per-order result to
   get "average days between orders" per customer (hint: think about a
   second layer of aggregation over this result)?
10. How would you validate one customer's chain of orders and gaps by
    listing their orders directly, sorted by date?

## Attempt

[space for learner]
