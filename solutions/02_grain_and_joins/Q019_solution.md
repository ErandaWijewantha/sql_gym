# Reasoning

## 1. Interpret the Business Question

Customer success wants, for customers who have both ordered and filed a
ticket, correct per-customer totals of each. The trap: `orders` and
`support_tickets` are two independent one-to-many children of
`customers`, and joining both directly in one query reproduces the same
fan-out family as Q011 and Q015 — this time across three tables instead
of two.

## 2. Output Grain

One row = one customer (restricted to those with >=1 order AND >=1
ticket).

## 3. Metric Definition

Total order count and total ticket count per customer, each counted
independently.

## 4. Required Data

`customers`: customer_id.
`orders`: customer_id, order_id.
`support_tickets`: customer_id, ticket_id.

## 5. Logical Decomposition

    Step 1 → pre-aggregate orders by customer_id → order_count
    Step 2 → pre-aggregate support_tickets by customer_id → ticket_count
    Step 3 → INNER JOIN the two summaries on customer_id (this naturally
              enforces "has both")

## 6. Pattern Recognition

"Combine two independent 1:many children of the same parent" →
aggregate each child to the parent's grain *first*, then join the two
already-aggregated results — never join both children directly to each
other or to the parent in the same non-aggregated query.

## 7. SQL

```sql
WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
),
ticket_counts AS (
    SELECT customer_id, COUNT(*) AS ticket_count
    FROM support_tickets
    GROUP BY customer_id
)
SELECT
    oc.customer_id,
    oc.order_count,
    tc.ticket_count
FROM order_counts oc
JOIN ticket_counts tc ON tc.customer_id = oc.customer_id
ORDER BY oc.customer_id;
```

## 8. Walkthrough

`order_counts` and `ticket_counts` each collapse their source table to
one row per `customer_id` before anything else happens. Joining them
to each other is then a clean one-to-one join — an `INNER JOIN`
naturally keeps only customers present in *both* summaries, which is
exactly "has at least one order AND at least one ticket," with no extra
filter needed.

## 9. Validation

- For one customer_id, independently run
  `SELECT COUNT(*) FROM orders WHERE customer_id=<id>` and
  `SELECT COUNT(*) FROM support_tickets WHERE customer_id=<id>` and
  confirm they match this query's output for that customer.
- Contrast with the naive fan-out version below on the same customer to
  see the counts inflate:

```sql
SELECT
    c.customer_id,
    COUNT(o.order_id) AS naive_order_count,
    COUNT(t.ticket_id) AS naive_ticket_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN support_tickets t ON t.customer_id = c.customer_id
GROUP BY c.customer_id
LIMIT 5;
```

If a customer has 5 orders and 3 tickets, the naive three-way join
produces 15 rows for that customer, and `COUNT(o.order_id)` returns 15
(not 5) while `COUNT(t.ticket_id)` also returns 15 (not 3) — both
counts are wrong, and wrong in the *same* inflated way, which makes the
bug easy to miss since nothing looks obviously broken (both numbers
just happen to be equal to `order_count * ticket_count`).

## 10. Edge Cases

- A customer with orders but zero tickets is correctly excluded by the
  `JOIN` between the two summaries (an `INNER JOIN` there requires
  presence in both) — if the business instead wanted *all* customers
  with orders, showing 0 for ticket_count where absent, a `LEFT JOIN`
  with `COALESCE(tc.ticket_count, 0)` would be the right tool instead.
- Note this differs from Q013/Q029's anti-join pattern: here we want
  the intersection (both exist), not the difference (one exists, the
  other doesn't).

## 11. Alternative Approach

`COUNT(DISTINCT o.order_id)` and `COUNT(DISTINCT t.ticket_id)` applied
to the naive three-way join *would* recover the correct counts (since
DISTINCT removes the duplication), and for small data this works. But
it's fragile: it relies on every future column added to the SELECT
list remembering to also use DISTINCT, and it does unnecessary work
(materializing the full cross-product before discarding most of it).
The pre-aggregate-then-join CTE approach is both clearer and cheaper.

## 12. Trade-offs

Pre-aggregating first is the more robust default whenever two or more
independent one-to-many children of the same table need to be combined
— it fails safe (wrong joins become obviously wrong row counts) rather
than failing silently (fan-out counts that are wrong but internally
"consistent" with each other).

## 13. Business Interpretation

This dataset lets customer success correlate order volume with support
burden per customer — a customer with high order_count and high
ticket_count might be a demanding-but-valuable account, while high
ticket_count with low order_count could flag a customer heading toward
churn (a theme Level 6's Q060 explores further).
