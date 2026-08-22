# Q029 — Customers Who Have Never Bought From a Category

## Business Context

The Jewelry & Watches category team wants a list of existing, active
customers who have never purchased anything from that category, as a
targeted-promotion list.

## Business Question

List every customer who has placed at least one completed order, but
has never had a "Jewelry & Watches" product in any of their completed
orders.

## Data Available

customers
orders
order_items
products
categories

## Think Before SQL

1. What does one output row represent?
2. This question has two conditions joined by "but": has ordered
   *something*, but never ordered *from this specific category*. Are
   these the same kind of condition, or different?
3. What SQL pattern expresses "never did X" when X requires walking
   through two joins (order_items → products → categories) to check?
4. Would a `LEFT JOIN` restricted to just Jewelry & Watches products,
   filtered with `IS NULL`, work here? What would the join condition
   need to look like for that to be correct (hint: where does the
   category filter belong — in the ON clause or a separate WHERE)?
5. Why would putting the category filter in a plain `WHERE` clause
   (after a LEFT JOIN) silently break this query? Think about what
   `WHERE` does to non-matching (NULL-extended) rows.
6. What would `NOT EXISTS (SELECT 1 FROM order_items oi JOIN products p
   ... WHERE oi.order_id IN (customer's orders) AND category = 'Jewelry
   & Watches')` need to look like as a correlated subquery?
7. How do you also enforce "has placed at least one completed order" as
   a separate condition from the anti-join?
8. Could you accidentally write a query that answers "has never bought
   Jewelry & Watches" but forgets to restrict to *completed* orders,
   and would that be wrong for this specific business question?
9. What would change about the query if "never" needed to mean "never,
   including cancelled/pending orders too" instead of just completed
   ones?
10. How would you validate the result for one customer by manually
    checking all of their completed orders' categories?

## Attempt

[space for learner]
