# Reasoning

## 1. Interpret the Business Question

The category manager wants a short, ranked reference list of the
priciest active phones — a simple top-N lookup, scoped to one category.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

`selling_price`, the customer-facing price — same reasoning as Q001.

## 4. Required Data

`products`: product_name, category_id, selling_price, status.
`categories`: category_id, category_name.

## 5. Logical Decomposition

    Step 1 → join products to categories to get category_name
    Step 2 → filter to category_name = 'Mobile Phones' and status = 'active'
    Step 3 → order by selling_price descending
    Step 4 → limit to 10 rows

## 6. Pattern Recognition

"Top N" without any grouping (just one flat ranked list) → `ORDER BY` +
`LIMIT`. This is deliberately *not* a ranking-window-function question —
that pattern (`ROW_NUMBER`/`RANK`) only becomes necessary once you need
top-N *within each group simultaneously* (see Q021).

## 7. SQL

```sql
SELECT
    p.product_name,
    p.selling_price
FROM products p
JOIN categories c ON c.category_id = p.category_id
WHERE c.category_name = 'Mobile Phones'
  AND p.status = 'active'
ORDER BY p.selling_price DESC
LIMIT 10;
```

## 8. Walkthrough

The JOIN attaches `category_name` to each product row without changing
the grain — `categories` has exactly one row per `category_id`, so the
join is many-to-one and cannot duplicate any product rows. `WHERE` then
filters down to the phones we care about, `ORDER BY` ranks them, and
`LIMIT 10` caps the output.

## 9. Validation

- Confirm the JOIN didn't drop any products: count active Mobile Phones
  products directly (`SELECT COUNT(*) FROM products p JOIN categories c
  ON ... WHERE ...`) and make sure it's >= 10 (otherwise fewer than 10
  rows is correct, not a bug).
- Confirm no row in the output belongs to a different category.

## 10. Edge Cases

- If fewer than 10 active phones exist, the query correctly returns
  fewer than 10 rows — that's not an error.
- A tie at the 10th price could arbitrarily include one product over
  another with the same price; add `ORDER BY p.selling_price DESC,
  p.product_id` for a deterministic tiebreak if that matters.
- `category_name` matching is exact-string; a typo or trailing space in
  the filter value silently returns zero rows rather than an error —
  worth double-checking against `SELECT DISTINCT category_name FROM categories`.

## 11. Alternative Approach

A subquery filtering on `category_id` directly (looked up once) instead
of a JOIN would also work, but the JOIN is more readable and scales
naturally if the SELECT list ever needs another category attribute.

## 12. Trade-offs

The JOIN version is preferred here for readability: it names the
category by its business-meaningful string once, rather than requiring
the reader to already know `category_id` for Mobile Phones.

## 13. Business Interpretation

This gives the category manager a direct, current snapshot of the
flagship pricing tier within Mobile Phones — useful for comparing
against competitor flagship pricing without also having to think about
inactive/discontinued listings.
