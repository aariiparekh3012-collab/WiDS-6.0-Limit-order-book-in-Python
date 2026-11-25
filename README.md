# Limit Order Book in Python (WiDS 6.0, IIT Bombay Analytics Club)

You will write the matching engine of a small exchange in Python, check it
against golden traces under the independent educational specification, then benchmark it
and use its order flow to look for a signal. See [curriculum](docs/CURRICULUM.md), [specification](docs/SPECIFICATION.md) and [completion criteria](docs/RUBRIC.md).

| Week | Theme | You do | Grader |
|---|---|---|---|
| 1 | Core book | limit and market orders, FIFO, cancel, top of book, depth | `python grade.py --tier 1` |
| 2 | Order types | IOC, FOK, modify | `python grade.py --tier 2` |
| 3 | Speed | choose Basic measurement or Intermediate profiling and one optimisation; optional Cancel Newest challenge | `python bench.py`, optional `python grade.py --tier 3` |
| 4 | Research | study whether order-book imbalance predicts short-term price moves; notebook and concise project summary | `python -m research.check_replay` (engine check only), your mentor reads the rest |

Four weeks, 6–8 hours/week, 4–6 mentees, individual projects throughout. A 10-minute screening quiz assesses basic Python and reasoning; no finance or ML prerequisites. Python 3.10+ standard library for the engine; NumPy, pandas, Matplotlib and scikit-learn for Week 4.

## Setup

```bash
git clone https://github.com/aariiparekh3012-collab/WiDS-6.0-Limit-order-book-in-Python.git
cd WiDS-6.0-Limit-order-book-in-Python
python grade.py            # everything fails with "not implemented yet": that is correct
```

Engine implementation belongs in **`lob/book.py`**; add your own tests, design notes, reports and research notebook.
## Week 4 kit

Opens in Week 4. You need `pip install -r requirements-research.txt` first.

```bash
python -m research.make_tapes          # control and signal tapes, seeds 1 to 3 (deterministic)
python -m research.check_replay        # does YOUR engine reproduce the reference on those tapes?
python -m research.record data/tapes/signal_s1.csv --out data/signal_s1_states.csv
python -m unittest research.test_features -v    # self-checks for the features you write
```

The notebook in `notebooks/analysis_template.ipynb` walks through the project. The simulator never writes
its hidden fair value to a tape, and your features must not try to recover it.

Do not edit `lob/events.py`, `lob/types.py`, `lob/exchange.py`, `lob/cli.py`,
`grade.py` or the files in `traces/`.

## Layout

```
lob/book.py        YOU WRITE THIS: class Book
lob/types.py       Order, Side, OrderType, STPMode, TopOfBook, MarketDepth
lob/events.py      the events your book emits (ACK, TRADE, ...)
lob/exchange.py    one Book per symbol (provided)
lob/cli.py         CSV runner: python -m lob.cli orders.csv
grade.py           compares your output with educational golden traces, line by line
bench.py           throughput benchmark
traces/            input CSVs and golden outputs (.jsonl) for the educational specification
docs/              DESIGN.md: data-structure notes (read this first)
tests/             small unit tests you can run while you work
research/          Week 4 kit: simulator, recorder, features, engine check
notebooks/         Week 4 analysis notebook template
assignments/       what to hand in each week
templates/         design notes, benchmark CSV and report formats
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

Only Cancel Newest is an optional STP challenge. See docs/SPECIFICATION.md for exact behaviour, including atomic FOK.

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

Basic: repeat measurements and explain results. Intermediate: also profile, analyse complexity and try one optimisation. No minimum speed target.

## Rules of the road

- Ask in your batch channel or a doubt slot before you are stuck for more than 45 minutes.
- Write your own code. Discuss ideas freely, do not copy another mentee's `book.py`.
- Two formal levels: Foundation (3 traces), Advanced (7 cumulative). Tier 3 is a separate optional Cancel Newest challenge; archived modes and compatibility fixtures are not graded.
- Completion is assessed through weekly milestones, correctness, reproducible research and clear final documentation.
- Weekly tasks and what to hand in are in `assignments/`. Submission formats are in `templates/`.
