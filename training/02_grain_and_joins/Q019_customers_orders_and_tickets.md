# Q019 — Customers With Both Orders and Support Tickets

## Business Context

Customer success wants to know, for customers who have both placed
orders and filed support tickets, their total order count and total
ticket count — a first step toward correlating support burden with
purchase volume (a theme that returns in Level 6's Q060).

## Business Question

For every customer who has at least one order AND at least one support
ticket, report their customer_id, total number of orders, and total
number of support tickets.

## Data Available

customers
orders
support_tickets

## Think Before SQL

1. What does one output row represent?
2. `orders` and `support_tickets` are both "many" tables hanging off
   `customers`. If you join customers → orders → support_tickets all
   directly in one query, what grain does the resulting joined row set
   live at?
3. If a customer has 5 orders and 3 tickets, how many rows does that
   three-way join produce for that customer alone? Is that number
   meaningful for anything?
4. If you now do `COUNT(o.order_id)` and `COUNT(t.ticket_id)` in the
   same query over that joined result, are either of those counts
   correct?
5. Specifically: would `COUNT(o.order_id)` overcount orders, undercount
   them, or get it right, given the fan-out from the ticket side? Walk
   through the 5-orders/3-tickets example concretely.
6. What's the general shape of this trap — how does it relate to
   Q011's payments+order_items problem?
7. What's the fix? Would counting `COUNT(DISTINCT o.order_id)` and
   `COUNT(DISTINCT t.ticket_id)` separately over the same three-way
   join actually solve it, or does it just hide the problem?
8. What alternative structure (pre-aggregating each fact table to
   customer grain independently, then joining those two summaries)
   avoids the fan-out entirely?
9. Which approach would you trust more in a production report, and why?
10. How would you validate one customer's order count and ticket count
    independently, outside of your main query, to catch a fan-out bug?

## Attempt

[space for learner]
