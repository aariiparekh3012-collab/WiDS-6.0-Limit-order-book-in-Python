"""Week 4 feature pipeline. YOUR JOB: fill in the functions marked TODO.

You get `load_states` and `add_quotes`. Everything else is yours. The functions
take and return pandas objects indexed by the command index `idx` that
`research.record` writes, so row t is "the market after command t".

Self-check as you go:    python -m unittest research.test_features -v

Rules that matter more than any formula
  * A feature at row t may use rows 0..t only. Never look forward.
  * Never use the simulator's hidden fair value. You cannot see it anyway.
  * Empty or crossed books have no mid price. Say so with NaN, do not invent one.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def load_states(path: str) -> pd.DataFrame:
    """Read a states file written by research.record. Provided."""
    return pd.read_csv(path).set_index("idx")


def add_quotes(df: pd.DataFrame) -> pd.DataFrame:
    """Add `valid`, `mid` and `spread`. Provided, read it to see the NaN convention.

    valid   True when both sides have a quote and bid < ask
    mid     (best_ask + best_bid) / 2 when valid, else NaN
    spread  best_ask - best_bid when valid, else NaN
    """
    out = df.copy()
    both = out["best_bid"].notna() & out["best_ask"].notna()
    out["valid"] = both & (out["best_bid"] < out["best_ask"])
    out["mid"] = np.where(out["valid"], (out["best_bid"] + out["best_ask"]) / 2.0, np.nan)
    out["spread"] = np.where(out["valid"], out["best_ask"] - out["best_bid"], np.nan)
    return out


# --------------------------------------------------------------------------- TODO


def depth_imbalance(df: pd.DataFrame, levels: int = 1) -> pd.Series:
    """TODO. (bid qty - ask qty) / (bid qty + ask qty), between -1 and +1.

    levels=1 uses bid_qty and ask_qty (the best quotes).
    levels=5 uses bid_depth5 and ask_depth5 (the best five levels per side).
    Return NaN where the book is not valid or the total quantity is zero.
    Example: bid 700 and ask 300 gives +0.4.
    """
    raise NotImplementedError("depth_imbalance")


def ofi(df: pd.DataFrame) -> pd.Series:
    """TODO. Order-flow imbalance contribution e_n at each row (Cont, Kukanov, Stoikov).

    With P and q the best price and quantity, and n-1 the previous row:
        e_n =  1[Pb_n >= Pb_(n-1)] * qb_n  -  1[Pb_n <= Pb_(n-1)] * qb_(n-1)
             - 1[Pa_n <= Pa_(n-1)] * qa_n  +  1[Pa_n >= Pa_(n-1)] * qa_(n-1)
    Positive means net buying pressure. Return NaN where this row or the
    previous row is not a valid book.
    """
    raise NotImplementedError("ofi")


def rolling_sum(s: pd.Series, window: int) -> pd.Series:
    """TODO. Sum of the last `window` values, ending at the current row.

    NaN until a full window exists. Use this to turn `ofi` into a windowed OFI.
    """
    raise NotImplementedError("rolling_sum")


def signed_volume(df: pd.DataFrame, window: int) -> pd.Series:
    """TODO. Aggressive buy volume minus aggressive sell volume over the last `window` commands.

    The `signed_vol` column is already signed per command. Sum it over the window.
    """
    raise NotImplementedError("signed_volume")


def rolling_vol(mid: pd.Series, window: int) -> pd.Series:
    """TODO. Standard deviation of one-step mid-price changes over the last `window` rows."""
    raise NotImplementedError("rolling_vol")


def lagged_returns(mid: pd.Series, lags=(1, 5, 10)) -> pd.DataFrame:
    """TODO. Past price changes: mid_t - mid_(t-k) for each k in lags.

    Name the columns ret_lag1, ret_lag5, ... Look BACKWARD only.
    """
    raise NotImplementedError("lagged_returns")


def make_labels(df: pd.DataFrame, horizon: int = 10) -> pd.Series:
    """TODO. The target: sign(mid[t + horizon] - mid[t]), so -1, 0 or +1.

    `horizon` counts COMMANDS, using the idx column. NaN when mid is missing at
    t or at t + horizon, and for the last `horizon` rows.
    This is the only place the future is allowed to appear, and only in the label.
    """
    raise NotImplementedError("make_labels")


def chrono_split(n: int, train: float = 0.6, val: float = 0.2, horizon: int = 10) -> dict:
    """TODO. Split rows 0..n-1 in time into train, validation and test index arrays.

    Boundaries sit at int(n * train) and int(n * (train + val)).
    Purge: drop any row whose label looks `horizon` rows ahead across a boundary,
    so no label in one part uses prices from the next part. The test part also
    drops its last `horizon` rows, which have no label.
    Return {"train": array, "val": array, "test": array} of row positions.
    """
    raise NotImplementedError("chrono_split")


# ------------------------------------------------------------------------ provided


def build(df: pd.DataFrame, horizon: int = 10) -> pd.DataFrame:
    """Assemble features and label from a states DataFrame. Provided; it calls your functions."""
    d = add_quotes(df)
    X = pd.DataFrame(index=d.index)
    X["spread"] = d["spread"]
    X["imb1"] = depth_imbalance(d, 1)
    X["imb5"] = depth_imbalance(d, 5)
    e = ofi(d)
    X["ofi10"] = rolling_sum(e, 10)
    X["ofi50"] = rolling_sum(e, 50)
    X["sv10"] = signed_volume(d, 10)
    X["sv50"] = signed_volume(d, 50)
    X["vol50"] = rolling_vol(d["mid"], 50)
    X = X.join(lagged_returns(d["mid"], (1, 5, 10)))
    X["mid"] = d["mid"]
    X["y"] = make_labels(d, horizon)
    return X


FEATURE_COLUMNS = ["spread", "imb1", "imb5", "ofi10", "ofi50", "sv10", "sv50", "vol50",
                   "ret_lag1", "ret_lag5", "ret_lag10"]
