# Reasoning

## 1. Interpret the Business Question

Compare payment methods by their failure rate — the fraction of
payment attempts on that method that ended up `failed`.

## 2. Output Grain

One row = one payment_method.

## 3. Metric Definition

`failure_rate = COUNT(payment_status='failed') / COUNT(*)`, per
payment_method, across all payment attempts (not just one per order —
every attempt, including retries, is a real data point about that
method's reliability).

## 4. Required Data

`payments`: payment_method, payment_status.

## 5. SQL

```sql
SELECT
    payment_method,
    COUNT(*) AS total_attempts,
    SUM(payment_status = 'failed') AS failed_attempts,
    ROUND(SUM(payment_status = 'failed') * 100.0 / COUNT(*), 2) AS failure_rate_pct
FROM payments
GROUP BY payment_method
ORDER BY failure_rate_pct DESC;
```

## 6. Walkthrough

A single `GROUP BY payment_method` with a conditional sum computes both
the total attempt count and the failed count per method in one pass;
dividing gives the failure rate directly. No joins are needed since
everything required lives on `payments` itself.

## 7. Validation

- `failed_attempts <= total_attempts` for every method, trivially.
- Sum of `total_attempts` across all methods should equal `SELECT
  COUNT(*) FROM payments`.

## 8. Edge Cases

- This counts every payment *attempt*, so an order with a failed
  attempt followed by a successful retry (recall the ~5% of completed
  orders built this way) contributes one `failed` row and one
  `success` row to whatever payment_method was used — both attempts are
  real data about that method, so both should count, not just the
  final outcome.
- A payment_method used rarely will have a noisier failure rate — worth
  showing `total_attempts` alongside the rate (already included) so a
  reader can judge how much to trust each number.

## 9. Alternative Approach

Restricting to one payment attempt per order (e.g., only the first
chronological attempt) would answer a subtly different question ("how
often does the *initial* attempt fail"), rather than "how often does
this method fail across all attempts" — a legitimate alternative
framing depending on what the payments team actually wants to measure.

## 10. Trade-offs

Counting every attempt (this solution) better reflects the method's
overall reliability including retries; counting only first attempts
better isolates a "first impression" failure rate — worth clarifying
with the payments team which one they mean, similar to Level 5's
definitional theme.

## 11. Business Interpretation

A payment method with a notably higher failure rate than its peers is
a concrete, quantified case for renegotiating with that specific
processor or reconsidering whether to keep offering it as an option.
