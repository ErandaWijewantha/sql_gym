# Q037 — Customers With Three Consecutive Months of Increasing Spend

## Business Context

Marketing wants to identify customers on a genuine upward trajectory —
not just a single good month, but a sustained three-month streak of
month-over-month spend growth — as candidates for an early loyalty
upgrade before a competitor pulls them away.

## Business Question

Identify customers who had at least one stretch of three consecutive
calendar months where each month's net spend was strictly higher than
the previous month's.

## Data Available

orders
order_items

## Think Before SQL

1. What does one output row represent?
2. What intermediate result do you need first — one row per what two
   dimensions together?
3. Once you have monthly spend per customer, what tells you whether one
   month was an increase over the previous one? (Recall LAG from
   Q023/Q024.)
4. If you flag each month as "increase" (1) or "not" (0) compared to
   its predecessor, what pattern are you now looking for across
   consecutive flagged rows?
5. This is different from every previous window-function question in
   this gym: you're not just comparing one row to its neighbor, you're
   looking for a *run* of 3 consecutive True flags. What's this
   general class of problem called?
6. One classic trick: if you subtract a row's own sequential position
   (via ROW_NUMBER, ordered by month) from a *separately computed*
   running count of only the "increase" flags, what does a constant
   result across consecutive rows indicate?
7. Do you need to worry about calendar gaps (a customer with no orders
   in some intervening month) breaking what looks like a streak in
   month-number terms? What would silently treating "consecutive rows
   in my result set" as "consecutive calendar months" get wrong?
8. What's the minimum number of consecutive increase-flags needed to
   constitute "three consecutive months of increasing spend" — is it 2
   flags (covering 3 months: flat, then two increases) or 3 flags?
   Work through the indexing carefully.
9. How would you structure the final query to return one row per
    customer who has *at least one* such streak anywhere in their
    history (not every qualifying window)?
10. How would you validate one customer's streak by listing their
    monthly spend sequence directly and checking three consecutive
    increases by eye?

## Attempt

[space for learner]
