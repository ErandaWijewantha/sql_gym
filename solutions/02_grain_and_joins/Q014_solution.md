# Reasoning

## 1. Interpret the Business Question

HR wants to compare employees against *other employees*, within the
same table, based on store and hire date proximity — a job for a
self-join.

## 2. Output Grain

One row = one unique pair of employees.

## 3. Metric Definition

No aggregation; the "metric" is really a filter condition: same store,
and `ABS(DATEDIFF(hire_date_1, hire_date_2)) <= 7`.

## 4. Required Data

`employees`: employee_id, store_id, hire_date.

## 5. Logical Decomposition

    Step 1 → self-join employees to employees on matching store_id
    Step 2 → enforce e1.employee_id < e2.employee_id to dedupe pairs and exclude self-pairs
    Step 3 → filter to ABS(DATEDIFF(...)) <= 7
    Step 4 → select both employees' IDs, store, and the day gap

## 6. Pattern Recognition

"Compare rows within the same table to each other" → self-join, using
two aliases of the same table. The `e1.employee_id < e2.employee_id`
trick is the standard idiom for producing unordered pairs exactly once.

## 7. SQL

```sql
SELECT
    e1.employee_id AS employee_1,
    e2.employee_id AS employee_2,
    e1.store_id,
    e1.hire_date AS hire_date_1,
    e2.hire_date AS hire_date_2,
    ABS(DATEDIFF(e1.hire_date, e2.hire_date)) AS day_gap
FROM employees e1
JOIN employees e2
    ON e1.store_id = e2.store_id
   AND e1.employee_id < e2.employee_id
WHERE ABS(DATEDIFF(e1.hire_date, e2.hire_date)) <= 7
ORDER BY e1.store_id, day_gap;
```

## 8. Walkthrough

Aliasing `employees` as `e1` and `e2` lets the same table act as both
sides of a join. `e1.store_id = e2.store_id` restricts pairs to
employees at the same store. `e1.employee_id < e2.employee_id` does two
jobs at once: it prevents an employee from being paired with themselves
(`e1.employee_id <> e2.employee_id` would allow both A-B and B-A; `<`
allows only one direction), and it guarantees each unordered pair
appears exactly once. `ABS(DATEDIFF(...))` measures the gap in days
regardless of which hire_date is earlier.

## 9. Validation

- Pick one resulting pair and manually confirm both employees'
  `store_id` matches and their hire dates are within 7 days.
- Confirm no row has `employee_1 = employee_2` (self-pairs) or
  `employee_1 > employee_2` (duplicate reverse pairs).
- If a store has 4 employees all hired within days of each other, you
  should see `C(4,2) = 6` pairs for that store, not 12 (which would
  indicate a directionality bug) and not 4 (self-pairs slipping
  through would suggest a different bug).

## 10. Edge Cases

- Two employees with the *identical* hire_date produce `day_gap = 0`,
  which correctly satisfies `<= 7`.
- The same employee can legitimately appear in multiple pairs (e.g.,
  three employees all hired within a week of each other at the same
  store produce 3 pairs, and each employee appears in 2 of them) — not
  a bug, just how pairwise combinations work.
- A store with only one employee produces zero pairs for that store,
  correctly.

## 11. Alternative Approach

A correlated subquery counting "how many other employees at this store
were hired within 7 days" per employee would answer a related but
different question (a per-employee count, not an explicit pair list) —
useful if HR actually wanted "flag employees who had company during
onboarding" rather than the pairs themselves.

## 12. Trade-offs

The self-join directly produces the pairs HR asked for and is the
natural fit; a correlated-subquery count would need a second query to
recover the actual pairs, so it's strictly less direct for this
specific question.

## 13. Business Interpretation

Pairs surfaced here are candidates for having gone through the same
onboarding batch — useful context if HR is auditing whether joint
orientation sessions actually happened as scheduled.
