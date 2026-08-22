# Reasoning

## 1. Interpret the Business Question

"Who should we target for win-back?" cannot be answered correctly
without first choosing a concrete definition of "at risk" — the right
first move is stating that assumption out loud, not guessing silently
and hoping it matches what the Head of Marketing meant.

**Chosen definition for this solution** (state yours before reading
further): a customer qualifies if (a) they have purchased before —
excluding never-purchased customers, who need a different acquisition
message entirely (Q013), (b) their recency is between 60 and 180 days
— long enough to be genuinely going quiet, but not so long that a
win-back message is unlikely to land (a customer silent for 2 years is
arguably already lost, not "at risk"), and (c) their historical spend
clears a minimum bar, so the campaign budget targets people worth
winning back.

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

`recency_days` (as in Q032), `lifetime_net_spend` (as in Q040), both
computed over the customer's order history.

## 4. Required Data

`customers`: customer_id.
`orders`: customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute recency_days and lifetime_net_spend per customer
    Step 2 → filter to recency_days BETWEEN 60 AND 180
    Step 3 → filter to lifetime_net_spend above a chosen minimum (here,
              LKR 20,000, roughly the middle of the spend distribution)

## 6. Pattern Recognition

This combines two already-familiar patterns (Q032's recency, Q040's
lifetime spend) under one filter — the "pattern" this question is
really testing is *recognizing that no SQL pattern can substitute for
a missing business definition*.

## 7. SQL

```sql
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        MAX(o.order_date) AS last_order_date,
        DATEDIFF('2025-12-31', MAX(o.order_date)) AS recency_days,
        COALESCE(SUM(
            CASE WHEN o.order_status = 'completed'
                 THEN oi.quantity * oi.unit_price - oi.discount_amount
                 ELSE 0 END
        ), 0) AS lifetime_net_spend
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id
)
SELECT customer_id, last_order_date, recency_days, lifetime_net_spend
FROM customer_metrics
WHERE recency_days BETWEEN 60 AND 180
  AND lifetime_net_spend >= 20000
ORDER BY lifetime_net_spend DESC;
```

## 8. Walkthrough

The `JOIN` to `orders` guarantees only customers with >= 1 order enter
this computation (never-purchased customers are automatically
excluded). `LEFT JOIN order_items` (rather than an inner join) ensures
an order with a status other than `completed` still contributes to
`recency_days` via its `order_date`, without incorrectly contributing
to `lifetime_net_spend` — the `CASE` inside the `SUM` only counts
line-item value for completed orders, everything else contributes 0.
The two filters then apply the chosen "at risk" definition explicitly.

## 9. Validation

- Confirm every row has `recency_days` strictly between 60 and 180.
- Confirm every row's `lifetime_net_spend >= 20000`.
- Sanity check the list size against the marketing budget context — if
  it's far too large or far too small to action, that's a signal to
  revisit the thresholds, not a query bug.

## 10. Edge Cases

- A customer with recency of exactly 200 days is excluded under this
  definition — arguably still "at risk" under a looser reading, which
  is exactly why the thresholds need to be stated and agreed on, not
  assumed.
- A customer with high historical spend but recency of 30 days (still
  quite active) is correctly excluded — they're not at risk yet.
- This definition is one reasonable choice among several; a colleague
  choosing "recency > 45 days, no spend minimum" would produce a
  substantially different (larger, lower-value) list — neither is
  objectively "more correct" absent more context from the business.

## 11. Alternative Approach

A trend-based definition (declining order frequency compared to the
customer's own historical cadence, rather than a fixed recency window)
would catch high-frequency VIPs starting to slow down *before* they
cross a generic 60-day threshold — arguably better for high-value
customers specifically, but requires meaningfully more logic (similar
to Q050's combined signal approach) and wouldn't work at all for
customers with too few historical orders to establish a baseline
cadence.

## 12. Trade-offs

A simple fixed-threshold definition (this solution) is easy to explain
to a non-technical stakeholder and easy to recompute regularly; a
trend-based definition is more sophisticated and potentially more
precise, but harder to explain and validate, and needs more historical
data per customer to work at all.

## 13. Business Interpretation

The single most important deliverable of this exercise isn't the SQL —
it's the sentence that should precede it: **"I'm defining 'at risk' as
recency between 60-180 days with historical spend above LKR 20,000 —
does that match what you have in mind, or would you rather adjust the
thresholds?"** Bringing back a list without that sentence is the
mistake this question exists to train against.
