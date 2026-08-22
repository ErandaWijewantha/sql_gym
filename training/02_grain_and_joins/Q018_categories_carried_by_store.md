# Q018 — Which Categories Does Each Store Actually Carry?

## Business Context

Merchandising wants to know, per store, which product categories are
represented in that store's inventory assortment (regardless of sales
volume), to check for assortment gaps against the regional plan.

## Business Question

For each store, list the distinct product categories that appear in
that store's inventory ledger at any point.

## Data Available

inventory
products
categories
stores

## Think Before SQL

1. What does one output row represent — a store, a store-category
   pair, or something else?
2. `inventory` links stores to products, and `products` links to
   `categories` — how many joins does it take to walk from `stores` to
   `categories`?
3. At what grain does `inventory` actually live (recall: store, product,
   date)? If you don't do anything about the date dimension, what
   happens to your category list?
4. If a store carried a category for 200 different inventory_dates,
   would a plain SELECT without DISTINCT show that category 200 times
   for that store?
5. What keyword collapses repeated (store, category) combinations
   arising from the date grain, down to one row per combination?
6. Is `DISTINCT` here masking an actual join problem, or is it the
   correct, deliberate tool for this specific question? What's the
   difference between those two situations?
7. Would `GROUP BY store_id, category_name` be an equally valid
   alternative to `SELECT DISTINCT`? When might you prefer one over the
   other (e.g., if you also wanted a count of something)?
8. What would you need to add if the question were instead "how many
   distinct products (not categories) does each store carry"?
9. How would you sanity check one store's category list against a
   manual look at its inventory rows?
10. What edge case exists for products explicitly excluded from every
    store's assortment (the "never sold" products from the data
    generator) — do they ever cause a category to be missing entirely
    from a store's list, even though other products in that category
    are carried?

## Attempt

[space for learner]
