"""Tests for instruction layouts."""
from solana.publickey import PublicKey

from pyserum._layouts.instructions import _VERSION, INSTRUCTIONS_LAYOUT, InstructionType
from pyserum.enums import OrderType, Side


def assert_parsed_layout(instruction_type, args, raw_bytes):
    parsed = INSTRUCTIONS_LAYOUT.parse(raw_bytes)
    assert parsed.version == _VERSION
    assert parsed.instruction_type == int(instruction_type)
    if args:
        assert parsed.args == args
    else:
        assert not parsed.args


def test_parse_initialize_market():
    """Test parsing raw initialize market data."""
    args = {
        "base_lot_size": 1,
        "quote_lot_size": 2,
        "fee_rate_bps": 3,
        "vault_signer_nonce": 4,
        "quote_dust_threshold": 5,
    }
    expected = bytes.fromhex(
        "000000000001000000000000000200000000000000030004000000000000000500000000000000"
    )  # Raw hex from serum.js
    assert INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.INITIALIZE_MARKET, args=args)) == expected
    assert_parsed_layout(InstructionType.INITIALIZE_MARKET, args, expected)


def test_parse_new_order():
    """Test parsing raw new order data."""
    args = {
        "limit_price": 1,
        "max_quantity": 2,
        "client_id": 3,
        "side": Side.SELL,
        "order_type": OrderType.POST_ONLY,
    }
    expected = bytes.fromhex(
        "00010000000100000001000000000000000200000000000000020000000300000000000000"
    )  # Raw hex from serum.js
    assert INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.NEW_ORDER, args=args)) == expected
    assert_parsed_layout(InstructionType.NEW_ORDER, args, expected)


def test_parse_match_orders():
    """Test parsing raw match orders data."""
    args = {"limit": 1}
    expected = bytes.fromhex("00020000000100")  # Raw hex from serum.js
    assert INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.MATCH_ORDER, args=args)) == expected
    assert_parsed_layout(InstructionType.MATCH_ORDER, args, expected)


def test_parse_consume_events():
    """Test parsing raw consume events data."""
    args = {"limit": 1}
    expected = bytes.fromhex("00030000000100")  # Raw hex from serum.js
    assert INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.CONSUME_EVENTS, args=args)) == expected
    assert_parsed_layout(InstructionType.CONSUME_EVENTS, args, expected)


def test_parse_cancel_order():
    """Test parsing raw cancel order data."""
    args = {
        "side": Side.BUY,
        "order_id": (1234567890).to_bytes(16, "little"),
        "open_orders_slot": 123,
        "open_orders": bytes(PublicKey(123)),
    }
    expected = bytes.fromhex(
        "000400000000000000d202964900000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000007b7b"
    )  # Raw hex from serum.js
    assert INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.CANCEL_ORDER, args=args)) == expected
    assert_parsed_layout(InstructionType.CANCEL_ORDER, args, expected)


def test_parse_settle_funds():
    """Test parsing raw settle funds data."""
    expected = bytes.fromhex("0005000000")  # Raw hex from serum.js
    assert INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.SETTLE_FUNDS, args=None)) == expected
    assert_parsed_layout(InstructionType.SETTLE_FUNDS, None, expected)


def test_parse_cancel_order_by_client_id():
    """Test parsing raw cancel order data."""
    args = {"client_id": 123}
    expected = bytes.fromhex("00060000007b00000000000000")  # Raw hex from serum.js
    assert (
        INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.CANCEL_ORDER_BY_CLIENT_ID, args=args))
        == expected
    )
    assert_parsed_layout(InstructionType.CANCEL_ORDER_BY_CLIENT_ID, args, expected)
