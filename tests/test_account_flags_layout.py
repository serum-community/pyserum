"""Tests for account flags layout."""

from src._layouts.account_flags import ACCOUNT_FLAGS_LAYOUT


def default_flags():
    return {
        "initialized": False,
        "market": False,
        "open_orders": False,
        "request_queue": False,
        "event_queue": False,
        "bids": False,
        "asks": False,
    }


def test_correct_size():
    """Test account flags layout has 8 bytes."""
    assert ACCOUNT_FLAGS_LAYOUT.sizeof() == 8


def test_decode():
    """Test account flag layout parses."""
    parsed = ACCOUNT_FLAGS_LAYOUT.parse(bytes(16))
    assert not parsed.initialized
    assert parsed == default_flags()

    expected = default_flags()
    expected["initialized"] = True
    expected["market"] = True
    parsed = ACCOUNT_FLAGS_LAYOUT.parse(bytes.fromhex("0300000000000000"))
    assert parsed == expected

    expected = default_flags()
    expected["initialized"] = True
    expected["open_orders"] = True
    parsed = ACCOUNT_FLAGS_LAYOUT.parse(bytes.fromhex("0500000000000000"))
    assert parsed == expected


def test_encode():
    """Test account flag layout serializes."""
    flags = default_flags()
    flags["initialized"] = True
    flags["asks"] = True
    assert ACCOUNT_FLAGS_LAYOUT.build(flags) == bytes.fromhex("4100000000000000")
