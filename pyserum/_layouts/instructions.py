"""Layouts for dex instructions data."""
from enum import IntEnum

from construct import Switch  # type: ignore
from construct import Bytes, Const, Int8ul, Int16ul, Int32ul, Int64ul, Pass
from construct import Struct as cStruct

from .slab import KEY


class InstructionType(IntEnum):
    InitializeMarket = 0
    NewOrder = 1
    MatchOrder = 2
    ConsumeEvents = 3
    CancelOrder = 4
    SettleFunds = 5
    CancelOrderByClientID = 6
    NewOrderV3 = 10
    CancelOrderV2 = 11
    CancelOrderByClientIdV2 = 12


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
    "side" / Int32ul,  # Enum
    "order_id" / KEY,
    "open_orders" / Bytes(32),
    "open_orders_slot" / Int8ul,
)

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
    "side" / Int32ul,  # Enum
    "order_id" / KEY,
)

_CANCEL_ORDER_BY_CLIENTID_V2 = cStruct("client_id" / Int64ul)

INSTRUCTIONS_LAYOUT = cStruct(
    "version" / Const(_VERSION, Int8ul),
    "instruction_type" / Int32ul,
    "args"
    / Switch(
        lambda this: this.instruction_type,
        {
            InstructionType.InitializeMarket: _INITIALIZE_MARKET,
            InstructionType.NewOrder: _NEW_ORDER,
            InstructionType.MatchOrder: _MATCH_ORDERS,
            InstructionType.ConsumeEvents: _CONSUME_EVENTS,
            InstructionType.CancelOrder: _CANCEL_ORDER,
            InstructionType.SettleFunds: Pass,  # Empty list
            InstructionType.CancelOrderByClientID: _CANCEL_ORDER_BY_CLIENTID,
            InstructionType.NewOrderV3: _NEW_ORDER_V3,
            InstructionType.CancelOrderV2: _CANCEL_ORDER_V2,
            InstructionType.CancelOrderByClientIdV2: _CANCEL_ORDER_BY_CLIENTID_V2,
        },
    ),
)
