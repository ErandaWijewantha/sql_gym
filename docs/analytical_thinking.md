# Analytical Thinking Framework

This is the mental sequence this entire gym is built to train. Every
question in `training/` is meant to be worked through in this order —
resist the urge to skip to step 9.

## The 11 steps

**1. Understand the question.**
Read it twice. What is the business actually asking, in plain
language, before any thought of tables or columns? If you can't
restate the question in your own words, you don't understand it yet.

**2. Define the business metric.**
What exact quantity answers the question? "Revenue" is not a metric
until you've decided gross, net, or something else (see
`docs/business_metrics.md`). Write the formula down in words before
writing any SQL.

**3. Define the output grain.**
Say, explicitly: "one row = ___." Every mistake in Level 2 traces back
to skipping this step. See `docs/grain.md`.

**4. Identify relevant entities.**
Which real-world things does this question involve — customers,
products, stores, orders? These map to your dimension and fact tables.

**5. Identify relevant events.**
What actions or transactions matter — a purchase, a return, a support
ticket, a campaign click? Events are usually fact-table rows.

**6. Identify the time dimension.**
Is this a point-in-time snapshot, a period comparison, a trend, a
recency measure, or a sequence? Time-shaped questions need a time-
shaped answer — see the LAG/LEAD/running-total/gaps-and-islands entries
in `docs/sql_pattern_library.md`.

**7. Build the intermediate result.**
What table would make the final step trivial if it already existed?
Usually this is a pre-aggregation to the right grain (Level 2's core
lesson) — build it explicitly as a CTE, named for what it represents.

**8. Identify the transformation pattern.**
Now, and only now, ask "what does this remind me of?" — ranking? an
anti-join? a running total? See `docs/sql_pattern_library.md` for the
full catalog of mental triggers.

**9. Choose a SQL approach.**
There is often more than one valid way to express the pattern you
identified (CTE vs. subquery vs. window function) — see
`docs/approach_selection.md`. Pick one deliberately, not by habit.

**10. Validate.**
Could this JOIN duplicate rows? Are NULLs handled? Is the denominator
right? Does the output grain match what you said in step 3? See
`docs/common_mistakes.md`.

**11. Interpret.**
What does the result actually tell the business? What would you say
out loud to the person who asked the question — including any caveats
about the assumptions you made along the way?

## The core discipline

> Think in transformations, not SQL keywords.

A SQL keyword (`JOIN`, `GROUP BY`, `WINDOW`) is a tool for expressing a
transformation you've already decided you need — not a starting point.
"I'll use a window function" is not a plan; "I need to compare each row
to a group-level benchmark without collapsing the row" is a plan, and
a window function is one way (of several) to execute it.

## Why this order matters

Steps 1-7 require zero SQL knowledge. If you find yourself stuck,
check which step you actually skipped — almost every "I don't know
what query to write" moment is really an unresolved step 2, 3, or 6,
not a missing SQL trick.
