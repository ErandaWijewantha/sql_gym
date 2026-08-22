# Q009 — Products Frequently Sold at a Discount

## Business Context

Pricing wants to know which products are rarely sold at full price, as
candidates for a permanent price cut instead of constant promotions.

## Business Question

For products with at least 5 recorded order line items, what percentage
of their line items were sold with a discount (discount_amount > 0)?
List the 15 highest by discount frequency.

## Data Available

order_items

## Think Before SQL

1. What does one output row represent?
2. What row-level condition defines "sold with a discount"?
3. How do you turn a per-line-item TRUE/FALSE condition into a
   percentage per product?
4. What expression lets you compute a percentage using CASE (or a
   boolean-to-number trick) inside an aggregate function?
5. What clause enforces the "at least 5 line items" requirement, and
   why must it apply after grouping rather than before?
6. What happens to products with only 1-2 line items if you skip that
   requirement — could they distort the "top 15" list?
7. What determines the sort order and row limit of the final output?
8. Do you need any other table for this question? Why or why not?
9. What would a result of exactly 100% or exactly 0% for a product
   mean, and is that plausible given the data generation (some
   products are deliberately never discounted vs frequently discounted)?
10. How would you spot-check one product's percentage manually?

## Attempt

[space for learner]
