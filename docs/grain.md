# Grain

## What is grain?

Grain is the answer to: **"What does one row of this table (or query
result) represent?"**

Every table has a grain. Every query result has a grain, whether or
not you thought about it. Getting the grain wrong is the single most
common source of subtly incorrect analytical SQL — code that runs,
returns a plausible-looking number, and is simply wrong.

## Why it matters

Most "the JOIN duplicated my rows" and "my average is wrong" bugs are
grain bugs in disguise. If you can state grain precisely before writing
a query, you can predict — before running anything — whether a JOIN
will fan out, whether an aggregate needs `DISTINCT`, and whether an
`AVG()` will average the thing you think it's averaging.

## Grain in this schema

| Table | Grain (one row = ) |
|---|---|
| `customers` | one customer |
| `products` | one product |
| `orders` | one order |
| `order_items` | one line item within one order |
| `payments` | one payment attempt on one order (can be >1 per order) |
| `returns` | one returned line (one product, one order, one return event) |
| `inventory` | one store, one product, one day |
| `customer_campaigns` | one customer's one interaction with one campaign, on one date |
| `support_tickets` | one ticket |

Notice that `orders` and `order_items` are **different grains** even
though they're obviously related — this single fact is responsible for
most of Level 2's exercises.

## How JOINs change grain

Joining two tables at the **same** grain (a 1:1 relationship) doesn't
change grain. Joining a "one" table to a "many" table (e.g., `orders`
to `order_items`) moves the *result's* grain down to match the "many"
side — after that join, one row represents one line item, not one
order, even though every column from `orders` is still there,
just repeated across every line item of that order.

Joining **two different "many" tables** to a shared parent in the same
query (e.g., `order_items` and `payments`, both hanging off `orders`)
produces a row for every combination of matching rows on each side —
a fan-out that has nothing to do with either JOIN condition being
"wrong." See Level 2's Q011, Q015, Q017, Q019 for four different
flavors of this exact trap.

## How aggregation changes grain

`GROUP BY` collapses grain up to whatever you group by. `GROUP BY
customer_id` on a table at order grain produces a result at customer
grain. This is the primary tool for *deliberately* changing grain —
the trouble only starts when a fan-out changes grain *accidentally*,
before you meant it to.

## How window functions preserve grain

This is the crucial difference between a window function and a
`GROUP BY` aggregate: **`GROUP BY` collapses rows; a window function
does not.** `SUM(x) OVER (PARTITION BY category)` computes a
group-level total and attaches it to *every row* in that group, without
reducing the row count. This is why window functions are the tool of
choice whenever you need a per-row detail *and* a group-level
comparison in the same result (percentage of total, ranking, running
totals) — see `docs/sql_pattern_library.md`.

## Worked example: double-counting from grain confusion

```sql
-- WRONG: joins two "many" tables directly to the parent
SELECT SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN payments p ON p.order_id = o.order_id
WHERE o.order_status = 'completed';
```

If an order has 3 line items and 2 payment rows (a failed attempt plus
a successful retry), this JOIN produces 3 x 2 = 6 rows for that one
order, and `SUM` counts each line item's value twice. The query result
is at neither order grain, nor line-item grain, nor payment grain — it's
at the grain of "(line item, payment) pairs within an order," which is
not a grain anyone actually wants. See Level 2's Q011 for the full
walkthrough and fix.

## The grain checklist, before every query

1. What grain does each table I'm about to touch actually have?
2. What grain do I want my *final result* to have?
3. Every time I JOIN, does it change grain — and is that on purpose?
4. If I'm joining two "many" tables to a shared parent, have I
   pre-aggregated each one to a safe grain *first*?
5. After I write the query, does `COUNT(DISTINCT primary_key)` match
   what I expect for the stated output grain?

Concrete grain examples used throughout this gym: transaction grain
(`payments`, `returns`), order grain (`orders`, or `order_items`
pre-aggregated), customer grain (`customers`, or orders grouped by
customer), customer-month grain (Level 4's cohort and time-series
questions), and product-month grain (Level 4's decline-streak
question, Q038).
