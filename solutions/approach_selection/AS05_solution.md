# AS05 — Solution

## Approach A — Window SUM OVER

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
       SUM(revenue) OVER (ORDER BY month_start) AS running_total
FROM monthly
ORDER BY month_start;
```

## Approach B — Correlated Subquery

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
    (SELECT SUM(m2.revenue) FROM monthly m2 WHERE m2.month_start <= m1.month_start) AS running_total
FROM monthly m1
ORDER BY m1.month_start;
```

## Approach C — Session Variable Accumulator (legacy anti-pattern)

```sql
SET @running := 0;
```

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
    month_start,
    revenue,
    (@running := @running + revenue) AS running_total
FROM monthly
ORDER BY month_start;
```

## Comparison

1. **Reliable ordering**: Approach A's window function has a
   well-defined, standardized evaluation order (governed entirely by
   its explicit `ORDER BY` clause inside `OVER (...)`) — the SQL
   standard and MySQL's implementation both guarantee this. Approach C
   relies on the *outer query's row processing order* matching the
   `ORDER BY` at the end of the statement, which historically was
   **not officially guaranteed** by MySQL's optimizer for arbitrary
   queries — the accumulation could silently happen in a different row
   order than the displayed `ORDER BY`, especially once an index,
   `JOIN` reordering, or query-plan change entered the picture. Even
   where it happens to work today, it's leaning on undocumented
   behavior rather than a guarantee.
2. **Why C is a legacy anti-pattern**: it predates window function
   support (added in MySQL 8.0); before that, session-variable
   accumulation was one of the few ways to compute a running total at
   all. Since window functions are now available and standardized,
   continuing to use variable accumulation trades a documented,
   optimizer-safe feature for an undocumented trick — with no
   remaining upside.
3. **When B might still beat A**: essentially never for a plain running
   total — B does meaningfully more work (a subquery re-scan per outer
   row) for an identical result. B is worth knowing mainly as a mental
   model for understanding *what* a running-total window function is
   conceptually doing under the hood, not as a real alternative.

## Recommendation

**Always use Approach A (window `SUM() OVER`)** for a running total on
MySQL 8+. Never reach for Approach C in new code — if you encounter it
in an existing legacy codebase, treat it as a candidate for refactoring
to a window function during the next touch of that query.
