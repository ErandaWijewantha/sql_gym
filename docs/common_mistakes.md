# Common Mistakes

Every entry below produces a query that **runs without error** and
**returns a plausible-looking number that is wrong**. That combination
is what makes these mistakes dangerous — nothing in the tooling tells
you to double-check.

---

## Duplicate rows after JOIN

**What happens**: joining two "many" tables directly to a shared parent
(or to each other) produces one row per *combination* of matching rows
on each side, inflating any subsequent `SUM`/`COUNT`.
**Where trained**: Q011, Q015, Q017, Q019.
**Fix**: pre-aggregate each "many" table to a safe grain independently
before joining (Q020's capstone pattern).

---

## COUNT vs COUNT DISTINCT

**What happens**: `COUNT(*)` after a one-to-many join counts *joined
rows* (e.g., line items), not the entity you meant (e.g., orders).
**Where trained**: Q012.
**Fix**: `COUNT(DISTINCT primary_key)` when you're past the entity's
own grain, or better, pre-aggregate first so a plain `COUNT(*)` is
already correct.

---

## LEFT JOIN becoming INNER JOIN

**What happens**: a condition on the joined (right) table placed in
`WHERE` instead of `ON` silently discards the NULL-extended
non-matching rows a `LEFT JOIN` was supposed to preserve — turning it
back into an `INNER JOIN` without any syntax error.
**Where trained**: called out explicitly in Q029's solution.
**Fix**: conditions that should still allow "no match" belong in the
`ON` clause; conditions meant to filter the *final result* (after
deciding whether a match exists) belong in `WHERE`.

---

## WHERE vs HAVING

**What happens**: a condition on an aggregate value (`SUM(...) > X`)
placed in `WHERE` is a syntax error in MySQL — but the deeper mistake is
conceptual: `WHERE` filters rows *before* grouping; `HAVING` filters
groups *after* aggregation.
**Where trained**: Q006 (the canonical HAVING example), Q042, Q044.
**Fix**: filter on raw columns with `WHERE`; filter on aggregate results
with `HAVING`.

---

## NULL handling

**What happens**: `NOT IN (subquery)` silently returns zero rows for
*every* outer row if the subquery's result set contains even one NULL
— because `x NOT IN (a, NULL)` evaluates to `UNKNOWN`, not `TRUE`,
regardless of `x`.
**Where trained**: AS02's full comparison of NOT EXISTS / LEFT JOIN+IS
NULL / NOT IN.
**Fix**: prefer `NOT EXISTS` or `LEFT JOIN ... WHERE <key> IS NULL` for
anti-joins; if you must use `NOT IN`, guarantee the subquery's column
is `NOT NULL` first.

---

## Incorrect window partition

**What happens**: a window function's `PARTITION BY` doesn't match the
entity you actually want compared within — e.g., ranking products
globally when you meant to rank within each category (missing
`PARTITION BY category_id` entirely).
**Where trained**: contrast Q002 (no partition needed, global top-N)
against Q021 (partition required, per-category top-N).
**Fix**: always ask "what group should this row be compared against?"
before writing `OVER (...)`.

---

## Incorrect ordering

**What happens**: a window function's `ORDER BY` doesn't reflect the
sequence the business actually cares about — e.g., ordering a `LAG`
window alphabetically or by an unrelated column instead of
chronologically, producing a "previous row" that isn't actually
temporally previous.
**Where trained**: implicit in every LAG/LEAD/running-total question
(Q023-Q026); made explicit in the "Think Before SQL" prompts for those
questions.
**Fix**: the `ORDER BY` inside `OVER (...)` should always match the
dimension the word "previous," "next," or "running" refers to.

---

## Ranking ties

**What happens**: `ROW_NUMBER()` silently picks one of several tied
"winners" and drops the rest, when `RANK()`/`DENSE_RANK()` would have
shown all of them.
**Where trained**: Q022 (RANK vs DENSE_RANK), Q053 (DENSE_RANK for a
tie-safe "second highest"), AS03.
**Fix**: use `RANK()` or `DENSE_RANK()` whenever a tie is plausible and
matters to the business question; reserve `ROW_NUMBER()` for when
exactly one row per group is explicitly required, with an agreed
tiebreak.

---

## Incorrect date boundaries

**What happens**: using `<= '2025-12-31'` against a `DATETIME` column
silently excludes any timestamp later than midnight on that day (e.g.,
`2025-12-31 14:30:00` is not `<= '2025-12-31 00:00:00'`).
**Where trained**: Q006's solution walks through this exact trap.
**Fix**: use a half-open range — `>= start_date AND < day_after_end_date`
— for any date-range filter on a `DATETIME` column.

---

## Double-counting

**What happens**: summing a measure over a joined result that fans out
(see "Duplicate rows after JOIN" above) inflates the sum, not just the
row count.
**Where trained**: Q011, Q017.
**Fix**: same as duplicate-row fixes — pre-aggregate before joining.

---

## Average of averages

**What happens**: averaging a per-line-item value directly (instead of
first summing to the grain you actually care about, then averaging
that) silently weights entities with more line items more heavily.
**Where trained**: Q016 (the full AOV grain trap), Q008.
**Fix**: pre-aggregate to the intended grain (e.g., one row per order)
*before* applying `AVG()`.

---

## Incorrect denominator

**What happens**: a rate or percentage is only as meaningful as its
denominator population — "return rate" alone is ambiguous between at
least three different denominators (units, orders, revenue), each
giving a genuinely different number.
**Where trained**: Q046 (the canonical example), Q044, Q045.
**Fix**: state the denominator explicitly before computing any rate;
when in doubt, compute more than one definition and compare.

---

## Filtering too early

**What happens**: applying a `WHERE` condition before an aggregation
that needed the excluded rows to compute correctly — e.g., filtering
out a customer's early orders before computing their *first* order
date.
**Where trained**: implicit throughout Level 4's recency/cohort
questions — always compute the full-history aggregate first, then
filter on the result.
**Fix**: aggregate first (in a CTE), filter the aggregate's result
second.

---

## Filtering too late

**What happens**: the opposite problem — computing an expensive
aggregate or join over far more data than necessary, then filtering the
final result down, when the filter could have been pushed earlier
(e.g., restricting a date range) to reduce the work done.
**Where trained**: Q042, Q069 restrict their date range in the base
`WHERE` before aggregating, rather than aggregating all 24 months and
discarding most of it afterward.
**Fix**: apply row-level filters (dates, status) as early as possible;
only defer filters that genuinely depend on an aggregate result.

---

## Using DISTINCT to hide a bad join

**What happens**: adding `DISTINCT` to make an inflated row count "look
right" without understanding *why* it was inflated in the first place —
sometimes correct (Q018's legitimate date-collapsing use), sometimes a
band-aid over an unrelated fan-out bug that also corrupted a `SUM` you
didn't notice.
**Where trained**: Q018 (a deliberate, correct use of DISTINCT) versus
Q011/Q015 (where DISTINCT would not fix the underlying SUM inflation).
**Fix**: understand *why* row count was inflated before reaching for
DISTINCT; if a SUM/COUNT elsewhere in the same query is also affected,
DISTINCT on one column won't fix it.

---

## Aggregating at the wrong grain

**What happens**: the umbrella mistake behind nearly everything above —
computing an aggregate over rows that aren't at the grain the metric's
definition assumes.
**Where trained**: every single Level 2 question, by design.
**Fix**: state the intended output grain explicitly (`docs/grain.md`'s
checklist) before writing any aggregate function.
