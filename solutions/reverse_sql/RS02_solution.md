# RS02 — Solution

## Grain
One row = one pair of consecutive orders for the same customer (an
"earlier" order and the very next order after it), restricted to pairs
at least 90 days apart.

## What is being computed
For every customer, every adjacent pair of orders (no other order for
that customer falls strictly between them, enforced by the `NOT
EXISTS`), with the day gap between them, filtered to gaps of 90+ days.

## Pattern
This is a self-join implementation of "compare an event to the next
event for the same entity" — functionally equivalent to what `LEAD()`
would compute directly, but written using a self-join plus a
correlated `NOT EXISTS` to enforce adjacency instead of a window
function.

## Likely business question
"Which customers had a gap of at least 90 days between two consecutive
orders?" — closely related to Q034's Customer Reactivation question,
though RS02 surfaces *every* qualifying gap in a customer's history
(not just the one immediately preceding their latest order).

## Notes
The `NOT EXISTS` subquery is doing the work that `LEAD() OVER (PARTITION
BY customer_id ORDER BY order_date)` would do far more directly — this
is a good example of "the same idea, expressed the harder way," useful
for recognizing when a window function would simplify a self-join.

## Verification query

```sql
SELECT o1.customer_id, o1.order_date AS earlier_order, o2.order_date AS later_order,
       DATEDIFF(o2.order_date, o1.order_date) AS gap_days
FROM orders o1
JOIN orders o2
    ON o1.customer_id = o2.customer_id
   AND o2.order_date > o1.order_date
WHERE NOT EXISTS (
    SELECT 1 FROM orders o3
    WHERE o3.customer_id = o1.customer_id
      AND o3.order_date > o1.order_date
      AND o3.order_date < o2.order_date
)
AND DATEDIFF(o2.order_date, o1.order_date) >= 90
LIMIT 20;
```
