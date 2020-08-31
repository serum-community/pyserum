"""Tests for enum."""
import pytest

from src.layouts.enum import Enum


def test_invalid():
    """Test invalid enums."""
    test_enum = Enum([])
    with pytest.raises(ValueError):
        test_enum.key(0)
    with pytest.raises(ValueError):
        test_enum.decode(b"\x00\x00\x00\x00")
    with pytest.raises(ValueError):
        test_enum.value("invalid")
    with pytest.raises(ValueError):
        test_enum.encode("invalid")


def test_encode():
    """Test encode enum."""
    side_layout = Enum(["buy", "sell"])
    assert side_layout.encode("buy") == b"\x00\x00\x00\x00"
    assert side_layout.encode("sell") == b"\x01\x00\x00\x00"
    order_type_layout = Enum(["limit", "ioc", "postOnly"])
    assert order_type_layout.encode("limit") == b"\x00\x00\x00\x00"
    assert order_type_layout.encode("ioc") == b"\x01\x00\x00\x00"
    assert order_type_layout.encode("postOnly") == b"\x02\x00\x00\x00"


def test_decode():
    """Test decode enum."""
    side_layout = Enum(["buy", "sell"])
    assert side_layout.decode(b"\x00\x00\x00\x00") == "buy"
    assert side_layout.decode(b"\x01\x00\x00\x00") == "sell"
    order_type_layout = Enum(["limit", "ioc", "postOnly"])
    assert order_type_layout.decode(b"\x00\x00\x00\x00") == "limit"
    assert order_type_layout.decode(b"\x01\x00\x00\x00") == "ioc"
    assert order_type_layout.decode(b"\x02\x00\x00\x00") == "postOnly"


def test_key_value():
    """Test enum key-values"""
    expected_key = "key"
    enum = Enum([expected_key])
    assert enum.key(0) == expected_key
    assert enum.value(expected_key) == 0
