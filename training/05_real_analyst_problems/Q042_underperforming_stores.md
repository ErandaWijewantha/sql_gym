# Q042 — Which Stores Are Underperforming?

## Business Context

The VP of Retail Operations asks: "Give me a list of underperforming
stores before the quarterly review."

## Business Question

Which stores are underperforming?

## Data Available

orders
order_items
stores
employees

## Think Before SQL

This question is **deliberately underspecified**.

1. "Underperforming" relative to *what*? List at least three candidate
   benchmarks: (a) other stores of the same type/region, (b) their own
   prior period, (c) a fixed target/budget number (which this dataset
   doesn't actually have — worth noticing that absence).
2. Is raw total revenue a fair comparison across stores of different
   types (`flagship` vs `outlet` vs `online`)? What would a fairer
   normalized measure look like (e.g., revenue per employee, revenue
   per square foot — do we even have that data)?
3. Does "underperforming" mean low absolute revenue, declining revenue
   trend, or low revenue *relative to store type peers*? Each implies
   a different query shape entirely.
4. Should a brand-new store (opened partway through the dataset, if any
   are) be judged the same way as a long-established one? Does this
   dataset actually have that scenario, and would you need to check?
5. What time window is "performance" measured over — the full 24
   months, the most recent quarter, or a trend across both?
6. Would you want a single ranked list, or a list of stores flagged
   against multiple independent signals (revenue trend AND order
   volume AND, say, return rate)?
7. If two stores have identical revenue but very different order
   counts (one has fewer, higher-value orders), is one of them
   automatically "underperforming"? Why or why not?
8. What would you tell the VP if you noticed the underlying data
   doesn't actually contain a budget/target figure to compare against —
   would you substitute peer-group average, or push back and ask for
   the target?
9. Once you pick a concrete definition, what tables does it require,
   and does it involve any of the join-fan-out traps from Level 2?
10. How would you present the result so the VP can see *why* a store
    was flagged, not just that it was?

## Attempt

State your chosen benchmark explicitly before writing any SQL.

[space for learner]
