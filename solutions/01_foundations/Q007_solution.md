# Reasoning

## 1. Interpret the Business Question

Regional operations wants regions where the *existing customer base* is
already large — this is about registered customers, not purchasing
behavior.

## 2. Output Grain

One row = one region (including, potentially, a "NULL region" group).

## 3. Metric Definition

A plain count of customers per region, regardless of whether they've
ever ordered anything.

## 4. Required Data

`customers`: region.

## 5. Logical Decomposition

    Step 1 → GROUP BY region
    Step 2 → COUNT(*) per group
    Step 3 → HAVING COUNT(*) > 500

## 6. Pattern Recognition

Same "aggregate, then filter on the aggregate" shape as Q006, but here
on a dimension table directly rather than through a fact-table join.

## 7. SQL

```sql
SELECT
    region,
    COUNT(*) AS customer_count
FROM customers
GROUP BY region
HAVING COUNT(*) > 500
ORDER BY customer_count DESC;
```

## 8. Walkthrough

`GROUP BY region` buckets all 12,000 customers by their region value —
including a bucket for `NULL`, since MySQL treats `NULL` as its own
group in `GROUP BY` rather than discarding those rows. `HAVING` then
keeps only regions whose customer count exceeds 500.

## 9. Validation

- Sum of `customer_count` across the *unfiltered* query (no HAVING)
  should equal `SELECT COUNT(*) FROM customers` (12,000).
- If a `NULL` region row appears in the filtered output, decide
  deliberately whether that's meaningful (e.g., "unknown region, but
  still a large enough group to matter operationally") or whether it
  should be excluded with `WHERE region IS NOT NULL` before grouping.

## 10. Edge Cases

- `~2%` of customers have `NULL` city/region by construction (a
  deliberately missing-demographics edge case) — with 12,000 customers
  that's on the order of ~200-250 rows, likely *below* the 500
  threshold and thus naturally excluded here, but this shouldn't be
  assumed without checking.
- This count includes customers who have *never placed an order* — if
  regional operations actually meant "customers we're currently
  serving" (i.e., with order history), this query overstates the base
  and a JOIN to `orders` (with `NOT EXISTS`/`EXISTS` reasoning, Level 3)
  would be needed instead.

## 11. Alternative Approach

`WHERE region IS NOT NULL` before the `GROUP BY` is a legitimate
variant if the business explicitly doesn't want an "unknown region"
bucket surfaced at all; the choice changes the *meaning* of the
output, not just its syntax, so it should be a deliberate decision.

## 12. Trade-offs

Not applicable beyond the NULL-handling decision above.

## 13. Business Interpretation

This identifies regions with enough existing registered customers to
justify a physical support desk, purely by headcount — it says nothing
yet about whether those customers are actually active, which is exactly
the gap Level 4's recency/frequency questions exist to close.
