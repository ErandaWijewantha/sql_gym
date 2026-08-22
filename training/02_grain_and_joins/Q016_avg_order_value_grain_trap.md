# Q016 — Two Different "Average Order Values"

## Business Context

Two analysts each computed "average order value" for the same store
and got two different numbers. Your manager wants to know which one is
right, and why they differ.

## Business Question

Compute average order value (net of discounts) for completed orders
two ways: (A) `AVG(quantity * unit_price - discount_amount)` taken
directly over the orders-joined-to-order_items result, and (B) the net
total per order computed first, then averaged across orders. Compare
the two numbers for any one store and explain the gap.

## Data Available

orders
order_items

## Think Before SQL

1. In version (A), what does each row being averaged actually
   represent — an order, or a single line item within an order?
2. In version (B), what does each row being averaged represent?
3. If one order has 1 item worth 10,000 and another order has 4 items
   worth 2,500 each (also totaling 10,000), do versions (A) and (B)
   treat these two orders the same way?
4. Which version implicitly gives more "weight" to orders with more
   line items? Is that ever what "average order value" is supposed to
   mean?
5. What intermediate result does version (B) need to compute first,
   before any AVG() is applied?
6. Is version (A) ever equal to version (B)? Under what (unrealistic)
   condition would they coincide?
7. Which version answers the business question "what does a typical
   order cost" and which one actually answers a different question
   ("what does a typical line item cost")?
8. Recall Q008's solution — which version does it match, and why did
   that solution insist on pre-aggregating or using COUNT(DISTINCT)?
9. How would you construct a tiny 2-order example by hand to prove the
   two versions diverge?
10. What's the general lesson about AVG() and grain that this exercise
    is really teaching?

## Attempt

[space for learner]
