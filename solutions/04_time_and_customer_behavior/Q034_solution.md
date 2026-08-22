# Reasoning

## 1. Interpret the Business Question

Marketing wants customers whose *most recent* purchase came after a
long silence — i.e., people who came back. This is not the same as
"currently dormant" (Q039, no recent order at all) — it's specifically
about detecting a **reactivation event that already happened**: the gap
immediately before their latest order was unusually long.

## 2. Output Grain

One row = one customer (restricted to those with >= 2 orders, where the
gap before their latest order was >= 90 days).

## 3. Metric Definition

For a customer's latest order, `gap_days = DATEDIFF(latest_order_date,
previous_order_date)`. A customer "reactivated" if `gap_days >= 90`.

## 4. Required Data

`customers`: customer_id (for readability in the output).
`orders`: customer_id, order_date.
`order_items` is listed as available but not needed for the core
question — it would only matter for a follow-up like "what did they buy
when they came back," an optional extension noted below.

## 5. Logical Decomposition

    Step 1 → identify each customer's purchase events (order_date per order)
    Step 2 → order them chronologically per customer
    Step 3 → for the latest order, calculate the previous purchase date
    Step 4 → calculate the gap between the two
    Step 5 → filter gap >= 90 days, and require a previous order to exist at all

## 6. Pattern Recognition

"Compare this event to the previous event for the same entity" → `LAG`,
partitioned by customer and ordered by date — but the twist here is
that we only care about this comparison *at the latest row* per
customer, not at every row. That means combining `LAG` (to get the
previous date) with a second ranking device (`ROW_NUMBER` ordered
descending) to isolate "the latest row" per customer.

## 7. SQL

```sql
WITH order_sequence AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date,
        ROW_NUMBER()     OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn_from_latest
    FROM orders
)
SELECT
    customer_id,
    prev_order_date,
    order_date AS latest_order_date,
    DATEDIFF(order_date, prev_order_date) AS gap_days
FROM order_sequence
WHERE rn_from_latest = 1
  AND prev_order_date IS NOT NULL
  AND DATEDIFF(order_date, prev_order_date) >= 90
ORDER BY gap_days DESC;
```

## 8. Walkthrough

`LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)`
attaches, to every order row, that same customer's immediately
preceding order date (ascending order, so "previous" means
chronologically earlier). Separately, `ROW_NUMBER() OVER (PARTITION BY
customer_id ORDER BY order_date DESC)` numbers each customer's orders
from most recent (1) backward — so `rn_from_latest = 1` isolates
exactly one row per customer: their latest order. On that one row,
`prev_order_date` (from the LAG computed in the same pass) is the date
of the order immediately before it, and `DATEDIFF` measures the gap.
Filtering `prev_order_date IS NOT NULL` excludes one-time customers,
who have no previous order to compare against — they cannot, by
definition, have "reactivated."

## 9. Validation

- Pick one flagged customer, list every one of their orders sorted by
  date, and confirm the gap between the last two really is >= 90 days.
- Confirm no one-time customer (order_count = 1 from Q033) ever
  appears in this result — `prev_order_date IS NOT NULL` should
  guarantee that structurally.
- Roughly cross-check against the data generator's design: ~15% of
  `occasional`/`regular` archetype customers were constructed with a
  deliberately truncated order history (their *last* order is 90-400
  days before the dataset end) — but note that's a different
  phenomenon (currently dormant, Q039) from what this question
  measures (a long gap *before* their latest order, which could have
  happened at any point in their history, including mid-history before
  several more recent orders followed).

## 10. Edge Cases

- A customer with exactly 2 orders, 89 days apart, is correctly
  excluded (gap must be `>= 90`, not `> 89` — same number, but worth
  being deliberate about the boundary).
- A customer whose latest order came only a few days after their
  previous one, but who *also* had a 200-day gap somewhere earlier in
  their history, is **not** flagged by this query — it only looks at
  the gap immediately preceding the *most recent* order, by design (the
  question is about their latest purchase specifically, not "has this
  customer ever had a long gap anywhere," which is a related but
  different question).
- Order status is deliberately not filtered here — a cancelled order
  still represents an attempt to purchase, and for a "did this person
  come back and try to engage" question, that's arguably the right
  call; a stricter version restricted to completed orders would change
  which gaps get measured.

## 11. Alternative Approach

A self-join version: join `orders` to itself, matching each customer's
order to *all* their earlier orders, taking `MAX(earlier order_date)`
per (customer, order) to get "previous order date" without a window
function, then filtering to each customer's own overall
`MAX(order_date)` row. This produces the same result but is
considerably more verbose than the `LAG` + `ROW_NUMBER` combination,
and is a good exercise for feeling *why* window functions exist.

## 12. Trade-offs

The window-function version is the clear choice here: it expresses
"previous row" and "latest row per group" directly, in their own
vocabulary, rather than reconstructing both via self-joins and nested
aggregates.

## 13. Business Interpretation

This surfaces customers who just re-engaged after a meaningful absence
— exactly the moment marketing wants to reinforce with a "welcome
back" message or a small incentive to convert the reactivation into a
new, sustained pattern, before they lapse again.

## Extension (Optional)

To also show what a reactivated customer bought on their comeback
order, join `order_items` (and `products`) onto the `latest_order_date`
row per customer — a natural next step once this base query is
working, left as an exercise rather than shown here.
