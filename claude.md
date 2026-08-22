# CLAUDE.md
# SQL Analytical Thinking Gym

## 1. PROJECT PURPOSE

Build a production-quality local SQL learning environment whose primary purpose is to transform the learner from:

> "I know SQL syntax"

into:

> "I can look at an unfamiliar business problem, decompose it analytically, recognize the SQL pattern required, choose an appropriate approach, write the SQL, validate it, and explain the business meaning."

This is NOT a LeetCode-style SQL question bank.

This is NOT primarily a syntax memorization project.

This is an:

# SQL ANALYTICAL THINKING GYM

The learner should develop the ability to think:

    Business Question
          ↓
    What is actually being asked?
          ↓
    What should one output row represent?
          ↓
    What is the metric?
          ↓
    What data is required?
          ↓
    What transformations are required?
          ↓
    What analytical pattern does this resemble?
          ↓
    What intermediate result should exist?
          ↓
    Which SQL approach expresses it clearly?
          ↓
    Write SQL
          ↓
    Validate
          ↓
    Interpret the business result


============================================================
2. CORE LEARNING PHILOSOPHY
============================================================

The project must teach these principles repeatedly:

### Principle 1 — SQL expertise is pattern recognition

Experts do not memorize every possible SQL query.

They recognize patterns such as:

    Top N within groups
        → ranking / window function

    Previous event
        → LAG

    Next event
        → LEAD

    Running total
        → window aggregation

    Customers who never did X
        → NOT EXISTS / anti-join

    Customers who did X and Y
        → EXISTS / joins / conditional aggregation

    Compare against group average
        → window / aggregate + comparison

    Consecutive periods
        → gaps and islands / date sequencing

    Multi-step analytical problem
        → CTE pipeline

    Remove duplicate business records
        → ROW_NUMBER / deduplication pattern

    Percentage of total
        → numerator / denominator + window or aggregate

The system should train these mental triggers.

---

### Principle 2 — Grain comes before SQL

The learner must repeatedly ask:

> "What does one row represent?"

Examples:

    one row = transaction
    one row = order
    one row = customer
    one row = customer-month
    one row = product-month
    one row = store-day
    one row = customer-product

Many advanced SQL mistakes are actually grain mistakes.

The training system must make grain a first-class concept.

---

### Principle 3 — Business definition comes before implementation

Do not assume metrics.

For example:

"Revenue" could mean:

    gross sales
    net sales
    sales after discounts
    sales after returns
    paid sales
    recognized revenue

The learner should learn to clarify the definition before writing SQL.

---

### Principle 4 — SQL that runs is not necessarily correct

Every important exercise must teach validation.

Ask:

    Could this JOIN duplicate rows?
    Could NULLs change the result?
    Am I double-counting?
    Is the denominator correct?
    Are cancelled orders included?
    Are returned items included?
    Are failed payments included?
    Is the date boundary correct?
    Am I averaging averages?
    Does the output grain match the business question?

---

### Principle 5 — Multiple approaches are valuable

Many SQL problems can be solved with:

    CTE
    subquery
    JOIN
    window function
    EXISTS
    conditional aggregation

Do not teach:

> "There is one correct SQL technique."

Teach:

> "Here are the possible approaches. Which best expresses this problem and why?"

============================================================
3. TARGET TECHNOLOGY
============================================================

Use:

- MySQL 8+
- Docker
- Docker Compose
- Python for deterministic synthetic data generation
- SQL
- MySQL CLI compatibility
- MySQL Workbench compatibility

Everything must run locally.

No external database is required.

Do not introduce unnecessary technologies.

============================================================
4. PROJECT STRUCTURE
============================================================

Create:

sql-analytical-thinking-gym/

