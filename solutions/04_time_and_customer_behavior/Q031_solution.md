# Reasoning

## 1. Interpret the Business Question

Customer analytics wants the two dates that anchor every lifecycle
metric: when a customer first showed up, and when they were last seen.

## 2. Output Grain

One row = one customer (restricted to those with >= 1 order).

## 3. Metric Definition

`MIN(order_date)` and `MAX(order_date)`, using *all* orders regardless
of status — a cancelled order still represents a moment the customer
engaged with the store, which is what "lifecycle" activity means here
(distinct from a *revenue* metric, which would rightly exclude
cancelled orders).

## 4. Required Data

`orders`: customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → GROUP BY customer_id
    Step 2 → MIN(order_date) and MAX(order_date) in the same pass

## 6. Pattern Recognition

"First and last event per entity" → `GROUP BY` + `MIN()`/`MAX()`,
computed together in one query — a direct extension of Q010's
single-`MAX()` pattern.

## 7. SQL

```sql
SELECT
    customer_id,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS last_order_date
FROM orders
GROUP BY customer_id;
```

## 8. Walkthrough

`GROUP BY customer_id` collapses every order down to one row per
customer; `MIN()` and `MAX()` are computed over the same grouped rows
in the same pass, at no extra scan cost. A customer with exactly one
order naturally has `first_order_date = last_order_date`.

## 9. Validation

- For any customer, `first_order_date <= last_order_date` must always
  hold — structurally guaranteed by MIN/MAX semantics, so this is more
  a sanity check on the query than on the data.
- Row count here should match Q010's row count exactly (both are
  "customers with >= 1 order").
- Spot check one customer with several orders: list all their
  order_dates directly and confirm the min/max match.

## 10. Edge Cases

- This uses *all* orders, not just completed ones — a deliberate choice
  since "lifecycle activity" (did this customer ever engage with
  placing an order) is a different question from "revenue" (Q005) or
  "confirmed spend" (Q017). Restricting to completed orders here would
  silently change what "first/last purchase" means to "first/last
  *successful* purchase," which may or may not be what's wanted — worth
  being explicit either way rather than defaulting silently.
- Two orders on the exact same calendar date (but different times)
  still resolve correctly since `order_date` is a full `DATETIME`.

## 11. Alternative Approach

Not applicable — this is the simplest correct shape for the question.

## 12. Trade-offs

Not applicable.

## 13. Business Interpretation

This is the foundational table every later Level 4 question builds on:
recency (Q032) subtracts `last_order_date` from today; tenure (Q040)
uses `first_order_date` alongside `registration_date`; reactivation
(Q034) needs the *sequence* of order dates, not just the endpoints, but
still starts from this same idea.
