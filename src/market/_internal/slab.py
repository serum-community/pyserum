from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, NamedTuple, Optional, Sequence

from solana.publickey import PublicKey

from ..._layouts.slab import SLAB_LAYOUT, NodeType


class SlabHeader(NamedTuple):
    bump_index: int
    free_list_length: int
    free_list_root: int
    root: int
    leaf_count: int


# Used as dummy value for SlabNode#next.
NONE_NEXT = -1


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
                    next=NONE_NEXT,
                )
            )
        elif node_type == NodeType.INNER_NODE:
            res.append(
                SlabInnerNode(
                    prefix_len=node.prefix_len,
                    key=int.from_bytes(node.key, "little"),
                    children=node.children,
                    is_initialized=True,
                    next=NONE_NEXT,
                )
            )
        elif node_type == NodeType.FREE_NODE:
            res.append(SlabNode(is_initialized=True, next=node.next))
        elif node_type == NodeType.LAST_FREE_NODE:
            res.append(SlabNode(is_initialized=True, next=NONE_NEXT))
        else:
            raise RuntimeError("Unrecognized node type" + node.tag)
    return res


class Slab:
    def __init__(self, header: SlabHeader, nodes: List[SlabNode]):
        self._header = header
        self._nodes = nodes

    @staticmethod
    def from_bytes(buffer: Sequence[int]) -> Slab:
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
