# Q040 — Lifetime Value Snapshot by Tenure Bucket

## Business Context

Finance wants a lifetime-value snapshot segmented by how long each
customer has been registered, to see whether longer-tenured customers
are actually worth more, or whether value plateaus early.

## Business Question

For every purchasing customer, compute their total net spend to date
(completed orders) and their tenure in months (from registration_date
to the dataset reference date). Bucket customers into tenure groups
("0-6 months," "6-12 months," "12-24 months," "24+ months") and report
average lifetime spend per bucket.

## Data Available

customers
orders
order_items

## Think Before SQL

1. What does one output row represent — say precisely what the *final*
   grain is, as distinct from any earlier intermediate grain.
2. What per-customer measures do you need before any bucketing or
   averaging can happen? Name all of them.
3. How do you compute "tenure in months" from a registration_date and a
   fixed reference date — what MySQL function handles this cleanly?
4. What expression turns a continuous tenure-in-months value into one
   of the four named buckets? (Recall Q003's price-tier CASE pattern.)
5. Does "total net spend to date" include only completed orders? What
   would including cancelled/refunded orders do to a lifetime-value
   figure specifically?
6. Should a customer with zero orders (but a valid registration_date
   and thus a tenure) appear in this analysis at all, given the
   question says "purchasing customer"?
7. What's the right order of operations: bucket first then average, or
   compute each customer's own spend and tenure first, then bucket and
   average afterward? Does it matter?
8. What would you expect to see if tenure and value were unrelated —
   would average spend per bucket look roughly flat across buckets?
9. What would a declining average-spend-per-bucket pattern across
   increasing tenure actually suggest about customer lifecycle (careful
   — there's a subtle survivorship consideration: are the customers in
   the "24+ months" bucket a representative sample, or a self-selected
   group who happened to still be around)?
10. How would you validate one customer's bucket assignment and spend
    figure independently?

## Attempt

[space for learner]
