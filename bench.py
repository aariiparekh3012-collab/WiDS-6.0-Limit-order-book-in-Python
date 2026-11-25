#!/usr/bin/env python3
"""Throughput benchmark: how many orders per second does YOUR book process?

    python bench.py                       # 100k commands against lob.book
    python bench.py --n 200000 --impl mentor_only.book_solution

Parsing is done before the clock starts, so this times only the engine. Compare the
number with the C++ benchmark numbers your mentor gives you, then read the "faster
design" section at the end of docs/DESIGN_cpp.md and try it.
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))

from fuzz_gen import gen  # noqa: E402
from lob.cli import _parse_side, _parse_type, load_factory  # noqa: E402
from lob.events import VectorSink  # noqa: E402
from lob.exchange import Exchange  # noqa: E402
from lob.types import Order, STPMode  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100_000)
    ap.add_argument("--impl", default="lob.book")
    args = ap.parse_args()

    lines = gen(seed=42, n=args.n, types=("LIMIT", "MARKET", "IOC"), invalid=False)
    cmds, ts = [], 0
    for line in lines:
        if line.startswith("#") or line.startswith("id,"):
            continue
        f = line.split(",")
        if f[0] == "CANCEL":
            cmds.append(("C", int(f[1])))
        else:
            ts += 1
            cmds.append(("S", Order(int(f[0]), _parse_side(f[2]), int(f[4]), int(f[5]), ts,
                                    _parse_type(f[3]), f[1])))

    ex = Exchange(STPMode.NONE, load_factory(args.impl))
    ex.add_symbol("AAPL")
    sink = VectorSink()
    t0 = time.perf_counter()
    for kind, payload in cmds:
        if kind == "S":
            ex.submit(payload, sink)
        else:
            ex.cancel(payload, sink)
        if len(sink.events) > 50_000:
            sink.clear()
    dt = time.perf_counter() - t0
    print("%d commands in %.2fs  ->  %.0f commands/sec  (%.1f us each)"
          % (len(cmds), dt, len(cmds) / dt, dt / len(cmds) * 1e6))


if __name__ == "__main__":
    main()
