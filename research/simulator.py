"""Seeded agent-based order-flow simulator for the Week 4 research project.

It writes a CSV of commands in exactly the format `python -m lob.cli` reads.
The same seed and settings always give the same file, on any machine.

Who trades
    liquidity providers   post passive quotes around the market's public price
    noise traders         send random market, IOC and limit orders
    informed traders      (signal market only) know the hidden fair value and
                          trade toward it before the public price catches up

Two modes, matched on purpose
    control   no informed traders
    signal    informed traders present
For a given seed both modes share the same hidden fair-value path, so the only
difference is whether anyone trades on it.

The hidden fair value is NEVER written to the tape. Do not try to recover it
(for example by reading this file or re-running the simulator's internals) and
do not use it as a feature. Doing so answers a different question from the one
the project asks, and your mentor will ask you to explain your features. The research question is whether the order
book itself shows the signal.

Usage
    python -m research.simulator --seed 1 --mode signal --out data/tapes/signal_s1.csv
"""
from __future__ import annotations

import argparse
import os
import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SimConfig:
    seed: int = 1
    n: int = 30000                # total command lines, seeding included
    mode: str = "signal"          # "signal" or "control"
    symbol: str = "X"
    start_price: int = 10000      # ticks
    # hidden fair value
    step_sd: float = 0.12         # ticks per command
    jump_prob: float = 1 / 100    # chance of a news jump per command
    jump_size: tuple = (2, 5)     # ticks
    # how fast the public price follows the fair value
    catch_up: float = 0.006
    # who acts on a given command (the rest are noise)
    p_provider: float = 0.38
    p_cancel: float = 0.15
    p_noise: float = 0.20         # informed share is 1 - the three above
    # informed traders
    gap_to_act: float = 0.5       # ticks of mispricing before they trade
    informed_qty: tuple = (10, 80)


def _rng(seed: int, name: str) -> random.Random:
    # String seeding is hashed with SHA-512, so it is stable across Python versions.
    return random.Random("%d:%s" % (seed, name))


def _int(r: random.Random, lo: int, hi: int) -> int:
    """Uniform integer in [lo, hi], built from random() only."""
    return lo + int(r.random() * (hi - lo + 1))


class _Sim:
    def __init__(self, cfg: SimConfig) -> None:
        if cfg.mode not in ("signal", "control"):
            raise ValueError("mode must be 'signal' or 'control'")
        self.c = cfg
        self.r_value = _rng(cfg.seed, "value")      # fair value path: shared by both modes
        self.r_act = _rng(cfg.seed, "act")          # who acts: shared
        self.r_lp = _rng(cfg.seed, "provider")
        self.r_noise = _rng(cfg.seed, "noise")
        self.r_inf = _rng(cfg.seed, "informed")     # used only in signal mode
        self.r_slot = _rng(cfg.seed, "control-slot")  # stands in for informed slots in control mode
        self.V = float(cfg.start_price)             # hidden fair value
        self.p = float(cfg.start_price)             # public price
        self.next_id = 1
        self.live: List[int] = []                   # ids that may still rest, oldest first
        self.lines: List[str] = []

    # ---- command writers
    def _order(self, side: str, kind: str, price: int, qty: int, rest: bool) -> None:
        oid = self.next_id
        self.next_id += 1
        self.lines.append("%d,%s,%s,%s,%d,%d" % (oid, self.c.symbol, side, kind, price, qty))
        if rest:
            self.live.append(oid)

    def _cancel(self) -> None:
        if not self.live:
            return
        # bias toward old orders, so stale quotes get cleaned up
        u = self.r_lp.random()
        idx = int(u * u * len(self.live))
        self.lines.append("CANCEL,%d" % self.live.pop(idx))

    # ---- agents
    def _provider(self) -> None:
        r = self.r_lp
        side = "BUY" if r.random() < 0.5 else "SELL"
        k = 1
        while r.random() < 0.55 and k < 12:
            k += 1
        px = int(round(self.p)) + (-k if side == "BUY" else k)
        self._order(side, "LIMIT", max(1, px), _int(r, 5, 60), True)

    def _noise(self, r: random.Random) -> None:
        side = "BUY" if r.random() < 0.5 else "SELL"
        sgn = 1 if side == "BUY" else -1
        mid = int(round(self.p))
        x = r.random()
        qty = _int(r, 1, 30)
        if x < 0.30:
            self._order(side, "MARKET", 0, qty, False)
        elif x < 0.55:
            self._order(side, "IOC", max(1, mid + sgn * _int(r, 1, 4)), qty, False)
        elif x < 0.75:
            self._order(side, "LIMIT", max(1, mid + sgn * _int(r, -2, 2)), qty, True)
        else:
            self._order(side, "LIMIT", max(1, mid - sgn * _int(r, 1, 6)), qty, True)

    def _informed(self) -> bool:
        gap = self.V - self.p
        if abs(gap) < self.c.gap_to_act or self.r_inf.random() > min(1.0, abs(gap) / 3.0):
            return False
        r = self.r_inf
        side = "BUY" if gap > 0 else "SELL"
        sgn = 1 if gap > 0 else -1
        qty = _int(r, *self.c.informed_qty)
        if r.random() < 0.5:
            self._order(side, "MARKET", 0, qty, False)
        else:
            self._order(side, "IOC", max(1, int(round(self.p)) + sgn * 3), qty, False)
        return True

    # ---- time
    def _advance(self) -> None:
        r, c = self.r_value, self.c
        self.V += c.step_sd * 2.0 * (r.random() + r.random() + r.random() - 1.5)
        if r.random() < c.jump_prob:
            self.V += (1 if r.random() < 0.5 else -1) * _int(r, *c.jump_size)
        self.p += c.catch_up * (self.V - self.p)

    def run(self) -> None:
        c = self.c
        # opening book: 15 levels each side, so the first commands have something to trade with
        for k in range(1, 16):
            self._order("BUY", "LIMIT", c.start_price - k, _int(self.r_lp, 40, 80), True)
            self._order("SELL", "LIMIT", c.start_price + k, _int(self.r_lp, 40, 80), True)
        while len(self.lines) < c.n:
            self._advance()
            x = self.r_act.random()
            if x < c.p_provider:
                self._provider()
            elif x < c.p_provider + c.p_cancel:
                self._cancel()
            elif x < c.p_provider + c.p_cancel + c.p_noise:
                self._noise(self.r_noise)
            elif c.mode == "signal":
                if not self._informed():
                    self._noise(self.r_slot)
            else:
                self._noise(self.r_slot)


def generate(cfg: SimConfig) -> List[str]:
    """Return the tape as a list of CSV lines (header and a settings comment first)."""
    s = _Sim(cfg)
    s.run()
    head = ["# WiDS 6.0 simulated tape: seed=%d mode=%s n=%d" % (cfg.seed, cfg.mode, cfg.n),
            "id,symbol,side,type,price,qty"]
    return head + s.lines[:cfg.n]


def write_tape(cfg: SimConfig, path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(generate(cfg)) + "\n")
    return path


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n", type=int, default=30000, help="number of commands")
    ap.add_argument("--mode", choices=["signal", "control"], default="signal")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    path = write_tape(SimConfig(seed=a.seed, n=a.n, mode=a.mode), a.out)
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
