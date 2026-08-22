# Reasoning

## 1. Interpret the Business Question

Marketing needs a precise audience: people who *have* purchased before
(unlike Q013's never-purchased population) but have now gone quiet for
at least 90 days as of the dataset's reference date.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

Same recency measure as Q032: `DATEDIFF('2025-12-31', MAX(order_date))
>= 90`. The "has purchased before" requirement is automatically
satisfied by definition, since the population is built from `orders`
directly.

## 4. Required Data

`orders`: customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → compute last_order_date per customer (same as Q031/Q032)
    Step 2 → compute recency_days from the fixed reference date
    Step 3 → HAVING recency_days >= 90

## 6. Pattern Recognition

This is *not* an anti-join pattern at all, despite superficially
resembling Q013/Q029/Q035 — it's simply Q032's recency calculation with
a `HAVING` threshold applied. Recognizing that a question doesn't need
the fancier pattern it might resemble is itself a skill: reaching for
`NOT EXISTS` here would be solving a problem this question doesn't
actually have (there's no "no match" condition — every row already has
a `MAX(order_date)` by construction).

## 7. SQL

```sql
SELECT
    customer_id,
    MAX(order_date) AS last_order_date,
    DATEDIFF('2025-12-31', MAX(order_date)) AS recency_days
FROM orders
GROUP BY customer_id
HAVING DATEDIFF('2025-12-31', MAX(order_date)) >= 90
ORDER BY recency_days DESC;
```

## 8. Walkthrough

`GROUP BY customer_id` with `MAX(order_date)` guarantees every row in
this result represents a customer with at least one order — so "has
purchased before" is true by construction, with no anti-join needed.
`HAVING` (not `WHERE`) is required because the filter condition depends
on `MAX(order_date)`, an aggregate that only exists after grouping.

## 9. Validation

- This result should be a strict subset of Q031/Q032's full population
  (all customers with >= 1 order), filtered down by the recency
  threshold.
- This result and Q013's "never purchased" result should be **mutually
  exclusive** (a customer can't be in both — one requires >= 1 order,
  the other requires exactly 0) — together with "recency < 90 days"
  customers, all three groups should partition the full 12,000-customer
  base with no overlap.
- Roughly cross-check magnitude against the data generator's dormancy
  design (~15% of `occasional`/`regular` archetype customers were built
  with a deliberately truncated recent history) plus any `one_time`
  customers whose single order happened to be more than 90 days before
  the reference date.

## 10. Edge Cases

- A `one_time` customer whose single order was, say, 500 days before
  the reference date is correctly included here — "dormant" doesn't
  require having been a *repeat* customer, just having purchased at
  least once and then gone quiet.
- This uses all orders regardless of status for the recency
  calculation, consistent with Q031/Q032/Q033's lifecycle framing — a
  customer whose only recent activity was a cancelled order still
  counts as "not silent" for this specific measure.
- The 90-day threshold is a business assumption, not a law of nature —
  worth stating explicitly (as this question does) rather than
  smuggling in an implicit default, the same lesson Level 5 hammers on
  repeatedly.

## 11. Alternative Approach

Building on Q032's output directly (as a CTE or view) and filtering
that with a plain `WHERE recency_days >= 90` in an outer query is
equivalent, and preferable if `recency_days` is already computed
elsewhere as a reusable base — avoids recomputing the aggregate
`HAVING` condition redundantly if this exact recency figure is needed
in multiple places.

## 12. Trade-offs

Not applicable beyond the reuse consideration above.

## 13. Business Interpretation

This is the correctly-scoped win-back audience: proven past purchasers
who've gone quiet, as distinct from people who were never engaged in
the first place (Q013) — the messaging, and the expected response
rate, should be very different for the two groups.
