# Q004 — Order Status Breakdown

## Business Context

Operations wants a health check on order fulfillment: how many orders
are landing in each status.

## Business Question

How many orders exist for each order_status, from most to least common?

## Data Available

orders

## Think Before SQL

1. What does one output row represent?
2. What is being counted — orders, customers, or something else?
3. Is COUNT(*) the same as COUNT(order_id) here? Would it ever differ?
4. What clause groups rows into one bucket per status?
5. What determines the sort order of the output?
6. Do you need a WHERE clause at all for this question?
7. What would it mean, business-wise, if "cancelled" were unexpectedly
   large?
8. What's the total across all statuses, and how would you check it
   against a simple `SELECT COUNT(*) FROM orders`?
9. Are there any statuses you'd expect to see zero rows for, and would
   this query even show a status with zero orders?
10. What edge case would break a naive assumption that every order has
    exactly one status?

## Attempt

[space for learner]
