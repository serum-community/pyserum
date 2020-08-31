"""Tests for enum."""
import pytest

from src.layouts.enum import Enum


def test_invalid():
    """Test invalid enums."""
    with pytest.raises(ValueError):
        Enum({"invalid1": 0, "invalid2": 0})
    with pytest.raises(ValueError):
        Enum({"invalid1": 0, "invalid2": 1, "invalid3": 4})
    with pytest.raises(ValueError):
        Enum({"invalid": 4294967296})

    test_enum = Enum({})
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
    side_layout = Enum({"buy": 0, "sell": 1})
    assert side_layout.encode("buy") == b"\x00\x00\x00\x00"
    assert side_layout.encode("sell") == b"\x01\x00\x00\x00"
    order_type_layout = Enum({"limit": 0, "ioc": 1, "postOnly": 2})
    assert order_type_layout.encode("limit") == b"\x00\x00\x00\x00"
    assert order_type_layout.encode("ioc") == b"\x01\x00\x00\x00"
    assert order_type_layout.encode("postOnly") == b"\x02\x00\x00\x00"


def test_decode():
    """Test decode enum."""
    side_layout = Enum({"buy": 0, "sell": 1})
    assert side_layout.decode(b"\x00\x00\x00\x00") == "buy"
    assert side_layout.decode(b"\x01\x00\x00\x00") == "sell"
    order_type_layout = Enum({"limit": 0, "ioc": 1, "postOnly": 2})
    assert order_type_layout.decode(b"\x00\x00\x00\x00") == "limit"
    assert order_type_layout.decode(b"\x01\x00\x00\x00") == "ioc"
    assert order_type_layout.decode(b"\x02\x00\x00\x00") == "postOnly"


def test_key_value():
    """Test enum key-values"""
    expected_key = "key"
    expected_value = 0
    enum = Enum({expected_key: expected_value})
    assert enum.key(expected_value) == expected_key
    assert enum.value(expected_key) == expected_value
