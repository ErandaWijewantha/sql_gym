# Business Metrics Guide

Every metric below has more than one legitimate definition in the real
world. This gym trains the habit of picking one explicitly and stating
it, rather than assuming everyone means the same thing by "revenue."

---

## Gross Sales

**Definition**: total value of goods sold, before any discounts,
returns, or cancellations are subtracted.
**Formula**: `SUM(quantity * unit_price)`.
**Required grain**: order_items (or any pre-aggregation of it).
**Possible ambiguity**: does it include cancelled/pending orders? Most
uses of "gross sales" implicitly mean *attempted* sales regardless of
fulfillment outcome — but confirm before assuming.
**SQL**: `SUM(oi.quantity * oi.unit_price)` — see Q005 (which
deliberately restricts to completed orders and calls this out).
**Validation**: should be strictly >= net sales for the same population.

---

## Net Sales

**Definition**: gross sales minus discounts.
**Formula**: `SUM(quantity * unit_price - discount_amount)`.
**Required grain**: order_items.
**Possible ambiguity**: does "net" also mean net of returns? Different
companies use "net sales" to mean different combinations of
(discounts) and (discounts + returns) — always state which.
**SQL**: see every "net revenue" computation from Q005 onward.
**Validation**: `net_sales <= gross_sales` always; the gap should be
consistent with the discount rate observed in Q009.

---

## Revenue

