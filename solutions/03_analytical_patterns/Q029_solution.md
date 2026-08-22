# Reasoning

## 1. Interpret the Business Question

The Jewelry & Watches team wants existing, purchasing customers who
have simply never bought from this one category — a targeted
cross-sell list, not a "never purchased anything" list (that's Q013).

## 2. Output Grain

One row = one customer.

## 3. Metric Definition

No numeric metric — a compound existence condition: EXISTS a completed
order (any category) AND NOT EXISTS a completed order containing a
Jewelry & Watches product.

## 4. Required Data

`customers`: customer_id.
`orders`: order_id, customer_id, order_status.
`order_items`: order_id, product_id.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → EXISTS: at least one completed order for this customer
    Step 2 → NOT EXISTS: any completed order line item in "Jewelry & Watches"
              for this customer
    Step 3 → combine both as a filter over customers

## 6. Pattern Recognition

"Never did X, where X requires walking through two joins" → `NOT
EXISTS` with a correlated subquery that itself contains the necessary
joins — the anti-join pattern from Q013, extended to a multi-hop
condition instead of a single-table match.

## 7. SQL

```sql
SELECT
    c.customer_id,
    c.customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.order_status = 'completed'
)
AND NOT EXISTS (
    SELECT 1
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p      ON p.product_id = oi.product_id
    JOIN categories cat   ON cat.category_id = p.category_id
    WHERE o.customer_id = c.customer_id
      AND o.order_status = 'completed'
      AND cat.category_name = 'Jewelry & Watches'
);
```

## 8. Walkthrough

The first `EXISTS` clause is a straightforward correlated existence
check: does at least one completed order exist for this customer? The
second, `NOT EXISTS`, runs a full mini-query per customer — join
through order_items, products, and categories, filtered to this
customer's completed orders and the specific category — and requires
that *no* row satisfies it. Both conditions are correlated to the
outer `customers` row via `c.customer_id`, and MySQL only needs to find
one matching row to short-circuit an `EXISTS` (or confirm zero rows to
satisfy `NOT EXISTS`), which is why this pattern is typically efficient
even though it "looks" like nested full scans.

## 9. Validation

- Pick one resulting customer_id: run
  `SELECT DISTINCT cat.category_name FROM orders o JOIN order_items oi
  ON ... JOIN products p ON ... JOIN categories cat ON ... WHERE
  o.customer_id = <id> AND o.order_status='completed'` and confirm
  "Jewelry & Watches" never appears in that list, while the list is
  non-empty (proving they've bought *something*).
- The result should be a strict subset of "customers with >=1 completed
  order" (Q010's population) — never include a customer with zero
  orders at all.

## 10. Edge Cases

- Putting the category filter inside a `LEFT JOIN`'s `ON` clause with a
  `WHERE ... IS NULL` afterward (rather than as a correlated `NOT
  EXISTS`) is a common but risky alternative: if the category filter
  is accidentally placed in `WHERE` instead of `ON`, the `LEFT JOIN`
  effectively becomes an `INNER JOIN` (since `WHERE` discards the
  NULL-extended non-matching rows before the "no match" logic ever
  applies) — a classic mistake covered in `docs/common_mistakes.md`
  under "LEFT JOIN becoming INNER JOIN."
- A customer whose *only* completed order contains both a Jewelry &
  Watches item and other items is still correctly excluded — the
  `NOT EXISTS` subquery finds a match (the Jewelry & Watches line item)
  regardless of what else is in that order.

## 11. Alternative Approach

```sql
SELECT c.customer_id, c.customer_name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
LEFT JOIN (
    SELECT DISTINCT o2.customer_id
    FROM orders o2
    JOIN order_items oi ON oi.order_id = o2.order_id
    JOIN products p ON p.product_id = oi.product_id
    JOIN categories cat ON cat.category_id = p.category_id
    WHERE o2.order_status = 'completed' AND cat.category_name = 'Jewelry & Watches'
) jewelry_buyers ON jewelry_buyers.customer_id = c.customer_id
WHERE jewelry_buyers.customer_id IS NULL
GROUP BY c.customer_id, c.customer_name;
```

Here, the category-restricted subquery is pre-computed as a *derived
table* of known Jewelry & Watches buyers, then anti-joined via `LEFT
JOIN`/`IS NULL` — functionally equivalent to the `NOT EXISTS` version,
and arguably easier to read for someone who prefers thinking in terms
of "a list of people to exclude" rather than a per-row existence check.
Note the `GROUP BY` here is necessary because the join to `orders` can
still produce multiple rows per customer.

## 12. Trade-offs

The `NOT EXISTS` version is more compact and avoids the extra `GROUP
BY` cleanup; the derived-table version makes the "list of people to
exclude" concept more explicit and may be easier to unit-test or reuse
elsewhere. Both are correct and reasonably efficient at this data
volume.

## 13. Business Interpretation

This is a precise cross-sell audience: proven purchasers (so payment
and delivery friction is a known non-issue) who simply haven't been
exposed to or convinced by the Jewelry & Watches category yet.
