# Reasoning

## 1. Interpret the Business Question

Merchandising wants a simple reference list: which active products sit
above a specific price point, ranked so the most expensive is first.
There's no aggregation involved — this is a filter-and-sort question.

## 2. Output Grain

One row = one product.

## 3. Metric Definition

No metric to aggregate. The relevant attribute is `selling_price` (what
the customer pays), not `cost` (what the business pays the supplier) —
"priced above LKR 100,000" is unambiguously about the customer-facing
price.

## 4. Required Data

`products`: product_id, product_name, selling_price, status.

## 5. Logical Decomposition

    Step 1 → filter to active products
    Step 2 → filter to selling_price > 100000
    Step 3 → sort descending by selling_price

## 6. Pattern Recognition

"List things matching a condition, in order" → plain SELECT / WHERE /
ORDER BY. No pattern more advanced than that is needed — resist the urge
to reach for anything fancier.

## 7. SQL

```sql
SELECT
    product_id,
    product_name,
    selling_price
FROM products
WHERE status = 'active'
  AND selling_price > 100000
ORDER BY selling_price DESC;
```

## 8. Walkthrough

`WHERE` applies both conditions row-by-row before any sorting happens.
`ORDER BY selling_price DESC` puts the most expensive product first.
No JOIN is needed because every column required lives on `products`.

## 9. Validation

- Confirm every row's `selling_price` is indeed > 100000 and
  `status = 'active'` (spot check a few rows).
- Confirm the list is monotonically non-increasing in `selling_price`.
- Cross-check the row count against
  `SELECT COUNT(*) FROM products WHERE status='active' AND selling_price>100000`.

## 10. Edge Cases

- Ties in `selling_price`: multiple products at the same price will
  appear adjacent but in no particular guaranteed sub-order — add a
  secondary `ORDER BY product_id` if a stable order matters.
- Discontinued products are excluded by design; if merchandising later
  wants to include them, drop the `status` filter.

## 11. Alternative Approach

None needed — this is a single-table filter/sort. Introducing a CTE or
subquery here would be an over-abstraction for the problem size.

## 12. Trade-offs

Not applicable at this level of complexity — readability is maximized
already; there's nothing to trade off.

## 13. Business Interpretation

The output is a reference list merchandising can use directly: it shows
exactly which currently-sellable products sit in the premium price
band, ordered so the flagship items are immediately visible at the top.
