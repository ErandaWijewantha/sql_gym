# Q056 — Where the Funnel Leaks

## Business Context

Marketing knows overall conversion rates per channel, but wants to know
*where in the funnel* each channel loses the most people — impression
to click, or click to conversion — since the fix for each is different.

## Business Question

For each campaign channel, show the drop-off rate at each stage of the
funnel: impression to click, and click to conversion.

## Data Available

campaigns
customer_campaigns

## Attempt

This question does not tell you the technique. Work through it
yourself first:

- What does one output row represent?
- A "funnel" implies stages that each depend on customers reaching the
  previous stage. What do you need to count at each stage, and for
  which population?
- Is this a per-interaction question, or a per-customer question? Could
  one customer generate multiple impressions for the same campaign, and
  would that change how you count?

[space for learner]
