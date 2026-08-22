# Q032 — Days Since Last Purchase (Recency)

## Business Context

Customer success wants a recency figure for every purchasing customer,
as of the most recent data available, to feed a simple RFM-style
scoring exercise.

## Business Question

For every customer who has placed at least one order, show their last
order date and how many days have passed since then, as of the
dataset's reference date.

## Data Available

orders

## Think Before SQL

1. What does one output row represent?
2. What is "the dataset's reference date" here, and why can't you use
   `CURDATE()` or `NOW()` for this calculation? (See
   `data_generation/README.md` if you're unsure.)
3. What function computes the day difference between two dates in
   MySQL, and in what order do its two arguments go (does swapping them
   change the sign of the result)?
4. Building on Q031, what's the one extra expression needed to turn
   "last order date" into "days since last order"?
5. Should recency be computed from all orders, or completed orders
   only? Does a cancelled order still represent a moment the customer
   engaged with placing an order?
6. What would a recency value of 0 mean? Is that possible in this
   dataset given its reference date?
7. What would a very large recency value (say, over 600 days) tell you
   about a customer, on its own, without any other information?
8. Is recency alone ever enough to say a customer has "churned," or
   does that require combining it with something else (a theme
   Level 5's Q050 returns to)?
9. How would you bucket this continuous recency value into meaningful
   tiers (e.g., "active," "cooling," "at risk," "dormant")? Is there one
   universally correct set of day thresholds?
10. How would you validate one customer's recency value against
    Q031's last_order_date for the same customer?

## Attempt

[space for learner]
