"""Generate the standard set of tapes: control and signal for seeds 1 to 3.

    python -m research.make_tapes

Writes data/tapes/{control,signal}_s{1,2,3}.csv. Generation is deterministic, so
your files are byte-for-byte the same as everyone else's, and
`python -m research.check_replay` confirms that.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from research.simulator import SimConfig, write_tape  # noqa: E402

SEEDS = (1, 2, 3)
MODES = ("control", "signal")
N = 30000
TAPE_DIR = os.path.join(os.path.dirname(HERE), "data", "tapes")


def tape_path(mode: str, seed: int) -> str:
    return os.path.join(TAPE_DIR, "%s_s%d.csv" % (mode, seed))


def main() -> int:
    for mode in MODES:
        for seed in SEEDS:
            print("wrote", write_tape(SimConfig(seed=seed, n=N, mode=mode), tape_path(mode, seed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
