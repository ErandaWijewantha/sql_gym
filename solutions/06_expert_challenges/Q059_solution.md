# Reasoning

## 1. Interpret the Business Question

Finance wants a classic SaaS/retail-style cohort revenue curve: group
customers by *when they started* (calendar time), then track their
revenue on a *customer-relative* clock (months since their own first
purchase) — two different notions of "time" that must be kept
straight throughout.

## 2. Output Grain

One row = one (cohort_month, months_since_first_purchase) pair.

## 3. Metric Definition

`cumulative_avg_revenue_per_customer` at relative month M = (sum of net
revenue from all cohort members' orders placed within M months of their
own first purchase) / (number of customers in the cohort).

## 4. Required Data

`orders`: order_id, customer_id, order_date, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.

## 5. Logical Decomposition

    Step 1 → find each customer's first purchase month (their personal
              "month 0")
    Step 2 → assign their cohort as the calendar month of that first purchase
    Step 3 → for every order, compute months_since_first_purchase relative
              to that customer's own month 0
    Step 4 → sum net revenue per (cohort, months_since_first_purchase)
    Step 5 → divide by cohort size to get per-customer average
    Step 6 → cumulative-sum that average across increasing
              months_since_first_purchase, within each cohort

## 6. SQL

```sql
WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(DATE_FORMAT(order_date, '%Y-%m-01')) AS cohort_month
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM first_purchase
    GROUP BY cohort_month
),
order_relative_month AS (
    SELECT
        o.customer_id,
        fp.cohort_month,
        PERIOD_DIFF(
            DATE_FORMAT(o.order_date, '%Y%m'),
            DATE_FORMAT(fp.cohort_month, '%Y%m')
        ) AS months_since_first_purchase,
        oi.quantity * oi.unit_price - oi.discount_amount AS line_net_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN first_purchase fp ON fp.customer_id = o.customer_id
    WHERE o.order_status = 'completed'
),
cohort_month_revenue AS (
    SELECT
        cohort_month,
        months_since_first_purchase,
        SUM(line_net_revenue) AS revenue_that_relative_month
    FROM order_relative_month
    GROUP BY cohort_month, months_since_first_purchase
)
SELECT
    cmr.cohort_month,
    cmr.months_since_first_purchase,
    cs.cohort_size,
    ROUND(
        SUM(cmr.revenue_that_relative_month) OVER (
            PARTITION BY cmr.cohort_month
            ORDER BY cmr.months_since_first_purchase
        ) / cs.cohort_size,
        2
    ) AS cumulative_avg_revenue_per_customer
FROM cohort_month_revenue cmr
JOIN cohort_sizes cs ON cs.cohort_month = cmr.cohort_month
ORDER BY cmr.cohort_month, cmr.months_since_first_purchase;
```

## 7. Walkthrough

`first_purchase` establishes each customer's personal "month 0" (their
cohort). `order_relative_month` re-expresses *every* order's timing
not as a calendar month, but as `months_since_first_purchase` relative
to that specific customer's own cohort month, using `PERIOD_DIFF` on
`YYYYMM`-formatted values (a clean way to diff calendar months without
worrying about day-of-month). `cohort_month_revenue` sums revenue at
each (cohort, relative-month) combination — note this is *already*
correctly aggregated per cohort, since every customer in a cohort
shares the same month-0 reference point. The final query applies a
running total (`SUM(...) OVER (PARTITION BY cohort_month ORDER BY
months_since_first_purchase)`) — the same running-total technique as
Q025, just partitioned by cohort instead of computed globally — then
divides by `cohort_size` to normalize into a per-customer average.

## 8. Validation

- For `months_since_first_purchase = 0`, every cohort's
  `cumulative_avg_revenue_per_customer` should reflect only first-month
  purchases — cross-check this against
  `SUM(first month's line_net_revenue for that cohort) / cohort_size`.
- The value at each successive `months_since_first_purchase` should be
  non-decreasing within a cohort (cumulative revenue can't decrease).
- Pick one small cohort and manually trace a couple of its members'
  orders to confirm the relative-month math.

## 9. Edge Cases

- Cohorts from very late in the dataset (e.g., customers whose first
  purchase was in November or December 2025) can only be observed for
  0 or 1 relative months before the dataset ends — comparing their
  early-month curve against an older cohort's full curve is an
  apples-to-oranges comparison unless explicitly restricted to the same
  relative-month range for all cohorts being compared, exactly the same
  caveat as Q036's trailing-cohort issue.
- A customer with a large single early purchase followed by nothing
  will show a curve that jumps early and then flattens — normal, not a
  bug, and a useful signal in its own right (front-loaded value vs.
  sustained value).

## 10. Alternative Approach

Computing the running total with a self-join (summing all rows with
`months_since_first_purchase <= current`) instead of a window function
would produce the same result at higher cost, and is worth mentioning
only as a way to build intuition for what the window function is doing.

## 11. Trade-offs

Not applicable beyond the running-total implementation choice already
covered elsewhere in this gym (Q025).

## 12. Business Interpretation

This curve is exactly what finance needs to model expected lifetime
revenue for a new customer: if newer cohorts consistently show a
steeper early curve than older ones, that's a positive signal about
recent acquisition or onboarding quality; if the opposite, it's worth
investigating what changed — but always compare cohorts only over the
relative-month range that all of them have actually had time to reach.
