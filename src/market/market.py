"""Market module to interact with Serum DEX."""
from __future__ import annotations

import logging
from typing import Any, Iterable, List, NamedTuple

from construct import Struct as cStruct  # type: ignore
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction, TransactionInstruction

from .._layouts.account_flags import ACCOUNT_FLAGS_LAYOUT
from .._layouts.market import MARKET_LAYOUT
from .._layouts.open_orders import OPEN_ORDERS_LAYOUT
from .._layouts.slab import Slab
from ..enums import OrderType, Side
from ..instructions import DEFAULT_DEX_PROGRAM_ID, CancelOrderParams, MatchOrdersParams, NewOrderParams
from ..instructions import cancel_order as cancel_order_inst
from ..instructions import match_orders as match_order_inst
from ..instructions import new_order as new_order_inst
from ..open_orders_account import OpenOrdersAccount, make_create_account_instruction
from ..queue_ import decode_event_queue, decode_request_queue
from ..utils import load_bytes_data
from .state import MarketState


# pylint: disable=too-many-public-methods
class Market:
    """Represents a Serum Market."""

    logger = logging.getLogger("serum.market")

    _decode: Any
    _baseSplTokenDecimals: int
    _quoteSplTokenDecimals: int
    _skipPreflight: bool
    _confirmations: int
    _porgram_id: PublicKey

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        market_state: MarketState,
        options: Any,  # pylint: disable=unused-argument
        conn: Client,
    ) -> None:
        # TODO: add options
        if not market_state.account_flags.initialized or not market_state.account_flags.market:
            raise Exception("Invalid market state")
        self.state = market_state
        self.conn = conn

    @staticmethod
    def LAYOUT() -> cStruct:  # pylint: disable=invalid-name
        """Construct layout of the market state."""
        return MARKET_LAYOUT

    @staticmethod
    # pylint: disable=unused-argument
    def load(conn: Client, market_address: str, options: Any, program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID) -> Market:
        """Factory method to create a Market."""
        bytes_data = load_bytes_data(PublicKey(market_address), conn)
        parsed_market = MARKET_LAYOUT.parse(bytes_data)
        market_state = MarketState.load(parsed_market, program_id, conn)
        return Market(market_state, options, conn)

    def find_open_orders_accounts_for_owner(self, owner_address: PublicKey) -> List[OpenOrdersAccount]:
        return OpenOrdersAccount.find_for_market_and_owner(
            self.conn, self.state.own_address, owner_address, self.state.program_id
        )

    def find_quote_token_accounts_for_owner(self, owner_address: PublicKey, include_unwrapped_sol: bool = False):
        raise NotImplementedError("find_quote_token_accounts_for_owner not implemented.")

    def load_bids(self) -> OrderBook:
        """Load the bid order book"""
        bytes_data = load_bytes_data(self.state.bids, self.conn)
        return OrderBook.decode(self, bytes_data)

    def load_asks(self) -> OrderBook:
        """Load the Ask order book."""
        bytes_data = load_bytes_data(self.state.asks, self.conn)
        return OrderBook.decode(self, bytes_data)

    def load_orders_for_owner(self) -> List[Order]:
        raise NotImplementedError("load_orders_for_owner not implemented.")

    def load_base_token_for_owner(self):
        raise NotImplementedError("load_base_token_for_owner not implemented.")

    def load_event_queue(self):  # returns raw construct type
        bytes_data = load_bytes_data(self.state.event_queue, self.conn)
        return decode_event_queue(bytes_data)

    def load_request_queue(self):  # returns raw construct type
        bytes_data = load_bytes_data(self.state.request_queue, self.conn)
        return decode_request_queue(bytes_data)

    def load_fills(self, limit=100) -> List[FilledOrder]:
        bytes_data = load_bytes_data(self.state.event_queue, self.conn)
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

        price = (price_before_fees * self.state.base_spl_token_multiplier()) / (
            self.state.quote_spl_token_multiplier() * event.native_quantity_paid
        )
        size = event.native_quantity_paid / self.state.base_spl_token_multiplier()
        return FilledOrder(
            order_id=int.from_bytes(event.order_id, "little"),
            side=side,
            price=price,
            size=size,
            fee_cost=event.native_fee_or_rebate * (1 if event.event_flags.maker else -1),
        )

    def place_order(
        self,
        payer: PublicKey,
        owner: Account,
        order_type: OrderType,
        side: Side,
        limit_price: int,
        max_quantity: int,
        client_id: int = 0,
    ):  # TODO: Add open_orders_address_key param
        transaction = Transaction()
        signers: List[Account] = [owner]
        open_order_accounts = self.find_open_orders_accounts_for_owner(owner.public_key())
        if not open_order_accounts:
            new_open_order_account = Account()
            mbfre_resp = self.conn.get_minimum_balance_for_rent_exemption(OPEN_ORDERS_LAYOUT.sizeof())
            balanced_needed = mbfre_resp["result"]
            transaction.add(
                make_create_account_instruction(
                    owner.public_key(),
                    new_open_order_account.public_key(),
                    balanced_needed,
                    self.state.program_id,
                )
            )
            signers.append(new_open_order_account)

        # TODO: Handle open_orders_address_key
        # TODO: Handle wrapped sol account

        transaction.add(
            self.make_place_order_instruction(
                payer,
                owner,
                order_type,
                side,
                limit_price,
                max_quantity,
                client_id,
                open_order_accounts[0].address if open_order_accounts else new_open_order_account.public_key(),
            )
        )
        return self._send_transaction(transaction, *signers)

    def make_place_order_instruction(
        self,
        payer: PublicKey,
        owner: Account,
        order_type: OrderType,
        side: Side,
        limit_price: int,
        max_quantity: int,
        client_id: int,
        open_order_account: PublicKey,
    ) -> TransactionInstruction:
        if self.state.base_size_number_to_lots(max_quantity) < 0:
            raise Exception("Size lot %d is too small." % max_quantity)
        if self.state.price_number_to_lots(limit_price) < 0:
            raise Exception("Price lot %d is too small." % limit_price)
        return new_order_inst(
            NewOrderParams(
                market=self.state.own_address,
                open_orders=open_order_account,
                payer=payer,
                owner=owner.public_key(),
                request_queue=self.state.request_queue,
                base_vault=self.state.base_vault,
                quote_vault=self.state.quote_vault,
                side=side,
                limit_price=limit_price,
                max_quantity=max_quantity,
                order_type=order_type,
                client_id=client_id,
                program_id=self.state.program_id,
            )
        )

    def cancel_order_by_client_id(self, owner: str) -> str:
        raise NotImplementedError("cancel_order_by_client_id not implemented.")

    def cancel_order(self, owner: Account, order: Order) -> str:
        txn = Transaction().add(self.make_cancel_order_instruction(owner.public_key(), order))
        return self._send_transaction(txn, owner)

    def match_orders(self, fee_payer: Account, limit: int) -> str:
        txn = Transaction().add(self.make_match_orders_instruction(limit))
        return self._send_transaction(txn, fee_payer)

    def make_cancel_order_instruction(self, owner: PublicKey, order: Order) -> TransactionInstruction:
        params = CancelOrderParams(
            market=self.state.own_address,
            owner=owner,
            open_orders=order.open_order_address,
            request_queue=self.state.request_queue,
            side=order.side,
            order_id=order.order_id,
            open_orders_slot=order.open_order_slot,
            program_id=self.state.program_id,
        )
        return cancel_order_inst(params)

    def make_match_orders_instruction(self, limit: int) -> TransactionInstruction:
        params = MatchOrdersParams(
            market=self.state.own_address,
            request_queue=self.state.request_queue,
            event_queue=self.state.event_queue,
            bids=self.state.bids,
            asks=self.state.asks,
            base_vault=self.state.base_vault,
            quote_vault=self.state.quote_vault,
            limit=limit,
            program_id=self.state.program_id,
        )
        return match_order_inst(params)

    def settle_funds(
        self, owner: Account, open_orders: OpenOrdersAccount, base_wallet: PublicKey, quote_wallet: PublicKey
    ) -> str:
        raise NotImplementedError("settle_funds not implemented.")

    def _send_transaction(self, transaction: Transaction, *signers: Account) -> str:
        res = self.conn.send_transaction(transaction, *signers, skip_preflight=self.state.skip_preflight)
        if self.state.confirmations > 0:
            self.logger.warning("Cannot confirm transaction yet.")
        signature = res.get("result")
        if not signature:
            raise Exception("Transaction not sent successfully.")
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
                price=self._market.state.price_lots_to_number(price_lots),
                size=self._market.state.base_size_lots_to_number(size_lots),
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
                    price=self._market.state.price_lots_to_number(price),
                    price_lots=price,
                    size=self._market.state.base_size_lots_to_number(node.quantity),
                    size_lots=node.quantity,
                ),
                side=Side.Buy if self._is_bids else Side.Sell,
                open_order_slot=node.owner_slot,
            )
