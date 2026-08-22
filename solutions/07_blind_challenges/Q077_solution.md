# Reasoning

## 1. Interpret the Business Question

Find the single busiest hour-of-day for online orders, and separately
for in-store orders.

## 2. Output Grain

One row per sales_channel (its single busiest hour).

## 3. Metric Definition

`HOUR(order_date)` extracts the hour (0-23); count orders per (channel,
hour), then take the top hour per channel.

## 4. Required Data

`orders`: sales_channel, order_date.

## 5. SQL

```sql
WITH hourly_counts AS (
    SELECT
        sales_channel,
        HOUR(order_date) AS order_hour,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY sales_channel, HOUR(order_date)
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY sales_channel ORDER BY order_count DESC) AS rn
    FROM hourly_counts
)
SELECT sales_channel, order_hour, order_count
FROM ranked
WHERE rn = 1;
```

## 6. Walkthrough

`hourly_counts` buckets every order by its channel and hour-of-day (via
`HOUR()`, which works directly on the `DATETIME` column). `ranked` then
picks the single top hour per channel using the same top-N-per-group
pattern as Q021/Q066, here with only 1 kept per group instead of 3 or
5.

## 7. Validation

- Manually list the top 3-4 hours per channel and confirm the returned
  hour genuinely has the highest count among them.
- Sanity check against the data generator's design: in-store orders
  were generated within business hours (9am-9pm), so the busiest
  in-store hour should fall within that range; online orders were
  generated across all 24 hours uniformly, so the busiest online hour
  is closer to a tie among many hours and may look less pronounced.

## 8. Edge Cases

- If two hours are exactly tied for busiest within a channel,
  `ROW_NUMBER()` arbitrarily picks one — `RANK()` would surface both
  ties instead, worth using if the business cares about seeing ties.
- In-store order times were generated uniformly within 9am-9pm in this
  dataset, meaning the "busiest hour" among in-store orders may be only
  marginally ahead of its neighbors rather than a sharp peak — worth
  showing the full hourly distribution rather than just the single top
  hour if operations wants to plan shift coverage across the whole day.

## 9. Alternative Approach

Showing the full 24-hour distribution per channel (dropping the
`ranked`/`WHERE rn=1` step entirely) gives operations a complete
staffing curve rather than just a single peak hour — likely more
useful in practice for actual shift planning.

## 10. Trade-offs

A single peak-hour answer directly satisfies the literal question; the
full-distribution version is more useful operationally but isn't what
was strictly asked.

## 11. Business Interpretation

The in-store peak hour should inform in-store staffing shift timing;
the online peak hour (if any meaningful peak exists at all, given the
uniform generation) should inform site reliability/capacity planning
and customer support staffing for the online channel.
