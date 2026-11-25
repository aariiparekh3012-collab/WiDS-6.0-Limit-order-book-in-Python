"""CSV runner. PROVIDED. Feeds a CSV of commands through your Book.

CSV format (same as the C++ lob_cli):
    id,symbol,side,type,price,qty[,trader_id]
    CANCEL,<order_id>
    MODIFY,<order_id>,<new_price>,<new_qty>
Lines starting with # and blank lines are ignored. Timestamps are assigned
1,2,3... to each order line (cancel/modify lines do not consume a timestamp).

Output is JSON lines: every event, then after each command one "state" line
per symbol (top of book + 5 levels of depth). The grader compares these lines
against the C++ engine's output.

Usage:  python -m lob.cli [--stp newest|oldest|both] orders.csv
"""
from __future__ import annotations

import importlib
import json
import sys
from typing import Any, Dict, List, Tuple

from .events import VectorSink
from .exchange import Exchange
from .types import Order, OrderType, Side, STPMode

STATE_DEPTH = 5


def _parse_side(s: str) -> Side:
    u = s.strip().upper()
    if u in ("BUY", "B"):
        return Side.BUY
    if u in ("SELL", "S"):
        return Side.SELL
    raise ValueError("bad side: " + s)


def _parse_type(s: str) -> OrderType:
    u = s.strip().upper()
    if u in ("LIMIT", "LMT", "L"):
        return OrderType.LIMIT
    if u in ("MARKET", "MKT", "M"):
        return OrderType.MARKET
    if u == "IOC":
        return OrderType.IOC
    if u == "FOK":
        return OrderType.FOK
    raise ValueError("bad type: " + s)


def parse_stp(s: str) -> STPMode:
    u = s.strip().upper()
    table = {"NONE": STPMode.NONE,
             "NEWEST": STPMode.CANCEL_NEWEST, "CANCEL_NEWEST": STPMode.CANCEL_NEWEST,
             "OLDEST": STPMode.CANCEL_OLDEST, "CANCEL_OLDEST": STPMode.CANCEL_OLDEST,
             "BOTH": STPMode.CANCEL_BOTH, "CANCEL_BOTH": STPMode.CANCEL_BOTH}
    if u not in table:
        raise ValueError("unknown STP mode: " + s)
    return table[u]


def state_dict(ex: Exchange, sym: str, levels: int = STATE_DEPTH) -> Dict[str, Any]:
    t = ex.top(sym)
    d = ex.depth(sym, levels)
    return {
        "state": sym,
        "best_bid": t.best_bid, "bid_qty": t.bid_qty,
        "best_ask": t.best_ask, "ask_qty": t.ask_qty,
        "bids": [[x.price, x.qty, x.order_count] for x in d.bids],
        "asks": [[x.price, x.qty, x.order_count] for x in d.asks],
    }


def run_csv(text: str, stp: STPMode = STPMode.NONE, book_factory=None
            ) -> List[Tuple[int, Dict[str, Any]]]:
    """Returns [(csv_line_number, json_dict), ...] in output order."""
    ex = Exchange(stp, book_factory)
    out: List[Tuple[int, Dict[str, Any]]] = []
    ts = 0

    def flush(lineno: int, sink: VectorSink) -> None:
        for e in sink.events:
            out.append((lineno, e.to_dict()))
        for sym in sorted(ex.symbols()):
            out.append((lineno, state_dict(ex, sym)))

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.upper().startswith("ID,"):
            continue
        f = [tok.strip() for tok in line.split(",")]
        head = f[0].upper()
        sink = VectorSink()
        try:
            if head == "CANCEL":
                ex.cancel(int(f[1]), sink)
            elif head == "MODIFY":
                ex.modify(int(f[1]), int(f[2]), int(f[3]), sink)
            else:
                if len(f) < 6:
                    continue
                ts += 1
                o = Order(id=int(f[0]), symbol=f[1], side=_parse_side(f[2]),
                          type=_parse_type(f[3]), price=int(f[4]), qty=int(f[5]), ts=ts)
                if len(f) >= 7 and f[6]:
                    o.trader_id = int(f[6])
                if not ex.has_symbol(o.symbol):
                    ex.add_symbol(o.symbol)
                ex.submit(o, sink)
        except (ValueError, IndexError) as err:
            print("%d: %s" % (lineno, err), file=sys.stderr)
            continue
        flush(lineno, sink)
    return out


def load_factory(impl: str):
    """'lob.book' (default) or e.g. 'mentor_only.book_solution' -> that module's Book."""
    return importlib.import_module(impl).Book


def main(argv: List[str]) -> int:
    stp, impl, path, events_only = STPMode.NONE, "lob.book", None, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--stp":
            i += 1
            stp = parse_stp(argv[i])
        elif a == "--impl":
            i += 1
            impl = argv[i]
        elif a == "--events-only":
            events_only = True
        else:
            path = a
        i += 1
    if not path:
        print(__doc__)
        return 1
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    for _, d in run_csv(text, stp, load_factory(impl)):
        if events_only and "state" in d:
            continue
        print(json.dumps(d, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
