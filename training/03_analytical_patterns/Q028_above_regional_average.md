# Q028 — Customers Spending Above Their Regional Average

## Business Context

Marketing wants to identify customers who are outspending their peers
in the same region, as candidates for a loyalty-tier upgrade offer.

## Business Question

Find every customer whose total net spend (completed orders) is above
the average total net spend of customers in their own region.

## Data Available

customers
orders
order_items

## Think Before SQL

1. What does one output row represent?
2. What must you compute first, per customer, before any regional
   comparison is possible?
3. What is being averaged, exactly — average spend per customer within
   a region, or something else? Could this go wrong if computed at the
   wrong grain (recall Q016)?
4. Name at least three different SQL structures that could each,
   independently, answer this question correctly. (This is exactly the
   kind of question with no single "right" approach — see
   `training/approach_selection/AS01.md` for a dedicated breakdown.)
5. If you use a window function, what does `AVG(customer_total) OVER
   (PARTITION BY region)` give you, on every customer's row?
6. If you use a correlated subquery instead, what would it need to
   compute per customer, and would it need to explicitly exclude that
   customer from their own regional average, or is including them
   fine?
7. If you use a CTE + self-join (customer totals joined to regional
   averages), how many logical steps does that take, and is it more or
   less readable than the window-function version?
8. Does a customer with a NULL region get compared to anyone? What
   would that comparison even mean?
9. Would you expect roughly half of each region's customers to clear
   their own region's average? Why might the real fraction differ from
   half?
10. How would you validate one region's average manually and confirm
    your query's threshold matches?

## Attempt

[space for learner]

## Approach Comparison

Before checking the solution, sketch (in words, not full SQL) how each
of these three approaches would work for this question:

- **A — CTE + JOIN**: pre-aggregate customer totals, pre-aggregate
  regional averages, join the two.
- **B — Window function**: compute customer totals and the regional
  average side by side using `AVG(...) OVER (PARTITION BY region)`.
- **C — Correlated subquery**: for each customer, a subquery computes
  their region's average directly.

Which would you choose in production, and why?
