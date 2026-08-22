# Q017 — Store Revenue, Without Payment-Retry Duplication

## Business Context

Finance wants total successfully-collected payment amount per store.
Recall from the data generator's design that about 5% of completed
orders have a failed payment attempt followed by a successful retry —
meaning some orders have *two* rows in `payments`.

## Business Question

For each store, compute total revenue based on `payments.amount` where
`payment_status = 'success'`, without letting orders with a failed
retry attempt contribute extra.

## Data Available

orders
payments
stores

## Think Before SQL

1. What grain does `payments` live at? Is it guaranteed to be one row
   per order?
2. If you filter `WHERE payment_status = 'success'` before joining to
   `stores`, does that already solve the duplication problem, or is
   there a separate issue?
3. For an order with one failed + one successful payment row, how many
   rows survive a `WHERE payment_status = 'success'` filter? Does that
   answer resolve any ambiguity about duplication?
4. Now consider an order with *two* successful payment rows (not part
   of this generator's design, but suppose it happened) — would your
   query silently double count it? What would guard against that
   possibility even if it's rare?
5. What's the difference between "duplication caused by a join
   producing extra rows" (Q011, Q015) and "duplication caused by the
   source table itself legitimately having multiple qualifying rows
   per order"?
6. Which approach is safer: summing `payments.amount` directly per
   store, or first collapsing payments to one confirmed amount per
   order (e.g., via `MAX` or a specific dedup rule), then joining to
   orders/stores?
7. Would `SUM(DISTINCT amount)` ever be a valid fix here? Why is that
   almost always the wrong tool (think about two different orders that
   happen to have the same amount)?
8. What's a robust rule for "the amount actually collected for this
   order," expressed as a single SQL step, before any store-level
   aggregation happens?
9. How would you verify, for one specific order with a retry, that your
   final store total counted it exactly once?
10. How does this connect to Q011's lesson about joining "many" tables
    directly together?

## Attempt

[space for learner]
