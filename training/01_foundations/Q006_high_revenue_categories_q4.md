# Q006 — High-Revenue Categories in Q4 2025

## Business Context

Category planning wants to know which product categories were the
biggest revenue drivers in the most recent quarter, to prioritize
shelf space and marketing budget for the upcoming season.

## Business Question

Which product categories generated more than LKR 50,000,000 in gross
sales from completed orders placed between 2025-10-01 and 2025-12-31
inclusive?

## Data Available

orders
order_items
products
categories

## Think Before SQL

1. What does one output row represent?
2. What is the metric, and which two columns combine to compute it per
   line item?
3. What defines "Q4 2025" as a concrete date range, and which table's
   date column do you filter on?
4. Why "completed orders" specifically — what would happen to the
   number if you didn't filter order_status at all?
5. What chain of joins gets you from order_items to a category name?
6. Do you aggregate before or after applying the >50,000,000 threshold?
   What clause is built for filtering on an aggregate?
7. Would WHERE work for the threshold check? Why or why not?
8. What's the difference between filtering the date range in WHERE vs
   filtering it after aggregation?
9. What edge case exists if a category has zero completed orders in Q4 —
   would it appear in your output, and should it?
10. How would you double check your date boundaries are inclusive of
    2025-12-31 and don't accidentally include 2026-01-01?

## Attempt

[space for learner]
