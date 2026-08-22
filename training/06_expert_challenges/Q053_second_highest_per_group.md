# Q053 — Runner-Up Products

## Business Context

Category managers already have their #1 best-seller memorized in each
brand-category combination. They want to know the #2 — the product
most likely to become the next hero SKU with a bit more marketing push.

## Business Question

For each (brand, category) combination that has at least 2 distinct
products with completed-order sales, find the second-highest-revenue
product.

## Data Available

orders
order_items
products
brands
categories

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- Would `MAX()` after excluding the actual maximum row work — and if
  so, how would you express "excluding the maximum" correctly when
  there could be a tie for first place?
- What's different about finding the *second* highest compared to
  finding the *highest* (which you've already done in an earlier
  level)?

[space for learner]
