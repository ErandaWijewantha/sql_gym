# Q014 — Employees Hired Close Together at the Same Store

## Business Context

HR is reviewing onboarding batches and wants to find pairs of employees
at the same store who were hired within 7 days of each other, to check
whether they went through joint orientation.

## Business Question

List every pair of employees who work at the same store and whose
hire_date values are within 7 days of each other (in either direction).
Each pair should appear once, not twice.

## Data Available

employees

## Think Before SQL

1. What does one output row represent — an employee, or a pair of
   employees?
2. This question compares rows in a table to *other rows in the same
   table*. What SQL technique lets you do that?
3. If you join the `employees` table to itself, what do you need in the
   ON clause to make sure you're comparing employees at the *same
   store*?
4. What do you need in the ON/WHERE clause to make sure you're not
   comparing an employee to themselves?
5. A self-join with `e1.employee_id <> e2.employee_id` would produce
   each pair twice (A-B and B-A). What condition instead produces each
   pair exactly once?
6. How do you express "within 7 days of each other, in either
   direction" — does `ABS(DATEDIFF(...))` help here, and if so, why
   does using `ABS` avoid needing two separate conditions?
7. What's the resulting SELECT list — do you want both employees'
   IDs, their store, and the day gap?
8. What would happen (how many rows) if you forgot the store-matching
   condition entirely?
9. Could the same employee appear in multiple pairs? Is that expected
   or a bug?
10. How would you validate one resulting pair manually by looking up
    both employees' hire_dates and stores directly?

## Attempt

[space for learner]
