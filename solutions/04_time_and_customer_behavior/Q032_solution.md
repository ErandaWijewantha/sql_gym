# Reasoning

## 1. Interpret the Business Question

Customer success wants a single recency number per customer: how many
days have elapsed since their last order, measured against a fixed
point in time rather than the ever-moving present.

## 2. Output Grain

One row = one customer (restricted to those with >= 1 order).

## 3. Metric Definition

`recency_days = DATEDIFF('2025-12-31', MAX(order_date))`. The reference
date is fixed at **2025-12-31** — the dataset's last day — precisely
because using `CURDATE()` would make this number grow every single day
this training environment is used, silently invalidating every
threshold discussed in this gym (see `data_generation/README.md`).

## 4. Required Data

`orders`: customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → GROUP BY customer_id, MAX(order_date) (same as Q031)
    Step 2 → DATEDIFF between the fixed reference date and that max date

## 6. Pattern Recognition

"How long since the last event" → the same MAX()-per-group pattern as
Q031, with one additional date-arithmetic step against a *fixed*
anchor, not the current system date.

## 7. SQL

```sql
SELECT
    customer_id,
    MAX(order_date) AS last_order_date,
    DATEDIFF('2025-12-31', MAX(order_date)) AS recency_days
FROM orders
GROUP BY customer_id
ORDER BY recency_days DESC;
```

## 8. Walkthrough

`DATEDIFF(a, b)` in MySQL returns `a - b` in whole days; here it's
`DATEDIFF('2025-12-31', last_order_date)`, so a customer whose last
order was on 2025-12-31 itself gets `recency_days = 0`, and one whose
last order was on 2024-01-01 (the dataset's very first day) gets the
maximum possible recency (~730). Swapping the argument order would flip
the sign — worth double-checking against one known example rather than
guessing.

## 9. Validation

- The minimum `recency_days` across all customers should be `>= 0` (no
  order can be dated after the reference date, since the dataset ends
  there) and the maximum should be `<= 730` (the dataset's full span).
- Cross-check against Q031: `last_order_date` here must match Q031's
  `last_order_date` for the same customer exactly.
- Pick a customer with a known recent order and confirm their
  `recency_days` is small.

## 10. Edge Cases

- `recency_days = 0` is possible and correctly means "their last order
  fell on the very last day of the dataset."
- Recency alone conflates two very different customers: a `one_time`
  archetype customer whose single order happened to be recent, and a
  `vip` archetype who orders constantly but happens to be between
  orders right now — a low recency number doesn't by itself mean
  "healthy," and Q050's churn early-warning question deliberately
  combines recency with frequency and monetary trend rather than
  relying on recency alone.
- There's no single universally correct set of tier thresholds (e.g.,
  "at risk" at 60 days vs 90 days) — that boundary is itself a business
  decision to make explicit, echoing Level 5's theme of stating
  assumptions rather than assuming a default.

## 11. Alternative Approach

Not applicable at this stage — a plain aggregate answers the question
directly.

## 12. Trade-offs

Not applicable.

## 13. Business Interpretation

This is the "R" in RFM analysis — on its own it tells you how long
it's been, but says nothing about how valuable or frequent that
customer's relationship with the business was. It's meant to be
combined with frequency and monetary measures, not read in isolation.
