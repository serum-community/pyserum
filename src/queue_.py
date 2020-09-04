import math
from typing import Any, Optional, Tuple

from ._layouts.queue import EVENT, QUEUE_HEADER, REQUEST


# Expect header_layout and node_layout to be construct layout
def _decode_queue(header_layout: Any, node_layout: Any, buffer: bytes, history: int) -> Tuple[Any, Any]:
    header = header_layout.parse(buffer)
    alloc_len = math.floor(float(len(buffer) - header_layout.sizeof() / node_layout.sizeof()))
    nodes = []
    num_of_nodes = min(history, alloc_len) if history else header.count
    for i in range(num_of_nodes):
        node_index = (header.head + header.count + alloc_len - 1 - i) % alloc_len
        nodes.append(node_layout.parse(buffer[header_layout.sizeof() + node_index * node_layout.sizeof() :]))
    return header, nodes


def decode_request_queue(buffer: bytes, history: Optional[int] = None):
    header, nodes = _decode_queue(QUEUE_HEADER, REQUEST, buffer, history)
    if not header.account_flags.initialized or not header.account_flags.request_queue:
        raise Exception("Invalid requests queue, either not initialized or not a request queue.")
    return nodes


def decode_event_queue(buffer: bytes, history: Optional[int] = None):
    header, nodes = _decode_queue(QUEUE_HEADER, EVENT, buffer, history)
    if not header.account_flags.initialized or not header.account_flags.event_queue:
        raise Exception("Invalid events queue, either not initialized or not a request queue.")
    return nodes
