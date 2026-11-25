"""YOUR JOB: implement the Book.

One Book = one symbol. It keeps resting orders on two sides (bids, asks), matches
incoming orders by price-time priority, and reports everything that happens by
calling sink.on_event(<event>) with the dataclasses from lob/events.py.

The tiers below match the grader (python grade.py --tier N). Do them in order.
Read docs/DESIGN_cpp.md first: the data-structure discussion there is the
best hint you will get. The rules you must reproduce are in README.md (section "The rules").
"""
from __future__ import annotations

from .events import (Ack, CancelAck, Filled, ModifyAck, Partial, Reject,  # noqa: F401
                     STPCancel, Trade)
from .types import (DepthLevel, MarketDepth, Order, OrderType, RestingOrder,  # noqa: F401
                    Side, STPMode, TopOfBook)


class Book:
    def __init__(self, stp: STPMode = STPMode.NONE) -> None:
        self.stp = stp
        # TODO (Tier 1): choose your data structures.
        #   - How do you keep each side sorted by price (best first)?
        #   - How do you keep FIFO order inside one price level?
        #   - How do you cancel an order by id without scanning the whole book?
        # Think about the complexity of every operation before you start typing.

    # ------------------------------------------------------------------ Tier 1
    def submit(self, order: Order, sink) -> None:
        """Process a new order. Limit and Market for Tier 1; IOC/FOK in Tier 2.

        Order of checks and events (the grader is strict about this):
          1. Reject("invalid price")      if type != MARKET and price <= 0
          2. Reject("invalid quantity")   if qty <= 0
          3. Reject("duplicate order id") if id is already resting in this book
          4. (Tier 2) FOK: Reject("FOK not fillable") if the full qty can't fill now
          5. Ack(order.id)
          6. match against the opposite side; for every fill emit
             Trade(aggressor, resting, resting_price, qty, order.ts) then
             Filled(resting_id) if the resting order is now fully done
          7. if fully filled: Filled(order.id)
             else LIMIT: rest the remainder, and if it traded at all emit Partial(id, remaining)
                  MARKET/IOC: if it traded at all emit Partial(id, remaining), then CancelAck(id)
        """
        raise NotImplementedError("Tier 1: submit")

    def cancel(self, order_id: int, sink) -> None:
        """Remove a resting order. CancelAck(id), or Reject(id, "order not found")."""
        raise NotImplementedError("Tier 1: cancel")

    def top(self) -> TopOfBook:
        """Best bid/ask prices and the TOTAL resting qty at each best price."""
        raise NotImplementedError("Tier 1: top")

    def depth(self, levels: int) -> MarketDepth:
        """Up to `levels` price levels per side, best first. Each level aggregates
        total qty and the number of orders at that price."""
        raise NotImplementedError("Tier 1: depth")

    def order_count(self) -> int:
        """Number of orders currently resting in this book."""
        raise NotImplementedError("Tier 1: order_count")

    # ------------------------------------------------------------------ Tier 2
    def modify(self, order_id: int, new_price: int, new_qty: int, sink) -> None:
        """Reprice and/or resize a RESTING order. Passive: never matches, even if
        the new price crosses. The order goes to the BACK of its (new) queue.
        Check order: not found -> Reject("order not found"); new_qty <= 0 ->
        Reject("invalid quantity"); new_price <= 0 -> Reject("invalid price").
        On success emit ModifyAck(id, new_price, new_qty). No other events."""
        raise NotImplementedError("Tier 2: modify")

    # ------------------------------------------------------------------ Tier 3
    # Self-trade prevention lives inside your matching loop, driven by self.stp.
    # It only fires when order.trader_id != 0 and equals the resting order's trader_id.
    #   CANCEL_NEWEST: emit STPCancel(agg, resting, self.stp); stop; aggressor is
    #                  cancelled -> CancelAck(agg). Trades already done stay done.
    #   CANCEL_OLDEST: emit STPCancel; remove the RESTING order; keep matching.
    #   CANCEL_BOTH:   emit STPCancel; remove the resting order; aggressor is
    #                  cancelled -> CancelAck(agg).
    # FOK's "can I fill?" pre-check must also skip same-trader resting orders.
