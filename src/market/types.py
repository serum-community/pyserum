from __future__ import annotations

from typing import NamedTuple

from solana.publickey import PublicKey

from .._layouts.account_flags import ACCOUNT_FLAGS_LAYOUT
from ..enums import Side


class AccountFlags(NamedTuple):
    initialized: bool = False
    market: bool = False
    open_orders: bool = False
    request_queue: bool = False
    event_queue: bool = False
    bids: bool = False
    asks: bool = False

    @staticmethod
    def from_bytes(date_bytes: bytes) -> AccountFlags:
        con = ACCOUNT_FLAGS_LAYOUT.parse(date_bytes)
        return AccountFlags(
            initialized=con.initialized,
            market=con.market,
            open_orders=con.open_orders,
            request_queue=con.request_queue,
            event_queue=con.event_queue,
            bids=con.bids,
            asks=con.asks,
        )


class FilledOrder(NamedTuple):
    order_id: int
    side: Side
    price: float
    size: float
    fee_cost: int


class OrderInfo(NamedTuple):
    price: float
    size: float
    price_lots: int
    size_lots: int


class Order(NamedTuple):
    order_id: int
    client_id: int
    open_order_address: PublicKey
    open_order_slot: int
    fee_tier: int
    order_info: OrderInfo
    side: Side
