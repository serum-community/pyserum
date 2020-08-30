"""Slab data stucture that is used to represent Order book."""
from construct import Int8ul, Int32ul, Int64ul, PaddedString, Padding  # type: ignore
from construct import Struct as cStruct

SLAB_HEADER_LAYOUT = cStruct(
    "bump_index" / Int32ul,
    "padding1" / Padding(4),
    "free_list_length" / Int32ul,
    "padding2" / Padding(4),
    "free_list_head" / Int32ul,
    "root" / Int32ul,
    "leaf_count" / Int32ul,
    "padding3" / Padding(4),
)

UNINTIALIZED = cStruct()

LEAF_NODE = cStruct(
    "owner_slot" / Int8ul,
    "fee_tier" / Int8ul,
    Padding(2),
    "key" / PaddedString(16, "ascii"),  # double check this.
    Padding(32),
    "quantity" / Int64ul,
)

SLAB_LAYOUT = cStruct(SLAB_HEADER_LAYOUT)
