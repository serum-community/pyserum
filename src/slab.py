"""Slab data stucture that is used to represent Order book."""
from construct import Int8ul, Int32ul, Int64ul, PaddedString, Padding  # type: ignore
from construct import Struct as cStruct
from construct import Switch

KEY = cStruct(
    "part1" / Int64ul,
    "part2" / Int64ul,
)

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

# Different node types
UNINTIALIZED = cStruct()
INNER_NODE = cStruct("prefixLen" / Int32ul, "key" / KEY, "children" / Int32ul[2])
LEAF_NODE = cStruct(
    "ownerSlot" / Int8ul,
    "feeTier" / Int8ul,
    Padding(2),
    "key" / KEY,
    "owner" / PaddedString(32, "utf-8"),
    "quantity" / Int64ul,
    "clientOrderId" / Int64ul,
)
FREE_NODE = cStruct(
    "next" / Int32ul,
)
LAST_FREE_NODE = cStruct()

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
