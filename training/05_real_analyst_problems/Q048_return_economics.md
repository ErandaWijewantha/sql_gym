# Q048 — Are We Losing Money on Returns for Any Product?

## Business Context

Finance is worried that heavy discounting combined with a high return
rate might mean some products are actually *losing* the company money
once returns are accounted for, even though they show positive revenue
on paper.

## Business Question

Are there any products where the net revenue actually collected (after
discounts and after subtracting returned units' value) is less than
the cost of goods sold for the units that were *not* returned?

## Data Available

products
order_items
returns

## Think Before SQL

1. What does one output row represent?
2. What does "cost of goods sold" require from the `products` table,
   and does it apply per unit or per order line?
3. What's the difference between "gross revenue," "net revenue after
   discount," and "net revenue after discount and after returns" for a
   single product? Write out the formula for each explicitly before
   coding anything.
4. Should COGS be charged against every unit *sold* (including ones
   later returned), or only against units the company ultimately kept
   sold (i.e., net of returns)? Which framing makes more sense for "are
   we losing money," and why might finance define it differently than
   you'd first guess?
5. What intermediate results do you need, and at what grain, before
   combining sales value, discount, return value, and cost into one
   per-product comparison?
6. Is this the same net-units-sold computation as Q015? Can you reuse
   that logic here?
7. What would it mean, concretely, for a product to fail this test —
   walk through a hypothetical product with real numbers (cost,
   selling price, discount rate, return rate) where the math tips
   negative.
8. Is a product with a *thin margin and normal return rate* different
   from a product with a *fat margin but extreme return rate*, in terms
   of which one is more likely to fail this test?
9. Would you want this at the product grain, or would category-level
   or brand-level answers change the story finance would tell from the
   result?
10. How would you validate one flagged product by manually reconstructing
    its revenue, discount, return, and cost figures?

## Attempt

[space for learner]
