# Q058 — The Cost of Empty Shelves

## Business Context

Supply chain wants a rough estimate of revenue potentially lost to
stockouts, to help justify investment in better replenishment
forecasting.

## Business Question

For each product, estimate how much additional revenue it might have
generated if it had never gone out of stock, based on its typical daily
sales rate on days when it *was* in stock.

## Data Available

inventory
order_items
orders
products

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What does "out of stock" look like in the data you have available?
- What would a fair estimate of "typical daily sales rate" be based
  on — and specifically, which days should and shouldn't be included in
  that calculation?
- Once you have a typical daily rate and a count of stocked-out days,
  how do you turn that into an estimated revenue figure? What are you
  implicitly assuming when you do?

[space for learner]
