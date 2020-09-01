"""Layouts for dex instructions data."""
from construct import Bytes, Int8ul, Int16ul, Int32ul, Int64ul  # type: ignore
from construct import Struct as cStruct
from construct import Switch

from .slab import KEY

INITIALIZE_MARKET = cStruct(
    "base_lot_size" / Int64ul,
    "quote_lot_size" / Int64ul,
    "fee_rate_bps" / Int16ul,
    "vault_signer_nonce" / Int64ul,
    "quote_dust_threshold" / Int64ul,
)

NEW_ORDER = cStruct(
    "side" / Int32ul,  # Enum
    "limit_price" / Int64ul,
    "max_quantity" / Int64ul,
    "order_type" / Int32ul,  # Enum
    "client_id" / Int64ul,
)

MATCH_ORDERS = cStruct("limit" / Int16ul)

CONSUME_EVENTS = cStruct("limit" / Int16ul)

CANCEL_ORDER = cStruct(
    "side" / Int32ul,  # Enum
    "order_id" / KEY,
    "open_orders" / Bytes(32),
    "open_orders_slot" / Int8ul,
)

CANCEL_ORDER_BY_CLIENTID = cStruct("client_id" / Int64ul)

INSTRUCTIONS_LAYOUT = cStruct(
    "version" / Int8ul,
    "instruction_type" / Int8ul,
    "params"
    / Switch(
        lambda this: this.instruction,
        {
            0: INITIALIZE_MARKET,
            1: NEW_ORDER,
            2: MATCH_ORDERS,
            3: CONSUME_EVENTS,
            4: CANCEL_ORDER,
            5: Bytes(0),  # Is this the right way to do an empty struct?
            6: CANCEL_ORDER_BY_CLIENTID,
        },
    ),
)
