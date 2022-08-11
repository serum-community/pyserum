"""Layouts for dex instructions data."""
from enum import IntEnum

from construct import Bytes, Const, Int8ul, Int16ul, Int32ul, Int64ul
from construct import Struct as cStruct
from construct import Switch

from .slab import KEY


class InstructionType(IntEnum):
    INITIALIZE_MARKET = 0
    NEW_ORDER = 1
    MATCH_ORDERS = 2
    CONSUME_EVENTS = 3
    CANCEL_ORDER = 4
    SETTLE_FUNDS = 5
    CANCEL_ORDER_BY_CLIENT_ID = 6
    NEW_ORDER_V3 = 10
    CANCEL_ORDER_V2 = 11
    CANCEL_ORDER_BY_CLIENT_ID_V2 = 12
    CLOSE_OPEN_ORDERS = 14
    INIT_OPEN_ORDERS = 15
    PRUNE = 16
    CONSUME_EVENTS_PERMISSIONED = 17


_VERSION = 0

_INITIALIZE_MARKET = cStruct(
    "base_lot_size" / Int64ul,
    "quote_lot_size" / Int64ul,
    "fee_rate_bps" / Int16ul,
    "vault_signer_nonce" / Int64ul,
    "quote_dust_threshold" / Int64ul,
)

_NEW_ORDER = cStruct(
    "side" / Int32ul,  # Enum
    "limit_price" / Int64ul,
    "max_quantity" / Int64ul,
    "order_type" / Int32ul,  # Enum
    "client_id" / Int64ul,
)

_MATCH_ORDERS = cStruct("limit" / Int16ul)

_CONSUME_EVENTS = cStruct("limit" / Int16ul)

_CANCEL_ORDER = cStruct(
    "side" / Int32ul,
    "order_id" / KEY,
    "open_orders" / Bytes(32),
    "open_orders_slot" / Int8ul,  # Enum
)
_SETTLE_FUNDS = cStruct()

_CANCEL_ORDER_BY_CLIENTID = cStruct("client_id" / Int64ul)

_NEW_ORDER_V3 = cStruct(
    "side" / Int32ul,  # Enum
    "limit_price" / Int64ul,
    "max_base_quantity" / Int64ul,
    "max_quote_quantity" / Int64ul,
    "self_trade_behavior" / Int32ul,
    "order_type" / Int32ul,  # Enum
    "client_id" / Int64ul,
    "limit" / Int16ul,
)

_CANCEL_ORDER_V2 = cStruct(
    "side" / Int32ul,
    "order_id" / KEY,
)  # Enum

_CANCEL_ORDER_BY_CLIENTID_V2 = cStruct("client_id" / Int64ul)

_CLOSE_OPEN_ORDERS = cStruct()
_INIT_OPEN_ORDERS = cStruct()
_PRUNE = cStruct("limit" / Int16ul)
_CONSUME_EVENTS_PERMISSIONED = cStruct("limit" / Int16ul)

INSTRUCTIONS_LAYOUT = cStruct(
    "version" / Const(_VERSION, Int8ul),
    "instruction_type" / Int32ul,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {
            InstructionType.INITIALIZE_MARKET: _INITIALIZE_MARKET,
            InstructionType.NEW_ORDER: _NEW_ORDER,
            InstructionType.MATCH_ORDERS: _MATCH_ORDERS,
            InstructionType.CONSUME_EVENTS: _CONSUME_EVENTS,
            InstructionType.CANCEL_ORDER: _CANCEL_ORDER,
            InstructionType.SETTLE_FUNDS: _SETTLE_FUNDS,  # Empty list
            InstructionType.CANCEL_ORDER_BY_CLIENT_ID: _CANCEL_ORDER_BY_CLIENTID,
            InstructionType.NEW_ORDER_V3: _NEW_ORDER_V3,
            InstructionType.CANCEL_ORDER_V2: _CANCEL_ORDER_V2,
            InstructionType.CANCEL_ORDER_BY_CLIENT_ID_V2: _CANCEL_ORDER_BY_CLIENTID_V2,
            InstructionType.CLOSE_OPEN_ORDERS: _CLOSE_OPEN_ORDERS,
            InstructionType.INIT_OPEN_ORDERS: _INIT_OPEN_ORDERS,
            InstructionType.PRUNE: _PRUNE,
            InstructionType.CONSUME_EVENTS_PERMISSIONED: _CONSUME_EVENTS_PERMISSIONED,
        },
    ),
)
