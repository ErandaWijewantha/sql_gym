# SQL Pattern Library

This is the pattern-recognition reference for the whole gym: the
mental trigger that should fire when you hear a certain kind of
business phrasing. Each entry follows the same structure. Cross-
references point to the specific question in `training/` where the
pattern is trained.

---

## Filtering

**Mental trigger**: "only rows where X" — a condition on a single row,
independent of any other row.
**Business wording**: "which products cost more than...", "orders
placed in March..."
**Grain before / after**: unchanged — filtering never changes grain.
**SQL techniques**: `WHERE`.
**Example**: Q001.
**Common mistakes**: filtering on an aggregate in `WHERE` instead of
`HAVING` (see Aggregation below); filtering too early, discarding rows
an aggregate step still needed (see `docs/common_mistakes.md`).
**Alternative approaches**: none needed for simple filters.
**Performance**: index the filtered column(s) when the table is large;
see `database/03_indexes.sql`.

---

## Aggregation

**Mental trigger**: "how many / how much, per group."
**Business wording**: "total revenue by category," "count of orders by
status."
**Grain before**: the raw table's grain. **Grain after**: one row per
group.
**SQL techniques**: `GROUP BY` + `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`.
Filter groups themselves with `HAVING`, not `WHERE`.
**Example**: Q004, Q005.
**Common mistakes**: averaging at the wrong grain (Q016); `COUNT(*)`
after a fan-out join counting the wrong thing (Q012).
**Alternative approaches**: a window function preserves grain instead
of collapsing it — appropriate when you need the aggregate *alongside*
detail rows (see Percentage of Total, below).
**Performance**: aggregating over a pre-filtered, indexed subset is far
cheaper than aggregating everything and filtering after.

---

## Conditional Aggregation

