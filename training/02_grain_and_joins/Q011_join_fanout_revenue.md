# Q011 — The Trouble With Joining Everything at Once

## Business Context

A junior analyst wrote a query joining `orders`, `order_items`, and
`payments` together to compute total gross revenue, and got a number
that looks suspiciously high. Your manager asks you to figure out why,
and to produce the correct number.

## Business Question

Compute total gross revenue (quantity x unit_price) across all
completed orders. First reproduce the junior analyst's naive query
(joining all three tables), then explain why it's wrong and produce the
correct figure.

## Data Available

orders
order_items
payments

## Think Before SQL

1. What grain does `order_items` live at? What grain does `payments`
   live at?
2. If one order has 3 order_items rows and 2 payments rows (e.g. one
   failed attempt, one successful), how many rows does joining all
   three tables together produce for that single order?
3. Does that row count match anything meaningful in the real world?
4. If you now SUM(quantity * unit_price) over that joined result, what
   happens to each line item's contribution?
5. Is this a JOIN *condition* problem, or a JOIN *structure* problem —
   i.e., would fixing the ON clause fix it, or is joining all three
   tables at once simply the wrong shape for this question?
6. What does `payments` actually contribute to the question "what is
   total gross revenue"? Do you need it at all?
7. What would the correct query look like instead?
8. How would you prove, with a concrete order_id, that the naive
   version overcounts that order specifically?
9. What's the general rule for when joining two "many" tables to a
   common "one" table (here, both order_items and payments hang off
   orders) becomes dangerous?
10. How would you check your corrected total against Q005's answer
    (which used a different, safe join path)?

## Attempt

[space for learner]
