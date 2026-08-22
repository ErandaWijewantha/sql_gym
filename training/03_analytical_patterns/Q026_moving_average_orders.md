# Q026 — 3-Month Moving Average of Order Volume per Store

## Business Context

Store operations wants a smoothed view of order volume trends per
store — raw month-to-month counts are noisy, and a moving average
would make genuine trends easier to spot on a dashboard chart.

## Business Question

For each store, for each calendar month, show that month's completed
order count and the 3-month moving average of order count (the current
month plus the two preceding months).

## Data Available

orders
stores

## Think Before SQL

1. What does one output row represent?
2. What intermediate result do you need first — one row per what?
3. A running total (Q025) accumulates every prior row. A moving average
   only looks at a fixed-size *window* of recent rows. What part of a
   window function's syntax controls exactly how many rows are
   included?
4. What does `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` mean in plain
   English, and why does "2 PRECEDING AND CURRENT ROW" add up to 3
   months, not 2?
5. What must the PARTITION BY be here, and what would happen to the
   moving average at a store's month boundary if you forgot it (i.e.,
   let the window span across different stores)?
6. What must the ORDER BY be inside the window, and why would getting
   the sort order wrong (e.g., alphabetical instead of chronological)
   silently produce a meaningless average?
7. For a store's first and second month of history, there aren't 2 full
   preceding months available. What does `ROWS BETWEEN 2 PRECEDING AND
   CURRENT ROW` do in that case — does it error, return NULL, or
   average over however many rows actually exist?
8. Is a "3-month moving average" using `AVG(...) OVER (...)` the same
   as a "3-month moving average" using `RANGE` instead of `ROWS`? What
   would differ if a store had a gap month with zero orders (and thus
   no row at all for that month)?
9. What would change if the business instead wanted a *centered* moving
   average (1 month before, the current month, 1 month after) instead
   of a trailing one?
10. How would you validate the moving average for one store's 3rd
    month by manually averaging its months 1, 2, and 3 order counts?

## Attempt

[space for learner]
