from construct import BitStruct, BitsInteger, BitsSwapped, Bytes, Const, Flag, Int8ul, Int32ul, Int64ul, Padding
from construct import Struct as cStruct

from .account_flags import ACCOUNT_FLAGS_LAYOUT

QUEUE_HEADER_LAYOUT = cStruct(
    Padding(5),
    "account_flags" / ACCOUNT_FLAGS_LAYOUT,
    "head" / Int32ul,
    Padding(4),
    "count" / Int32ul,
    Padding(4),
    "next_seq_num" / Int32ul,
    Padding(4),
)

REQUEST_FLAGS_LAYOUT = BitsSwapped(  # Swap to little endian
    BitStruct(
        "new_order" / Flag,
        "cancel_order" / Flag,
        "bid" / Flag,
        "post_only" / Flag,
        "ioc" / Flag,
        Const(0, BitsInteger(3)),  # Padding
    )
)

REQUEST_LAYOUT = cStruct(
    "request_flags" / REQUEST_FLAGS_LAYOUT,
    "open_order_slot" / Int8ul,
    "fee_tier" / Int8ul,
    Padding(5),
    "max_base_size_or_cancel_id" / Int64ul,
    "native_quote_quantity_locked" / Int64ul,
    "order_id" / Bytes(16),
    "open_orders" / Bytes(32),
    "client_order_id" / Int64ul,
)

EVENT_FLAGS_LAYOUT = BitsSwapped(
    BitStruct(
        "fill" / Flag,
        "out" / Flag,
        "bid" / Flag,
        "maker" / Flag,
        Padding(4),
    )
)

EVENT_LAYOUT = cStruct(
    "event_flags" / EVENT_FLAGS_LAYOUT,
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
