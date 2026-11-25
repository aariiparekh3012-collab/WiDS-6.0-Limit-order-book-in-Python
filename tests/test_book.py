"""Small unit tests to run while you work:  python -m unittest -v tests.test_book

They check behaviour you can reason about by hand. The grader is still the
real judge. Use  IMPL=some.module python -m unittest ...  to run another Book.
"""
import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lob.events import Ack, CancelAck, Filled, ModifyAck, Partial, Reject, Trade, VectorSink  # noqa: E402
from lob.types import Order, OrderType, Side  # noqa: E402

Book = importlib.import_module(os.environ.get("IMPL", "lob.book")).Book
ts = [0]


def mk(i, side, price, qty, typ=OrderType.LIMIT):
    ts[0] += 1
    return Order(i, side, price, qty, ts[0], typ, "X")


def run(book, order):
    s = VectorSink()
    book.submit(order, s)
    return s.events


class Tier1(unittest.TestCase):
    def test_rest_and_top(self):
        b = Book()
        self.assertEqual(run(b, mk(1, Side.BUY, 100, 10)), [Ack(1)])
        t = b.top()
        self.assertEqual((t.best_bid, t.bid_qty, t.best_ask), (100, 10, None))

    def test_trade_at_resting_price(self):
        b = Book()
        run(b, mk(1, Side.SELL, 101, 5))
        ev = run(b, mk(2, Side.BUY, 105, 5))
        self.assertEqual(ev, [Ack(2), Trade(2, 1, 101, 5, ts[0]), Filled(1), Filled(2)])

    def test_fifo_within_level(self):
        b = Book()
        run(b, mk(1, Side.BUY, 100, 5))
        run(b, mk(2, Side.BUY, 100, 5))
        ev = run(b, mk(3, Side.SELL, 100, 5))
        self.assertEqual(ev[1].resting_id, 1)

    def test_partial_then_rest(self):
        b = Book()
        run(b, mk(1, Side.SELL, 100, 3))
        ev = run(b, mk(2, Side.BUY, 100, 10))
        self.assertIsInstance(ev[-1], Partial)
        self.assertEqual(ev[-1].remaining, 7)
        self.assertEqual(b.top().best_bid, 100)

    def test_market_never_rests(self):
        b = Book()
        run(b, mk(1, Side.SELL, 100, 3))
        ev = run(b, mk(2, Side.BUY, 0, 10, OrderType.MARKET))
        self.assertIsInstance(ev[-1], CancelAck)
        self.assertEqual(b.order_count(), 0)

    def test_cancel_and_rejects(self):
        b = Book()
        run(b, mk(1, Side.BUY, 100, 5))
        s = VectorSink()
        b.cancel(1, s)
        self.assertEqual(s.events, [CancelAck(1)])
        s.clear()
        b.cancel(1, s)
        self.assertEqual(s.events, [Reject(1, "order not found")])
        self.assertEqual(run(b, mk(2, Side.BUY, 0, 5)), [Reject(2, "invalid price")])
        self.assertEqual(run(b, mk(3, Side.BUY, 5, 0)), [Reject(3, "invalid quantity")])

    def test_depth_aggregates(self):
        b = Book()
        run(b, mk(1, Side.BUY, 100, 5))
        run(b, mk(2, Side.BUY, 100, 7))
        d = b.depth(5)
        self.assertEqual((d.bids[0].price, d.bids[0].qty, d.bids[0].order_count), (100, 12, 2))


class Tier2(unittest.TestCase):
    def test_fok_all_or_nothing(self):
        b = Book()
        run(b, mk(1, Side.SELL, 100, 3))
        self.assertEqual(run(b, mk(2, Side.BUY, 100, 5, OrderType.FOK)), [Reject(2, "FOK not fillable")])
        self.assertEqual(b.top().ask_qty, 3)

    def test_modify_loses_priority_and_is_passive(self):
        b = Book()
        run(b, mk(1, Side.BUY, 100, 5))
        run(b, mk(2, Side.BUY, 100, 5))
        s = VectorSink()
        b.modify(1, 100, 4, s)
        self.assertEqual(s.events, [ModifyAck(1, 100, 4)])
        ev = run(b, mk(3, Side.SELL, 100, 5))
        self.assertEqual(ev[1].resting_id, 2)


if __name__ == "__main__":
    unittest.main()
