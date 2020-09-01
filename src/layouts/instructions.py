"""Layouts for dex instructions data."""
from construct import Bytes, Int8ul, Int16ul, Int32ul, Int64ul  # type: ignore
from construct import Struct as cStruct
from construct import Switch

from .slab import KEY

INITIALIZE_MARKET = cStruct(
    "baseLotSize" / Int64ul,
    "quoteLotSize" / Int64ul,
    "feeRateBps" / Int16ul,
    "vaultSignerNonce" / Int64ul,
    "quoteDustThreshold" / Int64ul,
)

NEW_ORDER = cStruct(
    "side" / Int32ul,  # Enum
    "limitPrice" / Int64ul,
    "maxQuantity" / Int64ul,
    "orderType" / Int32ul,  # Enum
    "clientId" / Int64ul,
)

MATCH_ORDERS = cStruct("limit" / Int16ul)

CONSUME_EVENTS = cStruct("limit" / Int16ul)

CANCEL_ORDER = cStruct(
    "side" / Int32ul,  # Enum
    "orderId" / KEY,
    "openOrders" / Bytes(32),
    "openOrdersSlot" / Int8ul,
)

CANCEL_ORDER_BY_CLIENTID = cStruct("cancelOrderByClientId" / Int64ul)

INSTRUCTIONS_LAYOUT = cStruct(
    "version" / Int8ul,
    "instruction" / Int8ul,
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