**Mental trigger**: "what fraction of rows meet a condition," or "count
X and Y separately, in one pass."
**Business wording**: "percentage of line items discounted," "orders
containing both category A and B."
**Grain before**: row grain. **Grain after**: one row per group, with
one or more condition-specific measures.
**SQL techniques**: `SUM(CASE WHEN condition THEN 1 ELSE 0 END)`,
`AVG(CASE WHEN condition THEN 1 ELSE 0 END)`, or the MySQL shorthand
`SUM(condition)` (a boolean evaluates to 1/0).
**Example**: Q009, Q030, Q063.
**Common mistakes**: forgetting `NULLIF` on a ratio's denominator when
it could be zero.
**Alternative approaches**: multiple independent `EXISTS` subqueries
(Q030's Approach B) instead of one grouped query with `HAVING`.
**Performance**: a single pass with conditional sums is usually cheaper
than N separate filtered aggregate queries.

---

## Joins (fact ↔ dimension, fact ↔ fact)

**Mental trigger**: "attach information from another table."
**Business wording**: "product's category name," "customer's region."
**Grain before / after**: unchanged when joining many-to-one (fact to
dimension); collapses to the finer grain when joining one-to-many.
**SQL techniques**: `JOIN` / `INNER JOIN`, `LEFT JOIN`.
**Example**: Q002 (safe many-to-one), Q011 (unsafe many-to-many via a
shared parent).
**Common mistakes**: joining two independent "many" tables directly to
each other or to a shared parent, producing a cross-product fan-out —
see `docs/grain.md`'s worked example, and Level 2 generally.
**Alternative approaches**: pre-aggregate each "many" side to a safe
grain before joining (Q015, Q020).
**Performance**: index every FK column used in a JOIN (already done in
`database/03_indexes.sql`).

---

## Anti-Joins

**Mental trigger**: "never did X," "no matching row exists."
**Business wording**: "customers who never ordered," "products never
sold."
**Grain before**: the "left" table's grain. **Grain after**: unchanged,
just filtered down.
**SQL techniques**: `LEFT JOIN ... WHERE <child key> IS NULL`, or
`NOT EXISTS` (see next entry).
**Example**: Q013, Q029, Q035.
**Common mistakes**: putting a condition on the joined (right) table in
`WHERE` instead of the `ON` clause, which silently turns a `LEFT JOIN`
back into an `INNER JOIN` (see `docs/common_mistakes.md`).
**Alternative approaches**: `NOT EXISTS`, `NOT IN` (risky with NULLs —
see AS02).
**Performance**: `NOT EXISTS` and `LEFT JOIN`/`IS NULL` typically
produce equivalent, efficient plans in MySQL 8; avoid `NOT IN` on a
subquery whose column could contain NULL.

---

## EXISTS / NOT EXISTS

**Mental trigger**: "does at least one matching row exist" (or not).
**Business wording**: "customers who have ever...", "orders that also
contain..."
**Grain before / after**: unchanged — `EXISTS` is a boolean filter, not
a join that changes row count.
**SQL techniques**: `WHERE EXISTS (correlated subquery)` /
`WHERE NOT EXISTS (...)`.
**Example**: Q029 (compound NOT EXISTS), Q030 Approach B (double
EXISTS), AS02.
**Common mistakes**: forgetting the correlation (the subquery must
reference the outer row, e.g. `WHERE oi.order_id = o.order_id`) —
without it, `EXISTS` just checks "does *any* row anywhere satisfy this,"
which is almost never what's intended.
**Alternative approaches**: `LEFT JOIN`/`IS NULL`; conditional
aggregation with `HAVING`.
**Performance**: MySQL only needs to find one matching row to
short-circuit `EXISTS`, so it's typically efficient even though it
"looks like" a per-row subquery scan.

---

## Subqueries

**Mental trigger**: "I need a value computed from a separate query,
either once (scalar) or per outer row (correlated)."
**Business wording**: varies — often hidden inside "above average,"
"compared to the maximum," etc.
**Grain**: depends on whether it's scalar (returns one value) or
correlated (conceptually re-evaluated per outer row).
**SQL techniques**: scalar subquery in `SELECT` or `WHERE`; correlated
subquery referencing an outer alias.
**Example**: Q028 Approach C (correlated), RS10 (non-correlated/
global).
**Common mistakes**: confusing whether a comparison should be
per-group (correlated) or global (non-correlated) — these produce very
different results for the same surface question (see RS10's notes).
**Alternative approaches**: CTE + JOIN, window function — see
`docs/approach_selection.md`.
**Performance**: a correlated subquery re-evaluated per outer row is
usually the most expensive of the three; prefer a window function or
CTE+JOIN at scale.

---

## CTEs (Common Table Expressions)

**Mental trigger**: "I need to name and reuse an intermediate result,
possibly built in multiple steps."
**Business wording**: no specific wording — this is a structuring tool,
used throughout every level from Q011 onward.
**Grain**: a CTE can be at any grain; its whole purpose is often
exactly to establish a new, deliberate grain (see Q020's capstone).
**SQL techniques**: `WITH name AS (...)`, optionally `WITH RECURSIVE`
for generating a calendar (Q037, Q055).
**Common mistakes**: skipping the pre-aggregation CTE and joining raw
fact tables directly (the root cause of most Level 2 mistakes).
**Alternative approaches**: a subquery inline achieves the same result
without a name — CTEs are preferred purely for readability and reuse
within the same query.
**Performance**: MySQL 8 may or may not materialize a CTE depending on
how it's used; for a CTE referenced multiple times, check `EXPLAIN` if
performance matters at scale.

---

## ROW_NUMBER / RANK / DENSE_RANK

**Mental trigger**: "top N," "Nth highest," "assign a rank."
**Business wording**: "top 3 per category," "second-highest revenue
product," "rank stores by revenue."
**Grain before**: unchanged (a window function never collapses rows).
**Grain after**: same as before, with a new rank column attached.
**SQL techniques**: `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`
for a unique 1,2,3,... sequence with arbitrary tiebreaks;
`RANK()` for ties sharing a rank with a gap afterward; `DENSE_RANK()`
for ties sharing a rank with no gap afterward.
**Example**: Q021 (top-N-per-group), Q022 (RANK vs DENSE_RANK), Q053
(second-highest via DENSE_RANK).
**Common mistakes**: using `ROW_NUMBER()` when ties matter, silently
picking one of several tied "winners" and dropping the rest (see AS03).
**Alternative approaches**: correlated subquery with `MAX`/count-of-
greater-values (AS03's Approach B) — works but doesn't scale as well.
**Performance**: a single pass with a window function; avoid N separate
correlated subqueries for the same effect.

---

## LAG / LEAD

**Mental trigger**: "compared to the previous / next period or event,
for the same entity."
**Business wording**: "month-over-month change," "days until next
order," "gap since previous purchase."
**Grain**: unchanged.
**SQL techniques**: `LAG(col) OVER (PARTITION BY entity ORDER BY
time)`, `LEAD(col) OVER (...)`.
**Example**: Q023 (LAG), Q024 (LEAD), Q034 (LAG + ROW_NUMBER combined).
**Common mistakes**: assuming "the previous row in the result" is the
same as "the previous calendar period" — false whenever a period could
be missing entirely (a gap month with zero activity). See AS04's full
comparison and the calendar-grid fix used in Q037/Q055.
**Alternative approaches**: self-join on a shifted time key (AS04
Approach B) — more verbose, but calendar-correct even with gaps.
**Performance**: `LAG`/`LEAD` are single-pass and efficient; the
calendar-grid fix costs an extra CROSS JOIN but is usually still cheap
at typical business-reporting data volumes.

---

## Running Totals

**Mental trigger**: "cumulative, from the start through now."
**Business wording**: "cumulative revenue," "running total."
**Grain**: unchanged.
**SQL techniques**: `SUM(x) OVER (ORDER BY time)`, using the default
frame (`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`); add
`PARTITION BY` for a per-group running total that resets per group.
**Example**: Q025, Q052 (running *maximum* instead of sum), Q059
(running total combined with a cohort partition).
**Common mistakes**: using the legacy session-variable accumulator
pattern (AS05's Approach C) — undocumented row-order dependency, avoid
in new code.
**Alternative approaches**: correlated subquery (AS05 Approach B) — 
correct but re-scans per row.
**Performance**: window `SUM` is a single pass; the session-variable
trick and correlated-subquery alternative are both worse and/or riskier.

---

## Moving Averages

**Mental trigger**: "smoothed trend over a fixed recent window."
**Business wording**: "3-month moving average."
**Grain**: unchanged.
**SQL techniques**: `AVG(x) OVER (PARTITION BY entity ORDER BY time
ROWS BETWEEN N PRECEDING AND CURRENT ROW)` — an explicit, bounded frame,
unlike a running total's unbounded one.
**Example**: Q026.
**Common mistakes**: forgetting that `ROWS BETWEEN` counts *rows*, not
calendar periods — a gap month silently widens the effective calendar
span the average covers.
**Alternative approaches**: self-join with explicit calendar-range
matching, for gap-proof correctness.
**Performance**: single pass; cheap at any realistic data volume.

---

## Percentage of Total

**Mental trigger**: "this row's share of its group's total," without
losing the row-level detail.
**Business wording**: "product's % of category revenue."
**Grain**: unchanged (this is the classic case where a window function
beats `GROUP BY`, which would collapse the detail you still need).
**SQL techniques**: `SUM(x) OVER (PARTITION BY group)` alongside the
row's own value, then divide.
**Example**: Q027.
**Common mistakes**: computing the group total via a separate `GROUP
BY` query and then needing an extra JOIN to bring it back to detail
grain — works, but is more steps than necessary (see AS01-style
Approach A vs B trade-off).
**Alternative approaches**: CTE + JOIN (Q027's "Alternative Approach"
section shows both side by side).
**Performance**: window-function version avoids a second aggregation
pass and an extra join.

---

## Cohort Analysis / Retention

**Mental trigger**: "group entities by when they started, then track
them on a clock relative to that start."
**Business wording**: "month-1 retention by signup cohort," "revenue
curve by customer age."
**Grain**: two different time axes at once — calendar time (which
defines the cohort) and relative time (months/periods since the
entity's own start) — keeping them straight is the whole difficulty.
**SQL techniques**: `MIN()` to find the cohort-defining event; `
PERIOD_DIFF`/`TIMESTAMPDIFF` to compute relative time; `GROUP BY`
cohort + relative-period.
**Example**: Q036 (month-1 retention), Q059 (full revenue curve).
**Common mistakes**: comparing a very recent cohort's early curve
against an older cohort's full curve, when the recent cohort simply
hasn't had time to reach later relative periods yet (Q036, Q059 both
flag this explicitly).
**Alternative approaches**: none structurally different — this pattern
is inherently a two-step "establish cohort, then measure relative to
it" shape.
**Performance**: fine at this dataset's scale; at larger scale, ensure
the cohort-defining `MIN()` step is indexed.

---

## Gaps and Islands

**Mental trigger**: "a run/streak of N consecutive qualifying periods."
**Business wording**: "3 consecutive months of decline," "longest
active streak."
**Grain**: row grain during flagging, then one row per streak (island)
after grouping.
**SQL techniques**: (1) build a full calendar grid so gaps are explicit
zero/false rows, not missing rows; (2) flag each row true/false; (3)
`ROW_NUMBER() OVER (PARTITION BY entity ORDER BY time) - ROW_NUMBER()
OVER (PARTITION BY entity, flag ORDER BY time)` — constant within a
consecutive run of the same flag, letting `GROUP BY` collapse each
island; (4) filter/measure islands as needed.
**Example**: Q037, Q038, Q051 (extended to find the MAX streak length).
**Common mistakes**: skipping the calendar-grid step — without it, two
non-adjacent active periods separated by a true gap period get
incorrectly treated as consecutive, because there's no gap *row* to
break the island-grouping trick.
**Alternative approaches**: procedural (application-code) iteration —
avoids the SQL machinery, but leaves the database and isn't reusable as
a query/view.
**Performance**: the calendar grid costs a CROSS JOIN (entities x
periods) — manageable for a few thousand entities across a couple of
years, worth checking row-count growth before scaling further.

---

## Funnel Analysis

**Mental trigger**: "stage-by-stage progression, where each stage is a
strict subset of the one before."
**Business wording**: "impression → click → conversion drop-off."
**Grain**: one row per group being funneled (e.g., per channel), with
one measure per stage.
**SQL techniques**: conditional `COUNT(DISTINCT CASE WHEN stage = X
THEN entity_id END)` per stage, computed independently in one pass —
not a chain of joins between stages.
**Example**: Q056.
**Common mistakes**: joining stage tables together directly (fan-out
risk again) instead of using independent conditional counts over one
joined base table.
**Alternative approaches**: separate pre-aggregated per-stage CTEs
joined together — equivalent, more verbose.
**Performance**: conditional aggregation in one pass beats multiple
separate stage queries.

---

## Deduplication

**Mental trigger**: "keep exactly one row per entity, by some rule
(usually 'the latest')."
**Business wording**: "each customer's most recent order."
**Grain before**: the raw table's grain. **Grain after**: one row per
entity.
**SQL techniques**: `ROW_NUMBER() OVER (PARTITION BY entity ORDER BY
tiebreak) = 1`, or `GROUP BY entity` + `MAX()`/`MIN()` if only the
extreme value (not the whole row) is needed.
**Example**: Q010 (via MAX), RS01/Q079 (via ROW_NUMBER, needed because
the whole row, not just the date, must be kept).
**Common mistakes**: using `GROUP BY` + `MAX(date)` when you also need
another column from *that specific row* (e.g., `order_id`) — a plain
`GROUP BY` can silently mismatch columns from different rows unless
every selected column is functionally dependent on the group key. Use
`ROW_NUMBER()` instead whenever you need more than the aggregated value
itself.
**Alternative approaches**: correlated subquery per entity — works, less
scalable.
**Performance**: `ROW_NUMBER()` in a single pass is preferred over a
self-join or correlated subquery for this purpose.

---

## Anomaly Detection

**Mental trigger**: "unusually far from what's typical for this
entity."
**Business wording**: "unusual days," "outlier revenue."
**Grain**: unchanged — one row per (entity, period), with statistics
attached via window functions.
**SQL techniques**: `AVG(x) OVER (PARTITION BY entity)` and `STDDEV(x)
OVER (PARTITION BY entity)` computed alongside every row, then flag
`ABS(x - mean) > k * stddev`.
**Example**: Q055.
**Common mistakes**: computing "typical" only over days that *had*
activity, silently excluding true zero-activity days from the baseline
— this both understates real variability and makes it impossible to
ever flag "unusually low" days, since there's no row for a true zero
day to even compare. Fix with a full calendar grid, same as Gaps and
Islands.
**Alternative approaches**: a seasonally-adjusted baseline (detrending
by day-of-week/month before flagging) — more accurate, more complex.
**Performance**: window functions in a single pass; the calendar grid
adds a manageable CROSS JOIN cost.
