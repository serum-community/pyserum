"""Slab data stucture that is used to represent Order book."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable, List, NamedTuple, Optional

from construct import Bytes, Int8ul, Int32ul, Int64ul, Padding  # type: ignore
from construct import Struct as cStruct
from construct import Switch
from solana.publickey import PublicKey

from .account_flags import ACCOUNT_FLAGS_LAYOUT

KEY = Bytes(16)

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


class NodeType(IntEnum):
    UNINTIALIZED = 0
    INNER_NODE = 1
    LEAF_NODE = 2
    FREE_NODE = 3
    LAST_FREE_NODE = 4


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
            NodeType.UNINTIALIZED: UNINTIALIZED,
            NodeType.INNER_NODE: INNER_NODE,
            NodeType.LEAF_NODE: LEAF_NODE,
            NodeType.FREE_NODE: FREE_NODE,
            NodeType.LAST_FREE_NODE: LAST_FREE_NODE,
        },
    ),
)

SLAB_LAYOUT = cStruct("header" / SLAB_HEADER_LAYOUT, "nodes" / SLAB_NODE_LAYOUT[lambda this: this.header.bump_index])

ORDER_BOOK_LAYOUT = cStruct(Padding(5), "account_flags" / ACCOUNT_FLAGS_LAYOUT, "slab_layout" / SLAB_LAYOUT, Padding(7))


class SlabHeader(NamedTuple):
    bump_index: int
    free_list_length: int
    free_list_root: int
    root: int
    leaf_count: int


# UninitializedNode, FreeNode and LastFreeNode all maps to this class.
@dataclass
class SlabNode:
    is_initialized: bool
    next: int


@dataclass
class SlabLeafNode(SlabNode):
    owner_slot: int
    fee_tier: int
    key: int
    owner: PublicKey
    quantity: int
    client_order_id: int


@dataclass
class SlabInnerNode(SlabNode):
    prefix_len: int
    key: int
    children: List[int]


def convert_construct_node_to_class(construct_nodes) -> List[SlabNode]:
    res: List[SlabNode] = []
    for construct_node in construct_nodes:
        node_type = construct_node.tag
        node = construct_node.node
        if node_type == NodeType.UNINTIALIZED:
            res.append(SlabNode(is_initialized=False, next=-1))
        elif node_type == NodeType.LEAF_NODE:
            res.append(
                SlabLeafNode(
                    owner_slot=node.owner_slot,
                    fee_tier=node.fee_tier,
                    key=int.from_bytes(node.key, "little"),
                    owner=PublicKey(node.owner),
                    quantity=node.quantity,
                    client_order_id=node.client_order_id,
                    is_initialized=True,
                    next=-1,
                )
            )
        elif node_type == NodeType.INNER_NODE:
            res.append(
                SlabInnerNode(
                    prefix_len=node.prefix_len,
                    key=int.from_bytes(node.key, "little"),
                    children=node.children,
                    is_initialized=True,
                    next=-1,
                )
            )
        elif node_type == NodeType.FREE_NODE:
            res.append(SlabNode(next=node.next, is_initialized=True))
        elif node_type == NodeType.LAST_FREE_NODE:
            res.append(SlabNode(next=-1, is_initialized=True))
        else:
            raise RuntimeError("Unrecognized node type" + node.tag)
    return res


class Slab:
    def __init__(self, header: SlabHeader, nodes: List[SlabNode]):
        self._header = header
        self._nodes = nodes

    @staticmethod
    def decode(buffer: bytes) -> Slab:
        slab_layout = SLAB_LAYOUT.parse(buffer)
        header = slab_layout.header
        nodes = slab_layout.nodes
        return Slab(
            SlabHeader(
                bump_index=header.bump_index,
                free_list_length=header.free_list_length,
                free_list_root=header.free_list_head,
                root=header.root,
                leaf_count=header.leaf_count,
            ),
            convert_construct_node_to_class(nodes),
        )

    def get(self, search_key: int) -> Optional[SlabLeafNode]:
        if self._header.leaf_count == 0:
            return None
        index: int = self._header.root
        while True:
            node: SlabNode = self._nodes[index]
            if isinstance(node, SlabLeafNode):  # pylint: disable=no-else-return
                return node if node.key == search_key else None
            elif isinstance(node, SlabInnerNode):
                if (node.key ^ search_key) >> (128 - node.prefix_len) != 0:
                    return None
                # Check if the n-th bit (start from the least significant, i.e. rightmost) of the key is set
                index = node.children[(search_key >> (128 - node.prefix_len - 1)) & 1]
            else:
                raise RuntimeError("Should not go here! Node type not recognize.")

    def __iter__(self) -> Iterable[SlabLeafNode]:
        return self.items(False)

    def items(self, descending=False) -> Iterable[SlabLeafNode]:
        """Depth first traversal of the Binary Tree.
        Parameter descending decides if the price should descending or not.
        """
        if self._header.leaf_count == 0:
            return
        stack = [self._header.root]
        while stack:
            index = stack.pop()
            node: SlabNode = self._nodes[index]
            if isinstance(node, SlabLeafNode):
                yield node
            elif isinstance(node, SlabInnerNode):
                if descending:
                    stack.append(node.children[0])
                    stack.append(node.children[1])
                else:
                    stack.append(node.children[1])
                    stack.append(node.children[0])
            else:
                raise RuntimeError("Neither of leaf node or tree node!")
