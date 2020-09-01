"""Serum Dex Instructions."""
from enum import Enum
from typing import List, NamedTuple

from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction

# Instruction Indices
_INITIALIZE_MARKET = 0
_NEW_ORDER = 1
_MATCH_ORDER = 2
_CONSUME_EVENTS = 3
_CANCEL_ORDER = 4
_SETTLE_FUND = 5
_CANCEL_ORDER_BY_CLIENT_ID = 6

DEX_PROGRAM_ID = PublicKey("4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn")


class InitializeMarketParams(NamedTuple):
    """Initalize market params."""

    market: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    bids: PublicKey
    """"""
    asks: PublicKey
    """"""
    base_vault: PublicKey
    """"""
    quote_vault: PublicKey
    """"""
    base_mint: PublicKey
    """"""
    quote_mint: PublicKey
    """"""
    base_lot_size: int
    """"""
    quote_lot_size: int
    """"""
    fee_rate_bps: int
    """"""
    vault_signer_nonce: int
    """"""
    quote_dust_threshold: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID


class NewOrderParams(NamedTuple):
    """New order params."""

    market: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    payer: PublicKey
    """"""
    owner: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    base_vault: PublicKey
    """"""
    quote_vault: PublicKey
    """"""
    side: Enum
    """"""
    limit_price: int
    """"""
    max_quantity: int
    """"""
    order_type: Enum
    """"""
    client_id: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID
    """"""


class MatchOrderParams(NamedTuple):
    """"Match order params."""

    market: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    bids: PublicKey
    """"""
    asks: PublicKey
    """"""
    base_vault: PublicKey
    """"""
    quote_vault: PublicKey
    """"""
    limit: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID
    """"""


class ConsumeEventsParams(NamedTuple):
    """Consume events params."""

    market: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    open_orders_accounts: List[PublicKey]
    """"""
    limit: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID
    """"""


class CancelOrderParams(NamedTuple):
    """Cancel order params."""

    market: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    side: Enum
    """"""
    order_id: int
    """"""
    open_orders_slot: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID
    """"""


class CancelOrderByClientIDParams(NamedTuple):
    """Cancel order by client ID params."""

    market: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    client_id: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID
    """"""


class SettleFundsParams(NamedTuple):
    """Settle fund params."""

    market: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    request_queue: PublicKey
    """"""
    base_vault: PublicKey
    """"""
    quote_vault: PublicKey
    """"""
    base_wallet: PublicKey
    """"""
    quote_wallet: PublicKey
    """"""
    vault_signer: PublicKey
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID


def decode_initialize_market(instruction: TransactionInstruction) -> InitializeMarketParams:
    raise NotImplementedError("decode_initialize_market not implemented.")


def decode_new_order(instruction: TransactionInstruction) -> NewOrderParams:
    raise NotImplementedError("decode_new_order not implemented")


def decode_match_order(instruction: TransactionInstruction) -> MatchOrderParams:
    raise NotImplementedError("decode_match_order not implemented")


def decode_consume_events(instruction: TransactionInstruction) -> ConsumeEventsParams:
    raise NotImplementedError("decode_consume_events not implemented")


def decode_cancel_order(instruction: TransactionInstruction) -> CancelOrderParams:
    raise NotImplementedError("decode_cancel_order not implemented")


def decode_settle_funds(instruction: TransactionInstruction) -> SettleFundsParams:
    raise NotImplementedError("decode_settle_funds not implemented")


def decode_cancel_order_by_client_id(instruction: TransactionInstruction) -> CancelOrderByClientIDParams:
    raise NotImplementedError("decode_cancel_order_by_client_id not implemented")


def initialize_market(params: InitializeMarketParams) -> TransactionInstruction:
    raise NotImplementedError("initialize_market not implemented")


def new_order(params: NewOrderParams) -> TransactionInstruction:
    raise NotImplementedError("new_order not implemented")


def match_order(params: MatchOrderParams) -> TransactionInstruction:
    raise NotImplementedError("match_order not implemented")


def consume_events(params: ConsumeEventsParams) -> TransactionInstruction:
    raise NotImplementedError("consume_events not implemented")


def cancel_order(params: CancelOrderParams) -> TransactionInstruction:
    raise NotImplementedError("cancel_order not implemented")


def settle_funds(params: SettleFundsParams) -> TransactionInstruction:
    raise NotImplementedError("settle_funds not implemented")


def cancel_order_by_client_id(params: CancelOrderByClientIDParams) -> TransactionInstruction:
    raise NotImplementedError("cancel_order_by_client_id not implemented")
