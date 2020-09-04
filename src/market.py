"""Market module to interact with Serum DEX."""
from __future__ import annotations

import base64
from typing import Any, Iterable, List, NamedTuple

from solana.publickey import PublicKey
from solana.rpc.api import Client

from ._layouts.account_flags import ACCOUNT_FLAGS_LAYOUT
from ._layouts.market import MARKET_LAYOUT, MINT_LAYOUT
from ._layouts.slab import Slab
from .instructions import DEFAULT_DEX_PROGRAM_ID
from .queue_ import decode_event_queue


class Market:
    """Represents a Serum Market."""

    _decode: Any
    _baseSplTokenDecimals: int
    _quoteSplTokenDecimals: int
    _skipPreflight: bool
    _confirmations: int
    _porgram_id: PublicKey

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        decoded: Any,
        base_mint_decimals: int,
        quote_mint_decimals: int,
        options: Any,  # pylint: disable=unused-argument
        endpoint: str,
        program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID,
    ) -> None:
        # TODO: add options
        if not decoded.account_flags.initialized or not decoded.account_flags.market:
            raise Exception("Invalid market state")
        self._decode = decoded
        self._base_spl_token_decimals = base_mint_decimals
        self._quote_spl_token_decimals = quote_mint_decimals
        self._skip_preflight = False
        self._confirmations = 10
        self._program_id = program_id
        self._endpoint = endpoint

    @staticmethod
    # pylint: disable=unused-argument
    def load(
        endpoint: str, market_address: str, options: Any, program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    ) -> Market:
        """Factory method to create a Market."""
        http_client = Client(endpoint)
        base64_res = http_client.get_account_info(market_address)["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(base64_res.encode("ascii"))
        market_state = MARKET_LAYOUT.parse(bytes_data)

        # TODO: add ownAddress check!
        if not market_state.account_flags.initialized or not market_state.account_flags.market:
            raise Exception("Invalid market")

        base_mint_decimals = Market.get_mint_decimals(endpoint, PublicKey(market_state.base_mint))
        quote_mint_decimals = Market.get_mint_decimals(endpoint, PublicKey(market_state.quote_mint))

        return Market(market_state, base_mint_decimals, quote_mint_decimals, options, endpoint)

    def address(self) -> PublicKey:
        """Return market address."""
        raise NotImplementedError("address is not implemented yet")

    def base_mint_address(self) -> PublicKey:
        """Returns base mint address."""
        raise NotImplementedError("base_mint_address is not implemented yet")

    def quote_mint_address(self) -> PublicKey:
        """Returns quote mint address."""
        raise NotImplementedError("quote_mint_address is not implemented yet")

    def __base_spl_token_multiplier(self) -> int:
        return 10 ** self._base_spl_token_decimals

    def __quote_spl_token_multiplier(self) -> int:
        return 10 ** self._quote_spl_token_decimals

    def price_lots_to_number(self, price: int) -> float:
        return float(price * self._decode.quote_lot_size * self.__base_spl_token_multiplier()) / (
            self._decode.base_lot_size * self.__quote_spl_token_multiplier()
        )

    def price_number_to_lots(self, price: float) -> int:
        raise NotImplementedError("price_number_to_lots is not implemented")

    def base_size_lots_to_number(self, size: int) -> float:
        return float(size * self._decode.base_lot_size) / self.__base_spl_token_multiplier()

    @staticmethod
    def get_mint_decimals(endpoint: str, mint_pub_key: PublicKey) -> int:
        """Get the mint decimals from given public key."""
        data = Client(endpoint).get_account_info(mint_pub_key)["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(data.encode("ascii"))
        return MINT_LAYOUT.parse(bytes_data).decimals

    def load_bids(self):
        """Load the bid order book"""
        bids_addr = PublicKey(self._decode.bids)
        res = Client(self._endpoint).get_account_info(bids_addr)
        data = res["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(data.encode("ascii"))
        return OrderBook.decode(self, bytes_data)

    def load_asks(self):
        """Load the Ask order book."""
        asks_addr = PublicKey(self._decode.asks)
        res = Client(self._endpoint).get_account_info(asks_addr)
        data = res["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(data.encode("ascii"))
        return OrderBook.decode(self, bytes_data)

    def load_fills(self, limit=100):
        event_queue_addr = PublicKey(self._decode.event_queue)
        res = Client(self._endpoint).get_account_info(event_queue_addr)
        data = res["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(data.encode("ascii"))
        events = decode_event_queue(bytes_data, limit)
        print("raw events", events)
        return list(filter(lambda event: event.event_flags.fill and event.native_quantity_paid > 0, events))


class OrderInfo(NamedTuple):
    price: float
    size: float
    price_lots: int
    size_lots: int


class Order(NamedTuple):
    order_id: int
    client_id: int
    open_order_address: PublicKey
    fee_tier: int
    order_info: OrderInfo
    side: str


# The key is constructed as the (price << 64) + (seq_no if ask_order else !seq_no)
def get_price_from_key(key: int) -> int:
    return key >> 64


class OrderBook:
    """Represents an order book."""

    _market: Market
    _is_bids: bool
    _slab: Slab

    def __init__(self, market: Market, account_flags: Any, slab: Slab) -> None:
        if not account_flags.initialized or not account_flags.bids ^ account_flags.asks:
            raise Exception("Invalid order book, either not initialized or neither of bids or asks")
        self._market = market
        self._is_bids = account_flags.bids
        self._slab = slab

    @staticmethod
    def decode(market: Market, buffer: bytes) -> OrderBook:
        """Decode the given buffer into an order book."""
        # This is a bit hacky at the moment. The first 5 bytes are padding, the
        # total length is 8 bytes which is 5 + 8 = 13 bytes.
        account_flags = ACCOUNT_FLAGS_LAYOUT.parse(buffer[5:13])
        slab = Slab.decode(buffer[13:])
        return OrderBook(market, account_flags, slab)

    def get_l2(self, depth: int) -> List[OrderInfo]:
        """Get the Level 2 market information."""
        descending = self._is_bids
        # The first elment of the inner list is price, the second is quantity.
        levels: List[List[int]] = []
        for node in self._slab.items(descending):
            price = get_price_from_key(node.key)
            if len(levels) > 0 and levels[len(levels) - 1][0] == price:
                levels[len(levels) - 1][1] += node.quantity
            elif len(levels) == depth:
                break
            else:
                levels.append([price, node.quantity])
        return [
            OrderInfo(
                price=self._market.price_lots_to_number(price_lots),
                size=self._market.base_size_lots_to_number(size_lots),
                price_lots=price_lots,
                size_lots=size_lots,
            )
            for price_lots, size_lots in levels
        ]

    def __iter__(self) -> Iterable[Order]:
        return self.orders()

    def orders(self) -> Iterable[Order]:
        for node in self._slab.items():
            key = node.key
            price = get_price_from_key(key)
            open_orders_address = node.owner

            yield Order(
                order_id=key,
                client_id=node.client_order_id,
                open_order_address=open_orders_address,
                fee_tier=node.fee_tier,
                order_info=OrderInfo(
                    price=self._market.price_lots_to_number(price),
                    price_lots=price,
                    size=self._market.base_size_lots_to_number(node.quantity),
                    size_lots=node.quantity,
                ),
                side="buy" if self._is_bids else "sell",
            )
