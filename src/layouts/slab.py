"""Slab data stucture that is used to represent Order book."""
from construct import Bytes, Int8ul, Int32ul, Int64ul, Padding  # type: ignore
from construct import Struct as cStruct
from construct import Switch

from .account_flags import ACCOUNT_FLAGS_LAYOUT

KEY = cStruct(
    "key" / Bytes(16),
)

SLAB_HEADER_LAYOUT = cStruct(
    "bump_index" / Int32ul,
    Padding(4),
    "free_list_length" / Int32ul,
    Padding(4),
    "free_list_head" / Int32ul,
    "root" / Int32ul,
    "leaf_count" / Int32ul,
    Padding(4),
)

# Different node types, we pad it all to size of 68 bytes.
UNINTIALIZED = cStruct(Padding(68))
INNER_NODE = cStruct("prefix_len" / Int32ul, "key" / KEY, "children" / Int32ul[2], Padding(40))
LEAF_NODE = cStruct(
    "owner_slot" / Int8ul,
    "fee_tier" / Int8ul,
    Padding(2),
    "key" / KEY,
    "owner" / Bytes(32),
    "quantity" / Int64ul,
    "client_order_id" / Int64ul,
)
FREE_NODE = cStruct("next" / Int32ul, Padding(64))
LAST_FREE_NODE = cStruct(Padding(68))

SLAB_NODE_LAYOUT = cStruct(
    "tag" / Int32ul,
    "node"
    / Switch(
        lambda this: this.tag,
        {
            0: UNINTIALIZED,
            1: INNER_NODE,
            2: LEAF_NODE,
            3: FREE_NODE,
            4: LAST_FREE_NODE,
        },
    ),
)

SLAB_LAYOUT = cStruct("header" / SLAB_HEADER_LAYOUT, "nodes" / SLAB_NODE_LAYOUT[lambda this: this.header.bump_index])

ORDER_BOOK_LAYOUT = cStruct(Padding(5), "account_flags" / ACCOUNT_FLAGS_LAYOUT, "slab_layout" / SLAB_LAYOUT, Padding(7))
