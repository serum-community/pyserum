"""Unit tests for market."""

import base64

from pyserum._layouts.market.slab import ORDER_BOOK_LAYOUT, SLAB_HEADER_LAYOUT, SLAB_LAYOUT, SLAB_NODE_LAYOUT
from pyserum.market._internal.slab import Slab

from tests.binary_file_path import ASK_ORDER_BIN_PATH

HEX_DATA = "0900000000000000020000000000000008000000000000000400000000000000010000001e00000000000040952fe4da5c1f3c860200000004000000030000000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d7b0000000000000000000000000000000200000002000000000000a0ca17726dae0f1e43010000001111111111111111111111111111111111111111111111111111111111111111410100000000000000000000000000000200000001000000d20a3f4eeee073c3f60fe98e010000000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d7b000000000000000000000000000000020000000300000000000040952fe4da5c1f3c8602000000131313131313131313131313131313131313131313131313131313131313131340e20100000000000000000000000000010000001f0000000500000000000000000000000000000005000000060000000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d7b0000000000000000000000000000000200000004000000040000000000000000000000000000001717171717171717171717171717171717171717171717171717171717171717020000000000000000000000000000000100000020000000000000a0ca17726dae0f1e430100000001000000020000000d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d7b000000000000000000000000000000040000000000000004000000000000000000000000000000171717171717171717171717171717171717171717171717171717171717171702000000000000000000000000000000030000000700000005000000000000000000000000000000171717171717171717171717171717171717171717171717171717171717171702000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"  # noqa: E501 # pylint: disable=line-too-long
DATA = bytes.fromhex(HEX_DATA)


def test_parse_order_book():
    """Test order book parsing."""
    with open(ASK_ORDER_BIN_PATH, "r") as input_file:
        base64_res = input_file.read()
        data = base64.decodebytes(base64_res.encode("ascii"))
        res = ORDER_BOOK_LAYOUT.parse(data)
        assert res.account_flags.initialized
        assert not res.account_flags.market
        assert res.account_flags.asks
        assert res.slab_layout.header.bump_index == 239
        assert res.slab_layout.header.free_list_length == 210
        assert res.slab_layout.header.free_list_head == 174
        assert res.slab_layout.header.root == 0
        assert res.slab_layout.header.leaf_count == 15
        assert len(res.slab_layout.nodes) == 239
        assert res.slab_layout.nodes[0].tag == 1
        assert res.slab_layout.nodes[0].node.prefix_len == 51


def test_parse_header():
    """Test parse slab headers."""
    # We only parse the data for the header which is the first 32 bytes.
    header = SLAB_HEADER_LAYOUT.parse(DATA[:32])
    assert header.bump_index == 9
    assert header.free_list_length == 2
    assert header.free_list_head == 8


def test_parse_node():
    """Test the parsing logic for a SLAB node."""
    # We only parse the data for the first node. The header is of length 32 bytes.
    # And the slab node layout requires 72 bytes (4 bytes for tag and 68 bytes for node data).
    slab_node = SLAB_NODE_LAYOUT.parse(DATA[32 : 32 + 72])  # noqa: E203
    assert slab_node.tag == 1
    assert slab_node.node.prefix_len == 30
    assert slab_node.node.children == [4, 3]


def test_parse_slab():
    slab = SLAB_LAYOUT.parse(DATA)
    assert len(slab.nodes) == 9
    assert slab.nodes[1].tag == 2
    assert slab.nodes[1].node.fee_tier == 0
    assert slab.nodes[1].node.quantity == 321


def test_slab_get():
    slab = Slab.from_bytes(DATA)
    assert slab.get(123456789012345678901234567890).owner_slot == 1
    assert slab.get(100000000000000000000000000000).owner_slot == 2
    assert slab.get(200000000000000000000000000000).owner_slot == 3
    assert slab.get(4).owner_slot == 4
    assert slab.get(0) is None
    assert slab.get(3) is None
    assert slab.get(5) is None
    assert slab.get(6) is None
    assert slab.get(200000000000000000000000000001) is None
    assert slab.get(100000000000000000000000000001) is None
    assert slab.get(123456789012345678901234567889) is None
    assert slab.get(123456789012345678901234567891) is None
    assert slab.get(99999999999999999999999999999) is None


def test_length_of_slab_iterator():
    slab = Slab.from_bytes(DATA)
    assert sum(1 for _ in slab.items()) == 4


def test_iterate_in_ascending_order():
    slab = Slab.from_bytes(DATA)
    prev = None
    for node in slab.items():
        curr_key = node.key
        if prev:
            assert curr_key > prev
        prev = curr_key


def test_iterate_in_descending_order():
    slab = Slab.from_bytes(DATA)
    prev = None
    for node in slab.items(descending=True):
        curr_key = node.key
        if prev:
            assert curr_key < prev
        prev = curr_key
