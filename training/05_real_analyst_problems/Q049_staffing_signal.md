# Q049 — Which Stores Need More Staff?

## Business Context

HR wants a data-informed starting point for next quarter's staffing
allocation review, based on how much order volume each store's current
staff is handling.

## Business Question

For each store, what is the average number of completed orders per
employee, and which stores look most stretched?

## Data Available

orders
employees
stores

## Think Before SQL

1. What does one output row represent?
2. What two independently-computed numbers do you need per store
   before you can divide one by the other?
3. Does "per employee" mean *every* employee at that store (including
   roles like Store Manager who may not directly handle order volume),
   or should some roles be excluded? What would you need to decide, and
   how would you justify it to HR?
4. What time window should "completed orders" be measured over — the
   full 24 months, or a more recent, staffing-relevant window (e.g.,
   last 3 months, since staffing should respond to *current* load, not
   historical average)?
5. Should online stores be included in this comparison at all, given
   their staff likely serve a fulfillment/ops role rather than direct
   customer-facing order handling?
6. If a store hired several new employees very recently, would a
   24-month average order-per-employee figure fairly reflect their
   *current* staffing adequacy, or understate/overstate it?
7. What join(s) get you from `orders` (which has `store_id`) to
   `employees` (which also has `store_id`) without any fan-out risk —
   are you joining two "many" tables directly to each other here, and
   if so, does that repeat a Level 2 mistake?
8. How would you structure this to avoid exactly that risk (hint:
   pre-aggregate each side to store grain independently, first)?
9. Is "high orders per employee" unambiguously bad (overworked staff)
   or could it also reflect a highly efficient, well-run store? What
   else would you want to know before recommending headcount changes?
10. How would you validate one store's ratio by independently counting
    its orders and its employees?

## Attempt

[space for learner]