├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── database/
│   ├── 01_create_database.sql
│   ├── 02_schema.sql
│   ├── 03_indexes.sql
│   ├── 04_views.sql
│   └── 05_validation.sql
│
├── data_generation/
│   ├── generate_data.py
│   ├── requirements.txt
│   └── README.md
│
├── training/
│   ├── 01_foundations/
│   ├── 02_grain_and_joins/
│   ├── 03_analytical_patterns/
│   ├── 04_time_and_customer_behavior/
│   ├── 05_real_analyst_problems/
│   ├── 06_expert_challenges/
│   └── 07_blind_challenges/
│
├── solutions/
│   ├── 01_foundations/
│   ├── 02_grain_and_joins/
│   ├── 03_analytical_patterns/
│   ├── 04_time_and_customer_behavior/
│   ├── 05_real_analyst_problems/
│   ├── 06_expert_challenges/
│   └── 07_blind_challenges/
│
├── docs/
│   ├── analytical_thinking.md
│   ├── grain.md
│   ├── sql_pattern_library.md
│   ├── business_metrics.md
│   ├── common_mistakes.md
│   ├── approach_selection.md
│   └── progression.md
│
├── progress/
│   ├── progress.csv
│   └── mistake_journal.md
│
└── scripts/
    ├── setup.sh
    ├── reset_db.sh
    └── validate_all_solutions.sh


============================================================
5. BUSINESS DOMAIN
============================================================

Build a realistic synthetic retail/e-commerce business.

The schema must be sufficiently rich to support:

- sales analytics
- customer analytics
- product analytics
- marketing analytics
- store analytics
- inventory analytics
- payment analytics
- returns analytics
- support analytics
- time-series analytics
- retention
- cohorts
- funnels
- behavioral analysis

Do NOT create a toy database.

Use at minimum:

CUSTOMERS

    customer_id
    customer_name
    gender
    date_of_birth
    registration_date
    city
    region
    customer_segment
    acquisition_channel

PRODUCTS

    product_id
    product_name
    category_id
    brand_id
    cost
    selling_price
    launch_date
    status

CATEGORIES

    category_id
    category_name

BRANDS

    brand_id
    brand_name

STORES

    store_id
    store_name
    city
    region
    store_type

EMPLOYEES

    employee_id
    store_id
    employee_role
    hire_date

ORDERS

    order_id
    customer_id
    store_id
    order_date
    order_status
    sales_channel
    payment_method

ORDER_ITEMS

    order_id
    product_id
    quantity
    unit_price
    discount_amount

PAYMENTS

    payment_id
    order_id
    payment_date
    amount
    payment_status
    payment_method

RETURNS

    return_id
    order_id
    product_id
    return_date
    quantity
    return_reason

INVENTORY

    store_id
    product_id
    inventory_date
    opening_stock
    received_quantity
    sold_quantity
    closing_stock

CAMPAIGNS

    campaign_id
    campaign_name
    channel
    start_date
    end_date
    budget

CUSTOMER_CAMPAIGNS

    customer_id
    campaign_id
    interaction_date
    interaction_type

SUPPORT_TICKETS

    ticket_id
    customer_id
    created_at
    resolved_at
    issue_type
    priority
    status


============================================================
6. DATA GENERATION
============================================================

Generate a meaningful synthetic dataset.

Minimum target:

    customers       >= 10,000
    products        >= 1,000
    categories      >= 20
    brands          >= 50
    stores          >= 30
    employees       >= 300
    orders          >= 100,000
    order_items     >= 300,000
    payments        >= 100,000
    returns         >= 10,000
    campaigns       >= 30
    interactions    >= 50,000
    support tickets >= 30,000

Generate at least 24 months of historical data.

Use a deterministic random seed.

The data must contain realistic patterns rather than uniform randomness.

Examples:

- high-value customers
- one-time customers
- repeat customers
- dormant customers
- best-selling products
- poor-performing products
- seasonal categories
- high-performing stores
- low-performing stores
- different customer segments
- successful campaigns
- unsuccessful campaigns
- failed payments
- cancelled orders
- returns
- stock shortages
- customers with long purchase gaps
- customers with frequent purchases

============================================================
7. IMPORTANT EDGE CASES
============================================================

Intentionally create realistic analytical edge cases.

Examples:

- customers with no orders
- products never sold
- stores with very low sales
- customers with exactly one order
- customers with many orders
- tied revenue values
- multiple orders on the same day
- multiple products in one order
- cancelled orders
- failed payments
- partial returns
- full returns
- NULL customer attributes
- campaigns with no meaningful conversion
- products with zero closing stock
- periods with zero sales

Do NOT break referential integrity.

The difficulty should come from analytical reasoning, not corrupted data.

============================================================
8. THE 80-PROBLEM CURRICULUM
============================================================

Create exactly 80 core challenges.

Do NOT create 100 repetitive questions.

