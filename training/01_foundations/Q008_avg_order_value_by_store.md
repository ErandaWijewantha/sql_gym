# Q008 — Average Order Value by Store

## Business Context

Store operations wants to compare how much a typical completed order is
worth across the top 10 stores by order volume.

## Business Question

For the 10 stores with the most completed orders, what is each store's
average order value (net of discounts)?

## Data Available

orders
order_items
stores

## Think Before SQL

1. What does one output row represent?
2. What does "average order value" mean here — average of what,
   computed over what population?
3. Is "net of discounts" the same number as gross revenue from Q005?
   What changes in the formula?
4. What does one row of order_items represent, and how is that
   different from what "one order" represents?
5. If you join orders to order_items and then just take
   AVG(quantity * unit_price - discount_amount), what are you actually
   averaging — order value, or line-item value? Are those the same?
6. What would you need to compute first, before you can average
   correctly at the order grain?
7. Which two things determine "the 10 stores with the most completed
   orders" — and is that the same ranking as "highest average order
   value"?
8. What join(s) do you need, and in what order would you reasonably
   build this query (subquery/CTE first, then join)?
9. What's a plausible range of values for an average order in this
   business, given individual products range from a few hundred to
   several hundred thousand LKR?
10. How would you verify your average isn't secretly an average of
    per-line-item amounts?

## Attempt

[space for learner]
