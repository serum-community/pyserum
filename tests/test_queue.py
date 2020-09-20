import base64

from src.market._internal.queue_ import decode_event_queue

from .binary_file_path import EVENT_QUEUE_BIN_PATH


def test_decode_event_queue():
    """Test decode event queue."""
    with open(EVENT_QUEUE_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        event_queue = decode_event_queue(data, 99)
        assert len(event_queue) == 99
        event_queue = decode_event_queue(data, 100)
        assert len(event_queue) == 100
        event = event_queue[0]
        assert not event.event_flags.fill
        assert event.event_flags.out
        assert event.event_flags.bid
        assert not event.event_flags.maker
        assert event.open_order_slot == 17
        assert event.fee_tier == 0
        assert event.native_fee_or_rebate == 0
