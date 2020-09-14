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


class AccountType(IntEnum):
    """Account types defined by their corresponding memory sizes."""

    Market = 368
    """"""
    RequestQ = 640
    """"""
    EventQ = 1 << 20
    """"""
    Bids = 1 << 16
    """"""
    Asks = 1 << 16
    """"""
