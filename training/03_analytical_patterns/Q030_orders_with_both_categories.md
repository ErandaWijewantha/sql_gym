# Q030 — Orders Containing Both Mobile Phones and Accessories

## Business Context

Merchandising suspects customers who buy a phone often add an
accessory to the same basket, and wants to quantify how often that
actually happens, as a case for a bundled checkout prompt.

## Business Question

Find every completed order that contains at least one "Mobile Phones"
product AND at least one "Electronics Accessories" product in the same
order.

## Data Available

orders
order_items
products
categories

## Think Before SQL

1. What does one output row represent?
2. This is the mirror image of Q029: instead of "never X," it's "both X
   and Y within the same entity (here, the same order)." What's
   different about how you'd express "both" versus "never" in SQL?
3. Would a simple `WHERE category_name IN ('Mobile Phones',
   'Electronics Accessories')` on a joined order_items/products/
   categories result correctly find orders with *both*? What would it
   actually find instead?
4. One approach: conditional aggregation. If you GROUP BY order_id and
   compute `SUM(CASE WHEN category='Mobile Phones' THEN 1 ELSE 0 END)`
   and a similar sum for the other category, what HAVING condition
   expresses "both present"?
5. Another approach: `EXISTS` twice — once checking for a Mobile Phones
   line item on this order, once for an Electronics Accessories line
   item. How would you structure that as a query over `orders`?
6. A third approach: self-join order_items to itself (matching on
   order_id, with each side restricted to a different category). What
   would the join condition need to look for, and how would you avoid
   counting the same pair of line items twice per order?
7. Which of these three approaches would you expect to be most
   readable to a teammate seeing it for the first time?
8. Does "at least one of each" ever require you to worry about
   quantity, or is presence/absence of each category on the order
   sufficient?
9. What would go wrong if you accidentally used `OR` instead of `AND`
   logic somewhere — what would the result set become instead (a
   superset? a different, unrelated set)?
10. How would you validate one resulting order_id by listing its full
    order_items with categories directly?

## Attempt

[space for learner]
