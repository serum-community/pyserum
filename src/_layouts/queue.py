from __future__ import annotations

from construct import BitStruct  # type: ignore
from construct import BitsInteger, BitsSwapped, Bytes, Const, Flag, Int8ul, Int32ul, Int64ul, Padding
from construct import Struct as cStruct  # type: ignore

from .account_flags import ACCOUNT_FLAGS_LAYOUT

# We will use a bitstruct with 64 bits instead of the widebits implementation in serum-js.
QUEUE_HEADER = cStruct(  # Swap to little endian
    Padding(5),
    "account_flags" / ACCOUNT_FLAGS_LAYOUT,
    "head" / Int32ul,
    Padding(4),
    "count" / Int32ul,
    Padding(4),
    "next_seq_num" / Int32ul,
    Padding(4),
)

REQUEST_FLAGS = BitsSwapped(
    BitStruct(
        "new_order" / Flag,
        "cancel_order" / Flag,
        "bid" / Flag,
        "postOnly" / Flag,
        "ioc" / Flag,
        Const(0, BitsInteger(3)),  # Padding
    )
)

REQUEST = cStruct(
    "request_flags" / REQUEST_FLAGS,
    "open_order_slot" / Int8ul,
    "fee_tier" / Int8ul,
    Padding(5),
    "max_base_size_or_cancelId" / Int64ul,
    "native_quote_quantity_locked" / Int64ul,
    "order_id" / Bytes(16),
    "open_orders" / Bytes(32),
    "client_order_id" / Int64ul,
)

EVENT_FLAGS = BitsSwapped(
    BitStruct(
        "fill" / Flag,
        "out" / Flag,
        "bid" / Flag,
        "maker" / Flag,
        Const(0, BitsInteger(4)),  # Padding
    )
)

EVENT = cStruct(
    "event_flags" / EVENT_FLAGS,
    "open_order_slot" / Int8ul,
    "fee_tier" / Int8ul,
    Padding(5),
    "native_quantity_released" / Int64ul,
    "native_quantity_paid" / Int64ul,
    "native_fee_or_rebate" / Int64ul,
    "order_id" / Bytes(16),
    "public_key" / Bytes(32),
    "client_order_id" / Int64ul,
)