The curriculum should contain:

    Level 1 — Foundations                 10
    Level 2 — Grain & Joins               10
    Level 3 — Analytical Patterns         10
    Level 4 — Time & Customer Behavior    10
    Level 5 — Real Analyst Problems       10
    Level 6 — Expert Challenges           10
    Level 7 — Blind Challenges            20

TOTAL = 80


============================================================
9. LEVEL 1 — FOUNDATIONS
============================================================

Questions 1–10.

Teach:

- SELECT
- WHERE
- ORDER BY
- LIMIT
- CASE
- GROUP BY
- HAVING
- basic aggregations
- basic joins
- basic business metrics

The learner should begin translating business questions into SQL operations.

Do not make these syntax drills.

Example:

"Which product categories generated more than LKR X in sales last quarter?"

The learner should identify:

    output grain = category
    metric = sales
    transformation = aggregation
    filtering = HAVING


============================================================
10. LEVEL 2 — GRAIN & JOINS
============================================================

Questions 11–20.

This level is extremely important.

Teach:

- fact table vs dimension
- one-to-many relationships
- many-to-one
- join duplication
- INNER JOIN
- LEFT JOIN
- self JOIN
- COUNT vs COUNT(DISTINCT)
- aggregation before/after joins
- customer/order/order-item grain

Include questions designed to cause incorrect answers if grain is misunderstood.

For example:

A naive join between:

    orders
    order_items
    payments

should create potential duplication.

Teach why.

The learner must learn:

> "Before I JOIN another table, I need to understand its grain."


============================================================
11. LEVEL 3 — ANALYTICAL PATTERNS
============================================================

Questions 21–30.

Teach recognition of:

- ROW_NUMBER
- RANK
- DENSE_RANK
- LAG
- LEAD
- running totals
- moving averages
- percentage of total
- above/below group benchmark
- EXISTS / NOT EXISTS
- conditional aggregation

The objective is:

Business wording → mental pattern.

Examples:

    "Top 3 in each category"
        → ranking within group

    "Previous month"
        → LAG

    "Never purchased"
        → NOT EXISTS / anti-join

    "Percentage of category sales"
        → numerator / denominator

    "Running sales"
        → window aggregation


============================================================
12. LEVEL 4 — TIME & CUSTOMER BEHAVIOR
============================================================

Questions 31–40.

Teach:

- customer lifetime behavior
- first purchase
- latest purchase
- recency
- purchase frequency
- repeat customers
- inactive customers
- retention
- cohorts
- period-over-period change
- consecutive periods
- gaps
- behavioral segmentation

Examples:

"Which customers purchased in January but not in February?"

"Which customers increased their spending for three consecutive months?"

"Which customers have not purchased in 90 days?"

"Which products declined for three consecutive months?"

The learner should recognize time and sequence patterns.


============================================================
13. LEVEL 5 — REAL ANALYST PROBLEMS
============================================================

Questions 41–50.

These must sound like actual stakeholder requests.

Examples:

    "Which customers should Marketing target?"

    "Which stores are underperforming?"

    "Did the new campaign actually improve sales?"

    "Which products should Operations investigate?"

    "Which customer segment is most valuable?"

The questions should require the learner to think about:

- metric definitions
- business assumptions
- denominator
- population
- time period
- exclusions
- edge cases

At least 5 of these questions should intentionally be ambiguous.

The correct analytical behavior may be:

> "I cannot answer this correctly until I clarify the definition."


============================================================
14. LEVEL 6 — EXPERT CHALLENGES
============================================================

Questions 51–60.

These should require multi-step reasoning.

Examples:

- gaps and islands
- consecutive activity
- complex customer journeys
- advanced cohort analysis
- multi-level ranking
- nested analytical transformations
- product/category comparisons
- complex time-series analysis
- anomaly identification
- multiple fact-table analysis

Questions should NOT reveal the expected SQL technique.

The learner must discover it.


============================================================
15. LEVEL 7 — BLIND CHALLENGES
============================================================

Questions 61–80.

This is the most important level.

Do NOT categorize the SQL technique.

Do NOT tell the learner:

    "This is a window function problem."

Do NOT tag the question visibly with:

    #window-function

Instead provide only:

    Business context
    Business question
    Available tables

The learner must determine:

- grain
- metric
- required data
- transformations
- SQL pattern
- approach

These questions should simulate a real analytics job.

============================================================
16. QUESTION FORMAT
============================================================

Every question should have its own QUESTION.md.

