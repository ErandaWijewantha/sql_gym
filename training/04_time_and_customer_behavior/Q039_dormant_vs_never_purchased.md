# Q039 — Dormant Customers (Previously Active, Now Silent)

## Business Context

Marketing keeps confusing two very different audiences: customers who
have *never* purchased (Q013's population) and customers who *used to*
purchase but have gone quiet. They want the second group specifically,
so the win-back message can reference their past purchase history.

## Business Question

Identify customers who placed at least one order, but whose most recent
order was at least 90 days before the dataset's reference date.

## Data Available

orders

## Think Before SQL

1. What does one output row represent?
2. How is "dormant" here different from "never purchased" (Q013)? Are
   they overlapping or mutually exclusive populations?
3. What single per-customer value from Q031/Q032 (last order date, or
   recency in days) does this question's threshold apply to?
4. Does this question require an anti-join pattern at all, or is it
   simply a threshold filter on an aggregate — and if so, which SQL
   clause applies that filter?
5. Would `WHERE` or `HAVING` be the right place for the 90-day
   condition, given it depends on `MAX(order_date)`?
6. Why is "at least one order" automatically guaranteed here without
   any extra anti-join logic, given how you're constructing the base
   population?
7. Does this population include customers whose *only* order was
   cancelled, if that order's date is >= 90 days old? Revisit your
   answer from Q031/Q032 about which order statuses count as
   "activity."
8. How does this relate to Q034's reactivation pattern — is a
   "currently dormant" customer the same as, or different from, a
   customer who once had a >=90-day gap and then came back?
9. What population size would you expect here relative to the total
   purchasing customer base, given the data generator's dormancy design
   (roughly 15% of occasional/regular customers)?
10. How would you validate one flagged customer's last order date
    directly against the 90-day threshold and the reference date?

## Attempt

[space for learner]
