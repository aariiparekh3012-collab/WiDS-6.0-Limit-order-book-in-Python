"""Events the book emits. Field names and order match the C++ JSON sink exactly."""
from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Dict, List

from .types import STPMode


class _Event:
    NAME = "?"

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"event": self.NAME}
        for f in fields(self):  # type: ignore[arg-type]
            v = getattr(self, f.name)
            d[f.name] = v.value if isinstance(v, Enum) else v
        return d


@dataclass
class Ack(_Event):
    order_id: int
    NAME = "ACK"


@dataclass
class Trade(_Event):
    aggressor_id: int
    resting_id: int
    price: int          # the RESTING order's price
    qty: int
    ts: int             # the aggressor's timestamp
    NAME = "TRADE"


@dataclass
class Filled(_Event):
    order_id: int
    NAME = "FILLED"


@dataclass
class Partial(_Event):
    order_id: int
    remaining: int
    NAME = "PARTIAL"


@dataclass
class CancelAck(_Event):
    order_id: int
    NAME = "CANCEL_ACK"


@dataclass
class Reject(_Event):
    order_id: int
    reason: str
    NAME = "REJECT"


@dataclass
class STPCancel(_Event):
    aggressor_id: int
    resting_id: int
    mode: STPMode
    NAME = "STP_CANCEL"


@dataclass
class ModifyAck(_Event):
    order_id: int
    new_price: int
    new_qty: int
    NAME = "MODIFY_ACK"


class VectorSink:
    """Collects events into a list. Pass one to Book.submit/cancel/modify."""

    def __init__(self) -> None:
        self.events: List[_Event] = []

    def on_event(self, event: _Event) -> None:
        self.events.append(event)

    def clear(self) -> None:
        self.events.clear()

    def __len__(self) -> int:
        return len(self.events)
