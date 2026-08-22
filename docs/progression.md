# Progression

## How difficulty escalates across the 7 levels

| Level | What's new | What's taken away |
|---|---|---|
| 1. Foundations | SELECT/WHERE/GROUP BY/HAVING/CASE, first encounter with metric ambiguity (Q005) | nothing yet — pure mechanics |
| 2. Grain & Joins | fact vs. dimension, join fan-out, correct aggregation grain | the assumption that a JOIN can't silently break a SUM |
| 3. Analytical Patterns | window functions, EXISTS/NOT EXISTS, conditional aggregation | explicit step-by-step scaffolding starts thinning |
| 4. Time & Customer Behavior | recency/frequency/cohorts/gaps-and-islands, a fixed reference date instead of NOW() | the luxury of a single-table answer — most questions need 2+ concepts combined |
| 5. Real Analyst Problems | ambiguous stakeholder language, multiple valid metric definitions | the assumption that the question is already well-posed |
| 6. Expert Challenges | multi-step reasoning, undisclosed technique in the wording | the "Think Before SQL" numbered hints — you're on your own |
| 7. Blind Challenges | full job simulation: context + question + tables only | everything except the data model itself |

## What "harder" actually means here

It is **not** simply "longer SQL." Difficulty escalates along four
independent axes, and later levels usually combine more than one at
once:

- **Grain complexity**: how many pre-aggregation steps are needed
  before a safe join is possible (Level 2 onward).
- **Pattern novelty**: how far the required SQL construct is from
  something already directly named in an earlier level (Level 3
  introduces the vocabulary; Level 6-7 expect you to recognize it
  without being told).
- **Definitional ambiguity**: how much of the work is deciding what the
  question even means before any SQL is possible (Level 5's core
  theme, revisited throughout Level 6-7).
- **Composition**: how many earlier patterns must be combined in one
  query (Level 4's Q050 and Level 6 generally).

## How to use levels if you get stuck

If a question feels impossible, check which axis is actually blocking
you:

- Can't get the join right? → re-read `docs/grain.md`, revisit Level 2.
- Recognize the shape but not the syntax? → check
  `docs/sql_pattern_library.md` for the matching mental trigger.
- Can't tell what's even being asked? → that's the point at Level 5+;
  write down your assumption explicitly and answer *that* version,
  same as the model solutions do.
- The question combines three things you each know separately? →
  decompose it into named CTEs, one per sub-question, before trying to
  write one query end to end.

## Suggested pacing

There's no required schedule, but a reasonable cadence for someone
working through this gym alongside other commitments:

- Levels 1-2: until grain reasoning feels automatic, not just
  "gettable with effort" — don't rush this, it's the foundation
  everything else depends on.
- Level 3: until you can name the pattern from the business wording
  before opening `docs/sql_pattern_library.md`.
- Level 4-5: expect these to take noticeably longer per question than
  Levels 1-3 — that's expected, not a sign you're doing something
  wrong.
- Level 6-7: attempt these cold, without re-reading earlier levels'
  solutions first, to genuinely test whether the pattern recognition
  has become automatic.

## Signs you're ready for the next level

- You state the output grain before writing any SQL, without being
  prompted to.
- You can predict, before running a query, whether a JOIN will fan out.
- You've been wrong at least once in a way that taught you something
  concrete (logged in `progress/mistake_journal.md`) — being wrong is
  part of the curriculum, not a detour from it.
