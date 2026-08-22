# Reasoning

## 1. Interpret the Business Question

Operations wants a fulfillment health check: a simple count of orders
per status, sorted so the largest bucket is immediately visible.

## 2. Output Grain

One row = one order_status value.

## 3. Metric Definition

A plain row count — no revenue or other measure involved. `COUNT(*)`
and `COUNT(order_id)` are equivalent here since `order_id` is the
primary key and never NULL.

## 4. Required Data

`orders`: order_status.

## 5. Logical Decomposition

    Step 1 → GROUP BY order_status
    Step 2 → COUNT(*) per group
    Step 3 → ORDER BY the count, descending

## 6. Pattern Recognition

"How many of each kind" → `GROUP BY` + `COUNT(*)`. The single most
common analytical pattern there is — recognizing it instantly here
matters, because later levels dress up the same shape in much more
business-y language.

## 7. SQL

```sql
SELECT
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;
```

## 8. Walkthrough

`GROUP BY order_status` collapses the ~118K order rows into one row per
distinct status value; `COUNT(*)` counts how many original rows fell
into each bucket; `ORDER BY order_count DESC` puts the most frequent
status first.

## 9. Validation

- Sum of `order_count` across all rows should equal
  `SELECT COUNT(*) FROM orders`.
- Every status appearing here should be one of the four values defined
  by the `order_status` ENUM (`completed`, `cancelled`, `pending`,
  `refunded`) — if a fifth value appeared, that would indicate a schema
  or data problem, not a query bug.

## 10. Edge Cases

- A `WHERE` clause is unnecessary and would be wrong here — filtering
  would defeat the purpose of seeing *all* statuses.
- `pending` orders are, by construction, concentrated in the last two
  weeks of the dataset (nothing further in the future is a candidate to
  resolve into completed/cancelled/refunded yet) — a naturally smaller
  count for `pending` is expected, not a bug.

## 11. Alternative Approach

None warranted — this is the canonical shape for this kind of question.

## 12. Trade-offs

Not applicable.

## 13. Business Interpretation

A disproportionately high `cancelled` or `refunded` count relative to
`completed` would be an early warning sign for operations to
investigate further (e.g., payment failures, fulfillment problems,
product quality) — this query is the first step of that investigation,
not the whole answer.
