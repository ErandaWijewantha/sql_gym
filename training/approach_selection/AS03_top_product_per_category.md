# AS03 — Approach Selection: Top-Selling Product per Category

## Business Question

Find the single best-selling product (by gross revenue) in each
category.

## Data Available

orders
order_items
products
categories

## Your Task

Sketch two different SQL structures:

- **A — Ranking Window Function**: `ROW_NUMBER()` or `RANK()`
  partitioned by category, ordered by revenue descending, filtered to
  rank 1.
- **B — Correlated Subquery with MAX**: for each product, a subquery
  checks whether its revenue equals the maximum revenue among all
  products in its category.

For each approach, answer:

1. What happens under approach B if two products in the same category
   are exactly tied for the highest revenue?
2. What happens under approach A (with `ROW_NUMBER()` specifically)
   under that same tie?
3. Would `RANK()` behave differently from `ROW_NUMBER()` here, and
   which would you actually want if a business stakeholder asked for
   "the" top product per category?

Then pick your production choice and write down why, before checking
`solutions/approach_selection/AS03_solution.md`.
