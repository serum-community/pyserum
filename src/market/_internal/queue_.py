import math
from typing import List, Optional, Sequence, Tuple

from construct import Container, Struct  # type: ignore

from ..._layouts.queue import EVENT_LAYOUT, QUEUE_HEADER_LAYOUT, REQUEST_LAYOUT


def __decode_queue(
    queue_layout: Struct, buffer: Sequence[int], history: Optional[int]
) -> Tuple[Container, List[Container]]:
    header = QUEUE_HEADER_LAYOUT.parse(buffer)
    alloc_len = math.floor(len(buffer) - QUEUE_HEADER_LAYOUT.sizeof() / queue_layout.sizeof())
    nodes = []
    if history:
        for i in range(min(history, alloc_len)):
            node_index = (header.head + header.count + alloc_len - 1 - i) % alloc_len
            offset = QUEUE_HEADER_LAYOUT.sizeof() + node_index * queue_layout.sizeof()
            nodes.append(queue_layout.parse(buffer[offset : offset + queue_layout.sizeof()]))  # noqa: E203
    else:
        for i in range(header.count):
            node_index = (header.head + i) % alloc_len
            offset = QUEUE_HEADER_LAYOUT.sizeof() + node_index * queue_layout.sizeof()
            nodes.append(queue_layout.parse(buffer[offset : offset + queue_layout.sizeof()]))  # noqa: E203
    return header, nodes


def decode_request_queue(buffer: bytes, history: Optional[int] = None) -> List[Container]:
    header, nodes = __decode_queue(REQUEST_LAYOUT, buffer, history)
    if not header.account_flags.initialized or not header.account_flags.request_queue:
        raise Exception("Invalid requests queue, either not initialized or not a request queue.")
    return nodes


def decode_event_queue(buffer: bytes, history: Optional[int] = None) -> List[Container]:
    header, nodes = __decode_queue(EVENT_LAYOUT, buffer, history)
    if not header.account_flags.initialized or not header.account_flags.event_queue:
        raise Exception("Invalid events queue, either not initialized or not a request queue.")
    return nodes
