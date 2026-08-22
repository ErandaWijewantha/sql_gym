# Reasoning

## 1. Interpret the Business Question

For each return_reason, what share of returns happen quickly (within 7
days of the order) versus later — testing QA's hypothesis that quick
returns and late returns have different underlying causes.

## 2. Output Grain

One row = one return_reason.

## 3. Metric Definition

`days_to_return = DATEDIFF(return_date, order_date)`. `fast_return =
days_to_return <= 7`.

## 4. Required Data

`returns`: order_id, return_date, return_reason.
`orders`: order_id, order_date.

## 5. SQL

```sql
SELECT
    r.return_reason,
    COUNT(*) AS total_returns,
    SUM(DATEDIFF(r.return_date, o.order_date) <= 7) AS fast_returns,
    ROUND(SUM(DATEDIFF(r.return_date, o.order_date) <= 7) * 100.0 / COUNT(*), 1) AS fast_return_pct
FROM returns r
JOIN orders o ON o.order_id = r.order_id
GROUP BY r.return_reason
ORDER BY fast_return_pct DESC;
```

## 6. Walkthrough

Joining `returns` to `orders` recovers each return's `order_date`,
letting `DATEDIFF` compute how long after the order the return
happened. The conditional sum counts how many of each reason's returns
fell within the 7-day window; dividing by the total gives the
percentage.

## 7. Validation

- Manually verify one return's day-gap and whether it's correctly
  classified as fast/slow.
- Confirm `fast_returns <= total_returns` for every reason.

## 8. Edge Cases

- `return_date` in this dataset is always constructed to be 1-45 days
  after the order date (per the data generator), so every return has a
  meaningful, positive day-gap — no same-day or negative-gap edge cases
  to worry about here.
- A reason with very few total returns produces a noisier percentage —
  worth checking `total_returns` isn't tiny before over-interpreting a
  100% or 0% fast-return rate for a rare reason.

## 9. Alternative Approach

A finer-grained bucketing (e.g., 0-3 days, 4-7 days, 8-14 days, 15+
days) instead of a single 7-day cutoff would reveal more shape in the
distribution per reason, at the cost of a less immediately-scannable
single percentage.

## 10. Trade-offs

A single threshold is easy to communicate; a multi-bucket histogram is
more informative but requires a chart rather than one number per row.

## 11. Business Interpretation

If "Defective" and "Wrong Item Delivered" skew heavily toward fast
returns while "No Longer Needed" and "Found Cheaper Elsewhere" skew
toward later returns, that confirms QA's hypothesis and supports
treating fast returns as a quality/fulfillment signal worth monitoring
separately from slower, preference-driven returns.
