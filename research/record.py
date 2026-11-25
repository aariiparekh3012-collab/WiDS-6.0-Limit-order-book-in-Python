"""Replay a tape through YOUR engine and record the market after every command.

Writes one row per command (orders AND cancels), with an explicit command index.
Use this index, not any timestamp: the CLI only timestamps orders, so cancels
would be missing from a timestamp column.

    python -m research.record data/tapes/signal_s1.csv --out data/signal_s1_states.csv

Columns
    idx           command number, 0,1,2,... counting every command line
    line          line number in the tape file
    kind          ORDER or CANCEL
    side          BUY or SELL for orders, empty for cancels
    trade_qty     total quantity traded by this command
    signed_vol    trade_qty, positive if the command was a buy, negative if a sell
    n_trades      number of trades this command caused
    rejected      1 if the engine rejected the command
    best_bid, bid_qty, best_ask, ask_qty   top of book after the command (empty if no quote)
    bid_depth5, ask_depth5                 total quantity in the best 5 levels per side
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from lob.cli import load_factory, run_csv  # noqa: E402
from lob.types import STPMode  # noqa: E402

COLUMNS = ["idx", "line", "kind", "side", "trade_qty", "signed_vol", "n_trades", "rejected",
           "best_bid", "bid_qty", "best_ask", "ask_qty", "bid_depth5", "ask_depth5"]


def _command_lines(text: str) -> Dict[int, List[str]]:
    out = {}
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.upper().startswith("ID,"):
            continue
        out[n] = [t.strip() for t in line.split(",")]
    return out


def replay(text: str, factory=None) -> Tuple[List[Dict[str, Any]], str]:
    """Return (rows, digest). The digest hashes every event and state line, in order."""
    cmds = _command_lines(text)
    by_line: Dict[int, List[Dict[str, Any]]] = {}
    h = hashlib.sha256()
    for lineno, d in run_csv(text, STPMode.NONE, factory):
        by_line.setdefault(lineno, []).append(d)
        h.update(json.dumps(d, separators=(",", ":")).encode("utf-8"))
        h.update(b"\n")
    rows = []
    for idx, lineno in enumerate(sorted(cmds)):
        f = cmds[lineno]
        is_cancel = f[0].upper() == "CANCEL"
        side = "" if is_cancel else f[2].upper()
        evs = by_line.get(lineno, [])
        trades = [e for e in evs if e.get("event") == "TRADE"]
        qty = sum(e["qty"] for e in trades)
        state = next((e for e in evs if "state" in e), {})
        rows.append({
            "idx": idx, "line": lineno, "kind": "CANCEL" if is_cancel else "ORDER", "side": side,
            "trade_qty": qty, "signed_vol": qty if side == "BUY" else -qty if side == "SELL" else 0,
            "n_trades": len(trades),
            "rejected": int(any(e.get("event") == "REJECT" for e in evs)),
            "best_bid": state.get("best_bid"), "bid_qty": state.get("bid_qty", 0),
            "best_ask": state.get("best_ask"), "ask_qty": state.get("ask_qty", 0),
            "bid_depth5": sum(x[1] for x in state.get("bids", [])),
            "ask_depth5": sum(x[1] for x in state.get("asks", [])),
        })
    return rows, h.hexdigest()


def write_states(rows: List[Dict[str, Any]], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in COLUMNS})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Replay a tape and record market states.")
    ap.add_argument("tape")
    ap.add_argument("--out", required=True)
    ap.add_argument("--impl", default="lob.book")
    a = ap.parse_args(argv)
    text = open(a.tape, encoding="utf-8").read()
    rows, digest = replay(text, load_factory(a.impl))
    write_states(rows, a.out)
    print("wrote %s (%d commands)" % (a.out, len(rows)))
    print("replay checksum", digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
