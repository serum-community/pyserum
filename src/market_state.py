from typing import NamedTuple

from solana.publickey import PublicKey


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
    base_deposit_total: int
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


def create_market_state(con) -> MarketState:
    return MarketState(
        account_flags=create_account_flags(con.account_flags),
        own_address=PublicKey(con.own_address),
        vault_signer_nonce=con.vault_signer_nonce,
        base_mint=PublicKey(con.base_mint),
        quote_mint=PublicKey(con.quote_mint),
        base_vault=PublicKey(con.base_vault),
        base_deposit_total=con.base_deposit_total,
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
    )
