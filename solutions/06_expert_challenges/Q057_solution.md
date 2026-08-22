# Reasoning

## 1. Interpret the Business Question

Merchandising wants genuine co-purchase pairs — products that show up
together in the same order — ranked by how often that happens, for a
"customers also bought" feature.

## 2. Output Grain

One row = one unordered pair of distinct products, limited to the top
10 by co-occurrence count.

## 3. Metric Definition

`pair_count` = number of distinct completed orders in which both
products of the pair appear as line items.

## 4. Required Data

`orders`: order_id, order_status.
`order_items`: order_id, product_id.

## 5. Logical Decomposition

    Step 1 → self-join order_items to itself on matching order_id
    Step 2 → enforce product_id_1 < product_id_2 to avoid double-counting
              (A,B)/(B,A) and self-pairs (A,A)
    Step 3 → GROUP BY the pair, COUNT DISTINCT orders
    Step 4 → ORDER BY count descending, LIMIT 10

## 6. Pattern Recognition

"Compare rows within the same table, restricted to the same parent
entity" → self-join, the same fundamental technique as Q014's
employee-pairs question, here restricted by `order_id` instead of
`store_id`, and ordered/deduplicated by product_id instead of
employee_id.

## 7. SQL

```sql
SELECT
    oi1.product_id AS product_id_1,
    oi2.product_id AS product_id_2,
    p1.product_name AS product_name_1,
    p2.product_name AS product_name_2,
    COUNT(DISTINCT oi1.order_id) AS pair_count
FROM order_items oi1
JOIN order_items oi2
    ON oi1.order_id = oi2.order_id
   AND oi1.product_id < oi2.product_id
JOIN orders o ON o.order_id = oi1.order_id
JOIN products p1 ON p1.product_id = oi1.product_id
JOIN products p2 ON p2.product_id = oi2.product_id
WHERE o.order_status = 'completed'
GROUP BY oi1.product_id, oi2.product_id, p1.product_name, p2.product_name
ORDER BY pair_count DESC
LIMIT 10;
```

## 8. Walkthrough

The self-join on `oi1.order_id = oi2.order_id` pairs up every two line
items that belong to the same order; `oi1.product_id < oi2.product_id`
does double duty exactly as in Q014 — it prevents a product from being
paired with itself, and it guarantees each unordered pair is produced
exactly once (not once as A-B and again as B-A). `COUNT(DISTINCT
oi1.order_id)` (rather than a plain `COUNT(*)`) guards against a pair
being counted more than once for a single order — which could happen
if either product appeared as more than one line item within the same
order (e.g., added in two separate line entries).

## 9. Validation

- Pick the #1 resulting pair and manually confirm: run `SELECT order_id
  FROM order_items WHERE product_id IN (id1, id2) GROUP BY order_id
  HAVING COUNT(DISTINCT product_id) = 2` and cross-check the count
  against `pair_count`.
- Confirm no row has `product_id_1 = product_id_2` (a self-pair) or
  `product_id_1 > product_id_2` (a reverse duplicate).
- Confirm `pair_count` is bounded by the smaller of the two products'
  total individual order counts (a pair can't co-occur more often than
  either product appears on its own).

## 10. Edge Cases

- Two products that are individually very popular but conceptually
  unrelated could still show a high raw `pair_count` purely because
  both are frequently purchased overall — a more sophisticated
  "frequently bought together" feature would normalize by each
  product's individual popularity (e.g., a lift or confidence score
  from market basket analysis) rather than raw co-occurrence count,
  which this simple version doesn't do.
- Products from the "never sold" set naturally can't appear in any
  pair, since they have no `order_items` rows at all.
- An order with 10 different products contributes `C(10,2) = 45` pairs
  — a busy order with many distinct products disproportionately
  influences many different pairs' counts, which is expected but worth
  being aware of when interpreting results.

## 11. Alternative Approach

Restricting the self-join further (e.g., only pairing products from
*different* categories) would surface cross-category bundling
opportunities specifically, rather than pairs that are both from the
same naturally-co-purchased category (e.g., two different phone
models, which customers are unlikely to buy together anyway) — a
useful refinement depending on what merchandising actually wants to
build.

## 12. Trade-offs

Raw co-occurrence count is simple and directly interpretable ("these
two products were bought together N times"), but doesn't account for
each product's baseline popularity the way a proper lift/confidence
metric would — reasonable for a first pass, worth upgrading if the
"customers also bought" feature needs to avoid just recommending
whatever's generically popular.

## 13. Business Interpretation

This gives merchandising a concrete, evidence-based starting list for
a "customers also bought" feature — with the caveat that raw counts
favor generically popular products, so a follow-up pass normalizing by
each product's individual sales volume would likely produce more
genuinely surprising and useful pairings.
