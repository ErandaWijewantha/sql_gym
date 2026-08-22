# RS04 — Solution

## Grain
One row = one customer.

## What is being computed
Every customer for whom no row in `orders` matches their customer_id —
i.e., customers with zero orders ever.

## Pattern
Anti-join via `NOT EXISTS` — "entities in A with no corresponding row
in B."

## Likely business question
"Which customers have never placed an order?" — this is Q013 from
Level 2, the target list for a first-purchase incentive campaign.

## Notes
`NOT EXISTS` is one of three common ways to express this (the others
being `LEFT JOIN ... WHERE <child key> IS NULL`, and the riskier `NOT
IN`, which breaks silently if the subquery's column can ever contain a
NULL) — see `training/approach_selection/AS02.md` for a full
comparison.

## Verification query

```sql
SELECT c.customer_id, c.customer_name, c.registration_date
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
)
LIMIT 20;
```
