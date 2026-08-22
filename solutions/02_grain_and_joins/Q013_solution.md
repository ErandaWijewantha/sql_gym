# Reasoning

## 1. Interpret the Business Question

Marketing wants exactly the complement of Q010's result: customers with
zero order history at all, for a win-back-style campaign — though
here it's actually a "first purchase incentive," since these customers
have never bought anything to begin with.

## 2. Output Grain

One row = one customer (restricted to those with zero orders).

## 3. Metric Definition

No metric — a filtered list, but the filter condition ("no matching
row in another table") requires a specific join pattern to express.

## 4. Required Data

`customers`: customer_id, customer_name, registration_date,
acquisition_channel.
`orders`: customer_id.

## 5. Logical Decomposition

    Step 1 → LEFT JOIN customers to orders on customer_id
    Step 2 → keep only rows where the orders side is NULL (no match)
    Step 3 → select the relevant customer columns

## 6. Pattern Recognition

"Customers who never did X" → anti-join, expressed here via `LEFT JOIN
... WHERE <child>.<key> IS NULL`. This is the LEFT JOIN / IS NULL form
of the anti-join; Level 3's Q029 revisits the same shape using
`NOT EXISTS`, and the approach-selection exercise AS02 compares all
three common forms (`LEFT JOIN`/`IS NULL`, `NOT EXISTS`, `NOT IN`)
directly.

## 7. SQL

```sql
SELECT
    c.customer_id,
    c.customer_name,
    c.registration_date,
    c.acquisition_channel
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;
```

## 8. Walkthrough

`LEFT JOIN` keeps every row from `customers` regardless of whether a
matching order exists; for customers with no orders, every column
pulled from `orders` (including `order_id`) comes back as `NULL`.
Filtering on `o.order_id IS NULL` afterward isolates exactly those
"no match" customers. `order_id` is chosen deliberately because it's
`orders`' primary key and can never be NULL in a real matched row —
so seeing `NULL` there unambiguously means "no match," which is safer
than testing a nullable column.

## 9. Validation

- The result count plus Q010's result count should equal 12,000 (total
  customers) — this dataset was constructed so ~4% of customers
  (the `zero` archetype) have no orders, so expect roughly 400-500 rows.
- Spot check one returned customer_id: confirm
  `SELECT COUNT(*) FROM orders WHERE customer_id = <id>` returns 0.

## 10. Edge Cases

- Filtering on `c.registration_date IS NULL` or any customer-side
  column instead of an orders-side column would be simply wrong — it
  has nothing to do with whether a matching order exists, and would
  instead (incorrectly) filter on that customer's own NULL demographic
  data.
- Using `WHERE customer_id NOT IN (SELECT customer_id FROM orders)`
  looks equivalent but has a well-known trap: if the subquery's result
  ever contains a NULL `customer_id` (not possible here, since
  `orders.customer_id` is `NOT NULL`, but a real risk in less
  constrained schemas), `NOT IN` silently returns zero rows for
  *everyone*, because `x NOT IN (a, b, NULL)` evaluates to `UNKNOWN`,
  not `TRUE`, for any `x`. `LEFT JOIN`/`IS NULL` and `NOT EXISTS` don't
  have this failure mode.
- This question is about "no orders at all," not "no *completed*
  orders" — a customer whose only order was cancelled still has an
  order_id and would correctly be excluded from this result.

## 11. Alternative Approach

```sql
SELECT
    c.customer_id, c.customer_name, c.registration_date, c.acquisition_channel
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
```

`NOT EXISTS` expresses the same intent more directly ("no order exists
for this customer") and is immune to the `NOT IN`/NULL trap since it
never materializes the subquery's values for comparison — it just
checks existence per row.

## 12. Trade-offs

`LEFT JOIN`/`IS NULL` and `NOT EXISTS` typically produce identical
query plans in MySQL 8 and are both safe; `NOT EXISTS` more directly
communicates intent to a reader ("prove no such row exists") while
`LEFT JOIN`/`IS NULL` is often more familiar to SQL beginners. `NOT IN`
should generally be avoided for this pattern unless the subquery column
is provably `NOT NULL`.

## 13. Business Interpretation

This is a genuinely different audience from Q041's "win-back" targets
(who *did* buy before and went quiet) — these customers have never
converted at all, so the right lever is a first-purchase incentive, not
a reactivation message.
