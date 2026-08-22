# Reasoning

## 1. Interpret the Business Question

Leadership wants a single ranked list of all stores by revenue, with
correct, business-meaningful behavior if any two stores are exactly
tied.

## 2. Output Grain

One row = one store.

## 3. Metric Definition

Total net revenue (completed orders): `SUM(quantity*unit_price -
discount_amount)` per store.

## 4. Required Data

`orders`: order_id, store_id, order_status.
`order_items`: order_id, quantity, unit_price, discount_amount.
`stores`: store_id, store_name.

## 5. Logical Decomposition

    Step 1 → compute net revenue per store (completed orders)
    Step 2 → RANK() and DENSE_RANK() over that revenue, descending
    Step 3 → compare the two side by side

## 6. Pattern Recognition

"Rank rows, and ties matter" → `RANK()` vs `DENSE_RANK()`. Both assign
the same rank to tied rows; they differ only in what happens to the
*next distinct value* after a tie. `ROW_NUMBER()` is the wrong tool
whenever ties are meaningful, since it always assigns distinct
sequential numbers even to identical values.

## 7. SQL

```sql
WITH store_revenue AS (
    SELECT
        s.store_id,
        s.store_name,
        SUM(oi.quantity * oi.unit_price - oi.discount_amount) AS net_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN stores s       ON s.store_id  = o.store_id
    WHERE o.order_status = 'completed'
    GROUP BY s.store_id, s.store_name
)
SELECT
    store_name,
    net_revenue,
    RANK()       OVER (ORDER BY net_revenue DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY net_revenue DESC) AS rank_no_gaps
FROM store_revenue
ORDER BY net_revenue DESC;
```

## 8. Walkthrough

If two stores tie for 2nd place, `RANK()` gives both of them rank 2 and
then skips to rank 4 for the next store (because 2 rows already
"occupied" ranks 2 and 3) — this is the "1, 2, 2, 4" behavior. `
DENSE_RANK()` also gives both tied stores rank 2, but the next store
gets rank 3, with no gap — "1, 2, 2, 3". Neither is more "correct" in
the abstract; the right choice depends on whether "there are 4 stores
ranked above 5th place" (RANK, matches ordinal position) or "there are
3 distinct revenue tiers above this one" (DENSE_RANK, matches distinct
value tiers) is the intended meaning.

## 9. Validation

- Check for actual ties in this dataset:
  `SELECT net_revenue, COUNT(*) FROM store_revenue GROUP BY net_revenue
  HAVING COUNT(*) > 1` — with continuous LKR totals across 35 stores,
  an exact tie is unlikely but not impossible; if none exist, `RANK()`
  and `DENSE_RANK()` will produce identical output here, and the
  distinction should be verified conceptually rather than empirically.
- Confirm rank 1 always corresponds to the single highest `net_revenue`
  value under both functions.

## 10. Edge Cases

- If leadership wants "no ties, ever — break by store_id for a stable
  ordering," `ROW_NUMBER() OVER (ORDER BY net_revenue DESC, store_id)`
  is the right tool, deliberately sacrificing tie-awareness for a
  strict 1-to-1 mapping between rows and rank numbers.
- A store with zero completed orders wouldn't appear in `store_revenue`
  at all (INNER JOIN requires a match) — if leadership wants
  underperforming/zero-revenue stores to appear ranked last, a `LEFT
  JOIN` from `stores` with `COALESCE(net_revenue, 0)` would be needed
  instead.

## 11. Alternative Approach

Not applicable beyond the three ranking functions already compared —
this question exists specifically to contrast them.

## 12. Trade-offs

`RANK()` and `DENSE_RANK()` cost nothing extra over `ROW_NUMBER()`
computationally; the choice is purely about what "rank" should mean to
the business, and that's worth pinning down explicitly rather than
defaulting to whichever function is most familiar.

## 13. Business Interpretation

For a leadership deck, `DENSE_RANK()` usually reads more naturally
("3rd-highest-revenue tier") while `RANK()` better answers "how many
stores are ahead of this one" — pick based on which sentence the deck
actually needs to support.
