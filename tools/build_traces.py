#!/usr/bin/env python3
"""MENTOR TOOL: regenerate fuzz CSVs, run the C++ engine on every trace, write
golden .jsonl files and traces/manifest.json.

    LOB_CPP="/path/to/limit order book" python3 tools/build_traces.py

Requires g++ (C++17). Hand-written scenario CSVs in traces/ are kept as they are.
Mentees never need to run this: the generated traces are committed.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from fuzz_gen import gen  # noqa: E402

LOB = os.environ.get("LOB_CPP", os.path.join(ROOT, "..", "limit order book"))
TRACES = os.path.join(ROOT, "traces")

# (name, csv, stp, tier, description)  -- csv=None means fuzz-generated
HAND = [
    ("t1_basic", "t1_basic.csv", "NONE", 1, "limit/market, FIFO, sweep, cancel, rejects, 2 symbols"),
    ("t2_ioc_fok", "t2_ioc_fok.csv", "NONE", 2, "IOC partials, FOK all-or-nothing"),
    ("t2_modify", "t2_modify.csv", "NONE", 2, "modify loses priority, passive reprice"),
    ("t3_stp_newest", "t3_stp.csv", "CANCEL_NEWEST", 3, "self-trade: cancel newest"),
    ("t3_stp_oldest", "t3_stp.csv", "CANCEL_OLDEST", 3, "self-trade: cancel oldest"),
    ("t3_stp_both", "t3_stp.csv", "CANCEL_BOTH", 3, "self-trade: cancel both"),
    ("t4_quirk_modify_invalid", "t4_quirk_modify_invalid.csv", "NONE", 4,
     "C++ swallows modify's own reject (see MENTOR_NOTES)"),
]
FUZZ = [
    ("t1_fuzz_s1", 1, 1, dict(n=400, symbols=("AAPL",), types=("LIMIT", "MARKET")), "NONE", "400 random limit/market/cancel"),
    ("t1_fuzz_s2", 2, 1, dict(n=400, symbols=("AAPL", "MSFT"), types=("LIMIT", "MARKET")), "NONE", "2 symbols"),
    ("t2_fuzz_s3", 3, 2, dict(n=600, symbols=("AAPL",), types=("LIMIT", "MARKET", "IOC", "FOK"), modify=True), "NONE", "all types + modify"),
    ("t2_fuzz_s4", 4, 2, dict(n=600, symbols=("AAPL", "MSFT"), types=("LIMIT", "MARKET", "IOC", "FOK"), modify=True), "NONE", "all types + modify, 2 symbols"),
    ("t3_fuzz_newest_s5", 5, 3, dict(n=600, types=("LIMIT", "MARKET", "IOC", "FOK"), modify=True, traders=3), "CANCEL_NEWEST", "STP newest, random flow"),
    ("t3_fuzz_oldest_s6", 6, 3, dict(n=600, types=("LIMIT", "MARKET", "IOC", "FOK"), modify=True, traders=3), "CANCEL_OLDEST", "STP oldest, random flow"),
    ("t3_fuzz_both_s7", 7, 3, dict(n=600, types=("LIMIT", "MARKET", "IOC", "FOK"), modify=True, traders=3), "CANCEL_BOTH", "STP both, random flow"),
]


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, **kw)


def main():
    exe = os.path.join(tempfile.mkdtemp(), "golden_gen")
    sh(["g++", "-std=c++17", "-O1", "-I" + os.path.join(LOB, "include"),
        os.path.join(LOB, "src", "book.cpp"), os.path.join(HERE, "golden_gen.cpp"), "-o", exe])

    manifest = []
    for name, csv, stp, tier, desc in HAND:
        manifest.append(dict(name=name, csv=csv, golden=name + ".jsonl", stp=stp, tier=tier, description=desc))
    for name, seed, tier, kw, stp, desc in FUZZ:
        csv = name + ".csv"
        with open(os.path.join(TRACES, csv), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(gen(seed, **kw)) + "\n")
        manifest.append(dict(name=name, csv=csv, golden=name + ".jsonl", stp=stp, tier=tier, description=desc))

    for m in manifest:
        args = [exe, os.path.join(TRACES, m["csv"])]
        if m["stp"] != "NONE":
            args[1:1] = ["--stp", m["stp"]]
        with open(os.path.join(TRACES, m["golden"]), "w", encoding="utf-8", newline="\n") as out:
            sh(args, stdout=out)
        print("golden", m["name"])
    manifest.sort(key=lambda m: (m["tier"], m["name"]))
    with open(os.path.join(TRACES, "manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
