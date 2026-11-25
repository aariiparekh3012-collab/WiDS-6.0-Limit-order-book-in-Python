"""The Week 4 engine check. Pass or fail, retry as often as you like.

    python -m research.check_replay                # all standard tapes
    python -m research.check_replay --impl my.module

For each tape it checks two things:
  1. the tape file is the one everybody should have (its SHA-256 matches), and
  2. your engine's replay of it matches the reference: every event and the
     book state after every command, summarised as one checksum.

If the checksum differs, run the Tier 1 and Tier 2 graders again. The tape uses
limit, market and IOC orders and cancels, so a failure here means a bug the
smaller traces did not catch. Build a smaller tape with
`python -m research.simulator --n 500 --out small.csv` and compare by eye.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from lob.cli import load_factory  # noqa: E402
from research.make_tapes import MODES, SEEDS, tape_path  # noqa: E402
from research.record import replay  # noqa: E402

EXPECTED = os.path.join(HERE, "expected.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--impl", default="lob.book")
    a = ap.parse_args(argv)
    expected = json.load(open(EXPECTED, encoding="utf-8"))
    factory = load_factory(a.impl)
    ok_all = True
    for mode in MODES:
        for seed in SEEDS:
            name = "%s_s%d" % (mode, seed)
            path = tape_path(mode, seed)
            if not os.path.exists(path):
                print("MISSING  %-12s run: python -m research.make_tapes" % name)
                ok_all = False
                continue
            raw = open(path, "rb").read()
            if hashlib.sha256(raw).hexdigest() != expected[name]["tape_sha256"]:
                print("CHANGED  %-12s the tape differs from the released one. Regenerate it." % name)
                ok_all = False
                continue
            try:
                _, digest = replay(raw.decode("utf-8"), factory)
            except NotImplementedError as err:
                print("TODO     %-12s engine not implemented yet (%s)" % (name, err))
                ok_all = False
                continue
            except Exception as err:  # noqa: BLE001
                print("CRASH    %-12s %r" % (name, err))
                ok_all = False
                continue
            good = digest == expected[name]["replay_sha256"]
            ok_all &= good
            print("%s  %-12s" % ("PASS    " if good else "FAIL    ", name))
    print("\nEngine check:", "PASSED" if ok_all else "not passed yet")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
