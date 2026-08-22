# Question Index

Reference date for all recency/time-window questions: **2025-12-31**
(the dataset spans 2024-01-01 to 2025-12-31). See
`data_generation/README.md` for why.

For Level 7 (blind challenges), **Main Concept is intentionally left
blank** — do not look it up elsewhere before attempting the question.
The point of that level is to discover the pattern yourself.

Legend: MA = flagged as a multi-approach exercise (see `## 5` below).

## 1. Level 1 — Foundations (Q001–Q010)

| ID | Business Area | Difficulty | Main Concept | Thinking Skill |
|----|----------------|------------|---------------|-----------------|
| Q001 | Products | Easy | SELECT / WHERE / ORDER BY | Reading a business filter into a predicate |
| Q002 | Products | Easy | ORDER BY + LIMIT | Top-N without ranking functions |
| Q003 | Products | Easy | CASE | Turning a continuous value into business tiers |
| Q004 | Sales | Easy | GROUP BY + COUNT | Grain = order_status |
| Q005 | Sales | Easy | GROUP BY + SUM | First encounter with "revenue" ambiguity |
| Q006 | Sales | Easy | GROUP BY + HAVING | Filtering on an aggregate, not a row |
| Q007 | Customers | Easy | GROUP BY + HAVING | Aggregate filter on a dimension table |
| Q008 | Stores | Medium | Basic JOIN + aggregation | Combining fact and dimension before aggregating |
| Q009 | Products | Easy | Conditional aggregation (CASE + SUM) | Turning row-level flags into a summary |
| Q010 | Customers | Medium | JOIN + GROUP BY MAX | First grain question: "one row per customer" |

## 2. Level 2 — Grain & Joins (Q011–Q020)

| ID | Business Area | Difficulty | Main Concept | Thinking Skill |
|----|----------------|------------|---------------|-----------------|
| Q011 | Sales | Medium | Join fan-out | Recognizing when a JOIN duplicates rows |
| Q012 | Sales | Medium | COUNT vs COUNT(DISTINCT) | Grain after a one-to-many join |
| Q013 | Customers | Medium | LEFT JOIN + IS NULL | Finding "no match" rows (pre-anti-join) |
| Q014 | Employees | Medium | Self JOIN | Comparing rows within the same table |
| Q015 | Products | Hard | Join fan-out across two children | Returns + order_items double-counting trap |
| Q016 | Sales | Hard | Grain mismatch | Average of line items vs average of orders |
| Q017 | Payments | Hard | Join fan-out | Ret09-payment duplication in revenue |
| Q018 | Stores | Medium | Multi-hop JOIN | Dimension chaining: product→category→inventory→store |
| Q019 | Customers | Hard | Two 1:many joins at once | Why joining two fact tables directly inflates counts |
| Q020 | Sales | Hard | Pre-aggregate then join | Capstone: build a clean order-grain dataset first |

## 3. Level 3 — Analytical Patterns (Q021–Q030)

| ID | Business Area | Difficulty | Main Concept | Thinking Skill | MA |
|----|----------------|------------|---------------|-----------------|----|
| Q021 | Products | Medium | ROW_NUMBER / RANK partitioned | "Top N per group" → ranking window | MA |
| Q022 | Stores | Medium | RANK vs DENSE_RANK | Handling ranking ties correctly |
| Q023 | Sales | Medium | LAG | "Compare to previous period" → LAG |
| Q024 | Sales | Medium | LEAD | "What happened next" → LEAD |
| Q025 | Sales | Medium | Running total (window SUM) | Cumulative aggregation without collapsing grain |
| Q026 | Stores | Hard | Moving average | Window frame (ROWS BETWEEN) |
| Q027 | Products | Medium | Percentage of total | Numerator/denominator via window | MA |
| Q028 | Customers | Hard | Compare to group benchmark | Window AVG vs correlated subquery vs CTE+JOIN | MA |
| Q029 | Customers | Medium | NOT EXISTS | "Never did X" → anti-join | MA |
| Q030 | Sales | Hard | EXISTS + conditional aggregation | "Did both X and Y" pattern |

## 4. Level 4 — Time & Customer Behavior (Q031–Q040)

| ID | Business Area | Difficulty | Main Concept | Thinking Skill | MA |
|----|----------------|------------|---------------|-----------------|----|
| Q031 | Customers | Medium | MIN/MAX per group | First/last event grain |
| Q032 | Customers | Medium | Recency (DATEDIFF from anchor date) | Fixed reference date, not NOW() |
| Q033 | Customers | Medium | Frequency segmentation | One-time vs repeat | MA |
| Q034 | Customers | Hard | LAG + gap detection | Customer reactivation (see solutions template) | MA |
| Q035 | Customers | Hard | Period anti-join | "In A but not B" across two time windows |
| Q036 | Customers | Expert | Cohort retention | Registration-month cohort → month+1 return rate |
| Q037 | Customers | Expert | Gaps and islands (increasing streak) | 3 consecutive months of growth | MA |
| Q038 | Products | Expert | Gaps and islands (declining streak) | 3 consecutive months of decline |
| Q039 | Customers | Hard | Recency among previously-active | Distinguish dormant from never-purchased |
| Q040 | Customers | Hard | Tenure-bucketed LTV snapshot | Combining recency, tenure and monetary value |

## 5. Level 5 — Real Analyst Problems (Q041–Q050)

