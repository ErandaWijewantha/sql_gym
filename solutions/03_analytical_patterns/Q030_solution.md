# Reasoning

## 1. Interpret the Business Question

Merchandising wants orders that combined a phone purchase with an
accessory purchase in the same basket — a "both X and Y" pattern,
the logical mirror of Q029's "neither/never" pattern.

## 2. Output Grain

One row = one order (restricted to those containing both categories).

## 3. Metric Definition

No numeric metric — a compound existence condition at the order grain.

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id, product_id.
`products`: product_id, category_id.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → for each completed order, determine whether it contains
              any "Mobile Phones" line item
    Step 2 → and whether it contains any "Electronics Accessories" line item
    Step 3 → keep orders where both are true

## 6. Pattern Recognition

"Both X and Y within the same entity" → conditional aggregation
(`SUM(CASE WHEN ... THEN 1 ELSE 0 END)` per category, then `HAVING` both
sums > 0) — one of at least three equally valid structures for this
shape (see Alternative Approaches below).

## 7. SQL — Approach A: Conditional Aggregation

```sql
SELECT
    o.order_id
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p      ON p.product_id = oi.product_id
JOIN categories c     ON c.category_id = p.category_id
WHERE o.order_status = 'completed'
GROUP BY o.order_id
HAVING
    SUM(CASE WHEN c.category_name = 'Mobile Phones' THEN 1 ELSE 0 END) > 0
    AND SUM(CASE WHEN c.category_name = 'Electronics Accessories' THEN 1 ELSE 0 END) > 0;
```

## Approach B: Double EXISTS

```sql
SELECT o.order_id
FROM orders o
WHERE o.order_status = 'completed'
  AND EXISTS (
      SELECT 1 FROM order_items oi
      JOIN products p ON p.product_id = oi.product_id
      JOIN categories c ON c.category_id = p.category_id
      WHERE oi.order_id = o.order_id AND c.category_name = 'Mobile Phones'
  )
  AND EXISTS (
      SELECT 1 FROM order_items oi
      JOIN products p ON p.product_id = oi.product_id
      JOIN categories c ON c.category_id = p.category_id
      WHERE oi.order_id = o.order_id AND c.category_name = 'Electronics Accessories'
  );
```

## 8. Walkthrough

**Approach A** joins order_items/products/categories once, groups by
order, and uses `SUM(CASE WHEN category = X THEN 1 ELSE 0 END) > 0` as
a per-category "does this order contain at least one line item from
category X" flag; `HAVING` requires both flags to be true
simultaneously. **Approach B** instead checks each category
independently via its own correlated `EXISTS` subquery, both filtered
to the same `o.order_id` — conceptually closer to the English "this
order has a phone item, and it also has an accessory item," expressed
as two independent existence proofs rather than one grouped
aggregation.

## 9. Validation

- Both approaches must return the identical set of order_ids — verify
  by comparing result sets directly.
- Pick one resulting order_id and list its full order_items with
  category names to manually confirm both "Mobile Phones" and
  "Electronics Accessories" are present.
- Confirm the result count is meaningfully smaller than the total
  completed order count — if it's a large fraction, double check the
  category name strings for typos (a filter that accidentally matches
  everything is a common silent failure mode).

## 10. Edge Cases

- An order with 5 Mobile Phones line items and 0 Electronics
  Accessories line items correctly does *not* appear — having "a lot"
  of one category doesn't substitute for "at least one" of the other.
- Using `WHERE category_name IN ('Mobile Phones', 'Electronics
  Accessories')` without the `HAVING`/`EXISTS` logic would instead find
  orders containing *either* category (or both) — a fundamentally
  different, broader result that answers a different question ("orders
  touching at least one of these two categories") rather than this
  one ("orders touching both").
- The self-join alternative (see below) requires care to avoid
  matching a line item against itself when both categories happen to
  overlap on the same product (not possible here, since each product
  belongs to exactly one category, but worth being aware of in a
  schema where that isn't guaranteed).

## 11. Alternative Approach: Self-Join

```sql
SELECT DISTINCT oi1.order_id
FROM order_items oi1
JOIN products p1 ON p1.product_id = oi1.product_id
JOIN categories c1 ON c1.category_id = p1.category_id
JOIN order_items oi2 ON oi2.order_id = oi1.order_id
JOIN products p2 ON p2.product_id = oi2.product_id
JOIN categories c2 ON c2.category_id = p2.category_id
JOIN orders o ON o.order_id = oi1.order_id
WHERE o.order_status = 'completed'
  AND c1.category_name = 'Mobile Phones'
  AND c2.category_name = 'Electronics Accessories';
```

This self-joins `order_items` to itself (via two independent alias
chains to `products`/`categories`) matching on `order_id`, so a phone
line item and an accessory line item from the *same* order pair up;
`DISTINCT` collapses cases where an order has multiple qualifying line
items on either side (e.g., 2 phones and 3 accessories would otherwise
produce 6 matching row-pairs for the same order).

## 12. Trade-offs

Approach A (conditional aggregation) is generally the most efficient —
one pass, one group, one HAVING. Approach B (double EXISTS) most
directly mirrors the business language ("has X, and also has Y") and
is easy to extend to a third condition by adding another `EXISTS`. The
self-join version is the least recommended of the three here — it's
more error-prone (the DISTINCT requirement is easy to forget) and
doesn't scale as cleanly if a third category condition were added
later.

## 13. Business Interpretation

A high co-occurrence rate between these two categories validates
merchandising's hunch and directly supports building a bundled
checkout prompt ("customers who bought this phone also added...") —
this query is the measurement step that should precede that product
decision, not replace it.
