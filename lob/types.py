"""Shared types. Prices are integer ticks, quantities whole units. No floats, ever."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"    # rests if not filled
    MARKET = "MARKET"  # sweeps at any price, never rests
    IOC = "IOC"        # fill what you can, kill the rest
    FOK = "FOK"        # all or nothing


class STPMode(Enum):
    """Self-trade prevention. The .value strings appear in STP_CANCEL events."""
    NONE = "NONE"
    CANCEL_NEWEST = "CANCEL_NEWEST"  # kill the incoming (aggressor) order
    CANCEL_OLDEST = "CANCEL_OLDEST"  # kill the resting order, keep matching
    CANCEL_BOTH = "CANCEL_BOTH"      # kill both


@dataclass
class Order:
    id: int
    side: Side
    price: int          # ignored for market orders
    qty: int
    ts: int
    type: OrderType = OrderType.LIMIT
    symbol: str = ""
    trader_id: int = 0  # 0 = no trader, STP never fires


@dataclass
class RestingOrder:
    id: int
    trader_id: int
    side: Side
    price: int
    remaining: int
    ts: int


@dataclass
class DepthLevel:
    price: int
    qty: int
    order_count: int


@dataclass
class TopOfBook:
    best_bid: Optional[int] = None
    best_ask: Optional[int] = None
    bid_qty: int = 0   # total resting qty at the best bid
    ask_qty: int = 0


@dataclass
class MarketDepth:
    bids: List[DepthLevel]  # best (highest price) first
    asks: List[DepthLevel]  # best (lowest price) first
