# Q033 — One-Time vs Repeat Customers

## Business Context

Marketing wants a basic split of the customer base: how many customers
have only ever placed one order versus multiple, since retention
strategy differs completely between the two groups.

## Business Question

Classify every purchasing customer as "one-time" (exactly 1 order ever)
or "repeat" (2 or more orders), and report how many customers and what
percentage of the purchasing base fall into each group.

## Data Available

orders

## Think Before SQL

1. What does one output row represent — a customer, or a segment?
   (Same two-stage shape as Q003's price tiers.)
2. What per-customer number determines which label they get?
3. Do you need a HAVING clause, a CASE expression, or both — and in
   what order do they logically apply?
4. Is this classification about *all* orders regardless of status, or
   completed orders only? Would a customer whose only 2 orders were
   both cancelled count as "repeat," and does that feel right for a
   retention strategy question?
5. What are (at least) two structurally different ways to compute this:
   one using a subquery/CTE that first counts orders per customer, then
   classifies; another using a window function that avoids collapsing
   to customer grain until the final step?
6. How do you turn per-customer counts into "number of customers per
   segment" — what's the final GROUP BY?
7. How do you compute "percentage of the purchasing base" from those
   segment counts?
8. Does this population include customers with zero orders at all? Why
   or why not, given the question says "purchasing customer"?
9. Given the data generator's archetype design (roughly 28% one-time,
   the rest occasional/regular/vip), what rough percentage split would
   you expect, and does your result match that expectation at least
   directionally?
10. How would you validate the two segment counts sum to the total
    number of customers with at least one order?

## Attempt

[space for learner]

## Approach Comparison

Sketch two structurally different ways to solve this (e.g., a CTE that
counts orders per customer then classifies, vs. a window-function
version that avoids an explicit customer-grain collapse until the very
last step). Which would you use in production, and why?
