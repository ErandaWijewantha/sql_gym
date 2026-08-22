# Reasoning

## 1. Interpret the Business Question

Pricing wants a distribution: how many active products land in each of
three price bands. This is really two steps fused into one: label each
product, then count by label.

## 2. Output Grain

The *intermediate* grain is one row = one product (while tagging). The
*final* output grain is one row = one price tier.

## 3. Metric Definition

The metric is a simple count of products; the tier itself is derived
from `selling_price` using fixed boundaries:
Budget < 5,000 <= Mid <= 50,000 < Premium.
(Choosing `<=` at the lower and upper bound of "Mid" means a product
priced at exactly 5,000 or exactly 50,000 lands in "Mid" — a boundary
decision worth stating explicitly rather than leaving implicit.)

## 4. Required Data

`products`: selling_price, status.

## 5. Logical Decomposition

    Step 1 → filter to active products
    Step 2 → compute a CASE expression that maps selling_price to a tier label
    Step 3 → GROUP BY that computed label
    Step 4 → COUNT(*) per group

## 6. Pattern Recognition

"Turn a continuous value into a business category, then summarize" →
`CASE` for the bucketing, `GROUP BY` for the summary. The key trick:
MySQL lets you `GROUP BY` a column alias defined in the SELECT list, so
the tagging and counting can be done in a single query.

## 7. SQL

```sql
SELECT
    CASE
        WHEN selling_price < 5000 THEN 'Budget'
        WHEN selling_price <= 50000 THEN 'Mid'
        ELSE 'Premium'
    END AS price_tier,
    COUNT(*) AS product_count
FROM products
WHERE status = 'active'
GROUP BY price_tier
ORDER BY FIELD(price_tier, 'Budget', 'Mid', 'Premium');
```

## 8. Walkthrough

The `CASE` expression evaluates top-to-bottom per row: anything under
5,000 is "Budget"; anything from 5,000 up to and including 50,000 is
"Mid" (the first condition already excluded values under 5,000, so this
branch implicitly starts at 5,000); everything else is "Premium". MySQL
allows grouping by the `price_tier` alias, collapsing the per-product
rows into three summary rows. `ORDER BY FIELD(...)` forces a logical
(not alphabetical) tier order in the output.

## 9. Validation

- The three tier counts should sum to the total active product count:
  `SELECT COUNT(*) FROM products WHERE status='active'`.
- Spot check one product just below and just above each boundary
  (4999, 5000, 50000, 50001) to confirm the tier logic behaves as
  intended.

## 10. Edge Cases

- A product priced at exactly 5,000: falls into "Mid" (not "Budget"),
  because the first WHEN's `< 5000` is false and the second WHEN's
  `<= 50000` is true. If the business actually meant a strict boundary
  the other way, this needs to be renegotiated, not silently assumed.
- If no active product happens to fall in a tier, that tier simply
  won't appear as a row — GROUP BY never invents empty groups. If the
  business needs to see "Budget: 0" explicitly, you'd need to
  cross-join against a fixed list of the three tier labels.

## 11. Alternative Approach

Two separate queries (one to tag, wrapped in a subquery/CTE, then an
outer `GROUP BY`) is equivalent and sometimes clearer when the tagging
logic is complex enough to want its own named step:

```sql
WITH tagged AS (
    SELECT
        CASE
            WHEN selling_price < 5000 THEN 'Budget'
            WHEN selling_price <= 50000 THEN 'Mid'
            ELSE 'Premium'
        END AS price_tier
    FROM products
    WHERE status = 'active'
)
SELECT price_tier, COUNT(*) AS product_count
FROM tagged
GROUP BY price_tier
ORDER BY FIELD(price_tier, 'Budget', 'Mid', 'Premium');
```

## 12. Trade-offs

The single-query version is shorter and fine for this simple case; the
CTE version is preferable once the tagging logic grows (e.g., combining
multiple columns), since it separates "define the tier" from "summarize
the tier" as two readable steps.

## 13. Business Interpretation

This tells pricing exactly how top-heavy or bottom-heavy the active
catalog is by price, which directly informs whether the assortment
skews toward volume (Budget/Mid) or margin (Premium) products.
