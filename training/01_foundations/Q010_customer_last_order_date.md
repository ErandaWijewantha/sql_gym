# Q010 — Most Recent Order per Customer

## Business Context

Customer success wants a reference list of every customer who has
purchased at least once, along with the date of their most recent
order, ahead of building a recency dashboard.

## Business Question

For every customer who has placed at least one order, what is their
most recent order date?

## Data Available

customers
orders

## Think Before SQL

1. What does one output row represent? Say it explicitly: "one row = ___".
2. Is that the same grain as the `orders` table, or a different one?
3. What aggregate function collapses many order dates down to one per
   customer?
4. What clause must accompany that aggregate function so SQL knows
   which column defines "per customer"?
5. What kind of JOIN connects customers to orders here, and what happens
   to a customer with zero orders under that join type?
6. Does this question's wording ("who has placed at least one order")
   tell you which join type to use, or does the join type decide the
   answer for you?
7. Would a LEFT JOIN change the *number of customer rows* in the
   output compared to an INNER JOIN, for this specific question?
8. What columns from `customers` can safely appear in the SELECT list
   given the GROUP BY?
9. What would "most recent" mean if two orders landed on the exact same
   date for one customer — does MAX still work correctly?
10. How would you check this result against Q004's total order count
    (e.g., does the number of customers here look consistent with
    ~12,000 total customers and a meaningful chunk having zero orders)?

## Attempt

[space for learner]
