# Q012 — How Many Orders, Really?

## Business Context

A dashboard widget shows "Total Completed Orders" and someone noticed
it doesn't match the number from `SELECT COUNT(*) FROM orders WHERE
order_status='completed'`. The widget's query joins to `order_items`.

## Business Question

Using a query that joins `orders` to `order_items`, show three numbers
side by side for completed orders: (a) COUNT(*), (b) COUNT(DISTINCT
order_id), and (c) the true order count from `orders` alone. Explain
why (a) and (c) differ while (b) and (c) match.

## Data Available

orders
order_items

## Think Before SQL

1. After joining orders to order_items, what does each row in the
   joined result represent — an order, or an order line item?
2. If `COUNT(*)` counts joined rows, what is it actually counting?
3. What does `COUNT(DISTINCT order_id)` do differently from `COUNT(*)`
   on that same joined result?
4. Why would `COUNT(DISTINCT order_id)` on the joined result equal
   `COUNT(*)` on the unjoined `orders` table?
5. Under what circumstance (if any) could `COUNT(DISTINCT order_id)`
   *not* match a plain count from `orders` directly? (Hint: think about
   what INNER JOIN requires.)
6. Is this a "bug" in the join, or a mismatch between what was asked
   for and what was computed?
7. What single-sentence rule would you give a junior analyst to avoid
   this mistake in the future?
8. How would you write the three-number comparison in one query using
   different aggregate expressions?
9. What's the smallest possible reproduction of this bug — one order
   with how many order_items would already show a divergence between
   (a) and (c)?
10. Does this same issue apply to `SUM()`? Why or why not?

## Attempt

[space for learner]
