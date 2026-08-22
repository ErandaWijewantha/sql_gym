# Q013 — Customers Who Have Never Ordered

## Business Context

Marketing wants a list of registered customers who have never placed a
single order, as a target list for a "welcome back" / first-purchase
incentive campaign.

## Business Question

List every customer who has never placed an order, along with their
registration date and acquisition channel.

## Data Available

customers
orders

## Think Before SQL

1. What does one output row represent?
2. Q010 used an INNER JOIN to find customers *with* orders. What
   changes if you use a LEFT JOIN from customers to orders instead?
3. After a LEFT JOIN, what value appears in the `orders` columns for a
   customer with no matching orders?
4. What WHERE condition, applied *after* the LEFT JOIN, isolates only
   those "no match" rows?
5. Why would `WHERE o.order_id IS NULL` work here but
   `WHERE o.customer_id IS NULL` would be risky to reason about (even
   though it might give the same result in this schema)?
6. Why would filtering on a customer-side column (like
   `c.some_column IS NULL`) never correctly express "no matching
   order," regardless of which column you pick?
7. Could you answer this with `NOT IN (SELECT customer_id FROM orders)`
   instead? What would you need to double check about NULLs in the
   subquery's result before trusting that version?
8. What's the difference in intent between "customers with zero
   orders" and "customers with zero *completed* orders" — which one is
   this question actually asking for, and does the schema's order_status
   values matter here at all?
9. How would you count the result set and sanity check it against
   Q010's result (they should be complementary subsets of all 12,000
   customers, roughly)?
10. What's the actual SQL pattern name for "rows in A with no
    corresponding row in B"?

## Attempt

[space for learner]
