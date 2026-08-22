# Q036 — Month-1 Retention by Registration Cohort

## Business Context

Growth wants to know how well each registration-month cohort "sticks":
of the customers who registered in a given month, what fraction went on
to place an order in the month immediately following their
registration month?

## Business Question

For each registration-month cohort, what percentage of that cohort
placed at least one order in the calendar month immediately after they
registered?

## Data Available

customers
orders

## Think Before SQL

1. What does one output row represent?
2. What defines a customer's "cohort"? Which column does that come
   from, and at what granularity (exact date, or month)?
3. What is the "denominator" population for each cohort — every
   customer who registered in that month, regardless of whether they
   ever ordered?
4. What is the "numerator" for each cohort — customers from that cohort
   who ordered in one *specific* subsequent month. Which month exactly,
   relative to their registration month?
5. How do you compute "the month immediately after registration month"
   for a customer registered on an arbitrary day within that month?
6. Would a customer who registered on 2025-01-31 and ordered on
   2025-02-01 count as retained? What about one who ordered on
   2025-03-01 instead?
7. What join type keeps every cohort member in the denominator even if
   they never ordered again — and what would the wrong join type
   silently do to your percentages?
8. Do you need one intermediate result per customer (registration
   month + whether they ordered in month+1), before any final
   GROUP BY aggregation into a per-cohort percentage?
9. What would you expect to see for the very last registration-month
   cohort in the dataset — is "month + 1" even fully observable for
   them, and should they be excluded or footnoted?
10. How would you validate one cohort's percentage by manually counting
    its registrants and how many of them appear in the following
    month's order list?

## Attempt

[space for learner]