Example:

# Q034 — Customer Reactivation

## Business Context

Marketing wants to identify customers who returned after a prolonged period of inactivity.

## Business Question

Identify customers whose latest purchase occurred after a gap of at least 90 days.

## Data Available

customers
orders
order_items

## Think Before SQL

Do not write SQL yet.

Answer:

1. What does one output row represent?
2. What is the business metric?
3. What event defines customer activity?
4. What is the relevant time sequence?
5. Do we need the first event, last event, or previous event?
6. What intermediate dataset would help?
7. Are we comparing rows?
8. Are we comparing time periods?
9. What SQL pattern might represent this?
10. What edge cases exist?

## Attempt

[space for learner]

Do not reveal the SQL here.


============================================================
17. SOLUTION FORMAT
============================================================

Every question gets a separate solution.

Example:

solutions/04_time_and_customer_behavior/Q034_solution.md

Structure:

# Reasoning

## 1. Interpret the Business Question

Explain what the business actually wants.

## 2. Output Grain

Explicitly state:

    One row = ...

## 3. Metric Definition

Explain exactly what is measured.

## 4. Required Data

List tables and relevant columns.

## 5. Logical Decomposition

Example:

    Step 1 → identify customer purchases
    Step 2 → order them chronologically
    Step 3 → calculate previous purchase date
    Step 4 → calculate gap
    Step 5 → filter gap >= 90 days

## 6. Pattern Recognition

Explain the mental trigger.

Example:

    "Compare current event with previous event"
        → LAG

## 7. SQL

Provide professional MySQL 8 SQL.

## 8. Walkthrough

Explain the query.

## 9. Validation

Explain how to verify correctness.

## 10. Edge Cases

Explain possible problems.

## 11. Alternative Approach

Where useful, provide another valid solution.

## 12. Trade-offs

Explain:

- readability
- maintainability
- performance
- correctness

## 13. Business Interpretation

Explain what the business can learn.


============================================================
18. DO NOT REVEAL PATTERNS TOO EARLY
============================================================

For Levels 1–6:

Hints may progressively reveal thinking.

Use:

    Hint 1 — Business interpretation
    Hint 2 — Grain
    Hint 3 — Decomposition
    Hint 4 — Pattern
    Hint 5 — SQL direction

Do not immediately reveal:

    "Use ROW_NUMBER."

The learner should discover it.

For Level 7 blind challenges:

Do not provide pattern hints before the attempt.


============================================================
19. APPROACH SELECTION TRAINING
============================================================

Create dedicated exercises where the learner chooses between approaches.

Example:

Business Question:

"Find customers whose spending is above their regional average."

Possible approaches:

    A — CTE + JOIN
    B — Window Function
    C — Correlated Subquery

The learner must choose one and explain why.

Then reveal:

- all valid approaches
- strengths
- weaknesses
- readability
- performance considerations
- maintainability

Teach:

> There is rarely one universally correct SQL solution.


============================================================
20. SAME PROBLEM, MULTIPLE SOLUTIONS
============================================================

At least 10 questions must have multiple reasonable solutions.

For example:

    CTE
    vs
    subquery
    vs
    window function

The goal is to develop SQL judgment.

After solving, ask:

> "Which version would you use in production and why?"


============================================================
21. REVERSE SQL TRAINING
============================================================

Create a separate folder:

training/reverse_sql/

Create at least 10 reverse-engineering exercises.

Give the learner SQL.

Do NOT give the business question.

The learner must infer:

- what the query is calculating
- output grain
- metric
- analytical pattern
- likely business question

This develops:

    SQL → analytical reasoning


============================================================
22. PATTERN RECOGNITION LIBRARY
============================================================

Create:

docs/sql_pattern_library.md

For each pattern explain:

1. Mental trigger
2. Business wording
3. Grain before
4. Grain after
5. SQL techniques
6. Example
7. Common mistakes
8. Alternative approaches
9. Performance considerations

Include at least:

- filtering
- aggregation
- conditional aggregation
- joins
- anti-joins
- EXISTS
- NOT EXISTS
- subqueries
- CTEs
- ROW_NUMBER
- RANK
- DENSE_RANK
- LAG
- LEAD
- running totals
- moving averages
- percentage of total
- cohort analysis
- retention
- gaps and islands
- funnel analysis
- deduplication
- anomaly detection


