# Reasoning

## 1. Interpret the Business Question

Customer success wants a per-customer snapshot of recency, but scoped
only to customers who have actually purchased before — this is the
foundational building block for every recency question in Level 4.

## 2. Output Grain

One row = one customer (restricted to customers with >= 1 order).

## 3. Metric Definition

`MAX(order_date)` per customer — the most recent order timestamp,
regardless of that order's status (a cancelled or refunded order still
represents the last time the customer *interacted* with placing an
order, which is what "recency" usually means unless stated otherwise).

## 4. Required Data

`customers`: customer_id, customer_name.
`orders`: customer_id, order_date.

## 5. Logical Decomposition

    Step 1 → join customers to orders on customer_id
    Step 2 → GROUP BY customer_id (and any customer attributes selected)
    Step 3 → MAX(order_date) per group

## 6. Pattern Recognition

"Most recent event per entity" → `GROUP BY` + `MAX()`. This is the
simplest form of a recurring shape in this gym: collapsing a one-to-many
relationship (customer → orders) down to one summary row per "one" side.

## 7. SQL

```sql
SELECT
    c.customer_id,
    c.customer_name,
    MAX(o.order_date) AS last_order_date
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name;
```

## 8. Walkthrough

The `JOIN` (not `LEFT JOIN`) between customers and orders means a
customer contributes rows to the result only if they have at least one
matching order — which is exactly what "who has placed at least one
order" requires. `GROUP BY customer_id` (with `customer_name` added
since it's functionally dependent on `customer_id`, MySQL allows
including it) collapses all of that customer's orders into a single
row, and `MAX(order_date)` picks the latest one.

## 9. Validation

- Row count of this result should be noticeably less than 12,000 (the
  full customer table) — roughly matching (1 - zero_order_archetype
  fraction), i.e., a bit under 96% of all customers, since ~4% of
  customers are constructed to have zero orders.
- Spot check one customer: run
  `SELECT order_date FROM orders WHERE customer_id = <id> ORDER BY order_date DESC LIMIT 1`
  and confirm it matches the `last_order_date` in this result.
- No `last_order_date` should ever be `NULL` in this result, since the
  INNER JOIN guarantees at least one order exists.

## 10. Edge Cases

- **Customers with zero orders are silently excluded** by the INNER
  JOIN — correct for this question's wording, but if the business
  instead wanted *all* customers (with `NULL` shown for those with no
  orders), a `LEFT JOIN` would be required instead. That's precisely
  the distinction Level 2's Q013 makes explicit: the choice of JOIN
  type *is* the answer to a different (but easily confused) question.
- Multiple orders on the same calendar date for one customer don't
  cause any issue — `MAX()` over a `DATETIME` column still correctly
  picks the single latest timestamp even if several orders share the
  same date.

## 11. Alternative Approach

A correlated subquery per customer (`SELECT MAX(order_date) FROM orders
o WHERE o.customer_id = c.customer_id`) in the SELECT list would produce
the same result without collapsing via `GROUP BY`, but re-executes the
subquery per customer row and is less idiomatic for this shape — prefer
the `JOIN` + `GROUP BY` form.

## 12. Trade-offs

The `JOIN` + `GROUP BY` form is standard, index-friendly (via
`idx_orders_customer_date`), and reads naturally. The correlated
subquery form becomes preferable only in narrower contexts, like
needing the max alongside *unaggregated* per-order columns in the same
row (a job better suited to a window function — see Level 3).

## 13. Business Interpretation

This is the raw material for a recency dashboard: customer success can
now compute "days since last order" for every purchasing customer, and
in Level 4 this same shape gets extended into dormancy detection,
reactivation, and churn signals.
