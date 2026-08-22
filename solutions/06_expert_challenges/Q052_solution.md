# Reasoning

## 1. Interpret the Business Question

Account management wants a specific journey shape: a customer's
quarterly spend tier rose at some point, and later fell back down —
distinct from a customer who simply rose and stayed, or one who was
always flat.

## 2. Output Grain

The intermediate grain is one row per (customer, quarter); the final
output grain is one row per customer matching the up-then-down pattern.

## 3. Metric Definition

Quarterly net spend (completed orders) per customer, bucketed into
tiers using fixed thresholds: "Low" (< LKR 15,000), "Mid" (LKR 15,000 -
75,000), "High" (> LKR 75,000). A customer qualifies if there exist two
quarters, Q_up and Q_down, with Q_up before Q_down, where their tier at
Q_up is strictly higher than their tier at the quarter immediately
before Q_up, and their tier at Q_down is strictly lower than their tier
at Q_up.

## 4. Required Data

`orders`: order_id, customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute net spend per (customer, quarter)
    Step 2 → map spend to an ordinal tier number (1=Low, 2=Mid, 3=High)
    Step 3 → for each customer's quarter sequence, find the running
              maximum tier reached so far
    Step 4 → flag customers where a later quarter's tier is below the
              running maximum reached in an earlier quarter

## 6. Pattern Recognition

"Rose, then later fell" is a *running maximum* comparison, not a simple
adjacent-quarter LAG comparison — the "fall" doesn't need to be
immediately after the "rise," so this needs a window function that
looks at the running peak-so-far, not just the previous row.

## 7. SQL

```sql
WITH quarterly_spend AS (
    SELECT
        o.customer_id,
        CONCAT(YEAR(o.order_date), '-Q', QUARTER(o.order_date)) AS year_quarter,
        MIN(o.order_date) AS quarter_sort_date,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_spend
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.customer_id, CONCAT(YEAR(o.order_date), '-Q', QUARTER(o.order_date))
),
tiered AS (
    SELECT
        customer_id,
        year_quarter,
        quarter_sort_date,
        CASE
            WHEN net_spend < 15000 THEN 1
            WHEN net_spend <= 75000 THEN 2
            ELSE 3
        END AS tier
    FROM quarterly_spend
),
with_running_peak AS (
    SELECT
        customer_id,
        year_quarter,
        tier,
        MAX(tier) OVER (
            PARTITION BY customer_id ORDER BY quarter_sort_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS peak_tier_before_this_quarter
    FROM tiered
)
SELECT DISTINCT customer_id
FROM with_running_peak
WHERE peak_tier_before_this_quarter IS NOT NULL
  AND tier < peak_tier_before_this_quarter;
```

## 8. Walkthrough

`quarterly_spend` collapses orders to one row per (customer, calendar
quarter), tracking `quarter_sort_date` for correct chronological
ordering across year boundaries. `tiered` maps each quarter's spend to
an ordinal 1/2/3 tier. `with_running_peak` computes, for each quarter,
the *highest tier reached in any strictly earlier quarter* using
`MAX(tier) OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)`
— explicitly excluding the current row from the window frame, so a
quarter is never compared against its own tier. The final filter finds
any quarter whose tier is lower than the peak already established
before it — meaning the customer previously reached a higher tier and
has since fallen from it.

## 9. Validation

- Pick one flagged customer and lay out their full quarterly tier
  sequence; confirm a later tier value is indeed lower than an earlier
  peak.
- A customer who only ever rises (Low → Mid → High, never back down)
  should **not** appear — their tier is never below any prior peak.
- A customer who stays flat throughout should not appear, for the same
  reason.

## 10. Edge Cases

- A customer's very first quarter can never trigger the flag on its
  own (the window frame `UNBOUNDED PRECEDING AND 1 PRECEDING` is empty
  for the first row, so `peak_tier_before_this_quarter` is `NULL`,
  excluded by the `IS NOT NULL` check).
- A customer active in only 1 quarter can never qualify (no "later"
  quarter exists to fall in) — correctly excluded, since the pattern
  requires at least 2 quarters of history.
- The specific tier thresholds (15,000 / 75,000) are a judgment call —
  as with every threshold in this gym, worth stating explicitly rather
  than treating as an objective cutoff.

## 11. Alternative Approach

A self-join comparing every pair of a customer's quarters (`q1.tier >
some_prior_peak` type logic) without a window function is possible but
significantly more verbose — computing a running maximum is exactly
what window functions with an explicit frame clause are for.

## 12. Trade-offs

The window-function version is compact and directly expresses "peak so
far, excluding now" via the frame clause — a good example of window
frames doing real analytical work beyond simple running totals (Q025)
or fixed-size moving averages (Q026).

## 13. Business Interpretation

These customers represent a specific risk pattern for account
management: they proved willing to spend at a higher tier once (so the
product/price point clearly can work for them) but didn't sustain it —
worth a different outreach than either a steadily-growing customer or
one who's simply always been in a low tier.
