from __future__ import annotations

from typing import NamedTuple

from solana.publickey import PublicKey

from .._layouts.account_flags import ACCOUNT_FLAGS_LAYOUT
from ..enums import Side


class AccountFlags(NamedTuple):
    initialized: bool = False
    """"""
    market: bool = False
    """"""
    open_orders: bool = False
    """"""
    request_queue: bool = False
    """"""
    event_queue: bool = False
    """"""
    bids: bool = False
    """"""
    asks: bool = False
    """"""

    @staticmethod
    def from_bytes(buffer: bytes) -> AccountFlags:
        con = ACCOUNT_FLAGS_LAYOUT.parse(buffer)
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
    """"""
    side: Side
    """"""
    price: float
    """"""
    size: float
    """"""
    fee_cost: int
    """"""


class OrderInfo(NamedTuple):
    price: float
    """"""
    size: float
    """"""
    price_lots: int
    """"""
    size_lots: int
    """"""


class Order(NamedTuple):
    order_id: int
    """"""
    client_id: int
    """"""
    open_order_address: PublicKey
    """"""
    open_order_slot: int
    """"""
    fee_tier: int
    """"""
    info: OrderInfo
    """"""
    side: Side
    """"""


class ReuqestFlags(NamedTuple):
    new_order: bool
    cancel_order: bool
    bid: bool
    post_only: bool
    ioc: bool


class Request(NamedTuple):
    request_flags: ReuqestFlags
    """"""
    open_order_slot: int
    """"""
    fee_tier: int
    """"""
    max_base_size_or_cancel_id: int
    """"""
    native_quote_quantity_locked: int
    """"""
    order_id: int
    """"""
    open_orders: PublicKey
    """"""
    client_order_id: int
    """"""


class EventFlags(NamedTuple):
    fill: bool
    out: bool
    bid: bool
    maker: bool


class Event(NamedTuple):
    event_flags: EventFlags
    """"""
    open_order_slot: int
    """"""
    fee_tier: int
    """"""
    native_quantity_released: int
    """"""
    native_quantity_paid: int
    """"""
    native_fee_or_rebate: int
    """"""
    order_id: int
    """"""
    public_key: PublicKey
    """"""
    client_order_id: int
    """"""


class MarketInfo(NamedTuple):
    name: str
    """"""
    address: PublicKey
    """"""
    program_id: PublicKey
    """"""


class TokenInfo(NamedTuple):
    name: str
    """"""
    address: PublicKey
    """"""
