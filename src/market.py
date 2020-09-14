"""Market module to interact with Serum DEX."""
from __future__ import annotations

import math
from typing import Any, Iterable, List, NamedTuple, Tuple

from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction, TransactionInstruction

from ._layouts.account_flags import ACCOUNT_FLAGS_LAYOUT
from ._layouts.market import MARKET_LAYOUT, MINT_LAYOUT
from ._layouts.slab import Slab
from .enums import Side
from .instructions import DEFAULT_DEX_PROGRAM_ID, CancelOrderParams, MatchOrdersParams, NewOrderParams
from .instructions import cancel_order as cancel_order_inst
from .instructions import match_orders as match_order_inst
from .queue_ import decode_event_queue, decode_request_queue
from .utils import load_bytes_data


# pylint: disable=too-many-public-methods
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
        bytes_data = load_bytes_data(PublicKey(market_address), endpoint)
        market_state = MARKET_LAYOUT.parse(bytes_data)

        # TODO: add ownAddress check!
        if not market_state.account_flags.initialized or not market_state.account_flags.market:
            raise Exception("Invalid market")

        base_mint_decimals = Market.get_mint_decimals(endpoint, PublicKey(market_state.base_mint))
        quote_mint_decimals = Market.get_mint_decimals(endpoint, PublicKey(market_state.quote_mint))

        return Market(market_state, base_mint_decimals, quote_mint_decimals, options, endpoint, program_id=program_id)

    def address(self) -> PublicKey:
        """Return market address."""
        return PublicKey(self._decode.own_address)

    def public_key(self) -> PublicKey:
        return self.address()

    def program_id(self) -> PublicKey:
        return self._program_id

    def base_mint_address(self) -> PublicKey:
        """Returns base mint address."""
        return PublicKey(self._decode.base_mint)

    def quote_mint_address(self) -> PublicKey:
        """Returns quote mint address."""
        return PublicKey(self._decode.quote_mint)

    def __base_spl_token_multiplier(self) -> int:
        return 10 ** self._base_spl_token_decimals

    def __quote_spl_token_multiplier(self) -> int:
        return 10 ** self._quote_spl_token_decimals

    def base_spl_size_to_number(self, size: int) -> float:
        return size / self.__base_spl_token_multiplier()

    def quote_spl_size_to_number(self, size: int) -> float:
        return size / self.__quote_spl_token_multiplier()

    def price_lots_to_number(self, price: int) -> float:
        return float(price * self._decode.quote_lot_size * self.__base_spl_token_multiplier()) / (
            self._decode.base_lot_size * self.__quote_spl_token_multiplier()
        )

    def price_number_to_lots(self, price: float) -> int:
        raise NotImplementedError("price_number_to_lots is not implemented")

    def base_size_lots_to_number(self, size: int) -> float:
        return float(size * self._decode.base_lot_size) / self.__base_spl_token_multiplier()

    def base_size_number_to_lots(self, size: float) -> int:
        return int(math.floor(size * 10 ** self._base_spl_token_decimals) / self._decode.base_lot_size)

    @staticmethod
    def get_mint_decimals(endpoint: str, mint_pub_key: PublicKey) -> int:
        """Get the mint decimals from given public key."""
        bytes_data = load_bytes_data(mint_pub_key, endpoint)
        return MINT_LAYOUT.parse(bytes_data).decimals

    def load_bids(self) -> OrderBook:
        """Load the bid order book"""
        bids_addr = PublicKey(self._decode.bids)
        bytes_data = load_bytes_data(bids_addr, self._endpoint)
        return OrderBook.decode(self, bytes_data)

    def load_asks(self) -> OrderBook:
        """Load the Ask order book."""
        asks_addr = PublicKey(self._decode.asks)
        bytes_data = load_bytes_data(asks_addr, self._endpoint)
        return OrderBook.decode(self, bytes_data)

    def load_event_queue(self):  # returns raw construct type
        event_queue_addr = PublicKey(self._decode.event_queue)
        bytes_data = load_bytes_data(event_queue_addr, self._endpoint)
        return decode_event_queue(bytes_data)

    def load_request_queue(self):  # returns raw construct type
        request_queue_addr = PublicKey(self._decode.request_queue)
        bytes_data = load_bytes_data(request_queue_addr, self._endpoint)
        return decode_request_queue(bytes_data)

    def load_fills(self, limit=100) -> List[FilledOrder]:
        event_queue_addr = PublicKey(self._decode.event_queue)
        bytes_data = load_bytes_data(event_queue_addr, self._endpoint)
        events = decode_event_queue(bytes_data, limit)
        return [
            self.parse_fill_event(event)
            for event in events
            if event.event_flags.fill and event.native_quantity_paid > 0
        ]

    def parse_fill_event(self, event) -> FilledOrder:
        if event.event_flags.bid:
            side = Side.Buy
            price_before_fees = (
                event.native_quantity_released + event.native_fee_or_rebate
                if event.event_flags.maker
                else event.native_quantity_released - event.native_fee_or_rebate
            )
        else:
            side = Side.Sell
            price_before_fees = (
                event.native_quantity_released - event.native_fee_or_rebate
                if event.event_flags.maker
                else event.native_quantity_released + event.native_fee_or_rebate
            )

        price = (price_before_fees * self.__base_spl_token_multiplier()) / (
            self.__quote_spl_token_multiplier() * event.native_quantity_paid
        )
        size = event.native_quantity_paid / self.__base_spl_token_multiplier()
        return FilledOrder(
            order_id=int.from_bytes(event.order_id, "little"),
            side=side,
            price=price,
            size=size,
            fee_cost=event.native_fee_or_rebate * (1 if event.event_flags.maker else -1),
        )

    def place_order(self, order_params: NewOrderParams):
        pass

    def make_place_order_transaction(self, order_params: NewOrderParams) -> Tuple[Transaction, List[PublicKey]]:
        pass

    def find_open_orders_accounts_for_owner(self, owner_address: PublicKey):
        pass

    def cancel_order_by_client_id(self, owner: str):
        pass

    def cancel_order(self, owner: Account, order: Order):
        transaction = Transaction()
        transaction.add(self._make_cancel_order_transaction(owner.public_key(), order))
        return self._send_transaction(transaction, [owner])

    def match_orders(self, fee_payer: Account, limit: int):
        transaction = Transaction()
        transaction.add(self._make_match_orders_transaction(limit))
        return self._send_transaction(transaction, [fee_payer])

    def _make_cancel_order_transaction(self, owner: PublicKey, order: Order) -> TransactionInstruction:
        params = CancelOrderParams(
            market=self.address(),
            owner=owner,
            open_orders=order.open_order_address,
            request_queue=self._decode.request_queue,
            side=order.side,
            order_id=order.order_id,
            open_orders_slot=order.open_order_slot,
            program_id=self._program_id,
        )
        return cancel_order_inst(params)

    def _make_match_orders_transaction(self, limit: int) -> TransactionInstruction:
        params = MatchOrdersParams(
            market=self.address(),
            request_queue=PublicKey(self._decode.request_queue),
            event_queue=PublicKey(self._decode.event_queue),
            bids=PublicKey(self._decode.bids),
            asks=PublicKey(self._decode.asks),
            base_vault=PublicKey(self._decode.base_vault),
            quote_vault=PublicKey(self._decode.quote_vault),
            limit=limit,
            program_id=self._program_id,
        )
        return match_order_inst(params)

    def _send_transaction(self, transaction: Transaction, signers: List[Account]) -> str:
        connection = Client(self._endpoint)
        res = connection.send_transaction(transaction, *signers, skip_preflight=self._skip_preflight)
        if self._confirmations > 0:
            print("cannot confirm transaction yet.")
        signature = res.get("result")
        if not signature:
            print("transaction not sent successfully")
        return str(signature)


class FilledOrder(NamedTuple):
    order_id: int
    side: Side
    price: float
    size: float
    fee_cost: int


class OrderInfo(NamedTuple):
    price: float
    size: float
    price_lots: int
    size_lots: int


class Order(NamedTuple):
    order_id: int
    client_id: int
    open_order_address: PublicKey
    open_order_slot: int
    fee_tier: int
    order_info: OrderInfo
    side: Side


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
                side=Side.Buy if self._is_bids else Side.Sell,
                open_order_slot=node.owner_slot,
            )
