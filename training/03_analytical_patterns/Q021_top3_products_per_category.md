# Q021 — Top 3 Products per Category by Revenue

## Business Context

Category managers each want a short list: the 3 best-selling products
(by gross revenue) within their own category, so they know exactly
which SKUs to never let go out of stock.

## Business Question

For every category, list its top 3 products by gross revenue from
completed orders.

## Data Available

orders
order_items
products
categories

## Think Before SQL

1. What does one output row represent?
2. How is this different from Q002, which also asked for a "top N"?
   Specifically: how many separate "top N" lists does this question
   actually require?
3. Could `ORDER BY revenue DESC LIMIT 3` alone ever produce this
   result? Why not?
4. What SQL feature lets you rank rows *separately within each
   category*, rather than across the whole table at once?
5. What does the PARTITION BY clause of a window function actually do,
   conceptually?
6. Once each product has a rank number within its category, what
   filters the result down to just the top 3 per category?
7. Can you filter directly on a window function's result in the same
   query it's computed in? What construct do you need (hint: think
   about clause evaluation order)?
8. What determines the revenue figure used for ranking — does it need
   to be computed first, at what grain, before ranking can happen?
9. What would go wrong if two products in the same category had
   exactly equal revenue — does your choice of ranking function change
   how many products end up in the "top 3"?
10. How would you validate one category's result by checking its
    products' revenue independently?

## Attempt

[space for learner]
