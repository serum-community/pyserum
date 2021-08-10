"""Market module to interact with Serum DEX."""
from __future__ import annotations

import itertools
import logging
from typing import List

from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.types import RPCResponse, TxOpts
from solana.system_program import CreateAccountParams, create_account
from solana.transaction import Transaction, TransactionInstruction
from spl.token.constants import ACCOUNT_LEN, TOKEN_PROGRAM_ID, WRAPPED_SOL_MINT
from spl.token.instructions import CloseAccountParams
from spl.token.instructions import InitializeAccountParams, close_account, initialize_account

from pyserum import instructions
import pyserum.market.types as t

from .._layouts.open_orders import OPEN_ORDERS_LAYOUT
from ..enums import OrderType, SelfTradeBehavior, Side
from ..open_orders_account import OpenOrdersAccount, make_create_account_instruction
from ..utils import load_bytes_data
from ._internal.queue import decode_event_queue, decode_request_queue
from .orderbook import OrderBook
from .state import MarketState

LAMPORTS_PER_SOL = 1000000000


# pylint: disable=too-many-public-methods
class Market:
    """Represents a Serum Market."""

    logger = logging.getLogger("pyserum.market.Market")

    def __init__(self, conn: Client, market_state: MarketState, force_use_request_queue: bool = False) -> None:
        self._conn = conn
        self.state = market_state
        self.force_use_request_queue = force_use_request_queue

    @staticmethod
    # pylint: disable=unused-argument
    def load(
        conn: Client,
        market_address: PublicKey,
        program_id: PublicKey = instructions.DEFAULT_DEX_PROGRAM_ID,
        force_use_request_queue: bool = False,
    ) -> Market:
        """Factory method to create a Market.

        :param conn: The connection that we use to load the data, created from `solana.rpc.api`.
        :param market_address: The market address that you want to connect to.
        :param program_id: The program id of the given market, it will use the default value if not provided.
        """
        market_state = MarketState.load(conn, market_address, program_id)
        return Market(conn, market_state, force_use_request_queue)

    def _use_request_queue(self) -> bool:
        return (
            # DEX Version 1
            self.state.program_id == PublicKey("4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn")
            or
            # DEX Version 1
            self.state.program_id == PublicKey("BJ3jrUzddfuSrZHXSCxMUUQsjKEyLmuuyZebkcaFp2fg")
            or
            # DEX Version 2
            self.state.program_id == PublicKey("EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o")
            or self.force_use_request_queue
        )

    def support_srm_fee_discounts(self) -> bool:
        raise NotImplementedError("support_srm_fee_discounts not implemented")

    def find_fee_discount_keys(self, owner: PublicKey, cache_duration: int):
        raise NotImplementedError("find_fee_discount_keys not implemented")

    def find_best_fee_discount_key(self, owner: PublicKey, cache_duration: int):
        raise NotImplementedError("find_best_fee_discount_key not implemented")

    def find_open_orders_accounts_for_owner(self, owner_address: PublicKey) -> List[OpenOrdersAccount]:
        return OpenOrdersAccount.find_for_market_and_owner(
            self._conn, self.state.public_key(), owner_address, self.state.program_id()
        )

    def find_quote_token_accounts_for_owner(self, owner_address: PublicKey, include_unwrapped_sol: bool = False):
        raise NotImplementedError("find_quote_token_accounts_for_owner not implemented")

    def load_bids(self) -> OrderBook:
        """Load the bid order book"""
        bytes_data = load_bytes_data(self.state.bids(), self._conn)
        return OrderBook.from_bytes(self.state, bytes_data)

    def load_asks(self) -> OrderBook:
        """Load the ask order book."""
        bytes_data = load_bytes_data(self.state.asks(), self._conn)
        return OrderBook.from_bytes(self.state, bytes_data)

    def load_orders_for_owner(self, owner_address: PublicKey) -> List[t.Order]:
        """Load orders for owner."""
        bids = self.load_bids()
        asks = self.load_asks()
        open_orders_accounts = self.find_open_orders_accounts_for_owner(owner_address)
        if not open_orders_accounts:
            return []

        all_orders = itertools.chain(bids.orders(), asks.orders())
        open_orders_addresses = {str(o.address) for o in open_orders_accounts}
        orders = [o for o in all_orders if str(o.open_order_address) in open_orders_addresses]
        return orders

    def load_base_token_for_owner(self):
        raise NotImplementedError("load_base_token_for_owner not implemented")

    def load_event_queue(self) -> List[t.Event]:
        """Load the event queue which includes the fill item and out item. For any trades two fill items are added to
        the event queue. And in case of a trade, cancel or IOC order that missed, out items are added to the event
        queue.
        """
        bytes_data = load_bytes_data(self.state.event_queue(), self._conn)
        return decode_event_queue(bytes_data)

    def load_request_queue(self) -> List[t.Request]:
        bytes_data = load_bytes_data(self.state.request_queue(), self._conn)
        return decode_request_queue(bytes_data)

    def load_fills(self, limit=100) -> List[t.FilledOrder]:
        bytes_data = load_bytes_data(self.state.event_queue(), self._conn)
        events = decode_event_queue(bytes_data, limit)
        return [
            self.parse_fill_event(event)
            for event in events
            if event.event_flags.fill and event.native_quantity_paid > 0
        ]

    def parse_fill_event(self, event) -> t.FilledOrder:
        if event.event_flags.bid:
            side = Side.BUY
            price_before_fees = (
                event.native_quantity_released + event.native_fee_or_rebate
                if event.event_flags.maker
                else event.native_quantity_released - event.native_fee_or_rebate
            )
        else:
            side = Side.SELL
            price_before_fees = (
                event.native_quantity_released - event.native_fee_or_rebate
                if event.event_flags.maker
                else event.native_quantity_released + event.native_fee_or_rebate
            )

        price = (price_before_fees * self.state.base_spl_token_multiplier()) / (
            self.state.quote_spl_token_multiplier() * event.native_quantity_paid
        )
        size = event.native_quantity_paid / self.state.base_spl_token_multiplier()
        return t.FilledOrder(
            order_id=event.order_id,
            side=side,
            price=price,
            size=size,
            fee_cost=event.native_fee_or_rebate * (1 if event.event_flags.maker else -1),
        )

    def place_order(  # pylint: disable=too-many-arguments,too-many-locals
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
        open_order_accounts = self.find_open_orders_accounts_for_owner(owner.public_key())
        if not open_order_accounts:
            new_open_orders_account = Account()
            place_order_open_order_account = new_open_orders_account.public_key()
            mbfre_resp = self._conn.get_minimum_balance_for_rent_exemption(OPEN_ORDERS_LAYOUT.sizeof())
            balanced_needed = mbfre_resp["result"]
            transaction.add(
                make_create_account_instruction(
                    owner_address=owner.public_key(),
                    new_account_address=new_open_orders_account.public_key(),
                    lamports=balanced_needed,
                    program_id=self.state.program_id(),
                )
            )
            signers.append(new_open_orders_account)
            # TODO: Cache new_open_orders_account
        else:
            place_order_open_order_account = open_order_accounts[0].address
        # TODO: Handle fee_discount_pubkey

        # unwrapped SOL cannot be used for payment
        if payer == owner.public_key():
            raise ValueError("Invalid payer account. Cannot use unwrapped SOL.")

        # TODO: add integration test for SOL wrapping.
        should_wrap_sol = (side == Side.BUY and self.state.quote_mint() == WRAPPED_SOL_MINT) or (
            side == Side.SELL and self.state.base_mint() == WRAPPED_SOL_MINT
        )

        if should_wrap_sol:
            wrapped_sol_account = Account()
            payer = wrapped_sol_account.public_key()
            signers.append(wrapped_sol_account)
            transaction.add(
                create_account(
                    CreateAccountParams(
                        from_pubkey=owner.public_key(),
                        new_account_pubkey=wrapped_sol_account.public_key(),
                        lamports=Market._get_lamport_need_for_sol_wrapping(
                            limit_price, max_quantity, side, open_order_accounts
                        ),
                        space=ACCOUNT_LEN,
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )
            )
            transaction.add(
                initialize_account(
                    InitializeAccountParams(
                        account=wrapped_sol_account.public_key(),
                        mint=WRAPPED_SOL_MINT,
                        owner=owner.public_key(),
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )
            )

        transaction.add(
            self.make_place_order_instruction(
                payer=payer,
                owner=owner,
                order_type=order_type,
                side=side,
                limit_price=limit_price,
                max_quantity=max_quantity,
                client_id=client_id,
                open_order_account=place_order_open_order_account,
            )
        )

        if should_wrap_sol:
            transaction.add(
                close_account(
                    CloseAccountParams(
                        account=wrapped_sol_account.public_key(),
                        owner=owner.public_key(),
                        dest=owner.public_key(),
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )
            )
        # TODO: extract `make_place_order_transaction`.
        return self._conn.send_transaction(transaction, *signers, opts=opts)

    @staticmethod
    def _get_lamport_need_for_sol_wrapping(
        price: float, size: float, side: Side, open_orders_accounts: List[OpenOrdersAccount]
    ) -> int:
        lamports = 0
        if side == Side.BUY:
            lamports = round(price * size * 1.01 * LAMPORTS_PER_SOL)
            if open_orders_accounts:
                lamports -= open_orders_accounts[0].quote_token_free
        else:
            lamports = round(size * LAMPORTS_PER_SOL)
            if open_orders_accounts:
                lamports -= open_orders_accounts[0].base_token_free

        return max(lamports, 0) + 10000000

    def make_place_order_instruction(  # pylint: disable=too-many-arguments
        self,
        payer: PublicKey,
        owner: Account,
        order_type: OrderType,
        side: Side,
        limit_price: float,
        max_quantity: float,
        client_id: int,
        open_order_account: PublicKey,
        fee_discount_pubkey: PublicKey = None,
    ) -> TransactionInstruction:
        if self.state.base_size_number_to_lots(max_quantity) < 0:
            raise Exception("Size lot %d is too small" % max_quantity)
        if self.state.price_number_to_lots(limit_price) < 0:
            raise Exception("Price lot %d is too small" % limit_price)
        if self._use_request_queue():
            return instructions.new_order(
                instructions.NewOrderParams(
                    market=self.state.public_key(),
                    open_orders=open_order_account,
                    payer=payer,
                    owner=owner.public_key(),
                    request_queue=self.state.request_queue(),
                    base_vault=self.state.base_vault(),
                    quote_vault=self.state.quote_vault(),
                    side=side,
                    limit_price=self.state.price_number_to_lots(limit_price),
                    max_quantity=self.state.base_size_number_to_lots(max_quantity),
                    order_type=order_type,
                    client_id=client_id,
                    program_id=self.state.program_id(),
                )
            )
        return instructions.new_order_v3(
            instructions.NewOrderV3Params(
                market=self.state.public_key(),
                open_orders=open_order_account,
                payer=payer,
                owner=owner.public_key(),
                request_queue=self.state.request_queue(),
                event_queue=self.state.event_queue(),
                bids=self.state.bids(),
                asks=self.state.asks(),
                base_vault=self.state.base_vault(),
                quote_vault=self.state.quote_vault(),
                side=side,
                limit_price=self.state.price_number_to_lots(limit_price),
                max_base_quantity=self.state.base_size_number_to_lots(max_quantity),
                max_quote_quantity=self.state.base_size_number_to_lots(max_quantity)
                * self.state.quote_lot_size()
                * self.state.price_number_to_lots(limit_price),
                order_type=order_type,
                client_id=client_id,
                program_id=self.state.program_id(),
                self_trade_behavior=SelfTradeBehavior.DECREMENT_TAKE,
                fee_discount_pubkey=fee_discount_pubkey,
                limit=65535,
            )
        )

    def cancel_order_by_client_id(
        self, owner: Account, open_orders_account: PublicKey, client_id: int, opts: TxOpts = TxOpts()
    ) -> RPCResponse:
        txs = Transaction().add(self.make_cancel_order_by_client_id_instruction(owner, open_orders_account, client_id))
        return self._conn.send_transaction(txs, owner, opts=opts)

    def make_cancel_order_by_client_id_instruction(
        self, owner: Account, open_orders_account: PublicKey, client_id: int
    ) -> TransactionInstruction:
        if self._use_request_queue():
            return instructions.cancel_order_by_client_id(
                instructions.CancelOrderByClientIDParams(
                    market=self.state.public_key(),
                    owner=owner.public_key(),
                    open_orders=open_orders_account,
                    request_queue=self.state.request_queue(),
                    client_id=client_id,
                    program_id=self.state.program_id(),
                )
            )
        return instructions.cancel_order_by_client_id_v2(
            instructions.CancelOrderByClientIDV2Params(
                market=self.state.public_key(),
                owner=owner.public_key(),
                open_orders=open_orders_account,
                bids=self.state.bids(),
                asks=self.state.asks(),
                event_queue=self.state.event_queue(),
                client_id=client_id,
                program_id=self.state.program_id(),
            )
        )

    def cancel_order(self, owner: Account, order: t.Order, opts: TxOpts = TxOpts()) -> RPCResponse:
        txn = Transaction().add(self.make_cancel_order_instruction(owner.public_key(), order))
        return self._conn.send_transaction(txn, owner, opts=opts)

    def make_cancel_order_instruction(self, owner: PublicKey, order: t.Order) -> TransactionInstruction:
        if self._use_request_queue():
            return instructions.cancel_order(
                instructions.CancelOrderParams(
                    market=self.state.public_key(),
                    owner=owner,
                    open_orders=order.open_order_address,
                    request_queue=self.state.request_queue(),
                    side=order.side,
                    order_id=order.order_id,
                    open_orders_slot=order.open_order_slot,
                    program_id=self.state.program_id(),
                )
            )
        return instructions.cancel_order_v2(
            instructions.CancelOrderV2Params(
                market=self.state.public_key(),
                owner=owner,
                open_orders=order.open_order_address,
                bids=self.state.bids(),
                asks=self.state.asks(),
                event_queue=self.state.event_queue(),
                side=order.side,
                order_id=order.order_id,
                open_orders_slot=order.open_order_slot,
                program_id=self.state.program_id(),
            )
        )

    def match_orders(self, fee_payer: Account, limit: int, opts: TxOpts = TxOpts()) -> RPCResponse:
        txn = Transaction().add(self.make_match_orders_instruction(limit))
        return self._conn.send_transaction(txn, fee_payer, opts=opts)

    def make_match_orders_instruction(self, limit: int) -> TransactionInstruction:
        params = instructions.MatchOrdersParams(
            market=self.state.public_key(),
            request_queue=self.state.request_queue(),
            event_queue=self.state.event_queue(),
            bids=self.state.bids(),
            asks=self.state.asks(),
            base_vault=self.state.base_vault(),
            quote_vault=self.state.quote_vault(),
            limit=limit,
            program_id=self.state.program_id(),
        )
        return instructions.match_orders(params)

    def settle_funds(  # pylint: disable=too-many-arguments
        self,
        owner: Account,
        open_orders: OpenOrdersAccount,
        base_wallet: PublicKey,
        quote_wallet: PublicKey,  # TODO: add referrer_quote_wallet.
        opts: TxOpts = TxOpts(),
    ) -> RPCResponse:
        # TODO: Handle wrapped sol accounts
        if open_orders.owner != owner.public_key():
            raise Exception("Invalid open orders account")
        vault_signer = PublicKey.create_program_address(
            [bytes(self.state.public_key()), self.state.vault_signer_nonce().to_bytes(8, byteorder="little")],
            self.state.program_id(),
        )
        transaction = Transaction()
        signers: List[Account] = [owner]

        should_wrap_sol = (self.state.quote_mint() == WRAPPED_SOL_MINT) or (self.state.base_mint() == WRAPPED_SOL_MINT)

        if should_wrap_sol:
            wrapped_sol_account = Account()
            signers.append(wrapped_sol_account)
            # make a wrapped SOL account with enough balance to
            # fund the trade, run the program, then send itself back home
            transaction.add(
                create_account(
                    CreateAccountParams(
                        from_pubkey=owner.public_key(),
                        new_account_pubkey=wrapped_sol_account.public_key(),
                        lamports=self._conn.get_minimum_balance_for_rent_exemption(165)["result"],
                        space=ACCOUNT_LEN,
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )
            )
            # this was also broken upstream. it should be minting wrapped SOL, and using the token program ID
            transaction.add(
                initialize_account(
                    InitializeAccountParams(
                        account=wrapped_sol_account.public_key(),
                        mint=WRAPPED_SOL_MINT,
                        owner=owner.public_key(),
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )
            )

        transaction.add(
            self.make_settle_funds_instruction(
                open_orders,
                base_wallet if self.state.base_mint() != WRAPPED_SOL_MINT else wrapped_sol_account.public_key(),
                quote_wallet if self.state.quote_mint() != WRAPPED_SOL_MINT else wrapped_sol_account.public_key(),
                vault_signer,
            )
        )

        if should_wrap_sol:
            # close out the account and send the funds home when the trade is completed/cancelled
            transaction.add(
                close_account(
                    CloseAccountParams(
                        account=wrapped_sol_account.public_key(),
                        owner=owner.public_key(),
                        dest=owner.public_key(),
                        program_id=TOKEN_PROGRAM_ID,
                    )
                )
            )
        return self._conn.send_transaction(transaction, owner, opts=opts)

    def make_settle_funds_instruction(
        self,
        open_orders_account: OpenOrdersAccount,
        base_wallet: PublicKey,
        quote_wallet: PublicKey,
        vault_signer: PublicKey,
    ) -> TransactionInstruction:
        if base_wallet == self.state.base_vault():
            raise ValueError("base_wallet should not be a vault address")
        if quote_wallet == self.state.quote_vault():
            raise ValueError("quote_wallet should not be a vault address")

        return instructions.settle_funds(
            instructions.SettleFundsParams(
                market=self.state.public_key(),
                open_orders=open_orders_account.address,
                owner=open_orders_account.owner,
                base_vault=self.state.base_vault(),
                quote_vault=self.state.quote_vault(),
                base_wallet=base_wallet,
                quote_wallet=quote_wallet,
                vault_signer=vault_signer,
                program_id=self.state.program_id(),
            )
        )
