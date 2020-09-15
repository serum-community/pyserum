import math
from typing import Any, Optional, Tuple

from ._layouts.queue import EVENT_LAYOUT, QUEUE_HEADER_LAYOUT, REQUEST_LAYOUT


# Expect header_layout and node_layout to be construct layout
def _decode_queue(header_layout: Any, node_layout: Any, buffer: bytes, history: Optional[int]) -> Tuple[Any, Any]:
    header = header_layout.parse(buffer)
    alloc_len = math.floor(len(buffer) - header_layout.sizeof() / node_layout.sizeof())
    nodes = []
    if history:
        for i in range(min(history, alloc_len)):
            node_index = (header.head + header.count + alloc_len - 1 - i) % alloc_len
            offset = header_layout.sizeof() + node_index * node_layout.sizeof()
            nodes.append(node_layout.parse(buffer[offset : offset + node_layout.sizeof()]))  # noqa: E203
    else:
        for i in range(header.count):
            node_index = (header.head + i) % alloc_len
            offset = header_layout.sizeof() + node_index * node_layout.sizeof()
            nodes.append(node_layout.parse(buffer[offset : offset + node_layout.sizeof()]))  # noqa: E203
    return header, nodes


def decode_request_queue(buffer: bytes, history: Optional[int] = None):
    header, nodes = _decode_queue(QUEUE_HEADER_LAYOUT, REQUEST_LAYOUT, buffer, history)
    if not header.account_flags.initialized or not header.account_flags.request_queue:
        raise Exception("Invalid requests queue, either not initialized or not a request queue.")
    return nodes


def decode_event_queue(buffer: bytes, history: Optional[int] = None):
    header, nodes = _decode_queue(QUEUE_HEADER_LAYOUT, EVENT_LAYOUT, buffer, history)
    if not header.account_flags.initialized or not header.account_flags.event_queue:
        raise Exception("Invalid events queue, either not initialized or not a request queue.")
    return nodes
