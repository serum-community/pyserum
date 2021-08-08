import math
from enum import IntEnum
from typing import List, Optional, Tuple, Union, cast

from construct import Container
from solana.publickey import PublicKey

from ..._layouts.queue import EVENT_LAYOUT, QUEUE_HEADER_LAYOUT, REQUEST_LAYOUT
from ..types import Event, EventFlags, Request, ReuqestFlags


class QueueType(IntEnum):
    EVENT = 1
    REQUEST = 2


def __from_bytes(
    buffer: bytes, queue_type: QueueType, history: Optional[int]
) -> Tuple[Container, List[Union[Event, Request]]]:
    header = QUEUE_HEADER_LAYOUT.parse(buffer)
    layout_size = EVENT_LAYOUT.sizeof() if queue_type == QueueType.EVENT else REQUEST_LAYOUT.sizeof()
    alloc_len = math.floor((len(buffer) - QUEUE_HEADER_LAYOUT.sizeof()) / layout_size)
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


def __parse_queue_item(buffer: bytes, queue_type: QueueType) -> Union[Event, Request]:
    if queue_type == QueueType.EVENT:  # pylint: disable=no-else-return
        parsed_item = EVENT_LAYOUT.parse(buffer)
        parsed_event_flags = parsed_item.event_flags
        event_flags = EventFlags(
            fill=parsed_event_flags.fill,
            out=parsed_event_flags.out,
            bid=parsed_event_flags.bid,
            maker=parsed_event_flags.maker,
        )

        return Event(
            event_flags=event_flags,
            open_order_slot=parsed_item.open_order_slot,
            fee_tier=parsed_item.fee_tier,
            native_quantity_released=parsed_item.native_quantity_released,
            native_quantity_paid=parsed_item.native_quantity_paid,
            native_fee_or_rebate=parsed_item.native_fee_or_rebate,
            order_id=int.from_bytes(parsed_item.order_id, "little"),
            public_key=PublicKey(parsed_item.public_key),
            client_order_id=parsed_item.client_order_id,
        )
    else:
        parsed_item = REQUEST_LAYOUT.parse(buffer)
        parsed_request_flags = parsed_item.request_flags
        request_flags = ReuqestFlags(
            new_order=parsed_request_flags.new_order,
            cancel_order=parsed_request_flags.cancel_order,
            bid=parsed_request_flags.bid,
            post_only=parsed_request_flags.post_only,
            ioc=parsed_request_flags.ioc,
        )

        return Request(
            request_flags=request_flags,
            open_order_slot=parsed_item.open_order_slot,
            fee_tier=parsed_item.fee_tier,
            max_base_size_or_cancel_id=parsed_item.max_base_size_or_cancel_id,
            native_quote_quantity_locked=parsed_item.native_quote_quantity_locked,
            order_id=int.from_bytes(parsed_item.order_id, "little"),
            open_orders=PublicKey(parsed_item.open_orders),
            client_order_id=parsed_item.client_order_id,
        )


def decode_request_queue(buffer: bytes, history: Optional[int] = None) -> List[Request]:
    header, nodes = __from_bytes(buffer, QueueType.REQUEST, history)
    if not header.account_flags.initialized or not header.account_flags.request_queue:
        raise Exception("Invalid requests queue, either not initialized or not a request queue.")
    return cast(List[Request], nodes)


def decode_event_queue(buffer: bytes, history: Optional[int] = None) -> List[Event]:
    header, nodes = __from_bytes(buffer, QueueType.EVENT, history)
    if not header.account_flags.initialized or not header.account_flags.event_queue:
        raise Exception("Invalid events queue, either not initialized or not a event queue.")
    return cast(List[Event], nodes)
