# Reasoning

## 1. Interpret the Business Question

Marketing wants the customer base split into two behaviorally distinct
groups: those who bought exactly once, and those who came back at
least one more time — using *all* orders (any status), since this is
about engagement/behavior, not confirmed revenue.

## 2. Output Grain

The intermediate grain is one row per customer; the final output grain
is one row per segment ("one-time" / "repeat").

## 3. Metric Definition

`order_count = COUNT(*)` per customer from `orders`; segment =
"one-time" if `order_count = 1`, else "repeat".

## 4. Required Data

`orders`: customer_id, order_id.

## 5. Logical Decomposition

    Step 1 → count orders per customer
    Step 2 → classify each customer as one-time or repeat
    Step 3 → GROUP BY that classification, COUNT customers, compute percentage

## 6. Pattern Recognition

Same two-stage "tag, then summarize" shape as Q003's price tiers,
applied to a customer-level aggregate instead of a raw product
attribute.

## 7. SQL — Approach A: CTE

```sql
WITH customer_order_counts AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
),
classified AS (
    SELECT
        customer_id,
        CASE WHEN order_count = 1 THEN 'one-time' ELSE 'repeat' END AS segment
    FROM customer_order_counts
)
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_purchasers
FROM classified
GROUP BY segment;
```

## Approach B: Window Function (no intermediate customer-grain collapse until the end)

```sql
SELECT DISTINCT
    segment,
    COUNT(*) OVER (PARTITION BY segment) AS customer_count,
    ROUND(COUNT(*) OVER (PARTITION BY segment) * 100.0 / COUNT(*) OVER (), 1) AS pct_of_purchasers
FROM (
    SELECT
        customer_id,
        CASE WHEN COUNT(*) OVER (PARTITION BY customer_id) = 1 THEN 'one-time' ELSE 'repeat' END AS segment
    FROM orders
) t;
```

## 8. Walkthrough

**Approach A** is the straightforward path: count orders per customer,
classify, then aggregate the classification. The final percentage uses
`SUM(COUNT(*)) OVER ()` — a window `SUM` over the already-grouped
`segment` counts — to divide each segment's count by the grand total
without a second query pass. **Approach B** instead computes
`COUNT(*) OVER (PARTITION BY customer_id)` directly on the raw `orders`
rows (no `GROUP BY` needed to get a per-customer count — the window
function gives every order row its own customer's total order count),
classifies each row, and then uses `COUNT(*) OVER (PARTITION BY
segment)` on top of that — hence needing `DISTINCT` at the very end to
collapse back down to one row per segment, since the inner subquery is
still at order grain.

## 9. Validation

- Both approaches must produce identical `customer_count` values per
  segment.
- The two `customer_count` values should sum to the total number of
  customers with >= 1 order (Q010/Q031's population).
- Given the data generator's archetype weights (4% zero, 28% one_time,
  33% occasional, 25% regular, 10% vip — all among *all* 12,000
  customers), roughly 28/96 ≈ 29% of *purchasing* customers should land
  in "one-time," with the rest in "repeat." Confirm the result is in
  that ballpark.

## 10. Edge Cases

- This uses all orders regardless of status — a customer with one
  completed order and one cancelled order still counts as "repeat"
  under this definition (2 orders placed), even though only 1 ever
  became real revenue. If marketing actually meant "repeat purchaser"
  in a revenue sense, the `order_count` should be computed only over
  completed orders instead — a definitional choice worth surfacing
  explicitly, echoing Level 5's theme.
- Customers with zero orders are excluded from this population by
  construction (they never appear in `orders` at all), consistent with
  the question's "purchasing customer" framing.

## 11. Alternative Approach

See section 7 — both are shown as co-equal alternatives for this
exercise.

## 12. Trade-offs

Approach A is more readable and is the natural default for most teams.
Approach B avoids an explicit `GROUP BY customer_id` step but requires
a `DISTINCT` cleanup at the end and is arguably harder to follow for a
reader unfamiliar with stacking multiple window functions at different
partition levels in one query — mostly useful as a demonstration that
window functions *can* replace a GROUP BY entirely, not because it's
clearer here.

## 13. Business Interpretation

A large one-time-customer share signals an acquisition-heavy,
retention-weak business — worth investigating whether onboarding,
product-market fit, or a lack of a second-purchase incentive is the
bottleneck, a question Level 5 and Level 6 dig into further.
