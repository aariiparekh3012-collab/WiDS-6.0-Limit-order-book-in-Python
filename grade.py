#!/usr/bin/env python3
"""Grader: runs your Book against golden traces for the educational specification.

    python grade.py                 # all tiers
    python grade.py --tier 1        # only tier 1 traces
    python grade.py --only t1_basic # one trace by name
    python grade.py -v              # show more context on failures
    python grade.py --impl some.module   # grade a Book from another module

A trace passes only if EVERY output line matches: each event, and the book state
(top of book + 5 depth levels) after every command.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lob.cli import load_factory, parse_stp, run_csv  # noqa: E402

TIER_NAMES = {1: "Tier 1  core book", 2: "Tier 2  IOC / FOK / modify",
              3: "Optional  Cancel Newest"}


def load_golden(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def run_trace(entry, factory, verbose):
    csv_path = os.path.join(HERE, "traces", entry["csv"])
    text = open(csv_path, encoding="utf-8").read()
    csv_lines = text.splitlines()
    want = load_golden(os.path.join(HERE, "traces", entry["golden"]))
    try:
        got = run_csv(text, parse_stp(entry.get("stp", "NONE")), factory)
    except NotImplementedError as err:
        return False, "not implemented yet (%s)" % err
    except Exception as err:  # noqa: BLE001  (show students their own crash clearly)
        import traceback
        return False, "crashed: %r\n%s" % (err, traceback.format_exc(limit=-3))

    for i in range(max(len(want), len(got))):
        w = want[i] if i < len(want) else None
        g = got[i][1] if i < len(got) else None
        if w == g:
            continue
        lineno = got[min(i, len(got) - 1)][0] if got else 0
        msg = ["first difference at output line %d (CSV line %d: %s)"
               % (i + 1, lineno, csv_lines[lineno - 1].strip() if lineno else "?")]
        lo = max(0, i - (3 if verbose else 1))
        for j in range(lo, i):
            msg.append("    ok       %s" % json.dumps(want[j], separators=(",", ":")))
        msg.append("    expected %s" % (json.dumps(w, separators=(",", ":")) if w else "<nothing, output ended>"))
        msg.append("    got      %s" % (json.dumps(g, separators=(",", ":")) if g else "<nothing, output ended>"))
        return False, "\n".join(msg)
    return True, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", type=int)
    ap.add_argument("--only")
    ap.add_argument("--impl", default="lob.book")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(HERE, "traces", "manifest.json"), encoding="utf-8"))
    factory = load_factory(args.impl)
    total = passed = 0
    by_tier = {}
    for entry in manifest:
        if args.tier and entry["tier"] != args.tier:
            continue
        if args.only and entry["name"] != args.only:
            continue
        ok, msg = run_trace(entry, factory, args.verbose)
        total += 1
        passed += ok
        t = by_tier.setdefault(entry["tier"], [0, 0])
        t[0] += ok
        t[1] += 1
        print("%s  %-34s %s" % ("PASS" if ok else "FAIL", entry["name"], entry.get("description", "")))
        if not ok:
            print("      " + msg.replace("\n", "\n      "))
    print()
    for tier in sorted(by_tier):
        a, b = by_tier[tier]
        print("%-40s %d/%d%s" % (TIER_NAMES.get(tier, "Tier %d" % tier), a, b, "  done" if a == b else ""))
    if not total:
        print("No active traces matched")
        return 2
    print("TOTAL %d/%d" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
