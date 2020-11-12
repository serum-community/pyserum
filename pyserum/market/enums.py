"""Serum specific enums."""

from enum import IntEnum


class Side(IntEnum):
    """Side of the orderbook to trade."""

    Buy = 0
    """"""
    Sell = 1
    """"""


class OrderType(IntEnum):
    """"Type of order."""

    Limit = 0
    """"""
    IOC = 1
    """"""
    PostOnly = 2
    """"""
