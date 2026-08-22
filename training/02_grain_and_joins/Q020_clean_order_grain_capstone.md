# Q020 — Capstone: Build a Clean Order-Grain Revenue Table

## Business Context

Your manager is tired of every new analyst reinventing (and
occasionally breaking) the same order-revenue logic. They want one
well-formed, order-grain intermediate result that the whole team can
build on top of for any future revenue question, without repeating the
grain mistakes from Q011, Q015, Q016, Q017, and Q019.

## Business Question

Build a single result set with exactly one row per completed order,
containing: order_id, customer_id, store_id, order_date, sales_channel,
net_order_value (sum of quantity*unit_price - discount_amount across
that order's line items), and item_count (number of line items). Then
use it to answer two questions at once: total net revenue per store,
and average order value per store — both correctly, from the same
base table.

## Data Available

orders
order_items

## Think Before SQL

1. What does one row in this new intermediate result represent? Say it
   explicitly.
2. Which of the earlier questions in this level (Q011–Q019) were really
   all instances of the same underlying mistake? What was it?
3. What must happen to `order_items` *before* it's safe to join to
   anything else that also hangs off `orders` (like `payments`,
   `returns`, or `support_tickets`)?
4. Does building this intermediate result require a CTE, a subquery, or
   could it also be a real view? What are the trade-offs?
5. Once you have one row per order, is a plain `AVG(net_order_value)`
   now correct for average order value? Why does pre-aggregation make
   `COUNT(DISTINCT ...)` unnecessary at this stage?
6. How would `SUM(net_order_value)` per store here compare to what
   you'd get from directly joining orders to order_items and summing —
   should the two numbers match exactly?
7. What's gained by materializing this as a *named, reusable*
   intermediate step rather than repeating the same subquery in every
   report?
8. What would you need to change about this intermediate result if
   someone later asked for it to also include cancelled orders (not
   just completed)?
9. How would you validate that `item_count` correctly reflects the
   number of `order_items` rows per order, not the sum of quantities?
10. What's the single sentence you'd write in a team wiki to explain
    *why* this intermediate table exists?

## Attempt

[space for learner]
