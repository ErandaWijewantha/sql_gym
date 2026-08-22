# Q007 — Regions With a Large Customer Base

## Business Context

Regional operations is deciding where to open a new support desk and
wants to focus on regions with a substantial existing customer base.

## Business Question

Which regions have more than 500 registered customers?

## Data Available

customers

## Think Before SQL

1. What does one output row represent?
2. What is being counted, and does it matter whether a customer has
   ever placed an order?
3. What clause groups customers into one bucket per region?
4. What clause filters on the count itself, rather than on a customer
   attribute?
5. Some customers have a NULL region. What happens to those rows in a
   GROUP BY region — do they vanish, or form their own group?
6. Is a NULL-region group a data problem, or a legitimate "unknown"
   bucket worth reporting separately?
7. What would change if the business had instead asked for regions with
   more than 500 *active* customers?
8. How would you sanity check the total across all regions (including
   NULL) against `SELECT COUNT(*) FROM customers`?
9. What ordering (if any) would make this list more useful to read?
10. What's the difference between filtering this with WHERE region IS
    NOT NULL versus not filtering at all?

## Attempt

[space for learner]
