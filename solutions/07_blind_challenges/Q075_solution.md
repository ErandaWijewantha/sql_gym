# Reasoning

## 1. Interpret the Business Question

Find customers who've placed completed orders at more than 3 distinct
physical/online stores.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

`distinct_store_count = COUNT(DISTINCT store_id)` per customer, from
completed orders.

## 4. Required Data

`orders`: customer_id, store_id, order_status.

## 5. SQL

```sql
SELECT
    customer_id,
    COUNT(DISTINCT store_id) AS distinct_store_count
FROM orders
WHERE order_status = 'completed'
GROUP BY customer_id
HAVING COUNT(DISTINCT store_id) > 3
ORDER BY distinct_store_count DESC;
```

## 6. Walkthrough

A single `GROUP BY customer_id` with `COUNT(DISTINCT store_id)` counts
how many *different* stores each customer has completed orders at, in
one pass over `orders` — no join needed since `store_id` already lives
on `orders` directly. `HAVING` filters on that aggregate.

## 7. Validation

- Manually list one flagged customer's orders and confirm their
  distinct store_id count exceeds 3.
- Confirm the maximum possible value is 35 (total store count) and no
  result exceeds that.

## 8. Edge Cases

- A customer who placed 20 orders all at the same store shows
  `distinct_store_count = 1` — order *volume* doesn't matter here, only
  store *variety*.
- This includes the small number of dedicated online stores as
  distinct "stores" in the count — a customer who shops online once and
  at 3 different physical stores would show `distinct_store_count = 4`
  and qualify, which may or may not match what "cross-store shopper"
  is meant to capture; worth clarifying whether online should count the
  same as a physical location for this specific analysis.

## 9. Alternative Approach

Restricting the count to `store_type != 'online'` first would answer a
narrower "cross-*physical*-location shopper" question specifically,
excluding online activity from the count.

## 10. Trade-offs

Including online stores in the count is simpler and matches the literal
question; excluding them is more precise if the actual business intent
is about physical-location loyalty specifically.

## 11. Business Interpretation

Customers on this list aren't tied to a single location, which affects
how store-level loyalty programs should be designed for them — a
program that only rewards visits to one specific store would
systematically under-reward this segment's actual spend.
