from typing import NamedTuple

from solana.publickey import PublicKey
from solana.rpc.api import Client

from ._layouts.market import MINT_LAYOUT
from .utils import load_bytes_data


class AccountFlags(NamedTuple):
    initialized: bool
    market: bool
    open_orders: bool
    request_queue: bool
    event_queue: bool
    bids: bool
    asks: bool


class MarketState(NamedTuple):
    account_flags: AccountFlags
    own_address: PublicKey
    vault_signer_nonce: int
    base_mint: PublicKey
    quote_mint: PublicKey
    base_vault: PublicKey
    base_deposits_total: int
    base_fees_accrued: int
    quote_vault: PublicKey
    quote_deposits_total: int
    quote_fees_accrued: int
    quote_dust_threshold: int
    request_queue: PublicKey
    event_queue: PublicKey
    bids: PublicKey
    asks: PublicKey
    base_lot_size: int
    quote_lot_size: int
    fee_rate_bps: int
    base_spl_token_decimals: int
    quote_spl_token_decimals: int
    program_id: PublicKey
    skip_preflight: bool
    confirmations: int


def get_mint_decimals(conn: Client, mint_pub_key: PublicKey) -> int:
    """Get the mint decimals from given public key."""
    bytes_data = load_bytes_data(mint_pub_key, conn)
    return MINT_LAYOUT.parse(bytes_data).decimals


def create_account_flags(con) -> AccountFlags:
    return AccountFlags(
        initialized=con.initialized,
        market=con.market,
        open_orders=con.open_orders,
        request_queue=con.request_queue,
        event_queue=con.event_queue,
        bids=con.bids,
        asks=con.asks,
    )


def create_market_state(con, program_id: PublicKey) -> MarketState:
    # TODO: add ownAddress check!
    if not con.account_flags.initialized or not con.account_flags.market:
        raise Exception("Invalid market")

    base_mint_decimals = get_mint_decimals(con, PublicKey(con.base_mint))
    quote_mint_decimals = get_mint_decimals(con, PublicKey(con.quote_mint))

    return MarketState(
        account_flags=create_account_flags(con.account_flags),
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

    def __base_spl_token_multiplier(self) -> int:
        return 10 ** self._market_state.base_spl_token_decimals

    def __quote_spl_token_multiplier(self) -> int:
        return 10 ** self._market_state.quote_spl_token_decimals

    def base_spl_size_to_number(self, size: int) -> float:
        return size / self.__base_spl_token_multiplier()

    def quote_spl_size_to_number(self, size: int) -> float:
        return size / self.__quote_spl_token_multiplier()

    def price_lots_to_number(self, price: int) -> float:
        return float(price * self._market_state.quote_lot_size * self.__base_spl_token_multiplier()) / (
            self._market_state.base_lot_size * self.__quote_spl_token_multiplier()
        )

    def price_number_to_lots(self, price: float) -> int:
        return int(
            round(
                (price * 10 ** self.__quote_spl_token_multiplier() * self._market_state.base_lot_size)
                / (10 ** self.__base_spl_token_multiplier() * self._market_state.quote_lot_size)
            )
        )

    def base_size_lots_to_number(self, size: int) -> float:
        return float(size * self._market_state.base_lot_size) / self.__base_spl_token_multiplier()

    def base_size_number_to_lots(self, size: float) -> int:
        return int(
            math.floor(size * 10 ** self._market_state.base_spl_token_decimals) / self._market_state.base_lot_size
        )
