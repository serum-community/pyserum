import math
from enum import IntEnum
from typing import List, Optional, Sequence, Tuple, Union, cast

from construct import Container  # type: ignore

from ..._layouts.queue import EVENT_LAYOUT, QUEUE_HEADER_LAYOUT, REQUEST_LAYOUT
from ..types import Event, Request


class QueueType(IntEnum):
    Event = 1
    Request = 2


def __from_bytes(
    buffer: Sequence[int], queue_type: QueueType, history: Optional[int]
) -> Tuple[Container, List[Union[Event, Request]]]:
    header = QUEUE_HEADER_LAYOUT.parse(buffer)
    layout_size = EVENT_LAYOUT.sizeof() if queue_type == QueueType.Event else REQUEST_LAYOUT.sizeof()
    alloc_len = math.floor(len(buffer) - QUEUE_HEADER_LAYOUT.sizeof() / layout_size)
    nodes: List[Union[Event, Request]] = []
    if history:
        for i in range(min(history, alloc_len)):
            node_index = (header.head + header.count + alloc_len - 1 - i) % alloc_len
            offset = QUEUE_HEADER_LAYOUT.sizeof() + node_index * layout_size
            nodes.append(__parse_queue_item(buffer[offset : offset + layout_size], queue_type))  # noqa: E203
    else:
        for i in range(header.count):
            node_index = (header.head + i) % alloc_len
            offset = QUEUE_HEADER_LAYOUT.sizeof() + node_index * layout_size
            nodes.append(__parse_queue_item(buffer[offset : offset + layout_size], queue_type))  # noqa: E203
    return header, nodes


def __parse_queue_item(buffer: Sequence[int], queue_type: QueueType) -> Union[Event, Request]:
    layout = EVENT_LAYOUT if queue_type.Event else REQUEST_LAYOUT
    parsed_item = layout.parse(buffer)
    parsed_item.pop("_io")
    return Event(**parsed_item) if queue_type == QueueType.Event else Request(**parsed_item)


def decode_request_queue(buffer: bytes, history: Optional[int] = None) -> List[Request]:
    header, nodes = __from_bytes(buffer, QueueType.Request, history)
    if not header.account_flags.initialized or not header.account_flags.request_queue:
        raise Exception("Invalid requests queue, either not initialized or not a request queue.")
    return cast(List[Request], nodes)


def decode_event_queue(buffer: bytes, history: Optional[int] = None) -> List[Event]:
    header, nodes = __from_bytes(buffer, QueueType.Event, history)
    if not header.account_flags.initialized or not header.account_flags.event_queue:
        raise Exception("Invalid events queue, either not initialized or not a request queue.")
    return cast(List[Event], nodes)
