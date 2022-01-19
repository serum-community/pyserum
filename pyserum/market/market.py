"""Market module to interact with Serum DEX."""
from __future__ import annotations

import base64
import time
from typing import List, Dict, Optional

from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.responses import AccountInfo
from solana.rpc.types import RPCResponse, TxOpts, TokenAccountOpts
from solana.transaction import Transaction
from spl.token._layouts import ACCOUNT_LAYOUT
from spl.token.constants import WRAPPED_SOL_MINT

import pyserum.market.types as t
from pyserum import instructions

from .._layouts.open_orders import OPEN_ORDERS_LAYOUT
from ..enums import OrderType, Side
from ..open_orders_account import OpenOrdersAccount
from ..utils import load_bytes_data
from ._internal.queue import decode_event_queue, decode_request_queue
from .core import MarketCore
from .orderbook import OrderBook
from .state import MarketState

LAMPORTS_PER_SOL = 1000000000


# pylint: disable=too-many-public-methods,abstract-method
class Market(MarketCore):
    """Represents a Serum Market."""

    def __init__(self, conn: Client, market_state: MarketState, force_use_request_queue: bool = False) -> None:
        super().__init__(market_state=market_state, force_use_request_queue=force_use_request_queue)
        self._conn = conn

    @classmethod
    # pylint: disable=unused-argument
    def load(
            cls,
            conn: Client,
            market_address: PublicKey,
            program_id: PublicKey = instructions.DEFAULT_DEX_PROGRAM_ID,
            force_use_request_queue: bool = False,
    ) -> Market:
        """Factory method to create a Market.

        :param conn: The connection that we use to load the data, created from `solana.rpc.api`.
        :param market_address: The market address that you want to connect to.
        :param program_id: The program id of the given market, it will use the default value if not provided.
        :param force_use_request_queue:
        """
        market_state = MarketState.load(conn, market_address, program_id)
        return cls(conn, market_state, force_use_request_queue)

    def find_open_orders_accounts_for_owner(self, owner_address: PublicKey) -> List[OpenOrdersAccount]:
        return OpenOrdersAccount.find_for_market_and_owner(
            self._conn, self.state.public_key(), owner_address, self.state.program_id()
        )

    def load_bids(self) -> OrderBook:
        """Load the bid order book"""
        bytes_data = load_bytes_data(self.state.bids(), self._conn)
        return self._parse_bids_or_asks(bytes_data)

    def load_asks(self) -> OrderBook:
        """Load the ask order book."""
        bytes_data = load_bytes_data(self.state.asks(), self._conn)
        return self._parse_bids_or_asks(bytes_data)

    def load_orders_for_owner(self, owner_address: PublicKey) -> List[t.Order]:
        """Load orders for owner."""
        bids = self.load_bids()
        asks = self.load_asks()
        open_orders_accounts = self.find_open_orders_accounts_for_owner(owner_address)
        return self._parse_orders_for_owner(bids, asks, open_orders_accounts)

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
        return self._parse_fills(bytes_data, limit)

    def place_order(  # pylint: disable=too-many-arguments,too-many-locals
            self,
            payer: PublicKey,
            owner: Keypair,
            order_type: OrderType,
            side: Side,
            limit_price: float,
            max_quantity: float,
            client_id: int = 0,
            opts: TxOpts = TxOpts(),
    ) -> RPCResponse:  # TODO: Add open_orders_address_key param and fee_discount_pubkey
        transaction = Transaction()
        signers: List[Keypair] = [owner]
        open_order_accounts = self.find_open_orders_accounts_for_owner(owner.public_key)
        if open_order_accounts:
            place_order_open_order_account = open_order_accounts[0].address
        else:
            mbfre_resp = self._conn.get_minimum_balance_for_rent_exemption(OPEN_ORDERS_LAYOUT.sizeof())
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
        return self._conn.send_transaction(transaction, *signers, opts=opts)

    def cancel_order_by_client_id(
            self, owner: Keypair, open_orders_account: PublicKey, client_id: int, opts: TxOpts = TxOpts()
    ) -> RPCResponse:
        txs = self._build_cancel_order_by_client_id_tx(
            owner=owner, open_orders_account=open_orders_account, client_id=client_id
        )
        return self._conn.send_transaction(txs, owner, opts=opts)

    def cancel_order(self, owner: Keypair, order: t.Order, opts: TxOpts = TxOpts()) -> RPCResponse:
        txn = self._build_cancel_order_tx(owner=owner, order=order)
        return self._conn.send_transaction(txn, owner, opts=opts)

    def match_orders(self, fee_payer: Keypair, limit: int, opts: TxOpts = TxOpts()) -> RPCResponse:
        txn = self._build_match_orders_tx(limit)
        return self._conn.send_transaction(txn, fee_payer, opts=opts)

    def settle_funds(  # pylint: disable=too-many-arguments
            self,
            owner: Keypair,
            open_orders: OpenOrdersAccount,
            base_wallet: PublicKey,
            quote_wallet: PublicKey,  # TODO: add referrer_quote_wallet.
            opts: TxOpts = TxOpts(),
    ) -> RPCResponse:
        # TODO: Handle wrapped sol accounts
        should_wrap_sol = self._settle_funds_should_wrap_sol()
        min_bal_for_rent_exemption = (
            self._conn.get_minimum_balance_for_rent_exemption(165)["result"] if should_wrap_sol else 0
        )  # value only matters if should_wrap_sol
        signers = [owner]
        transaction = self._build_settle_funds_tx(
            owner=owner,
            signers=signers,
            open_orders=open_orders,
            base_wallet=base_wallet,
            quote_wallet=quote_wallet,
            min_bal_for_rent_exemption=min_bal_for_rent_exemption,
            should_wrap_sol=should_wrap_sol,
        )
        return self._conn.send_transaction(transaction, *signers, opts=opts)

    def support_srm_fee_discounts(self) -> bool:
        return self.state.get_layout_version(self.state.program_id()) > 1

    @staticmethod
    def get_fee_rates(fee_tier: int) -> (int, int):  # taker, maker
        taker, maker = 0.0022, -0.0003
        if fee_tier == 1:  # SRM2
            taker, maker = 0.002, -0.0003
        elif fee_tier == 2:  # SRM3
            taker, maker = 0.0018, -0.0003
        elif fee_tier == 3:  # SRM4
            taker, maker = 0.0016, -0.0003
        elif fee_tier == 4:  # SRM5
            taker, maker = 0.0014, -0.0003
        elif fee_tier == 5:  # SRM6
            taker, maker = 0.0012, -0.0003
        elif fee_tier == 6:  # MSRM
            taker, maker = 0.001, -0.0005
        return taker, maker

    @staticmethod
    def get_fee_tier(msrm_balance: int, srm_balance: int) -> int:
        if msrm_balance >= 1:
            return 6
        elif srm_balance >= 1000000:
            return 5
        elif srm_balance >= 100000:
            return 4
        elif srm_balance >= 10000:
            return 3
        elif srm_balance >= 1000:
            return 2
        elif srm_balance >= 100:
            return 1
        else:
            return 0

    def find_base_token_accounts_for_owner(self, owner_address: PublicKey, include_unwrapped_sol: bool = False) \
            -> List[Dict[str, Optional[PublicKey, AccountInfo]]]:
        if self.state.base_mint() == WRAPPED_SOL_MINT and include_unwrapped_sol:
            wrapped = self.find_base_token_accounts_for_owner(owner_address=owner_address, include_unwrapped_sol=False)
            unwrapped = self._conn.get_account_info(pubkey=owner_address)
            if unwrapped["result"]["value"]:
                return [{"pubkey": owner_address, "account": unwrapped["result"]["value"]}] + wrapped
        else:
            return self.get_token_account_by_owner_for_mint(owner_address, self.state.base_mint())

    def find_quote_token_accounts_for_owner(self, owner_address: PublicKey, include_unwrapped_sol: bool = False) \
            -> List[Dict[str, Optional[PublicKey, AccountInfo]]]:
        if self.state.quote_mint() == WRAPPED_SOL_MINT and include_unwrapped_sol:
            wrapped = self.find_quote_token_accounts_for_owner(owner_address=owner_address, include_unwrapped_sol=False)
            unwrapped = self._conn.get_account_info(pubkey=owner_address)
            if unwrapped["result"]["value"]:
                return [{"pubkey": owner_address, "account": unwrapped["result"]["value"]}] + wrapped
        else:
            return self.get_token_account_by_owner_for_mint(owner_address, self.state.quote_mint())

    def get_token_account_by_owner_for_mint(self, owner_address: PublicKey, mint_address) \
            -> List[Dict[str, Optional[PublicKey, AccountInfo]]]:
        res = self._conn.get_token_accounts_by_owner(owner_address, TokenAccountOpts(mint=mint_address))
        return res["result"]["value"]

    @staticmethod
    def get_spl_token_balance_from_account_info(account_info: AccountInfo, decimals: int) -> float:
        bytes_data = base64.b64decode(account_info.data[0])
        account = ACCOUNT_LAYOUT.parse(bytes_data)
        balance = account.amount
        return balance / 10 ** decimals

    def find_fee_discount_keys(self, owner: PublicKey, cache_duration: int = 0) \
            -> List[Dict[str, Optional[PublicKey, int]]]:
        sorted_accounts = []
        now = int(time.time())
        str_owner = owner.to_base58().decode()
        if str_owner in self._fee_discount_keys_cache and \
            now - self._fee_discount_keys_cache[str_owner]["ts"] < cache_duration:
            return self._fee_discount_keys_cache[str_owner]["account"]
        return sorted_accounts

    def find_best_fee_discount_key(self, owner: PublicKey, cache_duration: int = 30000):
        pass
