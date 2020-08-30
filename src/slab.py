"""Slab data stucture that is used to represent Order book."""
from construct import Int8ul, Int32ul, Int64ul, PaddedString, Padding, Union, Switch  # type: ignore
from construct import Struct as cStruct

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
INNER_NODE = cStruct(
    "prefixLen" / Int32ul,
    "key" / PaddedString(16, "utf-8"),
    "children" / Int32ul[2]
)
LEAF_NODE = cStruct(
    "ownerSlot" / Int8ul,
    "feeTier" / Int8ul,
    Padding(2),
    "key" / PaddedString(16, "utf-8"),
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
    "node" / Switch(lambda this: this.tag,
    {
        0: UNINTIALIZED,
        1: INNER_NODE,
        2: LEAF_NODE,
        3: FREE_NODE,
        4: LAST_FREE_NODE,
    })


)

# Union(None,
#     "unintialized" / UNINTIALIZED,
#     "inner_node" / INNER_NODE,
#     "leaf_node" / LEAF_NODE,
#     "free_node" / FREE_NODE,
#     "last_free_node" / LAST_FREE_NODE,
# )

SLAB_LAYOUT = cStruct("header" / SLAB_HEADER_LAYOUT, SLAB_NODE_LAYOUT[lambda this: this.header.bump_index])
