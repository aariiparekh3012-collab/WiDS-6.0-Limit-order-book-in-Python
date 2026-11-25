# Week 1: Core order book

**Level 1 (Foundation).** Individual submission. Review your design with the mentor; choose your own structures.

**Goal:** a working Book for limit and market orders, with cancel, `top()`, `depth()` and `order_count()`.

**Hand in**
- `lob/book.py` passing all Tier 1 traces: `python grade.py --tier 1` shows 3/3 (`t1_basic`, `t1_fuzz_s1`, `t1_fuzz_s2`).
- Your commit history (commit as you go, not once at the end).
- Your grader output pasted into your submission.
- `templates/design.md` filled in with your answers to four questions:
  1. Why did you choose your price-ordering structure?
  2. How do you keep FIFO inside one price level?
  3. How do you find an order by id for cancel?
  4. What is the cost of `submit`, `cancel` and `top`, in terms of orders `n` and price levels `m`?

**Acceptance:** 3/3 Tier 1 traces. Prices are integer ticks and quantities whole units. No floats.
Do not edit `lob/events.py`, `lob/types.py`, `lob/exchange.py`, `lob/cli.py`, `grade.py` or `traces/`.
