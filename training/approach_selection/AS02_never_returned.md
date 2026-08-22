# AS02 — Approach Selection: Customers Who Never Returned a Product

## Business Question

Find customers who have placed at least one completed order, but have
never had a product from that order set returned.

## Data Available

customers
orders
returns

## Your Task

Sketch three different SQL structures:

- **A — NOT EXISTS**: a correlated subquery per customer checking for
  the absence of any matching return.
- **B — LEFT JOIN + IS NULL**: join customers/orders to returns, keep
  rows where the returns side is NULL.
- **C — NOT IN**: filter customer_id (or order_id) NOT IN a subquery
  listing everyone who has returned something.

For each approach, answer:

1. Does it correctly handle every customer, including one with zero
   orders at all?
2. What happens to approach C specifically if the subquery's result
   could ever contain a NULL value — even if you're confident it can't
   in *this* schema, what would break if it could?
3. Which of the three would you feel safest handing to a teammate who
   might reuse it in a slightly different context later?

Then pick your production choice and write down why, before checking
`solutions/approach_selection/AS02_solution.md`.
