"""Tests for instruction layouts."""
from solana.publickey import PublicKey

from src.enums import OrderType, Side
from src.layouts.instructions import _VERSION, INSTRUCTIONS_LAYOUT, InstructionType


def assert_parsed_layout(instruction_type, actual, expected_args):
    assert actual.version == _VERSION
    assert actual.instruction_type == int(instruction_type)
    assert actual.args == expected_args


def test_parse_initialize_market():
    """Test parsing raw initialize market data."""
    expected_args = {
        "base_lot_size": 1,
        "quote_lot_size": 2,
        "fee_rate_bps": 3,
        "vault_signer_nonce": 4,
        "quote_dust_threshold": 5,
    }
    raw = bytes.fromhex(
        "000000000001000000000000000200000000000000030004000000000000000500000000000000"
    )  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.InitializeMarket, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)


def test_parse_new_order():
    """Test parsing raw new order data."""
    expected_args = {
        "limit_price": 1,
        "max_quantity": 2,
        "client_id": 3,
        "side": Side.Sell,
        "order_type": OrderType.PostOnly,
    }
    raw = bytes.fromhex(
        "00010000000100000001000000000000000200000000000000020000000300000000000000"
    )  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.NewOrder, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)


def test_parse_match_orders():
    """Test parsing raw match orders data."""
    expected_args = {"limit": 1}
    raw = bytes.fromhex("00020000000100")  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.MatchOrder, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)


def test_parse_consume_events():
    """Test parsing raw consume events data."""
    expected_args = {"limit": 1}
    raw = bytes.fromhex("00030000000100")  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.ConsumeEvents, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)


def test_parse_cancel_order():
    """Test parsing raw cancel order data."""
    expected_args = {
        "side": Side.Buy,
        "order_id": (1234567890).to_bytes(16, "little"),
        "open_orders_slot": 123,
        "open_orders": bytes(PublicKey(123)),
    }
    raw = bytes.fromhex(
        "000400000000000000d202964900000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000007b7b"
    )  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.CancelOrder, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)


def test_parse_settle_funds():
    """Test parsing raw settle funds data."""
    raw = bytes.fromhex("0005000000")  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.SettleFunds, INSTRUCTIONS_LAYOUT.parse(raw), None)


def test_parse_cancel_order_by_client_id():
    """Test parsing raw cancel order data."""
    expected_args = {"client_id": 123}
    raw = bytes.fromhex("00060000007b00000000000000")  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.CancelOrderByClientID, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)
