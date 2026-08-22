# Reasoning

## 1. Interpret the Business Question

Merchandising wants an assortment map: which categories does each store
carry at all, irrespective of sales performance or how many days of
inventory history exist.

## 2. Output Grain

One row = one (store, category) combination.

## 3. Metric Definition

No numeric metric — this is a distinct-membership question.

## 4. Required Data

`inventory`: store_id, product_id, inventory_date.
`products`: product_id, category_id.
`categories`: category_id, category_name.
`stores`: store_id, store_name.

## 5. Logical Decomposition

    Step 1 → join inventory to products to products' category, to categories for the name
    Step 2 → join to stores for readability
    Step 3 → SELECT DISTINCT store, category (collapsing the date dimension entirely)

## 6. Pattern Recognition

"List distinct combinations, ignoring a finer-grained dimension" →
`SELECT DISTINCT` (or equivalently `GROUP BY` with no aggregate
function needed). The key insight is recognizing that `inventory_date`
is irrelevant to this question and must be collapsed away, or every
category would appear once per day it was stocked.

## 7. SQL

```sql
SELECT DISTINCT
    s.store_id,
    s.store_name,
    c.category_name
FROM inventory i
JOIN stores s      ON s.store_id    = i.store_id
JOIN products p    ON p.product_id  = i.product_id
JOIN categories c  ON c.category_id = p.category_id
ORDER BY s.store_id, c.category_name;
```

## 8. Walkthrough

Walking from `inventory` (store_id, product_id, inventory_date) to
`products` (product_id → category_id) to `categories` (category_id →
category_name) attaches a category name to every inventory row without
changing its grain — each join is many-to-one. `DISTINCT` then
collapses the (potentially hundreds of) date-level rows per (store,
category) pair down to exactly one.

## 9. Validation

- For one store, count how many rows this query returns for it, and
  compare against `SELECT COUNT(DISTINCT p.category_id) FROM inventory
  i JOIN products p ON p.product_id=i.product_id WHERE i.store_id =
  <id>` — the two counts should match.
- Confirm removing `DISTINCT` inflates the row count dramatically
  (roughly by a factor of ~730, the number of days in the dataset,
  divided by however many products-per-category collapse together) —
  this is a good way to *feel* why DISTINCT is essential here, not just
  believe it.

## 10. Edge Cases

- `DISTINCT` here is the deliberate, correct tool — not, as
  `docs/common_mistakes.md` warns against elsewhere, a band-aid papering
  over an unrelated join bug. The distinction: DISTINCT is legitimate
  when you've *intentionally* collapsed a real dimension (date) that
  the question doesn't care about; it's a red flag when it's added
  reflexively to make a suspiciously large row count "look right"
  without understanding why the count was large in the first place.
- Categories with products that exist but were never included in *any*
  store's inventory assortment (recall: each store only stocks a random
  ~50-100 product subset, and ~5% of products are excluded from every
  store) simply won't appear for that store — correct, since they
  aren't actually carried there.
- A store carrying only 1 product from a 40-product category still
  causes that whole category to show up as "carried" — this query
  answers "is it represented at all," not "how well is it represented"
  (a different, deeper question).

## 11. Alternative Approach

`GROUP BY s.store_id, s.store_name, c.category_name` with no aggregate
function in the SELECT list produces an identical result to
`SELECT DISTINCT` here — purely a style choice, though `DISTINCT` more
directly signals "I just want unique combinations" to a reader, while
`GROUP BY` more naturally invites adding a `COUNT(*)` or similar later.

## 12. Trade-offs

Prefer `GROUP BY` over `DISTINCT` if you anticipate the question
evolving into "how many distinct products per store-category" (Q009 of
the "attempt" style) — otherwise `DISTINCT` communicates intent more
plainly for a pure membership question.

## 13. Business Interpretation

This produces a store-by-category assortment matrix merchandising can
diff against the regional planogram to spot gaps — e.g., a store in a
region where "Garden & Outdoor" should be seasonal-stocked but doesn't
appear at all in this list.
