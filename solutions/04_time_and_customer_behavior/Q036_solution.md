# Reasoning

## 1. Interpret the Business Question

Growth wants classic month-1 cohort retention: group customers by their
registration month, and measure what fraction of each cohort came back
to order in the very next calendar month.

## 2. Output Grain

One row = one registration-month cohort.

## 3. Metric Definition

`retention_pct = (customers in cohort who ordered in registration_month
+ 1) / (all customers in that cohort) * 100`. The denominator includes
every registrant, whether or not they ever ordered at all.

## 4. Required Data

`customers`: customer_id, registration_date.
`orders`: customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → compute each customer's registration month (truncated to month)
    Step 2 → compute, per customer, whether they have any order in the
              calendar month immediately following their registration month
    Step 3 → GROUP BY registration month: count total cohort members and
              count of "retained" members
    Step 4 → retention_pct = retained / total * 100

## 6. Pattern Recognition

"Cohort retention" → bucket entities by a *starting* time dimension
(here, registration month), then measure presence/absence in a
*derived, relative* time window (registration month + 1) for each
entity, then aggregate to a per-cohort rate. The relative-window
computation is the part that differs from a simple fixed-date anti-join
like Q035.

## 7. SQL

```sql
WITH cohort AS (
    SELECT
        customer_id,
        DATE_FORMAT(registration_date, '%Y-%m-01') AS cohort_month
    FROM customers
),
retained_flag AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        EXISTS (
            SELECT 1 FROM orders o
            WHERE o.customer_id = c.customer_id
              AND o.order_date >= DATE_ADD(c.cohort_month, INTERVAL 1 MONTH)
              AND o.order_date <  DATE_ADD(c.cohort_month, INTERVAL 2 MONTH)
        ) AS retained
    FROM cohort c
)
SELECT
    cohort_month,
    COUNT(*) AS cohort_size,
    SUM(retained) AS retained_count,
    ROUND(SUM(retained) * 100.0 / COUNT(*), 1) AS retention_pct
FROM retained_flag
GROUP BY cohort_month
ORDER BY cohort_month;
```

## 8. Walkthrough

`cohort` truncates every customer's `registration_date` to the first
of its month. `retained_flag` then checks, per customer, whether an
order exists strictly within the calendar month right after their own
cohort month — `DATE_ADD(c.cohort_month, INTERVAL 1 MONTH)` to
`DATE_ADD(c.cohort_month, INTERVAL 2 MONTH)` (a half-open range,
correctly handling any day-of-month registration). `EXISTS` returns a
boolean per customer, which MySQL happily treats as 1/0 when placed
inside `SUM()`. The final `GROUP BY cohort_month` then produces one row
per cohort with both the raw counts and the derived percentage.

## 9. Validation

- `cohort_size` summed across every cohort_month should equal 12,000
  (total customers).
- For one cohort, manually list a few of its members and check their
  orders directly against the following month's date range.
- The very last cohort_month(s) close to the dataset's end will have an
  incomplete or entirely unobservable "month + 1" window — see Edge
  Cases.

## 10. Edge Cases

- Customers who registered in **November or December 2025** have a
  "month + 1" window that falls partially or entirely **after the
  dataset's end (2025-12-31)** — for December 2025 registrants, the
  entire "month + 1" window (January 2026) doesn't exist in the data at
  all, so `retained` will always be `false` for that cohort, not
  because they didn't come back, but because there's no data to
  observe. **These trailing cohorts should be excluded or clearly
  footnoted**, not compared at face value against earlier, fully
  observable cohorts.
- A customer with a `NULL` region or other demographic field is
  unaffected here — cohort membership depends only on
  `registration_date`, which is `NOT NULL` for every customer.
- This measures "ordered at all" in month+1, regardless of order
  status — a cancelled order still counts as returning/engaging, which
  is arguably the right call for a *retention* (as opposed to revenue)
  metric.

## 11. Alternative Approach

A single query using conditional aggregation instead of a correlated
`EXISTS` — join `customers` to `orders` with the date condition baked
into the `ON` clause, then use `COUNT(DISTINCT ...)` — can express the
same computation, but correctly handling "0 for customers with no
matching order" requires care with `LEFT JOIN` semantics; the `EXISTS`
version above is more directly readable for this particular shape.

## 12. Trade-offs

The correlated-subquery (`EXISTS`) version is simple to reason about
per customer but does one subquery execution per customer row; for
12,000 customers this is entirely fine, but at far larger scale a
set-based `LEFT JOIN` + date-range approach would be worth revisiting
for performance.

## 13. Business Interpretation

A declining retention_pct across successive cohorts would suggest
something about the *acquisition* or *onboarding* experience is
degrading over time (not a demand problem, since these customers did
register) — exactly the kind of signal growth needs to catch early,
with the crucial caveat that the most recent 1-2 cohorts are not yet
fully observable and shouldn't be judged the same way.
