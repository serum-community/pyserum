import base64

from src.queue_ import decode_event_queue

def test_decode_event_queue():
    """Test order book parsing."""
    with open("tests/binary/event_queue_binary.txt", "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        event_queue = decode_event_queue(data, 99)
        assert len(event_queue) == 99
        event_queue = decode_event_queue(data, 100)
        assert len(event_queue) == 100
        e = event_queue[0]
        assert not e.event_flags.fill
        assert e.event_flags.out
        assert e.event_flags.bid
        assert not e.event_flags.maker
        assert e.open_order_slot == 17
        assert e.fee_tier == 0
        assert e.native_fee_or_rebate == 0
        