# AS04 — Solution

## Approach A — LAG Window Function

```sql
WITH monthly AS (
    SELECT DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m-01')
)
SELECT month_start, revenue,
       LAG(revenue) OVER (ORDER BY month_start) AS prev_month_revenue
FROM monthly
ORDER BY month_start;
```

## Approach B — Self-Join on Shifted Month

```sql
WITH monthly AS (
    SELECT DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m-01')
)
SELECT
    m1.month_start, m1.revenue,
    m2.revenue AS prev_month_revenue
FROM monthly m1
LEFT JOIN monthly m2 ON m2.month_start = DATE_SUB(m1.month_start, INTERVAL 1 MONTH)
ORDER BY m1.month_start;
```

## Approach C — Correlated Subquery

```sql
WITH monthly AS (
    SELECT DATE_FORMAT(o.order_date, '%Y-%m-01') AS month_start,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'completed'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m-01')
)
SELECT
    m1.month_start, m1.revenue,
    (SELECT m2.revenue FROM monthly m2
     WHERE m2.month_start = DATE_SUB(m1.month_start, INTERVAL 1 MONTH)) AS prev_month_revenue
FROM monthly m1
ORDER BY m1.month_start;
```

## Comparison

1. **The gap-month problem**: if some calendar month had zero completed
   orders (and therefore no row at all in `monthly`), **Approach A's
   `LAG`** silently treats *whatever row is previous in the sort
   order* as "the previous month" — if January and March both have data
   but February doesn't, `LAG` at the March row returns January's
   revenue, incorrectly implying January and March are adjacent.
   **Approaches B and C**, by contrast, explicitly look for the row
   matching `DATE_SUB(month, INTERVAL 1 MONTH)` — if no such row exists
   (a true gap month), the `LEFT JOIN` (B) or subquery (C) correctly
   returns `NULL` for `prev_month_revenue`, accurately reflecting "no
   data for the actual previous calendar month," not "here's some
   earlier month's number, mislabeled."
2. **Robustness**: B and C are naturally robust to gaps because they
   compute the expected previous month explicitly rather than relying
   on row order; A is only safe if you've independently verified (or
   guaranteed via a full calendar grid, as in Q037/Q055) that no gap
   months exist in the underlying data.

## Recommendation

**Use Approach A (`LAG`) whenever the underlying series is known to
have no gaps** — it's the most concise and idiomatic choice, and this
project's month-over-month questions (Q023, RS07) rely on it. **Use
Approach B (self-join on shifted month) whenever gap months are a
real possibility and calendar-correctness matters** — it's more
verbose but doesn't silently misrepresent adjacency. Approach C is
functionally equivalent to B but usually less efficient (a correlated
subquery re-evaluated per row vs. a single join), so prefer B over C
when calendar-correctness is the deciding factor.
