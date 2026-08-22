# Reasoning

## 1. Interpret the Business Question

Retention wants, per order, a look *forward* to the customer's next
order — the mirror image of Q010/Q032's backward-looking recency logic.

## 2. Output Grain

One row = one order.

## 3. Metric Definition

`next_order_date` = the chronologically next order_date for the same
customer (NULL if none). `days_until_next_order = DATEDIFF(next_order_date,
order_date)`.

## 4. Required Data

`orders`: order_id, customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → order each customer's orders chronologically
    Step 2 → LEAD(order_date) partitioned by customer, ordered by order_date
    Step 3 → DATEDIFF between the two dates

## 6. Pattern Recognition

"What happens next" → `LEAD()`, the forward-looking counterpart to
`LAG()`. Same partitioning logic as Q023, just looking one row ahead
instead of one row behind.

## 7. SQL

```sql
SELECT
    order_id,
    customer_id,
    order_date,
    LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_date,
    DATEDIFF(
        LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date),
        order_date
    ) AS days_until_next_order
FROM orders
ORDER BY customer_id, order_date;
```

## 8. Walkthrough

`PARTITION BY customer_id` ensures each customer's orders are only ever
compared against their *own* other orders. `ORDER BY order_date` within
that partition defines "next" as chronologically next. For a
customer's most recent (last) order, there is no subsequent row in
their partition, so `LEAD()` returns `NULL` — and `DATEDIFF(NULL, ...)`
correctly also evaluates to `NULL`, matching the requirement that
orders with no next order show NULL for both fields.

## 9. Validation

- A customer with exactly one order should show exactly one row, with
  both `next_order_date` and `days_until_next_order` as `NULL`.
- For a customer with 3+ orders, manually list their orders sorted by
  date and confirm each row's `next_order_date` matches the
  chronologically following order.
- `days_until_next_order` should never be negative (since `LEAD` always
  looks at a later-or-equal row in the ordering, and two orders on the
  exact same date would produce `0`, not a negative number).

## 10. Edge Cases

- Two orders placed on the exact same calendar date for one customer:
  `ORDER BY order_date` (a `DATETIME` column, so really down to the
  second) still produces a well-defined chronological sequence between
  them, since `order_date` includes a time component — same-day orders
  are not actually tied at this precision, though two orders placed in
  the same *second* would be an edge case MySQL would order arbitrarily
  (a non-issue in this dataset).
- Changing `LAG` to `LEAD` (or vice versa) is the *only* difference
  needed to flip this into a "days since previous order" question —
  everything else (PARTITION BY, ORDER BY) stays identical.
- Averaging `days_until_next_order` per customer (ignoring NULLs, which
  `AVG()` does automatically) gives a per-customer "typical repurchase
  gap" — the natural next question, and exactly the kind of measure
  Level 4's dormancy/reactivation questions build on.

## 11. Alternative Approach

A self-join (`o2.customer_id = o1.customer_id AND o2.order_date > o1.order_date`,
keeping only the minimum such `o2.order_date` per `o1` row) achieves
the same result without `LEAD`, but requires an extra aggregation step
to pick the *minimum* qualifying next date — more verbose for no
benefit here.

## 12. Trade-offs

`LEAD()` is the clearly preferred, idiomatic tool for "next row in an
ordered partition" — there's no realistic scenario in this dataset
where the self-join alternative would be worth its extra complexity.

## 13. Business Interpretation

This per-order gap measure is the raw material for understanding
typical repurchase cadence — retention can aggregate it per customer,
per segment, or per acquisition channel to see who buys again quickly
versus who takes a long time (or never does), directly feeding into
Level 4's reactivation and churn-signal questions.
