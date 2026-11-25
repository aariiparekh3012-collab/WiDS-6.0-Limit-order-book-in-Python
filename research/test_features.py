"""Self-checks for research/features.py.   python -m unittest research.test_features -v

Small hand-made examples. Passing them does not prove your features are right,
but failing them tells you exactly what is off.
"""
import unittest

try:
    import numpy as np
    import pandas as pd
except ImportError as exc:  # pragma: no cover
    raise unittest.SkipTest("install the research packages first: pip install -r requirements-research.txt") from exc

from research import features as F


def book(rows):
    """rows: (best_bid, bid_qty, best_ask, ask_qty, bid_depth5, ask_depth5, signed_vol)"""
    cols = ["best_bid", "bid_qty", "best_ask", "ask_qty", "bid_depth5", "ask_depth5", "signed_vol"]
    df = pd.DataFrame(rows, columns=cols)
    df.index.name = "idx"
    return F.add_quotes(df)


class TestFeatures(unittest.TestCase):
    def test_depth_imbalance_example(self):
        d = book([(100, 700, 101, 300, 900, 600, 0)])
        self.assertAlmostEqual(F.depth_imbalance(d, 1).iloc[0], 0.4)
        self.assertAlmostEqual(F.depth_imbalance(d, 5).iloc[0], 0.2)

    def test_depth_imbalance_missing_or_crossed(self):
        d = book([(None, 0, 101, 300, 0, 300, 0), (101, 5, 100, 5, 5, 5, 0), (100, 0, 101, 0, 0, 0, 0)])
        self.assertTrue(F.depth_imbalance(d, 1).isna().all())

    def test_ofi_quantity_added_at_bid(self):
        d = book([(100, 10, 101, 10, 10, 10, 0), (100, 15, 101, 10, 15, 10, 0)])
        e = F.ofi(d)
        self.assertTrue(np.isnan(e.iloc[0]))
        self.assertAlmostEqual(e.iloc[1], 5.0)

    def test_ofi_bid_price_rises(self):
        d = book([(100, 10, 102, 10, 10, 10, 0), (101, 5, 102, 10, 5, 10, 0)])
        # bid rises to 101 (+5 new), ask unchanged at 102 (-10 now, +10 before): 5 - 0 - 10 + 10
        self.assertAlmostEqual(F.ofi(d).iloc[1], 5.0)

    def test_rolling_sum_needs_full_window(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        r = F.rolling_sum(s, 3)
        self.assertTrue(r.iloc[:2].isna().all())
        self.assertEqual(list(r.iloc[2:]), [6.0, 9.0])

    def test_signed_volume_window(self):
        d = book([(100, 1, 101, 1, 1, 1, v) for v in (5, -2, 3, 0)])
        self.assertEqual(list(F.signed_volume(d, 2).iloc[1:]), [3.0, 1.0, 3.0])

    def test_rolling_vol_is_std_of_changes(self):
        mid = pd.Series([100.0, 101.0, 101.0, 103.0])
        v = F.rolling_vol(mid, 2)
        self.assertAlmostEqual(v.iloc[3], float(np.std([0.0, 2.0], ddof=1)))

    def test_lagged_returns_look_backward(self):
        mid = pd.Series([100.0, 101.0, 103.0, 102.0])
        r = F.lagged_returns(mid, (1, 2))
        self.assertEqual(list(r.columns), ["ret_lag1", "ret_lag2"])
        self.assertAlmostEqual(r["ret_lag1"].iloc[2], 2.0)
        self.assertAlmostEqual(r["ret_lag2"].iloc[3], 1.0)
        self.assertTrue(np.isnan(r["ret_lag1"].iloc[0]))

    def test_labels(self):
        mids = [100, 100, 101, 100, 100, 99, 99, 99, 99, 99, 99, 100]
        d = pd.DataFrame({"mid": [float(m) for m in mids]})
        y = F.make_labels(d, horizon=3)
        self.assertEqual(y.iloc[0], 0.0)   # 100 -> 100
        self.assertEqual(y.iloc[1], 0.0)   # 100 -> 100
        self.assertEqual(y.iloc[2], -1.0)  # 101 -> 99 (row 5)
        self.assertTrue(y.iloc[-3:].isna().all())

    def test_labels_skip_missing_mid(self):
        d = pd.DataFrame({"mid": [100.0, np.nan, 101.0, 102.0, 103.0]})
        y = F.make_labels(d, horizon=2)
        self.assertEqual(y.iloc[0], 1.0)
        self.assertTrue(np.isnan(y.iloc[1]))

    def test_chrono_split_is_ordered_and_purged(self):
        n, h = 1000, 10
        s = F.chrono_split(n, 0.6, 0.2, h)
        for k in ("train", "val", "test"):
            self.assertTrue(len(s[k]) > 0)
        # the last label in each part must look ahead no further than the start of the next part
        self.assertLess(s["train"].max() + h, s["val"].min())
        self.assertLess(s["val"].max() + h, s["test"].min())
        self.assertLessEqual(s["test"].max() + h, n - 1)
        self.assertEqual(len(set(s["train"]) & set(s["val"])) + len(set(s["val"]) & set(s["test"])), 0)


if __name__ == "__main__":
    unittest.main()
