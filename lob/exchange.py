"""Routes orders to one Book per symbol. PROVIDED, you do not need to edit this.

Educational router: probe each book; forward success or an existing order's validation rejection.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from .events import CancelAck, ModifyAck, Reject, VectorSink
from .types import MarketDepth, Order, STPMode, TopOfBook


class Exchange:
    def __init__(self, stp: STPMode = STPMode.NONE,
                 book_factory: Optional[Callable[[STPMode], object]] = None) -> None:
        if book_factory is None:
            from .book import Book
            book_factory = Book
        self._factory = book_factory
        self._stp = stp
        self._books: Dict[str, object] = {}

    def add_symbol(self, sym: str) -> None:
        self._books.setdefault(sym, self._factory(self._stp))

    def has_symbol(self, sym: str) -> bool:
        return sym in self._books

    def symbols(self) -> List[str]:
        return list(self._books)

    def submit(self, order: Order, sink) -> None:
        book = self._books.get(order.symbol)
        if book is None:
            sink.on_event(Reject(order.id, "unknown symbol: " + order.symbol))
            return
        book.submit(order, sink)

    def cancel(self, order_id: int, sink) -> None:
        for book in self._books.values():
            if book.order_count() == 0:
                continue
            probe = VectorSink()
            book.cancel(order_id, probe)
            if any(isinstance(e, CancelAck) for e in probe.events):
                for e in probe.events:
                    sink.on_event(e)
                return
        sink.on_event(Reject(order_id, "order not found"))

    def modify(self, order_id: int, new_price: int, new_qty: int, sink) -> None:
        for book in self._books.values():
            if book.order_count() == 0:
                continue
            probe = VectorSink()
            book.modify(order_id, new_price, new_qty, probe)
            if any(isinstance(e, ModifyAck) or
                   (isinstance(e, Reject) and e.reason != "order not found")
                   for e in probe.events):
                for e in probe.events:
                    sink.on_event(e)
                return
        sink.on_event(Reject(order_id, "order not found"))

    def top(self, sym: str) -> TopOfBook:
        book = self._books.get(sym)
        return book.top() if book else TopOfBook()

    def depth(self, sym: str, levels: int) -> MarketDepth:
        book = self._books.get(sym)
        return book.depth(levels) if book else MarketDepth([], [])
