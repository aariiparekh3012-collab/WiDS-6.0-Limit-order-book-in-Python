"""Seeded random order-flow generator. Same seed -> same CSV, always.

Produces realistic-ish flow around a drifting mid price: mostly passive limits,
some aggressive crossing orders, cancels (of live and dead ids), optional
modifies, optional trader ids for STP, and a sprinkling of invalid orders
(price<=0, qty<=0, duplicate ids) to exercise every reject path.

Order ids are globally unique except deliberate duplicates, which always reuse
an id in the SAME symbol (so cancel/modify routing stays unambiguous).
"""
from __future__ import annotations

import random
from typing import List, Sequence


def gen(seed: int, n: int = 400, symbols: Sequence[str] = ("AAPL",),
        types: Sequence[str] = ("LIMIT", "MARKET"), modify: bool = False,
        traders: int = 0, invalid: bool = True) -> List[str]:
    r = random.Random(seed)
    weights = {"LIMIT": 6.0, "MARKET": 1.0, "IOC": 1.5, "FOK": 1.0}
    kinds = [t for t in types if t in weights]
    w = [weights[t] for t in kinds]

    header = "id,symbol,side,type,price,qty" + (",trader_id" if traders else "")
    lines = ["# seed=%d n=%d symbols=%s types=%s modify=%s traders=%d"
             % (seed, n, ",".join(symbols), ",".join(types), modify, traders), header]
    mid = {s: 10000 for s in symbols}
    issued = []          # (id, symbol)
    next_id = 1

    for _ in range(n):
        sym = r.choice(list(symbols))
        mid[sym] = max(100, mid[sym] + r.choice([-1, 0, 0, 1]))
        x = r.random()

        if issued and x < 0.12:                                   # cancel
            oid = r.choice(issued)[0] if r.random() < 0.85 else 900000 + r.randint(0, 99)
            lines.append("CANCEL,%d" % oid)
            continue
        if issued and modify and x < 0.22:                        # modify (always valid values)
            oid, osym = r.choice(issued)
            lines.append("MODIFY,%d,%d,%d" % (oid, max(1, mid[osym] + r.randint(-12, 12)), r.randint(1, 150)))
            continue

        side = r.choice(["BUY", "SELL"])
        kind = r.choices(kinds, w)[0]
        off = r.randint(-3, 14)
        price = mid[sym] - off if side == "BUY" else mid[sym] + off
        qty = r.choice([r.randint(1, 20), r.randint(1, 100), r.randint(50, 300)])
        if kind == "MARKET":
            price = 0
        oid = next_id
        consume = True

        if invalid and r.random() < 0.03:
            bad = r.choice(["qty0", "qtyneg", "price0", "dup"])
            if bad == "qty0":
                qty = 0
            elif bad == "qtyneg":
                qty = -5
            elif bad == "price0" and kind != "MARKET":
                price = 0
            elif bad == "dup":
                same = [i for i, s in issued if s == sym]
                if same:
                    oid, consume = r.choice(same), False

        row = "%d,%s,%s,%s,%d,%d" % (oid, sym, side, kind, price, qty)
        if traders:
            row += ",%d" % r.randint(0, traders)
        lines.append(row)
        if consume:
            issued.append((oid, sym))
            next_id += 1
    return lines
