# Reasoning

## 1. Interpret the Business Question

HR wants a starting point, not a final headcount decision — a ratio of
recent order volume to current employee count per store, restricted to
customer-facing roles and a recent, staffing-relevant time window.

## 2. Output Grain

One row = one physical (non-online) store.

## 3. Metric Definition

`orders_per_employee = completed orders in the last 3 months of the
dataset (2025-10-01 to 2025-12-31) / count of current employees in
customer-facing roles (Sales Associate, Cashier, Assistant Manager) at
that store`.

## 4. Required Data

`orders`: order_id, store_id, order_date, order_status.
`employees`: employee_id, store_id, employee_role.
`stores`: store_id, store_name, store_type.

## 5. Logical Decomposition

    Step 1 → pre-aggregate recent completed order count per store
    Step 2 → pre-aggregate customer-facing employee count per store
    Step 3 → join the two (both already at store grain, so no fan-out risk)
    Step 4 → divide, restricted to physical stores

## 6. SQL

```sql
WITH recent_orders AS (
    SELECT store_id, COUNT(*) AS order_count_3mo
    FROM orders
    WHERE order_status = 'completed'
      AND order_date >= '2025-10-01' AND order_date < '2026-01-01'
    GROUP BY store_id
),
staff_count AS (
    SELECT store_id, COUNT(*) AS customer_facing_staff
    FROM employees
    WHERE employee_role IN ('Sales Associate', 'Cashier', 'Assistant Manager')
    GROUP BY store_id
)
SELECT
    s.store_id,
    s.store_name,
    ro.order_count_3mo,
    sc.customer_facing_staff,
    ROUND(ro.order_count_3mo / sc.customer_facing_staff, 1) AS orders_per_employee
FROM stores s
JOIN recent_orders ro ON ro.store_id = s.store_id
JOIN staff_count sc    ON sc.store_id = s.store_id
WHERE s.store_type != 'online'
ORDER BY orders_per_employee DESC;
```

## 7. Walkthrough

`recent_orders` and `staff_count` are each independently pre-aggregated
to store grain before ever being joined to each other — avoiding the
exact two-independent-"many"-tables fan-out trap Q019 warned about
(here, `orders` and `employees` both hang off `stores`). Once both
sides are at store grain, joining them is safe one-to-one, and the
division is straightforward. `WHERE s.store_type != 'online'` excludes
online "stores," whose staff serve a fulfillment/ops role rather than
directly handling the order volume being measured.

## 8. Validation

- For one store, independently count its recent completed orders and
  its qualifying employees, and confirm the ratio matches.
- Confirm no online store appears in the output.
- The highest-ratio stores are the ones to look at first for
  potential understaffing — cross-check a couple against their
  absolute order counts to make sure a high ratio isn't just an
  artifact of a store having very few staff overall (1 order per day
  with 1 employee looks identical in ratio to 100 orders per day with
  100 employees, but the operational reality is very different).

## 9. Edge Cases

- A store that just hired several new employees very recently will
  show a lower (better-looking) ratio than its *current* staffing
  actually reflects historically, since the denominator counts *all
  current* employees regardless of hire_date, while the numerator only
  looks at the last 3 months — this is actually the right behavior for
  a forward-looking staffing decision (you care about current capacity
  against current demand), but worth being aware the ratio isn't a
  historical average.
- A store with zero customer-facing employees (all managers, unlikely
  but structurally possible) would produce a division error — not
  observed in this dataset's generation, but worth a defensive
  `NULLIF` in a production version.

## 10. Alternative Approach

Restricting to a longer window (e.g., 12 months) would smooth out any
single unusually busy or slow quarter, at the cost of being less
responsive to *current* conditions — a genuine trade-off HR should
weigh depending on whether staffing decisions are meant to respond to
recent trends or long-run averages.

## 11. Trade-offs

The 3-month window used here is more responsive to recent conditions
but noisier for smaller stores; a 12-month window is more stable but
slower to reflect a genuine recent change in demand.

## 12. Business Interpretation

This ratio is a starting point for a conversation, not a staffing
formula — a high ratio might mean genuinely overworked staff (support
this with support-ticket or return-rate data as a secondary check), or
it might mean an efficient, well-run store; HR should pair this
signal with a qualitative check before reallocating headcount.
