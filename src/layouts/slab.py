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


class Slab:
    def __init__(self, header, nodes):
        self._header = header
        self._nodes = nodes

    @staticmethod
    def decode(buffer: bytes):
        slab_layout = SLAB_LAYOUT.parse(buffer)
        return Slab(slab_layout.header, slab_layout.nodes)

    def get(self, key: int):
        if self._header.leaf_count == 0:
            return None
        index: int = self._header.root
        while True:
            # This contains `tag` and `node`.
            slab_node = self._nodes[index]
            node_type:int = slab_node.tag
            node = slab_node.node
            # None of tree node or inner node
            if node_type not in (1, 2):
                raise Exception("Cannot find " + str(key) + " in slab.")

            # Node key is in bytes, convert it to int.
            node_key:int = int.from_bytes(node.key, "little")
            # Leaf Node that matches
            if node_type == 2:
                if node_key == key:
                    return node
                return None
            elif node_type == 1:  # no-qa: no-else-return
                if (node_key ^ key) >> (128 - slab_node.node.prefix_len) != 0:
                    return None
                # Check if the n-th bit (start from the least significant, i.e. rightmost) of the key is set
                index = node.children[(key >> (128 - node.prefix_len - 1)) & 1]

    def __iter__(self):
        return self

    def __next__(self):
        return self.items(False)

    def items(self, descending=False):
        """Depth first traversal of the Binary Tree.
        Parameter descending decides if the price should descending or not.
        """
        if self._header.leaf_count == 0:
            return
        stack = [self._header.root]
        while stack:
            index = stack.pop()
            slab_node = self._nodes[index]
            node_type = slab_node.tag
            node = slab_node.node
            if node_type == 2:
                yield node
            elif node_type == 1:
                if descending:
                    stack.append(node.children[0])
                    stack.append(node.children[1])
                else:
                    stack.append(node.children[1])
                    stack.append(node.children[0])
