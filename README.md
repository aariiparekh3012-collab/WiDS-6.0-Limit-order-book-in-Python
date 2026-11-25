# Limit Order Book in Python (WiDS 6.0, IIT Bombay Analytics Club)

You will write the matching engine of a small exchange in Python, check it
against golden traces produced by a reference engine, then make it fast
and use its order flow to look for a signal.

| Week | Theme | You do | Grader |
|---|---|---|---|
| 1 | Core book | limit and market orders, FIFO, cancel, top of book, depth | `python grade.py --tier 1` |
| 2 | Order types | IOC, FOK, modify | `python grade.py --tier 2` |
| 3 | Speed | self-trade prevention, profile, benchmark, faster design | `python grade.py --tier 3`, `python bench.py` |
| 4 | Analysis | simulator, tape and a signal challenge | set by your mentor |

Time budget is 6 to 8 hours a week. Python 3.10 or newer, standard library only.

## Setup

```bash
git clone https://github.com/aariiparekh3012-collab/WiDS-6.0-Limit-order-book-in-Python.git
cd WiDS-6.0-Limit-order-book-in-Python
python grade.py            # everything fails with "not implemented yet": that is correct
```

Your work happens in **one file**: `lob/book.py`. Everything else is provided.
Do not edit `lob/events.py`, `lob/types.py`, `lob/exchange.py`, `lob/cli.py`,
`grade.py` or the files in `traces/`.

## Layout

```
lob/book.py        YOU WRITE THIS: class Book
lob/types.py       Order, Side, OrderType, STPMode, TopOfBook, MarketDepth
lob/events.py      the events your book emits (ACK, TRADE, ...)
lob/exchange.py    one Book per symbol (provided)
lob/cli.py         CSV runner: python -m lob.cli orders.csv
grade.py           compares your output with the reference engine's, line by line
bench.py           throughput benchmark
traces/            input CSVs and golden outputs (.jsonl) from the reference engine
docs/              DESIGN.md: data-structure notes (read this first)
tests/             small unit tests you can run while you work
```

## The rules

Prices are integer ticks and quantities are whole units. No floats.
One `Book` holds one symbol. Matching is **price-time priority**: best price
first, and within a price, the order that arrived first.

`submit(order, sink)` does these steps in this order. The grader is strict.

1. `type != MARKET` and `price <= 0`: `Reject("invalid price")`.
2. `qty <= 0`: `Reject("invalid quantity")`.
3. id already resting in this book: `Reject("duplicate order id")`.
4. FOK that cannot be filled in full right now: `Reject("FOK not fillable")`.
5. `Ack(id)`.
6. Match against the opposite side. For every fill emit
   `Trade(aggressor, resting, resting_price, qty, order.ts)`, and then
   `Filled(resting_id)` if the resting order is now done. Trades happen at the
   **resting** order's price.
7. If the order is completely filled, `Filled(id)`. Otherwise:
   - LIMIT: the remainder rests; if it traded at all, emit `Partial(id, remaining)`.
   - MARKET and IOC: if it traded at all emit `Partial(id, remaining)`, then `CancelAck(id)`.

`cancel(id, sink)`: `CancelAck(id)`, or `Reject(id, "order not found")`.

`modify(id, new_price, new_qty, sink)` (Week 2): passive, never matches even if
it crosses, goes to the **back** of its queue. Check order: not found, then
`new_qty <= 0`, then `new_price <= 0`. Success emits only `ModifyAck`.

Self-trade prevention (Week 3) fires only when `order.trader_id != 0` and equals
the resting order's `trader_id`. See the docstring at the bottom of `lob/book.py`.

## Workflow

1. Read `docs/DESIGN.md` and the docstrings in `lob/book.py`.
2. Implement a tier, run `python grade.py --tier N`, read the first difference.
3. `python grade.py -v` shows more context around a failure.
4. Commit when a tier goes green.
5. Debug a single trace: `python grade.py --only t1_basic`, then read its CSV in
   `traces/` next to the expected `.jsonl`.

A trace passes only if every event and the book state after every command match.

## Benchmark (Week 3)

```bash
python bench.py                  # 100k commands
python bench.py --n 200000
```

Always profile before optimising (`python -m cProfile -s cumtime bench.py`).
Your mentor will give you the reference numbers to compare against.

## Rules of the road

- Ask in your batch channel or a doubt slot before you are stuck for more than 45 minutes.
- Write your own code. Discuss ideas freely, do not copy another mentee's `book.py`.
- Tier 4 (`t4_quirk_modify_invalid`) is optional and already passes if tiers 1 to 3 are right.
