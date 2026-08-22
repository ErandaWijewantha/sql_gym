# Q002 — Top 10 Priced Phones

## Business Context

A category manager for Mobile Phones wants a quick reference of the
most expensive active phones currently carried, to check against
competitor flagship pricing.

## Business Question

List the 10 highest-priced active products in the "Mobile Phones"
category.

## Data Available

products
categories

## Think Before SQL

1. What does one output row represent?
2. What defines "in the Mobile Phones category" — which table holds
   category names, and which holds the product-to-category link?
3. What does "active" mean here, and where does that live?
4. What determines "top 10"?
5. Do you need a JOIN, and if so, what kind?
6. Could the JOIN change how many rows represent one product? Why or
   why not, for this specific case?
7. What clause caps the result at 10 rows?
8. What happens if two products are tied at the 10th price — is that
   a problem for this question specifically?
9. What would you check to confirm the JOIN didn't accidentally filter
   out or duplicate anything?
10. What business decision might this list actually inform?

## Attempt

[space for learner]
