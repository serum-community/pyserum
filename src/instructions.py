"""Serum Dex Instructions."""
from typing import List, NamedTuple

from solana.publickey import PublicKey
from solana.transaction import AccountMeta, TransactionInstruction, verify_instruction_keys

from .enums import OrderType, Side
from .layouts.instructions import INSTRUCTIONS_LAYOUT, InstructionType

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
    side: Side
    """"""
    limit_price: int
    """"""
    max_quantity: int
    """"""
    order_type: OrderType
    """"""
    client_id: int
    """"""
    program_id: PublicKey = DEX_PROGRAM_ID
    """"""


class MatchOrdersParams(NamedTuple):
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
    side: Side
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
    """Decode an instialize market instruction and retrieve the instruction params."""
    verify_instruction_keys(instruction, 9)
    data = INSTRUCTIONS_LAYOUT.parse(instruction.data)
    return InitializeMarketParams(
        market=instruction.keys[0].pubkey,
        request_queue=instruction.keys[1].pubkey,
        event_queue=instruction.keys[2].pubkey,
        bids=instruction.keys[3].pubkey,
        asks=instruction.keys[4].pubkey,
        base_vault=instruction.keys[5].pubkey,
        quote_vault=instruction.keys[6].pubkey,
        base_mint=instruction.keys[7].pubkey,
        quote_mint=instruction.keys[8].pubkey,
        base_lot_size=data.args.base_lot_size,
        quote_lot_size=data.args.quote_lot_size,
        fee_rate_bps=data.args.fee_rate_bps,
        vault_signer_nonce=data.args.vault_signer_nonce,
        quote_dust_threshold=data.args.quote_dust_threshold,
        program_id=instruction.program_id,
    )


def decode_new_order(instruction: TransactionInstruction) -> NewOrderParams:
    raise NotImplementedError("decode_new_order not implemented")


def decode_match_orders(instruction: TransactionInstruction) -> MatchOrdersParams:
    """Decode a match orders instruction and retrieve the instruction params."""
    verify_instruction_keys(instruction, 7)
    data = INSTRUCTIONS_LAYOUT.parse(instruction.data)
    return MatchOrdersParams(
        market=instruction.keys[0].pubkey,
        request_queue=instruction.keys[1].pubkey,
        event_queue=instruction.keys[2].pubkey,
        bids=instruction.keys[3].pubkey,
        asks=instruction.keys[4].pubkey,
        base_vault=instruction.keys[5].pubkey,
        quote_vault=instruction.keys[6].pubkey,
        limit=data.args.limit,
    )


def decode_consume_events(instruction: TransactionInstruction) -> ConsumeEventsParams:
    """Decode a consume events instruction and retrieve the instruction params."""
    verify_instruction_keys(instruction, 2)
    data = INSTRUCTIONS_LAYOUT.parse(instruction.data)
    return ConsumeEventsParams(
        open_orders_accounts=[a_m.pubkey for a_m in instruction.keys[:-2]],
        market=instruction.keys[-2].pubkey,
        event_queue=instruction.keys[-1].pubkey,
        limit=data.args.limit,
    )


def decode_cancel_order(instruction: TransactionInstruction) -> CancelOrderParams:
    raise NotImplementedError("decode_cancel_order not implemented")


def decode_settle_funds(instruction: TransactionInstruction) -> SettleFundsParams:
    raise NotImplementedError("decode_settle_funds not implemented")


def decode_cancel_order_by_client_id(instruction: TransactionInstruction) -> CancelOrderByClientIDParams:
    raise NotImplementedError("decode_cancel_order_by_client_id not implemented")


def initialize_market(params: InitializeMarketParams) -> TransactionInstruction:
    """Generate a transaction instruction to initialize a Serum market."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.base_mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.quote_mint, is_signer=False, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.InitializeMarket,
                args=dict(
                    base_lot_size=params.base_lot_size,
                    quote_lot_size=params.quote_lot_size,
                    fee_rate_bps=params.fee_rate_bps,
                    vault_signer_nonce=params.vault_signer_nonce,
                    quote_dust_threshold=params.quote_dust_threshold,
                ),
            ),
        ),
    )


def new_order(params: NewOrderParams) -> TransactionInstruction:
    raise NotImplementedError("new_order not implemented")


def match_orders(params: MatchOrdersParams) -> TransactionInstruction:
    """Generate a transaction instruction to match order."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(instruction_type=InstructionType.MatchOrder, args=dict(limit=params.limit))
        ),
    )


def consume_events(params: ConsumeEventsParams) -> TransactionInstruction:
    """Generate a transaction instruction to consume market events."""
    keys = [
        AccountMeta(pubkey=pubkey, is_signer=False, is_writable=True)
        for pubkey in params.open_orders_accounts + [params.market, params.event_queue]
    ]
    return TransactionInstruction(
        keys=keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(instruction_type=InstructionType.ConsumeEvents, args=dict(limit=params.limit))
        ),
    )


def cancel_order(params: CancelOrderParams) -> TransactionInstruction:
    raise NotImplementedError("cancel_order not implemented")


def settle_funds(params: SettleFundsParams) -> TransactionInstruction:
    raise NotImplementedError("settle_funds not implemented")


def cancel_order_by_client_id(params: CancelOrderByClientIDParams) -> TransactionInstruction:
    raise NotImplementedError("cancel_order_by_client_id not implemented")
