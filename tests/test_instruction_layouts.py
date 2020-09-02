"""Tests for instruction layouts."""
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


def test_parse_match_orders():
    """Test parsing raw match orders data."""
    expected_args = {"limit": 1}
    raw = bytes.fromhex("00020000000100")  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.MatchOrder, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)


def test_consume_events():
    """Test parsing raw consume events data."""
    expected_args = {"limit": 1}
    raw = bytes.fromhex("00030000000100")  # Raw hex from serum.js
    assert_parsed_layout(InstructionType.ConsumeEvents, INSTRUCTIONS_LAYOUT.parse(raw), expected_args)
