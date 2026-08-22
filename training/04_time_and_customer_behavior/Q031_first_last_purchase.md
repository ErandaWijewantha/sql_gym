# Q031 — First and Last Purchase per Customer

## Business Context

Customer analytics wants the basic building block for every lifecycle
metric they'll ever compute: each customer's first and last order date.

## Business Question

For every customer who has placed at least one order, show their first
order date and their most recent order date.

## Data Available

orders

## Think Before SQL

1. What does one output row represent?
2. Which two aggregate functions do you need, and do they need separate
   GROUP BY clauses or can they share one?
3. Does this question restrict to completed orders, or all orders
   regardless of status? Which interpretation matches "customer
   lifecycle" — has a cancelled order ever placed still count as
   evidence the customer was "active" on that date?
4. What's the smallest possible customer case — someone with exactly
   one order — and what should first and last order date look like for
   them?
5. Could first_order_date ever be later than last_order_date? Why is
   that structurally impossible given how MIN and MAX work?
6. Do you need any table besides `orders`?
7. What column(s) do you GROUP BY?
8. Would this same shape work if "purchase" needed to mean something
   narrower, like "first *completed* order" specifically? What would
   change?
9. How is this question a stepping stone toward Q032 (recency) — what
   one additional calculation turns "last order date" into "days since
   last order"?
10. How would you validate one customer's first/last dates against a
    manual listing of all their orders sorted by date?

## Attempt

[space for learner]
