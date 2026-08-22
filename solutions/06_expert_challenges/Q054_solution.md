# Reasoning

## 1. Interpret the Business Question

Leadership wants to see rank *movement*, not just a static monthly
ranking — which stores are climbing or sliding relative to their peers,
month over month.

## 2. Output Grain

One row = one (store, month) pair.

## 3. Metric Definition

`revenue_rank` = the store's rank among all stores that month, by net
revenue (completed orders), highest revenue = rank 1. `rank_change =
previous_month_rank - current_month_rank` (positive means the store
climbed; negative means it fell).

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → compute net revenue per (store, month)
    Step 2 → RANK() stores within each month, ordered by revenue descending
    Step 3 → LAG(rank) partitioned by store, ordered by month
    Step 4 → rank_change = previous rank - current rank

## 6. Pattern Recognition

This stacks two different window functions with two different
`PARTITION BY` dimensions on the same data: first rank *across stores
within a month* (`PARTITION BY month`), then compare *across months
within a store* (`PARTITION BY store`) — a rank of a rank, computed in
two clearly separated steps via a CTE rather than attempted in one
pass.

## 7. SQL

```sql
WITH monthly_store_revenue AS (
    SELECT
        o.store_id,
        DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY o.store_id, DATE_FORMAT(o.order_date, '%Y-%m-01')
),
ranked_by_month AS (
    SELECT
        store_id,
        month_start,
        net_revenue,
        RANK() OVER (PARTITION BY month_start ORDER BY net_revenue DESC) AS revenue_rank
    FROM monthly_store_revenue
)
SELECT
    store_id,
    month_start,
    net_revenue,
    revenue_rank,
    LAG(revenue_rank) OVER (PARTITION BY store_id ORDER BY month_start) AS prev_month_rank,
    CAST(LAG(revenue_rank) OVER (PARTITION BY store_id ORDER BY month_start) AS SIGNED)
        - CAST(revenue_rank AS SIGNED) AS rank_change
FROM ranked_by_month
ORDER BY store_id, month_start;
```

## 8. Walkthrough

`monthly_store_revenue` collapses to one row per (store, month).
`ranked_by_month`'s window function partitions **by month** (not by
store) — this is the step that produces a fresh 1-to-35 ranking every
single month, comparing stores against their *peers that month*.
The outer query's `LAG` then partitions **by store** (not by month) —
looking at the *same store's* rank in the immediately preceding month.
`rank_change` is defined as previous-minus-current so that a positive
number means the store's rank number got smaller (better) — i.e., the
store climbed — matching the intuitive meaning of "positive = improved."
Both operands are explicitly `CAST(... AS SIGNED)` before subtracting —
`RANK()` returns an unsigned integer type in MySQL, and computing
`smaller_unsigned - larger_unsigned` directly would wrap around to a
huge positive number (or raise an out-of-range error under strict SQL
mode) instead of producing the negative number a declining store should
show.

## 9. Validation

- For any single month, `revenue_rank` values across all stores should
  be exactly 1 through 35 (or fewer + gaps if any store had zero
  revenue that month and thus no row) with no duplicates unless a true
  revenue tie exists.
- Pick one store, list its `revenue_rank` sequence across all 24
  months, and manually confirm each `rank_change` value against
  consecutive entries.
- A store's first appearing month should show `prev_month_rank = NULL`
  and `rank_change = NULL`.

## 10. Edge Cases

- **Unsigned integer subtraction**: forgetting the `CAST(... AS
  SIGNED)` step is a genuine trap, not a stylistic choice — MySQL's
  window ranking functions return an unsigned type, so
  `revenue_rank - LAG(revenue_rank)` for a store that *improved* its
  rank (a smaller current number than before) computes
  `small_unsigned - large_unsigned`, which either errors under strict
  SQL mode or silently wraps to a nonsensical huge value otherwise —
  exactly the kind of silent numeric-type bug `docs/common_mistakes.md`
  warns about.
- A store with zero completed orders in some month simply has no row
  for that month in `monthly_store_revenue`, meaning that month is
  skipped in its `LAG` sequence — the "previous month" compared against
  might actually be two or more calendar months prior. As with
  Q023/Q037, a full calendar grid would be needed to make month-to-
  month comparisons strictly calendar-adjacent if that precision
  matters for this specific report.
- `RANK()` (not `DENSE_RANK()`) is used deliberately here, since
  leadership cares about literal ordinal position among all stores
  (echoing the distinction from Q022) — a tie for 5th means the next
  store is ranked 7th, not 6th.

## 11. Alternative Approach

Using `DENSE_RANK()` instead of `RANK()` for the monthly ranking would
change how ties affect subsequent stores' rank numbers, which would in
turn change `rank_change` for anyone near a tie — worth being
deliberate about which ranking function leadership actually wants
before computing movement on top of it.

## 12. Trade-offs

Not applicable beyond the RANK vs DENSE_RANK choice already discussed.

## 13. Business Interpretation

A store climbing several ranks in a single month is a stronger signal
worth investigating (positively or negatively) than one sitting
consistently at the same rank — this view lets leadership spot
momentum, not just current standing.
