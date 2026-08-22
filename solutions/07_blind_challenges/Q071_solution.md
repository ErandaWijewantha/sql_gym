# Reasoning

## 1. Interpret the Business Question

Among Premium-segment customers' high/urgent tickets, find the most
common issue_type.

## 2. Output Grain

One row per issue_type (or just the single top one, depending on
presentation preference — this solution shows the full ranked list).

## 3. Metric Definition

Simple count of tickets, filtered to `priority IN ('high', 'urgent')`
and `customer_segment = 'Premium'`.

## 4. Required Data

`support_tickets`: customer_id, priority, issue_type.
`customers`: customer_id, customer_segment.

## 5. SQL

```sql
SELECT
    st.issue_type,
    COUNT(*) AS ticket_count
FROM support_tickets st
JOIN customers c ON c.customer_id = st.customer_id
WHERE st.priority IN ('high', 'urgent')
  AND c.customer_segment = 'Premium'
GROUP BY st.issue_type
ORDER BY ticket_count DESC;
```

## 6. Walkthrough

A single many-to-one join (`support_tickets` to `customers`) attaches
segment without any fan-out risk (`customers` is the "one" side).
`WHERE` filters to the relevant priority levels and segment before
grouping by `issue_type` and counting.

## 7. Validation

- Confirm every row satisfies both filter conditions.
- Cross-check the top result's count against a direct manual filter and
  count for that specific issue_type.

## 8. Edge Cases

- `priority IN ('high', 'urgent')` treats these as one combined
  population — if the business actually wants them reported
  separately (a high-priority billing issue might need a different
  response than an urgent one), add `priority` to the `GROUP BY` and
  `SELECT` list instead of combining them.
- A ticket with a `NULL` or unexpected `issue_type` would form its own
  (or a NULL) group — worth checking the ENUM/allowed values don't
  contain surprises.

## 9. Alternative Approach

Reporting `priority` and `issue_type` together (rather than combining
`high`/`urgent`) gives a more granular breakdown — a simple change to
the `GROUP BY`/`SELECT` list, worth considering if support wants to
distinguish urgency levels rather than treat them as one bucket.

## 10. Trade-offs

Combining high/urgent gives a larger, more stable sample per
issue_type; splitting them gives more precision at the cost of smaller,
noisier per-group counts.

## 11. Business Interpretation

The top issue_type here tells support exactly what's driving urgent
complaints from the highest-value customer tier — the natural next step
is drilling into a sample of those specific tickets to understand root
cause, not just the category label.
