# AS01 — Approach Selection: Above the Regional Average

## Business Question

Find customers whose total net spend is above the average total net
spend of customers in their own region.

## Data Available

customers
orders
order_items

## Your Task

Before looking at any solution, sketch **three** different SQL
structures that could each correctly answer this question:

- **A — CTE + JOIN**: pre-aggregate customer totals, pre-aggregate
  regional averages as their own named result, then join the two.
- **B — Window Function**: compute each customer's total alongside
  their region's average using `AVG(...) OVER (PARTITION BY region)`,
  without a second aggregation pass.
- **C — Correlated Subquery**: for each customer, a subquery computes
  their region's average directly, correlated on region.

For each approach, write down (in words, not full SQL):

1. What intermediate result(s) does it need?
2. How many times does it conceptually scan the customer-spend data?
3. Would you expect it to be easy or hard for a teammate unfamiliar
   with SQL window functions to read?

Then pick the one you'd actually put into production, and write down
why, before checking `solutions/approach_selection/AS01_solution.md`.
