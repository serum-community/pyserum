"""Tests for account flags layout."""

from src.layouts.account_flags import ACCOUNT_FLAGS_LAYOUT


def default_flags():
    return {
        "initialized": False,
        "market": False,
        "openOrders": False,
        "requestQueue": False,
        "eventQueue": False,
        "bids": False,
        "asks": False,
    }


def test_correct_size():
    """Test account flags layout has 8 bytes."""
    assert ACCOUNT_FLAGS_LAYOUT.sizeof() == 8


def test_parses():
    """Test account flag layout parses."""
    parsed = ACCOUNT_FLAGS_LAYOUT.parse(bytes(16))
    assert not parsed["initialized"]
    assert parsed == default_flags()

    expected = default_flags()
    expected["initialized"] = True
    expected["market"] = True
    parsed = ACCOUNT_FLAGS_LAYOUT.parse(bytes.fromhex("0300000000000000"))
    assert parsed == expected

    expected = default_flags()
    expected["initialized"] = True
    expected["openOrders"] = True
    parsed = ACCOUNT_FLAGS_LAYOUT.parse(bytes.fromhex("0500000000000000"))
    assert parsed == expected


def test_serializes():
    flags = default_flags()
    flags["initialized"] = True
    flags["asks"] = True
    flags[None] = False  # XXX: Set empty flag
    assert ACCOUNT_FLAGS_LAYOUT.build(flags) == bytes.fromhex("4100000000000000")
