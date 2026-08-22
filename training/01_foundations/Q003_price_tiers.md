# Q003 — Price Tier Distribution

## Business Context

Pricing wants a quick view of how the active catalog is distributed
across informal price tiers before a pricing-strategy meeting.

## Business Question

Tag every active product as "Budget" (< LKR 5,000), "Mid" (LKR 5,000 to
50,000), or "Premium" (> LKR 50,000), then report how many active
products fall into each tier.

## Data Available

products

## Think Before SQL

1. What does one output row represent — a product, or a tier?
   (Hint: this question actually has two natural stages.)
2. What expression turns a continuous price into one of three labels?
3. Is the tier boundary a strict `<`/`>` or does it need `<=`/`>=`
   somewhere? Check your own boundary values (5,000 and 50,000 exactly).
4. Once every product has a tier label, what turns per-product rows into
   per-tier counts?
5. Can you do the tagging and the counting in one query? What would let
   you GROUP BY a computed expression rather than a stored column?
6. What filter needs to apply before tagging?
7. What edge case exists if a product's selling_price is exactly on a
   boundary?
8. How many tiers should appear in the output at most?
9. What would an empty tier (zero products) look like in your result,
   and would you notice if one were missing?
10. How would you validate your tier boundaries produced sensible
    counts (e.g., not 0 Budget products when the catalog has cheap
    items)?

## Attempt

[space for learner]
