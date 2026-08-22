# Q023 — Month-over-Month Revenue Change by Category

## Business Context

Category planning wants to see, for each category and each month,
how much revenue changed compared to the previous month — both in
absolute LKR and as a percentage.

## Business Question

For each category, for each calendar month in the dataset, show that
month's gross revenue, the previous month's gross revenue, the
absolute change, and the percentage change.

## Data Available

orders
order_items
products
categories

## Think Before SQL

1. What does one output row represent?
2. What intermediate result do you need before any month-over-month
   comparison is possible — what grain must it be at?
3. Once you have one row per (category, month) with that month's
   revenue, what window function retrieves "the same category's
   previous row's value"?
4. What does the PARTITION BY clause need to be here, and why would
   omitting it produce nonsense (e.g., comparing one category's January
   to a *different* category's December)?
5. What does the ORDER BY clause inside that window function need to
   be, and why does its direction (ascending vs descending) matter for
   which row counts as "previous"?
6. What happens for the very first month of a category's history — is
   there a "previous month" at all, and what does the window function
   return in that case?
7. How do you compute percentage change from the current and previous
   values, and what happens if the previous value is zero or NULL?
8. Is this a single-step query, or do you need a CTE to first build
   the (category, month, revenue) table before applying the window
   function?
9. What would "month" mean as a groupable value — do you need to
   extract year and month separately, or is a single truncated date
   value cleaner?
10. How would you spot-check one category's percentage change against
    a manual calculation for one specific month pair?

## Attempt

[space for learner]
