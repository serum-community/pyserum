from __future__ import annotations

from typing import Iterable, List, Union

import pyserum.market.types as t

from ..enums import Side
from ._internal.slab import Slab, SlabInnerNode, SlabLeafNode
from .state import MarketState


class OrderBook:
    """Represents an order book."""

    _market_state: MarketState
    _is_bids: bool
    _slab: Slab

    def __init__(self, market_state: MarketState, account_flags: t.AccountFlags, slab: Slab) -> None:
        if not account_flags.initialized or not account_flags.bids ^ account_flags.asks:
            raise Exception("Invalid order book, either not initialized or neither of bids or asks")
        self._market_state = market_state
        self._is_bids = account_flags.bids
        self._slab = slab

    @staticmethod
    def __get_price_from_slab(node: Union[SlabInnerNode, SlabLeafNode]) -> int:
        """Get price from a slab node key.

        The key is constructed as the (price << 64) + (seq_no if ask_order else !seq_no).
        """
        return node.key >> 64

    @staticmethod
    def from_bytes(market_state: MarketState, buffer: bytes) -> OrderBook:
        """Decode the given buffer into an order book."""
        # This is a bit hacky at the moment. The first 5 bytes are padding, the
        # total length is 8 bytes which is 5 + 8 = 13 bytes.
        account_flags = t.AccountFlags.from_bytes(buffer[5:13])
        slab = Slab.from_bytes(buffer[13:])
        return OrderBook(market_state, account_flags, slab)

    def get_l2(self, depth: int) -> List[t.OrderInfo]:
        """Get the Level 2 market information."""
        descending = self._is_bids
        # The first element of the inner list is price, the second is quantity.
        levels: List[List[int]] = []
        for node in self._slab.items(descending):
            price = self.__get_price_from_slab(node)
            if len(levels) > 0 and levels[len(levels) - 1][0] == price:
                levels[len(levels) - 1][1] += node.quantity
            elif len(levels) == depth:
                break
            else:
                levels.append([price, node.quantity])
        return [
            t.OrderInfo(
                price=self._market_state.price_lots_to_number(price_lots),
                size=self._market_state.base_size_lots_to_number(size_lots),
                price_lots=price_lots,
                size_lots=size_lots,
            )
            for price_lots, size_lots in levels
        ]

    def __iter__(self) -> Iterable[t.Order]:
        return self.orders()

    def orders(self) -> Iterable[t.Order]:
        for node in self._slab.items():
            price = self.__get_price_from_slab(node)
            open_orders_address = node.owner

            yield t.Order(
                order_id=node.key,
                client_id=node.client_order_id,
                open_order_address=open_orders_address,
                fee_tier=node.fee_tier,
                info=t.OrderInfo(
                    price=self._market_state.price_lots_to_number(price),
                    price_lots=price,
                    size=self._market_state.base_size_lots_to_number(node.quantity),
                    size_lots=node.quantity,
                ),
                side=Side.BUY if self._is_bids else Side.SELL,
                open_order_slot=node.owner_slot,
            )
