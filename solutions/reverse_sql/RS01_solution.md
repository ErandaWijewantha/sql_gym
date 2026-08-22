# RS01 — Solution

## Grain
One row = one customer.

## What is being computed
Each customer's single most recent order (order_id and order_date),
using `ROW_NUMBER()` partitioned by customer and ordered by date
descending, then keeping only `rn = 1`.

## Pattern
Deduplication via `ROW_NUMBER()` — "keep the latest row per group," the
same pattern used in Q010 (via `MAX`) and Q079 (via this exact
`ROW_NUMBER` idiom).

## Likely business question
"What is each customer's most recent order?" — the foundational
building block for any recency analysis (Q032, Q039).

## Notes on alternative phrasing
This could equally have been written as `SELECT customer_id,
MAX(order_date) FROM orders GROUP BY customer_id` if only the date
were needed — the `ROW_NUMBER()` version is necessary specifically
because it also needs to carry along the matching `order_id`, which a
plain `GROUP BY` + `MAX` can't safely do without risking picking a
mismatched order_id if a customer had two orders on the same date.

## Verification query

```sql
SELECT
    customer_id,
    order_id,
    order_date
FROM (
    SELECT
        customer_id,
        order_id,
        order_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
    FROM orders
) ranked
WHERE rn = 1
LIMIT 20;
```
