# Reasoning

## 1. Interpret the Business Question

A board member asking "what's our return rate" is really asking for
whichever single number is standard in the industry — but there isn't
one universal standard, and the three candidate definitions can differ
substantially. This solution computes all three and shows they're not
interchangeable.

## 2. Metric Definitions

- **(a) Unit return rate**: `SUM(returns.quantity) /
  SUM(order_items.quantity)` from completed orders.
- **(b) Order return rate**: `COUNT(DISTINCT orders with >= 1 return) /
  COUNT(DISTINCT completed orders)`.
- **(c) Revenue return rate**: `SUM(returned units' original sale
  value) / SUM(gross revenue)`.

## 3. Required Data

`order_items`, `returns`, `orders`.

## 4. SQL

```sql
WITH sold AS (
    SELECT oi.order_id, oi.product_id, oi.quantity, oi.unit_price
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    WHERE o.order_status = 'completed'
),
returned AS (
    SELECT r.order_id, r.product_id, r.quantity
    FROM returns r
    JOIN orders o ON o.order_id = r.order_id
    WHERE o.order_status IN ('completed', 'refunded')
)
SELECT
    -- (a) unit return rate
    ROUND(
        (SELECT COALESCE(SUM(quantity), 0) FROM returned) * 100.0
        / (SELECT SUM(quantity) FROM sold),
        2
    ) AS unit_return_rate_pct,

    -- (b) order return rate
    ROUND(
        (SELECT COUNT(DISTINCT order_id) FROM returned) * 100.0
        / (SELECT COUNT(DISTINCT order_id) FROM sold),
        2
    ) AS order_return_rate_pct,

    -- (c) revenue return rate (returned units valued at their original unit_price)
    ROUND(
        (SELECT COALESCE(SUM(rt.quantity * s.unit_price), 0)
         FROM returned rt
         JOIN sold s ON s.order_id = rt.order_id AND s.product_id = rt.product_id) * 100.0
        / (SELECT SUM(quantity * unit_price) FROM sold),
        2
    ) AS revenue_return_rate_pct;
```

## 5. Walkthrough

`sold` and `returned` are each pre-aggregated at the same
(order_id, product_id) grain, avoiding any join fan-out between them
(the same lesson as Q015). Each of the three rates is computed as an
independent scalar subquery pair (numerator, denominator) rather than
mixed into one grouped query, since each definition has a genuinely
different denominator population. Definition (c) joins `returned` back
to `sold` on the matching (order_id, product_id) to recover the
original `unit_price` each returned unit was actually sold at (a return
row itself doesn't store price).

## 6. Validation

- All three percentages should be single-digit-to-low-double-digit
  numbers for a real business; if any comes back wildly different in
  magnitude from the others, suspect a denominator/numerator mismatch
  rather than assuming the metrics are "supposed to" disagree that
  much.
- Manually recompute one of the three for a single product or single
  month as an independent spot check.
- Confirm (b)'s numerator (`COUNT(DISTINCT order_id)` in `returned`)
  never exceeds its denominator — every order with a return must, by
  construction, be a subset of completed/refunded orders.

## 7. Edge Cases

- Definitions (a) and (c) can diverge meaningfully if returns cluster
  on expensive or cheap products disproportionately — a business could
  have a low unit return rate but a high revenue return rate if
  high-value items get returned more often, or vice versa.
- Definition (b) treats an order with 1 of 5 items returned identically
  to an order with all 5 returned — it answers "how often does a return
  happen at all," not "how much of what we sold came back."
- None of these three include cancelled orders' items in either
  numerator or denominator (since those units were never actually
  fulfilled) — a defensible choice, but one worth stating.

## 8. Business Interpretation

The honest answer to the board is: **"It depends on what you mean — by
units, it's X%; by orders affected, it's Y%; by revenue, it's Z%.
They tell different stories: [X] says how often a *unit* comes back,
[Y] says how often an *order* is touched by a return at all, and [Z]
says how much *money* is at stake. Which one matters most depends on
whether we're managing operations cost (units), customer experience
(orders), or P&L impact (revenue)."** Picking one silently and
reporting it as "the" return rate is the mistake this question exists
to prevent.
