"""Market module to interact with Serum DEX."""
from __future__ import annotations

from typing import List

from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import RPCResponse, TxOpts
from solana.transaction import Transaction

from pyserum import instructions
import pyserum.market.types as t

from .._layouts.open_orders import OPEN_ORDERS_LAYOUT
from ..enums import OrderType, Side
from ..async_open_orders_account import AsyncOpenOrdersAccount
from ..async_utils import load_bytes_data
from ._internal.queue import decode_event_queue, decode_request_queue
from .orderbook import OrderBook
from .state import MarketState
from .core import MarketCore

LAMPORTS_PER_SOL = 1000000000


# pylint: disable=too-many-public-methods,abstract-method
class AsyncMarket(MarketCore):
    """Represents a Serum Market."""

    def __init__(self, conn: AsyncClient, market_state: MarketState, force_use_request_queue: bool = False) -> None:
        super().__init__(market_state=market_state, force_use_request_queue=force_use_request_queue)
        self._conn = conn

    @classmethod
    # pylint: disable=unused-argument
    async def load(
        cls,
        conn: AsyncClient,
        market_address: PublicKey,
        program_id: PublicKey = instructions.DEFAULT_DEX_PROGRAM_ID,
        force_use_request_queue: bool = False,
    ) -> AsyncMarket:
        """Factory method to create a Market.

        :param conn: The connection that we use to load the data, created from `solana.rpc.api`.
        :param market_address: The market address that you want to connect to.
        :param program_id: The program id of the given market, it will use the default value if not provided.
        """
        market_state = await MarketState.async_load(conn, market_address, program_id)
        return cls(conn, market_state, force_use_request_queue)

    async def find_open_orders_accounts_for_owner(self, owner_address: PublicKey) -> List[AsyncOpenOrdersAccount]:
        return await AsyncOpenOrdersAccount.find_for_market_and_owner(
            self._conn, self.state.public_key(), owner_address, self.state.program_id()
        )

    async def load_bids(self) -> OrderBook:
        """Load the bid order book"""
        bytes_data = await load_bytes_data(self.state.bids(), self._conn)
        return self._parse_bids_or_asks(bytes_data)

    async def load_asks(self) -> OrderBook:
        """Load the ask order book."""
        bytes_data = await load_bytes_data(self.state.asks(), self._conn)
        return self._parse_bids_or_asks(bytes_data)

    async def load_orders_for_owner(self, owner_address: PublicKey) -> List[t.Order]:
        """Load orders for owner."""
        bids = await self.load_bids()
        asks = await self.load_asks()
        open_orders_accounts = await self.find_open_orders_accounts_for_owner(owner_address)
        return self._parse_orders_for_owner(bids, asks, open_orders_accounts)

    async def load_event_queue(self) -> List[t.Event]:
        """Load the event queue which includes the fill item and out item. For any trades two fill items are added to
        the event queue. And in case of a trade, cancel or IOC order that missed, out items are added to the event
        queue.
        """
        bytes_data = await load_bytes_data(self.state.event_queue(), self._conn)
        return decode_event_queue(bytes_data)

    async def load_request_queue(self) -> List[t.Request]:
        bytes_data = await load_bytes_data(self.state.request_queue(), self._conn)
        return decode_request_queue(bytes_data)

    async def load_fills(self, limit=100) -> List[t.FilledOrder]:
        bytes_data = await load_bytes_data(self.state.event_queue(), self._conn)
        return self._parse_fills(bytes_data, limit)

    async def place_order(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        payer: PublicKey,
        owner: Account,
        order_type: OrderType,
        side: Side,
        limit_price: float,
        max_quantity: float,
        client_id: int = 0,
        opts: TxOpts = TxOpts(),
    ) -> RPCResponse:  # TODO: Add open_orders_address_key param and fee_discount_pubkey
        transaction = Transaction()
        signers: List[Account] = [owner]
        open_order_accounts = await self.find_open_orders_accounts_for_owner(owner.public_key())
        if open_order_accounts:
            place_order_open_order_account = open_order_accounts[0].address
        else:
            mbfre_resp = await self._conn.get_minimum_balance_for_rent_exemption(OPEN_ORDERS_LAYOUT.sizeof())
            place_order_open_order_account = self._after_oo_mbfre_resp(
                mbfre_resp=mbfre_resp, owner=owner, signers=signers, transaction=transaction
            )
            # TODO: Cache new_open_orders_account
        # TODO: Handle fee_discount_pubkey

        self._prepare_order_transaction(
            transaction=transaction,
            payer=payer,
            owner=owner,
            order_type=order_type,
            side=side,
            signers=signers,
            limit_price=limit_price,
            max_quantity=max_quantity,
            client_id=client_id,
            open_order_accounts=open_order_accounts,
            place_order_open_order_account=place_order_open_order_account,
        )
        return await self._conn.send_transaction(transaction, *signers, opts=opts)

    async def cancel_order_by_client_id(
        self, owner: Account, open_orders_account: PublicKey, client_id: int, opts: TxOpts = TxOpts()
    ) -> RPCResponse:
        txs = self._build_cancel_order_by_client_id_tx(
            owner=owner, open_orders_account=open_orders_account, client_id=client_id
        )
        return await self._conn.send_transaction(txs, owner, opts=opts)

    async def cancel_order(self, owner: Account, order: t.Order, opts: TxOpts = TxOpts()) -> RPCResponse:
        txn = self._build_cancel_order_tx(owner=owner, order=order)
        return await self._conn.send_transaction(txn, owner, opts=opts)

    async def match_orders(self, fee_payer: Account, limit: int, opts: TxOpts = TxOpts()) -> RPCResponse:
        txn = self._build_match_orders_tx(limit)
        return await self._conn.send_transaction(txn, fee_payer, opts=opts)

    async def settle_funds(  # pylint: disable=too-many-arguments
        self,
        owner: Account,
        open_orders: AsyncOpenOrdersAccount,
        base_wallet: PublicKey,
        quote_wallet: PublicKey,  # TODO: add referrer_quote_wallet.
        opts: TxOpts = TxOpts(),
    ) -> RPCResponse:
        # TODO: Handle wrapped sol accounts
        should_wrap_sol = self._settle_funds_should_wrap_sol()
        if should_wrap_sol:
            mbfre_resp = await self._conn.get_minimum_balance_for_rent_exemption(165)
            min_bal_for_rent_exemption = mbfre_resp["result"]
        else:
            min_bal_for_rent_exemption = 0  # value only matters if should_wrap_sol
        transaction = self._build_settle_funds_tx(
            owner=owner,
            open_orders=open_orders,
            base_wallet=base_wallet,
            quote_wallet=quote_wallet,
            min_bal_for_rent_exemption=min_bal_for_rent_exemption,
            should_wrap_sol=should_wrap_sol,
        )
        return await self._conn.send_transaction(transaction, owner, opts=opts)