============================================================
23. GRAIN GUIDE
============================================================

Create:

docs/grain.md

Explain:

    What is grain?
    Why does it matter?
    How to identify it?
    How JOINs change grain?
    How aggregation changes grain?
    How window functions preserve grain?

Include concrete examples.

Show:

    transaction grain
    order grain
    customer grain
    customer-month grain
    product-month grain

Demonstrate double-counting caused by incorrect grain.


============================================================
24. BUSINESS METRICS GUIDE
============================================================

Create:

docs/business_metrics.md

Define:

- gross sales
- net sales
- revenue
- discount
- returns
- COGS
- gross profit
- margin
- average order value
- customer lifetime value
- retention
- churn
- conversion
- return rate
- purchase frequency

For each metric explain:

    Definition
    Formula
    Required grain
    Possible ambiguity
    SQL implementation
    Validation


============================================================
25. COMMON MISTAKES
============================================================

Create:

docs/common_mistakes.md

Include:

- duplicate rows after JOIN
- COUNT vs COUNT DISTINCT
- LEFT JOIN becoming INNER JOIN
- WHERE vs HAVING
- NULL handling
- incorrect window partition
- incorrect ordering
- ranking ties
- incorrect date boundaries
- double-counting
- average of averages
- incorrect denominator
- filtering too early
- filtering too late
- using DISTINCT to hide a bad join
- aggregating at the wrong grain


============================================================
26. ANALYTICAL THINKING GUIDE
============================================================

Create:

docs/analytical_thinking.md

Teach this framework:

    1. Understand the question
    2. Define the business metric
    3. Define the output grain
    4. Identify relevant entities
    5. Identify relevant events
    6. Identify time dimension
    7. Build intermediate result
    8. Identify transformation pattern
    9. Choose SQL approach
    10. Validate
    11. Interpret

Emphasize:

> Think in transformations, not SQL keywords.


============================================================
27. THINKING SCORE
============================================================

Every question should support a score from 0–10.

Score separately:

THINKING SCORE

    0–2
    Cannot decompose the problem.

    3–4
    Understands some requirements but misses grain/pattern.

    5–6
    Correct grain and basic decomposition.

    7–8
    Correct pattern and approach.

    9
    Correct reasoning, SQL and validation.

    10
    Correct reasoning + alternative approach + business interpretation.

SQL SCORE

    0–10

BUSINESS UNDERSTANDING SCORE

    0–10


============================================================
28. PROGRESS TRACKING
============================================================

Create:

progress/progress.csv

Columns:

    question_id
    date
    thinking_score
    sql_score
    business_score
    pattern_identified
    pattern_correct
    grain_correct
    validation_done
    mistake_type
    time_minutes
    notes

Create:

progress/mistake_journal.md

Template:

# Question

# My Thinking

# Where I Went Wrong

# Correct Thinking

# Pattern I Missed

# Grain Mistake

YES / NO

# Business Definition Mistake

YES / NO

# SQL Syntax Mistake

YES / NO

# Join Mistake

YES / NO

# Lesson

# Next Time I See...


============================================================
29. QUESTION INDEX
============================================================

Create:

training/QUESTION_INDEX.md

Columns:

| ID | Level | Business Area | Difficulty | Main Concept | Thinking Skill |
|----|-------|---------------|------------|--------------|----------------|

Do NOT expose SQL pattern tags for blind challenges.


============================================================
30. DATA VALIDATION
============================================================

Create:

database/05_validation.sql

Check:

- primary key uniqueness
- foreign key consistency
- null patterns
- row counts
- duplicate business keys
- order/item consistency
- payment consistency
- return consistency

Also create Python validation where useful.


============================================================
31. SOLUTION VALIDATION
============================================================

Every solution must be executable.

Create:

scripts/validate_all_solutions.sh

The system should execute all SQL solutions against MySQL.

Fix every failing query.

Do not declare the project complete until all solutions execute successfully.

For expected-result validation, where practical, include sanity checks such as:

- row count > 0
- expected columns exist
- no impossible values
- totals within reasonable ranges


============================================================
32. README
============================================================

Create a comprehensive README explaining:

- project purpose
- learning philosophy
- architecture
- setup
- Docker usage
- database connection
- how to practice
- how to score yourself
- how to maintain mistake journal
- curriculum
- progression
- how to run validation

Most importantly explain:

