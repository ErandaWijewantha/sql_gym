# SQL Analytical Thinking Gym

A local SQL training environment for going from "I know SQL syntax" to
"I can take an unfamiliar business question, figure out what it's
really asking, and write correct, validated SQL to answer it." Runs
against your own local MySQL 8 install.

This is not a LeetCode-style question bank. See `claude.md` for the
full design brief and learning philosophy this project is built around.

## Learning philosophy

Every question is meant to be worked through this chain of thought:

```
Business Question → What's actually being asked? → What is one output
row? → What is the metric? → What data is required? → What analytical
pattern does this resemble? → What SQL approach expresses it? → Write
SQL → Validate → Interpret the business result
```

Read `docs/analytical_thinking.md`, `docs/grain.md`, and
`docs/sql_pattern_library.md` before starting the curriculum.

## Architecture

```
database/          schema, indexes, views, validation SQL (MySQL 8)
data_generation/    deterministic synthetic data generator (Python)
training/           80 core questions + reverse SQL + approach-selection exercises
solutions/          one solution file per question, same structure
docs/               pattern library, grain guide, business metrics, common mistakes
progress/           your own progress tracker + mistake journal
scripts/            setup / reset / solution-validation helper scripts
```

---

## Getting started (one-time setup)

**Already done in this environment** — the `sql_gym` database exists on
your local MySQL, the schema is loaded, and the full dataset is
generated. Skip straight to "Ongoing: how to practice" below.

If you're setting this up somewhere new (a different machine, or after
wiping the database), here's the full sequence:

```bash
cp .env.example .env
# Edit .env: set MYSQL_ROOT_PASSWORD to your local MySQL root password
# (used once, for bootstrap only), and adjust MYSQL_PORT if your local
# server isn't on the default 3306.

scripts/bootstrap_local_mysql.sh   # creates the sql_gym DB + gym_user account
# then blank MYSQL_ROOT_PASSWORD back out in .env -- it isn't needed again

mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym < database/01_create_database.sql
mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym < database/02_schema.sql
mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym < database/03_indexes.sql
mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym < database/04_views.sql

cd data_generation
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python generate_data.py
```

`scripts/setup.sh` automates the Python/data-generation half.
`scripts/reset_db.sh` reapplies the schema and regenerates fresh data
in one step, any time you want a clean slate — the seed is fixed, so
you always get back the exact same dataset.

If your `mysql` client isn't on `PATH` (common on Windows even after
installing MySQL Server), use the full path, typically:
`"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"`.

**Connecting:**

```bash
mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym    # password: gym_pw (see .env)
```

Or connect with MySQL Workbench using the same host/port/credentials.

The dataset spans **2024-01-01 to 2025-12-31** (24 months). Treat
**2025-12-31** as "today" for any recency question — see
`data_generation/README.md` for why the data doesn't use `CURDATE()`.

---

## Ongoing: how to practice

This is the loop you repeat for every one of the 80 questions (plus
the reverse-SQL and approach-selection exercises). **Do not open the
solution first** — the whole point is the struggle before the SQL.

1. Open `training/QUESTION_INDEX.md`, pick the next question in order
   (start at Q001 if you haven't begun), and read
   `training/<level>/Q0XX_*.md` — business context + question only.
2. Close the solution. Answer the "Think Before SQL" questions in
   writing: grain, metric, required data, decomposition, likely
   pattern. (Levels 6-7 deliberately don't give you these prompts —
   work them out yourself.)
3. Predict which SQL pattern this resembles — check
   `docs/sql_pattern_library.md` if you're unsure what a pattern even
   is, but try to name it yourself first.
4. Write your SQL. Run it against `sql_gym` (any client — `mysql` CLI,
   MySQL Workbench, whatever you're comfortable with).
5. Validate your own result before peeking: could this JOIN duplicate
   rows? Are NULLs handled? Is the denominator right? (see
   `docs/common_mistakes.md`)
6. Only now open `solutions/<level>/Q0XX_solution.md`. Compare your
   *reasoning*, not just your SQL, against theirs — the 13-section
   structure (grain, metric, decomposition, pattern, validation,
   edge cases, business interpretation) is the actual point.
7. Try the alternative approach where one is given.
8. Score yourself (below) and log any real miss in
   `progress/mistake_journal.md` while it's still fresh.

### Scoring yourself

Every question supports three 0–10 scores — record them in
`progress/progress.csv` (one row per attempt):

- **Thinking score** — did you correctly identify grain, metric, and
  pattern before writing SQL? (0–2 couldn't decompose it at all; 9–10
  correct reasoning + validation + business interpretation)
- **SQL score** — does the query run and produce the right result?
- **Business understanding score** — do you actually know what the
  output means for the business, including its caveats?

### Mistake journal

When you get something wrong (wrong pattern, wrong grain, wrong
assumption, a JOIN that silently duplicated rows), copy the template
from `progress/mistake_journal.md` and fill it in immediately. Re-read
your accumulated entries before starting each new level — patterns in
your own mistakes are worth more than any single solution's write-up.

### Curriculum map

See `training/QUESTION_INDEX.md` for the full 80-question map across
7 levels, plus the reverse-SQL and approach-selection tracks. Levels
get progressively less guided:

| Level | Range | What's trained |
|-------|-------|-----------------|
| 1 Foundations | Q001–Q010 | SELECT/WHERE/GROUP BY/HAVING/CASE, basic metrics |
| 2 Grain & Joins | Q011–Q020 | fact vs dimension, join fan-out, grain-correct aggregation |
| 3 Analytical Patterns | Q021–Q030 | window functions, EXISTS/NOT EXISTS, conditional aggregation |
| 4 Time & Customer Behavior | Q031–Q040 | recency/frequency, cohorts, gaps and islands |
| 5 Real Analyst Problems | Q041–Q050 | ambiguous stakeholder asks, definition-first thinking |
| 6 Expert Challenges | Q051–Q060 | multi-step reasoning, undisclosed technique |
| 7 Blind Challenges | Q061–Q080 | full simulation: context + question only |

Once you finish the core 80, do `training/reverse_sql/` (given SQL, no
question — infer the business intent) and
`training/approach_selection/` (compare 2-3 valid ways to solve the
same problem) — see `docs/progression.md` for pacing suggestions and
`docs/approach_selection.md` for how to think about choosing between
approaches.

### Validating solutions

```bash
scripts/validate_all_solutions.sh
```

Extracts and executes every solution's SQL against the live database
and reports PASS/FAIL per question — useful after you edit or add a
solution, or just to confirm your local database is in a working
state.

### Data validation

```bash
mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym < database/05_validation.sql
```

Checks referential integrity, grain uniqueness, inventory-ledger
arithmetic, and prints row counts for a sanity check against the
volumes in `claude.md` §6. Run this any time you suspect the data
might be in a weird state, or after `scripts/reset_db.sh`.
