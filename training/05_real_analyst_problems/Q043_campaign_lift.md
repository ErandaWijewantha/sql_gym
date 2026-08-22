# Q043 — Did the New Campaign Actually Improve Sales?

## Business Context

A Marketing Director asks: "We ran that big campaign last quarter — did
it actually improve sales?"

## Business Question

Did a specific campaign of your choosing actually improve sales?

## Data Available

campaigns
customer_campaigns
orders
order_items
customers

## Think Before SQL

This is the hardest kind of ambiguous question: it *sounds* answerable
with a single number, but causal attribution is genuinely difficult
with this data alone.

1. What would "improve sales" need to mean, precisely — sales during
   the campaign vs. before it? Sales *by customers the campaign
   touched* vs. customers it didn't touch?
2. Before/after comparison: what confound does this ignore (e.g.,
   seasonality — what if the campaign happened to run during a
   naturally high-revenue month anyway, per the category seasonality
   patterns from Level 1)?
3. Touched-vs-untouched comparison: is a customer who happened to see
   an impression, click, or convert a *random* subset of customers, or
   could campaigns have deliberately targeted higher-value customers to
   begin with (making "touched customers spent more" unsurprising even
   with zero campaign effect)?
4. What does this dataset actually give you to approximate a "control
   group" — is there a clean one, or only a rough approximation?
5. What time window after a campaign interaction would you count as
   "attributable" sales — the campaign's own date range? A fixed window
   afterward (7 days? 30 days)? Forever? Why does this choice matter a
   lot for the final number?
6. If a customer converted (per `customer_campaigns.interaction_type`),
   does that automatically mean the campaign caused a sale, or could
   they have ordered anyway? What would you need to be honest about
   here?
7. Would you present a single "yes/no, it worked" verdict to the
   Marketing Director, or a set of different cuts (before/after,
   touched/untouched, with caveats) and let them weigh the evidence?
8. What's the minimum caveat you'd attach to any number you report,
   given you don't have a true randomized control group?
9. Which of this dataset's available signals (impressions, clicks,
   conversions, order value) would you weight most heavily, and why?
10. Is "no, we can't cleanly answer that with this data" itself ever
    the correct, professional answer to bring back?

## Attempt

Pick one specific campaign, state your chosen comparison method and
its main weakness explicitly, then compute your answer.

[space for learner]
