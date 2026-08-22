# Q027 — Each Product's Share of Its Category's Revenue

## Business Context

Category managers want to know product concentration: does a category's
revenue come from a broad spread of products, or is it dominated by a
handful of hero SKUs?

## Business Question

For each product, show its gross revenue (completed orders) and what
percentage that represents of its own category's total gross revenue.

## Data Available

orders
order_items
products
categories

## Think Before SQL

1. What does one output row represent?
2. What two numbers does a "percentage of total" question always
   require — and at what two different grains do they each live?
3. Could you compute the category totals with a separate GROUP BY
   query and then join them back to the product-level revenue? What
   would that require (how many passes over the data)?
4. Is there a window function that can compute "this category's total"
   *without* collapsing the result down to one row per category —
   i.e., while keeping the product-level grain intact?
5. What does `SUM(product_revenue) OVER (PARTITION BY category_id)`
   actually return, on every product row belonging to that category?
6. Once you have both the product's own revenue and its category's
   total (both available on the same row), how do you compute the
   percentage?
7. Do the percentages for all products within one category sum to
   100%? Why must that be true, and how would you verify it?
8. What happens to a product with zero revenue (never sold) — does it
   appear in this result at all, and if not, does that affect whether
   percentages still sum to 100%?
9. Would a correlated subquery (recomputing the category total once
   per product row) produce the same result as the window-function
   version? What's different about how many times the underlying data
   gets scanned?
10. How would you validate one category's percentages sum to
    (approximately) 100, accounting for rounding?

## Attempt

[space for learner]
