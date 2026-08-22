# Q044 — Which Products Should Operations Investigate?

## Business Context

The Operations Director asks: "Pull me a list of products we need to
look into."

## Business Question

Which products should Operations investigate?

## Data Available

products
order_items
orders
returns
inventory

## Think Before SQL

This question is **deliberately underspecified** — "investigate" could
mean several unrelated things.

1. List at least four independent, legitimate reasons a product might
   need investigating (e.g., unusually high return rate, frequent
   stockouts, a steep sales decline, being sold at a loss after
   discounts).
2. Are these four reasons mutually exclusive, or could one product
   qualify under multiple? Would that make it a *higher* priority?
3. For "high return rate," what's the denominator — return rate per
   unit sold, per order, or per revenue? (This is exactly Q046's
   question, and the answer isn't obvious.)
4. For "frequent stockouts," what does the `inventory` table let you
   measure directly (recall `closing_stock`)?
5. For "steep sales decline," is this the same pattern as Q038 (3
   consecutive declining months), or a looser, single-number version
   (e.g., this quarter vs last quarter)?
6. For "sold at a loss," what two columns on `products` do you need,
   and how does `discount_amount` from `order_items` change the
   calculation versus just comparing `cost` to `selling_price`?
7. Would you present Operations with one combined "risk score," or
   four separate lists they can triage independently? What are the
   trade-offs of collapsing multiple signals into one number?
8. Is a product that's simply low-volume (a handful of sales) but has
   one single return automatically "high return rate" by percentage —
   and is that a meaningful signal, or noise? (Recall Q009's minimum
   sample size guard.)
9. Would you weight these signals equally, or does one (say, selling
   at a loss) deserve more urgency than another (a minor stock
   shortage)?
10. What would you say back to Operations to scope this down to
    something a single query (or small set of queries) can actually
    answer well?

## Attempt

Pick at least two of the signals you identified above, compute each
independently, and note where they overlap.

[space for learner]
