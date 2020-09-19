from __future__ import annotations

import math
from typing import Any, NamedTuple

from solana.publickey import PublicKey
from solana.rpc.api import Client

from src._layouts.market import MINT_LAYOUT
from src.utils import load_bytes_data


class AccountFlags(NamedTuple):
    initialized: bool = False
    market: bool = False
    open_orders: bool = False
    request_queue: bool = False
    event_queue: bool = False
    bids: bool = False
    asks: bool = False

    @staticmethod
    # Argument is construct parsed account flags.
    def init(con: Any) -> AccountFlags:
        return AccountFlags(
            initialized=con.initialized,
            market=con.market,
            open_orders=con.open_orders,
            request_queue=con.request_queue,
            event_queue=con.event_queue,
            bids=con.bids,
            asks=con.asks,
        )


class MarketState(NamedTuple):
    account_flags: AccountFlags = AccountFlags()
    own_address: PublicKey = PublicKey(0)
    vault_signer_nonce: int = 0
    base_mint: PublicKey = PublicKey(0)
    quote_mint: PublicKey = PublicKey(0)
    base_vault: PublicKey = PublicKey(0)
    base_deposits_total: int = 0
    base_fees_accrued: int = 0
    quote_vault: PublicKey = PublicKey(0)
    quote_deposits_total: int = 0
    quote_fees_accrued: int = 0
    quote_dust_threshold: int = 0
    request_queue: PublicKey = PublicKey(0)
    event_queue: PublicKey = PublicKey(0)
    bids: PublicKey = PublicKey(0)
    asks: PublicKey = PublicKey(0)
    base_lot_size: int = 1
    quote_lot_size: int = 1
    fee_rate_bps: int = 0
    base_spl_token_decimals: int = 0
    quote_spl_token_decimals: int = 0
    program_id: PublicKey = PublicKey(0)
    skip_preflight: bool = False
    confirmations: int = 0

    def base_spl_token_multiplier(self) -> int:
        return 10 ** self.base_spl_token_decimals

    def quote_spl_token_multiplier(self) -> int:
        return 10 ** self.quote_spl_token_decimals

    def base_spl_size_to_number(self, size: int) -> float:
        return size / self.base_spl_token_multiplier()

    def quote_spl_size_to_number(self, size: int) -> float:
        return size / self.quote_spl_token_multiplier()

    def price_lots_to_number(self, price: int) -> float:
        return float(price * self.quote_lot_size * self.base_spl_token_multiplier()) / (
            self.base_lot_size * self.quote_spl_token_multiplier()
        )

    def price_number_to_lots(self, price: float) -> int:
        return int(
            round(
                (price * 10 ** self.quote_spl_token_multiplier() * self.base_lot_size)
                / (10 ** self.base_spl_token_multiplier() * self.quote_lot_size)
            )
        )

    def base_size_lots_to_number(self, size: int) -> float:
        return float(size * self.base_lot_size) / self.base_spl_token_multiplier()

    def base_size_number_to_lots(self, size: float) -> int:
        return int(math.floor(size * 10 ** self.base_spl_token_decimals) / self.base_lot_size)

    # The first argument is construct parsed account flags.
    @staticmethod
    def load(con: Any, program_id: PublicKey, client: Client) -> MarketState:
        # TODO: add ownAddress check!
        if not con.account_flags.initialized or not con.account_flags.market:
            raise Exception("Invalid market")

        base_mint_decimals = get_mint_decimals(client, PublicKey(con.base_mint))
        quote_mint_decimals = get_mint_decimals(client, PublicKey(con.quote_mint))

        return MarketState(
            account_flags=AccountFlags.init(con.account_flags),
            own_address=PublicKey(con.own_address),
            vault_signer_nonce=con.vault_signer_nonce,
            base_mint=PublicKey(con.base_mint),
            quote_mint=PublicKey(con.quote_mint),
            base_vault=PublicKey(con.base_vault),
            base_deposits_total=con.base_deposits_total,
            base_fees_accrued=con.base_fees_accrued,
            quote_vault=PublicKey(con.quote_vault),
            quote_deposits_total=con.quote_deposits_total,
            quote_fees_accrued=con.quote_fees_accrued,
            quote_dust_threshold=con.quote_dust_threshold,
            request_queue=PublicKey(con.request_queue),
            event_queue=PublicKey(con.event_queue),
            bids=PublicKey(con.bids),
            asks=PublicKey(con.asks),
            base_lot_size=con.base_lot_size,
            quote_lot_size=con.quote_lot_size,
            fee_rate_bps=con.fee_rate_bps,
            base_spl_token_decimals=base_mint_decimals,
            quote_spl_token_decimals=quote_mint_decimals,
            program_id=program_id,
            skip_preflight=False,
            confirmations=10,
        )


def get_mint_decimals(conn: Client, mint_pub_key: PublicKey) -> int:
    """Get the mint decimals from given public key."""
    bytes_data = load_bytes_data(mint_pub_key, conn)
    return MINT_LAYOUT.parse(bytes_data).decimals
