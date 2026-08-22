# AS02 — Solution

## Approach A — NOT EXISTS

```sql
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id AND o.order_status = 'completed'
)
AND NOT EXISTS (
    SELECT 1 FROM orders o
    JOIN returns r ON r.order_id = o.order_id
    WHERE o.customer_id = c.customer_id
);
```

## Approach B — LEFT JOIN + IS NULL

```sql
SELECT c.customer_id, c.customer_name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id AND o.order_status = 'completed'
LEFT JOIN returns r ON r.order_id = o.order_id
GROUP BY c.customer_id, c.customer_name
HAVING SUM(r.return_id IS NOT NULL) = 0;
```

## Approach C — NOT IN

```sql
SELECT c.customer_id, c.customer_name
FROM customers c
WHERE c.customer_id IN (SELECT customer_id FROM orders WHERE order_status = 'completed')
  AND c.customer_id NOT IN (
      SELECT o.customer_id FROM orders o JOIN returns r ON r.order_id = o.order_id
  );
```

## Comparison

1. **Zero-order customers**: Approach A's first `EXISTS` clause
   correctly excludes them (they fail the "has ordered" check).
   Approach B's inner `JOIN` to `orders` (not `LEFT JOIN`) also excludes
   them naturally. Approach C's first `IN` condition excludes them too.
   All three handle this correctly.
2. **The NOT IN / NULL trap**: if the subquery in Approach C's `NOT IN`
   clause (`SELECT o.customer_id FROM orders o JOIN returns r ...`)
   could ever produce a NULL `customer_id` value — not possible here
   since `orders.customer_id` is `NOT NULL`, but a real risk if this
   pattern were reused against a differently-constrained table — `NOT
   IN` against a list containing even one NULL returns **no rows at
   all**, for every single outer row, silently. This is because `x NOT
   IN (a, NULL)` evaluates to `UNKNOWN` (treated as not-true) rather
   than `TRUE`, regardless of what `x` and `a` are. Neither `NOT EXISTS`
   (Approach A) nor `LEFT JOIN`/`IS NULL` (Approach B) has this failure
   mode, since neither ever compares the outer value against a
   materialized list of values.
3. **Safety for reuse**: Approach A or B — both are immune to the NULL
   trap regardless of future schema changes.

## Recommendation

**Approach A (NOT EXISTS)** is the clearest expression of intent here
("no return exists for this customer's orders") and is immune to the
NULL trap. **Approach B** is equally safe and may be more familiar to
teams that reach for `LEFT JOIN`/`IS NULL` as their default anti-join
idiom, at the cost of needing a `GROUP BY`/`HAVING` step that A doesn't
need. **Approach C (NOT IN)** should be avoided for this pattern as a
default habit — even when the current schema happens to make it safe,
reusing the same query shape against a table where the subquery column
*can* be NULL is a realistic, easy-to-miss way to introduce a silent
bug later.
