# Q022 — Ranking Stores by Revenue, Correctly Handling Ties

## Business Context

Regional leadership wants a ranked list of all stores by total net
revenue from completed orders, for a quarterly performance review
presentation.

## Business Question

Rank every store by total net revenue (completed orders), highest
first. If two stores are exactly tied, they should receive the same
rank, and you should be able to explain what happens to the rank number
immediately after a tie.

## Data Available

orders
order_items
stores

## Think Before SQL

1. What does one output row represent?
2. What must you compute first, before any ranking can happen?
3. Name two SQL window functions that assign a rank number to rows in
   order. How do they differ in what happens after a tie?
4. If stores B and C are tied for 2nd place, what rank does the store
   in 4th place actually receive under each function?
5. Which function would make "there are 5 stores in the top 3" a
   coherent, correct statement, and which function would not?
6. Is a plain `ROW_NUMBER()` ever an appropriate choice when ties are
   possible and matter to the business? Why or why not?
7. How likely are exact revenue ties between two stores in this
   dataset — does that likelihood change how much this distinction
   matters in practice?
8. What clause orders the final output — is it the same expression used
   inside the window function, or does it need repeating?
9. How would you construct a small synthetic example (3-4 stores, one
   tie) to verify your chosen function behaves the way you expect?
10. If leadership specifically wants "exactly one store per rank
    number, no ties, tiebreak by store_id," which function would you
    reach for instead?

## Attempt

[space for learner]