> DO NOT look at the solution immediately.

Recommended workflow:

    1. Read question
    2. Close solution
    3. Write thinking
    4. Identify grain
    5. Identify metric
    6. Decompose
    7. Predict pattern
    8. Write SQL
    9. Run SQL
    10. Validate
    11. Read solution
    12. Compare reasoning
    13. Try alternative
    14. Record mistake


============================================================
33. QUALITY REQUIREMENTS
============================================================

The project must NOT contain:

- repetitive questions
- artificial syntax drills
- meaningless toy data
- solutions that only show SQL
- unexplained magic queries
- incorrect business metrics
- broken SQL
- questions with impossible data requirements
- ambiguous questions without acknowledging ambiguity

The project MUST contain:

- realistic business scenarios
- meaningful synthetic data
- progressive difficulty
- grain-focused exercises
- analytical pattern recognition
- multiple approaches
- validation
- business interpretation
- ambiguity
- expert-level problems
- blind problems


============================================================
34. FINAL CURRICULUM DISTRIBUTION
============================================================

The final curriculum must be:

Q001–Q010
FOUNDATIONS

Q011–Q020
GRAIN & JOINS

Q021–Q030
ANALYTICAL PATTERNS

Q031–Q040
TIME & CUSTOMER BEHAVIOR

Q041–Q050
REAL ANALYST PROBLEMS

Q051–Q060
EXPERT CHALLENGES

Q061–Q080
BLIND CHALLENGES


Additionally:

Reverse SQL:
10 exercises

Multiple-approach exercises:
10+ of the main 60

Ambiguous business questions:
at least 5

============================================================
35. FINAL VALIDATION CHECKLIST
============================================================

Before completing the project, verify:

[ ] Docker starts
[ ] MySQL starts
[ ] Database initializes
[ ] Schema loads
[ ] Data loads
[ ] Foreign keys work
[ ] Indexes work
[ ] Dataset contains realistic volumes
[ ] 80 core challenges exist
[ ] 80 solutions exist
[ ] Reverse SQL exercises exist
[ ] All solutions execute
[ ] Questions are non-repetitive
[ ] Grain is explicitly trained
[ ] Business metric definition is trained
[ ] Window functions are trained
[ ] CTEs are trained
[ ] Subqueries are trained
[ ] EXISTS / NOT EXISTS are trained
[ ] Time-series analysis is trained
[ ] Customer behavior is trained
[ ] Cohort analysis is trained
[ ] Gaps and islands are trained
[ ] Multiple approaches are trained
[ ] Ambiguity is trained
[ ] Validation is trained
[ ] Mistake journal exists
[ ] Progress tracker exists
[ ] Documentation exists


============================================================
36. IMPORTANT IMPLEMENTATION RULE
============================================================

Do not simply generate all files immediately without thinking about curriculum quality.

Work in this order:

PHASE 1
Design business domain and schema.

PHASE 2
Design data-generation strategy.

PHASE 3
Generate database and validate it.

PHASE 4
Design all 80 questions at a curriculum level.

Before writing SQL solutions, review the question progression and ensure that each question teaches a distinct analytical idea.

PHASE 5
Generate questions.

PHASE 6
Generate solutions.

PHASE 7
Execute every solution.

PHASE 8
Review questions for:

- repetition
- inappropriate difficulty
- missing reasoning
- bad business assumptions
- grain problems

PHASE 9
Fix everything.

PHASE 10
Create documentation.

PHASE 11
Run final validation.

Only then declare the project complete.


============================================================
37. THE ULTIMATE LEARNING OBJECTIVE
============================================================

The learner should eventually be able to encounter a completely unfamiliar question such as:

> "Management wants to understand which customers are becoming less valuable even though they are still purchasing."

and NOT immediately think:

    "Which SQL query do I use?"

Instead they should think:

    What does "less valuable" mean?

    Revenue?
    Profit?
    Frequency?
    AOV?

    What is the time period?

    What is the customer grain?

    Do I need customer-month?

    Do I need to compare current period with previous period?

    Do I need LAG?

    Do I need a rolling metric?

    What population should be included?

    How do I validate the result?

Only after those questions should SQL begin.

That is the skill this project is designed to build.

The goal is NOT:

> "I can write complicated SQL."

The goal is:

> "Give me a business problem I have never seen before, and I can figure out how to solve it with SQL."