At least 5 of these are **intentionally ambiguous** (marked AMB) — the
correct first move is naming the assumption you're making, not writing SQL.

| ID | Business Area | Difficulty | Main Concept | Thinking Skill | AMB |
|----|----------------|------------|---------------|-----------------|-----|
| Q041 | Marketing | Hard | Win-back targeting | Defining "at risk" before querying | AMB |
| Q042 | Stores | Hard | Underperformance | Benchmark choice: region avg? prior period? target? | AMB |
| Q043 | Marketing | Expert | Campaign lift | Before/after vs control group, attribution window | AMB |
| Q044 | Products | Hard | Investigation triage | Multiple valid signals (returns, stock, sales trend) | AMB |
| Q045 | Customers | Hard | Segment value | Revenue vs profit vs LTV vs margin | AMB |
| Q046 | Returns | Medium | Rate definition | Denominator choice: per order, per unit, per revenue | AMB |
| Q047 | Marketing | Hard | Channel quality | LTV by acquisition channel |  |
| Q048 | Products | Expert | Return economics | Cost vs price vs return volume |  |
| Q049 | Stores | Medium | Staffing signal | Revenue/orders per employee |  |
| Q050 | Customers | Expert | Churn early-warning | Multi-signal capstone (R + F + M trend) |  |

## 6. Level 6 — Expert Challenges (Q051–Q060)

Question wording does not name the technique — figure it out from the ask.

| ID | Business Area | Difficulty | Main Concept | Thinking Skill | MA |
|----|----------------|------------|---------------|-----------------|----|
| Q051 | Customers | Expert | Longest active streak | Advanced gaps and islands | |
| Q052 | Customers | Expert | Spend-tier journey | Multi-step state transitions across quarters | |
| Q053 | Products | Expert | Second-highest per group | Multi-level ranking, avoiding the naive MAX trap | MA |
| Q054 | Stores | Expert | Rank-of-rank | Month-over-month rank delta | |
| Q055 | Stores | Expert | Anomaly detection | Statistical outliers via AVG/STDDEV window | |
| Q056 | Marketing | Expert | Funnel drop-off | Multi-stage conversion funnel | |
| Q057 | Products | Expert | Market-basket pairs | Self-join on order_items | MA |
| Q058 | Inventory | Expert | Stockout impact | Multi-fact: inventory + sales trend | |
| Q059 | Customers | Expert | Cohort revenue curve | Cumulative revenue by months-since-first-purchase | |
| Q060 | Support | Expert | Cross-fact correlation | Ticket resolution time vs churn | |

## 7. Level 7 — Blind Challenges (Q061–Q080)

Only business context, question, and available tables are given —
deliberately no "Main Concept" column here.

| ID | Business Area | Difficulty |
|----|----------------|------------|
| Q061 | Customers | Expert |
| Q062 | Returns | Hard |
| Q063 | Products | Expert |
| Q064 | Customers | Expert |
| Q065 | Marketing | Hard |
| Q066 | Products | Hard |
| Q067 | Inventory | Hard |
| Q068 | Customers | Expert |
| Q069 | Employees | Expert |
| Q070 | Payments | Medium |
| Q071 | Support | Hard |
| Q072 | Customers | Expert |
| Q073 | Returns | Hard |
| Q074 | Marketing | Expert |
| Q075 | Customers | Hard |
| Q076 | Products | Hard |
| Q077 | Sales | Medium |
| Q078 | Stores | Expert |
| Q079 | Customers | Medium |
| Q080 | Products | Expert |

## 8. Reverse SQL (training/reverse_sql/, RS01–RS10)

Given SQL, no business question. Learner infers grain, metric, pattern,
and a plausible business question.

| ID | Pattern under the hood |
|----|--------------------------|
| RS01 | ROW_NUMBER dedup — latest row per customer |
| RS02 | Correlated subquery detecting a >90-day gap |
| RS03 | GROUP BY + HAVING on a derived sum |
| RS04 | NOT EXISTS anti-join |
| RS05 | Running total via window SUM |
| RS06 | RANK partitioned by region, filtered to top 3 |
| RS07 | CTE + LAG computing % change |
| RS08 | Self-join on order_items (basket pairs) |
| RS09 | Conditional aggregation computing a rate |
| RS10 | Subquery against a global (non-correlated) benchmark |

## 9. Approach Selection (training/approach_selection/, AS01–AS05)

Dedicated "choose and justify" exercises — see CLAUDE.md §19. Distinct
from the MA-flagged questions above, which instead present multiple
solutions *after* the learner has already solved it one way.

| ID | Business Question | Approaches contrasted |
|----|--------------------|--------------------------|
| AS01 | Customers spending above their regional average | CTE+JOIN / window function / correlated subquery |
| AS02 | Customers who never returned a product | NOT EXISTS / LEFT JOIN+IS NULL / NOT IN (and its NULL trap) |
| AS03 | Top-selling product per category | ROW_NUMBER window / correlated subquery with MAX |
| AS04 | Month-over-month revenue change | LAG window / self-join on shifted month / correlated subquery |
| AS05 | Running total of revenue | Window SUM OVER / correlated subquery / session-variable anti-pattern |

## 10. Curriculum totals

- 80 core questions (Q001–Q080)
- 10 reverse SQL exercises
- 5 dedicated approach-selection exercises
- 10 of the 80 core questions carry a documented alternative solution (MA)
- 6 of the Level 5 questions are intentionally ambiguous (AMB)