**Definition**: deliberately not defined further here — "revenue" is
an umbrella term that, without qualification, could mean gross sales,
net sales, net-of-returns sales, or recognized revenue (a formal
accounting concept this schema doesn't model at all, since it involves
timing rules this dataset doesn't capture). **Always qualify which one
you mean** — see Q046 for a worked example of why this matters.

---

## Discount

**Definition**: the amount subtracted from a line item's list price at
the point of sale.
**Formula**: `order_items.discount_amount` (already a total per line,
not a rate — divide by `quantity * unit_price` to get a percentage).
**Required grain**: order_items.
**Possible ambiguity**: is a discount rate meant per line item, per
order, or per product across all its sales? Each needs a different
denominator.
**SQL**: see Q009 (discount frequency) and Q076 (average discount
depth by category over time).
**Validation**: `discount_amount` should never exceed `quantity *
unit_price` for the same line (would imply a negative sale price).

---

## Returns

**Definition**: units a customer sent back after purchase, recorded
independently of the original sale.
**Formula**: `returns.quantity`, joined back to `order_items` via
(order_id, product_id) to recover the original sale price if a dollar
value is needed.
**Required grain**: returns (order, product level); a return row does
not itself carry price information.
**Possible ambiguity**: return *rate* has at least three distinct valid
denominators — see Q046 for the full breakdown (unit-based,
order-based, revenue-based).
**SQL**: see Q015 (net units sold), Q046 (three return-rate
definitions), Q073 (return timing).
**Validation**: `returns.quantity` should never exceed the quantity
originally purchased on the matching order+product (checked directly
in `database/05_validation.sql`).

---

## COGS (Cost of Goods Sold)

**Definition**: what the business paid (or committed to pay) for the
units it sold.
**Formula**: `SUM(quantity * products.cost)` — note `cost` lives on
`products`, not `order_items`, so this always requires a join.
**Required grain**: order_items joined to products.
**Possible ambiguity**: charged against units sold, or units *kept*
(net of returns)? Q048 works through this exact question explicitly.
**SQL**: see Q048.
**Validation**: `cost < selling_price` should hold for the large
majority of products (by construction in this dataset, margins are
18-45%) — a cost exceeding selling price would be a red flag worth
investigating, not silently trusting.

---

## Gross Profit

**Definition**: net sales minus COGS.
**Formula**: `SUM(quantity * (selling_price - cost)) - SUM(discount_amount)`
— note discounts reduce profit directly, since they reduce what was
actually collected without changing what was paid to acquire the
goods.
**Required grain**: order_items joined to products.
**Possible ambiguity**: should returned units' original margin be
backed out? See Q048's discussion of return economics.
**SQL**: see Q045's approximate margin calculation (and its stated
caveat about discount allocation across units).
**Validation**: gross profit should be less than net sales for any
product with `cost > 0` (margin can't exceed 100% of net sales unless
cost is zero, which doesn't occur in this dataset).

---

## Margin

**Definition**: gross profit expressed as a percentage of net sales
(or sometimes of selling price, at the per-unit level — state which).
**Formula**: `gross_profit / net_sales * 100`, or per-unit:
`(selling_price - cost) / selling_price * 100`.
**Required grain**: whatever grain gross profit and net sales are
computed at (product, category, order, customer — all valid, must
match).
**Possible ambiguity**: margin on gross sales vs. margin on net (post-
discount) sales gives different numbers for the same product.
**SQL**: derive from Gross Profit and Net Sales above at a consistent
grain.
**Validation**: margin percentage should be between 0% and 100% for
any product not sold at a loss; a negative margin is a legitimate,
flaggable result (see Q048), not necessarily a bug.

---

## Average Order Value (AOV)

**Definition**: typical net value of one order.
**Formula**: `SUM(net order value) / COUNT(DISTINCT order_id)` — **not**
a plain `AVG()` taken directly over a table already joined down to
line-item grain (that computes an average *line item* value instead —
see Q016 for the full worked-out trap).
**Required grain**: must be computed at order grain (pre-aggregate
order_items to one row per order first, then average).
**Possible ambiguity**: over which population of orders (completed
only? all statuses?) and over what time window?
**SQL**: see Q008 and Q016.
**Validation**: cross-check total net revenue / total order count
against the AOV figure — they should reconcile exactly for the same
population.

---

## Customer Lifetime Value (CLV / LTV)

**Definition**: total value a customer has generated (historical/
"to-date" version) or is expected to generate (predictive version —
not attempted in this gym, which only computes the historical version).
**Formula**: `SUM(net order value)` across a customer's history,
optionally restricted to completed orders.
**Required grain**: customer.
**Possible ambiguity**: to-date vs. predicted; gross vs. net; does it
include or exclude a customer's very recent, possibly-still-pending
orders?
**SQL**: see Q040 (tenure-bucketed lifetime spend) — note its explicit
survivorship-bias caveat.
**Validation**: no customer's LTV should be negative under a net-of-
discount, completed-orders-only definition.

---

## Retention

**Definition**: the fraction of a starting population that remains
active in a later period.
**Formula**: varies by cohort design — see Q036's month-1 retention and
Q080's category-level retention for two different concrete
implementations.
**Required grain**: cohort x relative-period (see the Cohort Analysis
entry in `docs/sql_pattern_library.md`).
**Possible ambiguity**: "active" could mean any order, any completed
order, or a spend threshold; the relative-period window (next month?
next quarter?) must be stated.
**SQL**: Q036, Q080.
**Validation**: retention percentage must be between 0 and 100; trailing
cohorts that haven't had time to reach the measured relative period
should be excluded or footnoted, not compared at face value (see Q036's
caveat).

---

## Churn

**Definition**: the inverse of retention — customers who stop being
active. This gym treats churn as a *recency-based signal* (Q039) or a
*multi-signal combination* (Q050) rather than a single hard cutoff,
since "churned" vs. "just infrequent" is itself a judgment call.
**Formula**: no single canonical formula in this schema; see Q039 and
Q050 for two different concrete operationalizations.
**Required grain**: customer.
**Possible ambiguity**: entirely — this is one of the most contested
metric definitions in retail/e-commerce; always state the recency
threshold and any secondary signals used.
**SQL**: Q039, Q050.
**Validation**: cross-check a churn flag's threshold sensitivity — how
much does the flagged population change if the threshold moves by 10%?

---

## Conversion (rate)

**Definition**: the fraction of a population that completed a target
action, given exposure to an earlier stage.
**Formula**: `COUNT(DISTINCT converted entities) / COUNT(DISTINCT
exposed entities)`.
**Required grain**: whatever grain the funnel stages are being measured
at (per campaign, per channel — see Q056).
**Possible ambiguity**: counting distinct entities (people) vs. raw
event counts produces different rates if one entity can trigger a
stage multiple times.
**SQL**: Q056 (full funnel), Q065 (clicked-but-not-converted).
**Validation**: conversion count should never exceed the exposure count
it's a fraction of.

---

## Return Rate

See the dedicated three-definition breakdown in Q046 — repeated here
for completeness because it's the gym's canonical example of a metric
with genuinely multiple valid formulas:
- **Unit-based**: `SUM(returned units) / SUM(units sold)`.
- **Order-based**: `COUNT(DISTINCT orders with >=1 return) /
  COUNT(DISTINCT orders)`.
- **Revenue-based**: `SUM(returned units' original sale value) /
  SUM(gross revenue)`.

These can differ substantially depending on whether returns cluster on
high- or low-value items — never report just "the return rate" without
naming which one.

---

## Purchase Frequency

**Definition**: how often a customer buys, over a given window.
**Formula**: `COUNT(orders) / time span`, or simply
`COUNT(orders)` per customer over a fixed window (see Q033's one-time
vs. repeat split, a frequency threshold at the simplest possible
level).
**Required grain**: customer.
**Possible ambiguity**: all orders, or completed only? Fixed calendar
window, or "since first purchase"?
**SQL**: Q033 (frequency segmentation), Q072 (time-to-second-purchase,
a frequency-adjacent measure).
**Validation**: frequency should never be negative or fractional per
the counting method chosen (a count of discrete events).
