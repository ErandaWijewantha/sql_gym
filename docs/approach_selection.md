# Approach Selection

## There is rarely one universally correct SQL solution

Many problems in this gym can be solved with a CTE, a subquery, a JOIN,
a window function, or `EXISTS` — often several of these at once, in
combination. This document is the general framework; see
`training/approach_selection/` for five dedicated exercises that apply
it, and note that at least ten of the main 80 questions (flagged "MA"
in `training/QUESTION_INDEX.md`) also carry a documented alternative
solution in their own solution file.

## The four questions to ask when choosing an approach

**1. What does each approach actually compute, step by step?**
Before comparing performance or style, make sure every candidate
approach produces the *same* correct result under the *same* edge
cases (ties, NULLs, gaps). An elegant approach that's subtly wrong
under a tie (AS03) or a NULL (AS02) isn't a real alternative.

**2. How does it behave at the boundaries?**
Every approach in this gym's comparisons is stress-tested against a
specific edge case: a tie for first place, a gap month, a NULL in a
subquery's result. These boundaries are usually where two
"equivalent-looking" approaches actually diverge.

**3. How readable is it to someone who didn't write it?**
A CTE + JOIN is usually the most readable to someone unfamiliar with
window functions, at the cost of more steps. A window function is
often more compact once a team is fluent in it. A correlated subquery
often reads closest to the original English sentence, at a real
performance cost. None of these is "the best" independent of who's
going to maintain the query.

**4. How does it perform, and does that matter here?**
A correlated subquery re-evaluated per outer row is usually the most
expensive of the common alternatives — fine for a one-off analysis
over a few thousand rows, potentially a real problem at production
scale. Always ask whether this query will run once, or run on every
dashboard refresh.

## The five approach-selection exercises

| ID | Question | What's contrasted |
|---|---|---|
| AS01 | Above regional average | CTE+JOIN vs window function vs correlated subquery |
| AS02 | Never returned a product | NOT EXISTS vs LEFT JOIN+IS NULL vs NOT IN (and its NULL trap) |
| AS03 | Top product per category | ROW_NUMBER/RANK window vs correlated MAX subquery |
| AS04 | Month-over-month change | LAG window vs self-join on shifted month vs correlated subquery |
| AS05 | Running total | Window SUM OVER vs correlated subquery vs legacy session-variable accumulator |

## After solving it one way: the follow-up question

Once you've solved a problem with your first instinct, ask: **"Which
version would I actually put into production, and why?"** — not as a
rhetorical exercise, but because the answer forces you to weigh
readability, correctness under edge cases, and performance against
each other explicitly, rather than defaulting to whatever syntax you
happen to reach for out of habit.
