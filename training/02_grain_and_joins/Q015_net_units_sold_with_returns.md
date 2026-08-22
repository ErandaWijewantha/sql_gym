# Q015 — Net Units Sold, Accounting for Returns

## Business Context

Supply chain wants net unit sales per product (units sold minus units
returned) to feed a replenishment model. An analyst's first attempt
joined `order_items` directly to `returns` and got numbers that look
inflated for popular products.

## Business Question

For each product, compute (a) total units sold from order_items, (b)
total units returned from returns, and (c) net units sold. Produce a
version that gets this right, and be ready to explain what goes wrong
with a single query that joins order_items directly to returns and sums
both sides in the same row set.

## Data Available

order_items
returns

## Think Before SQL

1. What grain does `order_items` live at? What grain does `returns`
   live at? Are they the same events, or different events entirely?
2. If a product has 100 order_items rows and 8 returns rows, and you
   join them together with `JOIN returns r ON r.product_id =
   oi.product_id` (matching only on product, not on a specific
   order/line item), how many rows does that join produce, roughly?
3. If you then `SUM(oi.quantity)` over that joined result, what happens
   to each order_item row's quantity?
4. Why does joining two "many" tables directly to each other (rather
   than each one separately to a shared "one" side) cause this?
5. What's the fix — should you join order_items to returns at all for
   this question, or compute each side independently first?
6. What two independent aggregations do you actually need, and how do
   you combine them into one result set per product?
7. Would a `LEFT JOIN` between two independently pre-aggregated
   subqueries/CTEs (one per product for sold, one per product for
   returned) solve the problem? Why?
8. What should happen to a product with sales but zero returns — should
   it disappear, or show 0 returned?
9. What SQL construct guarantees a product with no returns still shows
   up with a 0 (rather than vanishing due to an INNER JOIN)?
10. How would you validate net units sold is never negative for any
    product (and what would it mean if it somehow were)?

## Attempt

[space for learner]
