"""Serum specific enums."""

from enum import Enum


class Side(Enum):
    """Side of the orderbook to trade."""

    Buy = 0
    """"""
    Sell = 1
    """"""


class OrderType(Enum):
    """"Type of order."""

    Limit = 0
    """"""
    IOC = 1
    """"""
    PostOnly = 2
    """"""
