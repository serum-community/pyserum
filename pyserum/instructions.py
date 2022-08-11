"""Serum Dex Instructions."""
from typing import Dict, List, NamedTuple, Optional

from construct import Container
from solana.publickey import PublicKey
from solana.sysvar import SYSVAR_RENT_PUBKEY
from solana.transaction import AccountMeta, TransactionInstruction
from solana.utils.validate import validate_instruction_keys, validate_instruction_type
from spl.token.constants import TOKEN_PROGRAM_ID

from ._layouts.instructions import INSTRUCTIONS_LAYOUT, InstructionType
from .enums import OrderType, SelfTradeBehavior, Side

# V3
DEFAULT_DEX_PROGRAM_ID = PublicKey("9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin")


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
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""
    authority: Optional[PublicKey] = None
    """"""
    prune_authority: Optional[PublicKey] = None
    """"""
    crank_authority: Optional[PublicKey] = None
    """"""


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
    client_id: int = 0
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""
    fee_discount_pubkey: Optional[PublicKey] = None
    """"""


class MatchOrdersParams(NamedTuple):
    """Match order params."""

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
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class ConsumeEventsParams(NamedTuple):
    """Consume events params."""

    market: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    coin_fee: PublicKey
    """"""
    pc_fee: PublicKey
    """"""
    open_orders_accounts: List[PublicKey]
    """"""
    limit: int
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class ConsumeEventsPermissionedParams(NamedTuple):
    """Consume events params."""

    market: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    crank_authority: PublicKey
    """"""
    open_orders_accounts: List[PublicKey]
    """"""
    limit: int
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
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
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
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
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class SettleFundsParams(NamedTuple):
    """Settle fund params."""

    market: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    owner: PublicKey
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
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""
    referrer_quote_wallet: Optional[PublicKey] = None


class NewOrderV3Params(NamedTuple):
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
    side: Side
    """"""
    limit_price: int
    """"""
    max_base_quantity: int
    """"""
    max_quote_quantity: int
    """"""
    order_type: OrderType
    """"""
    self_trade_behavior: SelfTradeBehavior
    """"""
    program_id: PublicKey
    """"""
    limit: int = 65545
    """"""
    client_id: int = 0
    """"""
    fee_discount_pubkey: Optional[PublicKey] = None
    """"""


class CancelOrderV2Params(NamedTuple):
    """Cancel order params."""

    market: PublicKey
    """"""
    bids: PublicKey
    """"""
    asks: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    side: Side
    """"""
    order_id: int
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class CancelOrderByClientIDV2Params(NamedTuple):
    """Cancel order by client ID params."""

    market: PublicKey
    """"""
    bids: PublicKey
    """"""
    asks: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    client_id: int
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class CloseOpenOrdersParams(NamedTuple):
    """Cancel order by client ID params."""

    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    sol_wallet: PublicKey
    """"""
    market: PublicKey
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class InitOpenOrdersParams(NamedTuple):
    """Cancel order by client ID params."""

    open_orders: PublicKey
    """"""
    owner: PublicKey
    """"""
    market: PublicKey
    """"""
    market_authority: Optional[PublicKey] = None
    """"""
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID
    """"""


class PruneParams(NamedTuple):
    """Prune"""

    market: PublicKey
    """"""
    bids: PublicKey
    """"""
    asks: PublicKey
    """"""
    event_queue: PublicKey
    """"""
    prune_authority: PublicKey
    """"""
    open_orders: PublicKey
    """"""
    open_orders_owner: PublicKey
    """"""
    program_id: PublicKey
    """"""
    limit: int


def __parse_and_validate_instruction(
    instruction: TransactionInstruction, instruction_type: InstructionType
) -> Container:
    instruction_type_to_length_map: Dict[InstructionType, int] = {
        InstructionType.INITIALIZE_MARKET: 9,
        InstructionType.NEW_ORDER: 9,
        InstructionType.MATCH_ORDERS: 7,
        InstructionType.CONSUME_EVENTS: 2,
        InstructionType.CANCEL_ORDER: 4,
        InstructionType.CANCEL_ORDER_BY_CLIENT_ID: 4,
        InstructionType.SETTLE_FUNDS: 9,
        InstructionType.NEW_ORDER_V3: 12,
        InstructionType.CANCEL_ORDER_V2: 6,
        InstructionType.CANCEL_ORDER_BY_CLIENT_ID_V2: 6,
        InstructionType.CLOSE_OPEN_ORDERS: 4,
        InstructionType.INIT_OPEN_ORDERS: 3,
        InstructionType.PRUNE: 7,
    }
    validate_instruction_keys(instruction, instruction_type_to_length_map[instruction_type])
    data = INSTRUCTIONS_LAYOUT.parse(instruction.data)
    validate_instruction_type(data, instruction_type)
    return data


def decode_initialize_market(
    instruction: TransactionInstruction,
) -> InitializeMarketParams:
    """Decode an instialize market instruction and retrieve the instruction params."""
    data = __parse_and_validate_instruction(instruction, InstructionType.INITIALIZE_MARKET)
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
        authority=instruction.keys[10].pubkey if len(instruction.keys) > 10 else None,
        prune_authority=instruction.keys[11].pubkey if len(instruction.keys) > 11 else None,
        crank_authority=instruction.keys[12].pubkey if len(instruction.keys) > 12 else None,
    )


def decode_new_order(instruction: TransactionInstruction) -> NewOrderParams:
    data = __parse_and_validate_instruction(instruction, InstructionType.NEW_ORDER)
    return NewOrderParams(
        market=instruction.keys[0].pubkey,
        open_orders=instruction.keys[1].pubkey,
        request_queue=instruction.keys[2].pubkey,
        payer=instruction.keys[3].pubkey,
        owner=instruction.keys[4].pubkey,
        base_vault=instruction.keys[5].pubkey,
        quote_vault=instruction.keys[6].pubkey,
        side=data.args.side,
        limit_price=data.args.limit_price,
        max_quantity=data.args.max_quantity,
        order_type=data.args.order_type,
        client_id=data.args.client_id,
    )


def decode_match_orders(instruction: TransactionInstruction) -> MatchOrdersParams:
    """Decode a match orders instruction and retrieve the instruction params."""
    data = __parse_and_validate_instruction(instruction, InstructionType.MATCH_ORDERS)
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
    data = __parse_and_validate_instruction(instruction, InstructionType.CONSUME_EVENTS)
    return ConsumeEventsParams(
        open_orders_accounts=[a_m.pubkey for a_m in instruction.keys[:-4]],
        market=instruction.keys[-4].pubkey,
        event_queue=instruction.keys[-3].pubkey,
        coin_fee=instruction.keys[-2].pubkey,
        pc_fee=instruction.keys[-1].pubkey,
        limit=data.args.limit,
        program_id=instruction.program_id,
    )


def decode_cancel_order(instruction: TransactionInstruction) -> CancelOrderParams:
    data = __parse_and_validate_instruction(instruction, InstructionType.CANCEL_ORDER)
    return CancelOrderParams(
        market=instruction.keys[0].pubkey,
        open_orders=instruction.keys[1].pubkey,
        request_queue=instruction.keys[2].pubkey,
        owner=instruction.keys[3].pubkey,
        side=Side(data.args.side),
        order_id=int.from_bytes(data.args.order_id, "little"),
        open_orders_slot=data.args.open_orders_slot,
    )


def decode_settle_funds(instruction: TransactionInstruction) -> SettleFundsParams:
    # data = __parse_and_validate_instruction(instruction, InstructionType.SettleFunds)
    return SettleFundsParams(
        market=instruction.keys[0].pubkey,
        open_orders=instruction.keys[1].pubkey,
        owner=instruction.keys[2].pubkey,
        base_vault=instruction.keys[3].pubkey,
        quote_vault=instruction.keys[4].pubkey,
        base_wallet=instruction.keys[5].pubkey,
        quote_wallet=instruction.keys[6].pubkey,
        vault_signer=instruction.keys[7].pubkey,
    )


def decode_cancel_order_by_client_id(
    instruction: TransactionInstruction,
) -> CancelOrderByClientIDParams:
    data = __parse_and_validate_instruction(instruction, InstructionType.CANCEL_ORDER_BY_CLIENT_ID)
    return CancelOrderByClientIDParams(
        market=instruction.keys[0].pubkey,
        open_orders=instruction.keys[1].pubkey,
        request_queue=instruction.keys[2].pubkey,
        owner=instruction.keys[3].pubkey,
        client_id=data.args.client_id,
    )


def decode_new_order_v3(instruction: TransactionInstruction) -> NewOrderV3Params:
    data = __parse_and_validate_instruction(instruction, InstructionType.NEW_ORDER_V3)
    return NewOrderV3Params(
        market=instruction.keys[0].pubkey,
        open_orders=instruction.keys[1].pubkey,
        request_queue=instruction.keys[2].pubkey,
        event_queue=instruction.keys[3].pubkey,
        bids=instruction.keys[4].pubkey,
        asks=instruction.keys[5].pubkey,
        payer=instruction.keys[6].pubkey,
        owner=instruction.keys[7].pubkey,
        base_vault=instruction.keys[8].pubkey,
        quote_vault=instruction.keys[9].pubkey,
        side=Side(data.args.side),
        limit_price=data.args.limit_price,
        max_base_quantity=data.args.max_base_quantity,
        max_quote_quantity=data.args.max_quote_quantity,
        self_trade_behavior=SelfTradeBehavior(data.args.self_trade_behavior),
        order_type=OrderType(data.args.order_type),
        client_id=data.args.client_id,
        limit=data.args.limit,
        program_id=instruction.program_id,
        fee_discount_pubkey=instruction.keys[12].pubkey if len(instruction.keys) > 12 else None,
    )


def decode_cancel_order_v2(instruction: TransactionInstruction) -> CancelOrderV2Params:
    data = __parse_and_validate_instruction(instruction, InstructionType.CANCEL_ORDER_V2)
    return CancelOrderV2Params(
        market=instruction.keys[0].pubkey,
        bids=instruction.keys[1].pubkey,
        asks=instruction.keys[2].pubkey,
        open_orders=instruction.keys[3].pubkey,
        owner=instruction.keys[4].pubkey,
        event_queue=instruction.keys[5].pubkey,
        side=Side(data.args.side),
        order_id=int.from_bytes(data.args.order_id, "little"),
        program_id=instruction.program_id,
    )


def decode_cancel_order_by_client_id_v2(instruction: TransactionInstruction) -> CancelOrderByClientIDV2Params:
    data = __parse_and_validate_instruction(instruction, InstructionType.CANCEL_ORDER_BY_CLIENT_ID_V2)
    return CancelOrderByClientIDV2Params(
        market=instruction.keys[0].pubkey,
        bids=instruction.keys[1].pubkey,
        asks=instruction.keys[2].pubkey,
        open_orders=instruction.keys[3].pubkey,
        owner=instruction.keys[4].pubkey,
        event_queue=instruction.keys[5].pubkey,
        client_id=data.args.client_id,
        program_id=instruction.program_id,
    )


def decode_close_open_orders(
    instruction: TransactionInstruction,
) -> CloseOpenOrdersParams:
    return CloseOpenOrdersParams(
        open_orders=instruction.keys[0].pubkey,
        owner=instruction.keys[1].pubkey,
        sol_wallet=instruction.keys[2].pubkey,
        market=instruction.keys[3].pubkey,
    )


def decode_init_open_orders(
    instruction: TransactionInstruction,
) -> InitOpenOrdersParams:
    market_authority = instruction.keys[-1].pubkey if len(instruction.keys) == 5 else None
    return InitOpenOrdersParams(
        open_orders=instruction.keys[0].pubkey,
        owner=instruction.keys[1].pubkey,
        market=instruction.keys[2].pubkey,
        market_authority=market_authority,
    )


def decode_prune(
    instruction: TransactionInstruction,
) -> PruneParams:
    data = __parse_and_validate_instruction(instruction, InstructionType.PRUNE)
    return PruneParams(
        market=instruction.keys[0].pubkey,
        bids=instruction.keys[1].pubkey,
        asks=instruction.keys[2].pubkey,
        prune_authority=instruction.keys[3].pubkey,
        open_orders=instruction.keys[4].pubkey,
        open_orders_owner=instruction.keys[5].pubkey,
        event_queue=instruction.keys[6].pubkey,
        program_id=instruction.program_id,
        limit=data.args.limit,
    )


def initialize_market(params: InitializeMarketParams) -> TransactionInstruction:
    """Generate a transaction instruction to initialize a Serum market."""
    touched_keys = [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.base_mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=params.quote_mint, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=params.quote_mint if params.authority else SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False
        ),
    ]
    if params.authority:
        touched_keys.append(AccountMeta(pubkey=params.authority, is_signer=False, is_writable=False))
    if params.authority and params.prune_authority:
        touched_keys.append(AccountMeta(pubkey=params.prune_authority, is_signer=False, is_writable=False))
    if params.authority and params.prune_authority and params.crank_authority:
        touched_keys.append(AccountMeta(pubkey=params.crank_authority, is_signer=False, is_writable=False))
    return TransactionInstruction(
        keys=touched_keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.INITIALIZE_MARKET,
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
    """Generate a transaction instruction to place new order."""
    touched_keys = [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.payer, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    if params.fee_discount_pubkey:
        touched_keys.append(AccountMeta(pubkey=params.fee_discount_pubkey, is_signer=False, is_writable=False))
    args = dict(
        side=params.side,
        limit_price=params.limit_price,
        max_quantity=params.max_quantity,
        order_type=params.order_type,
        client_id=params.client_id,
    )
    return TransactionInstruction(
        keys=touched_keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.NEW_ORDER,
                args=args,
            )
        ),
    )


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
            dict(
                instruction_type=InstructionType.MATCH_ORDERS,
                args=dict(limit=params.limit),
            )
        ),
    )


def consume_events(params: ConsumeEventsParams) -> TransactionInstruction:
    """Generate a transaction instruction to consume market events."""
    keys = [AccountMeta(pubkey=pubkey, is_signer=False, is_writable=True) for pubkey in params.open_orders_accounts] + [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.coin_fee, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.pc_fee, is_signer=False, is_writable=True),
    ]
    return TransactionInstruction(
        keys=keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CONSUME_EVENTS,
                args=dict(limit=params.limit),
            )
        ),
    )


def consume_events_permissioned(params: ConsumeEventsPermissionedParams) -> TransactionInstruction:
    """Generate a transaction instruction to consume market events."""
    keys = [AccountMeta(pubkey=pubkey, is_signer=False, is_writable=True) for pubkey in params.open_orders_accounts] + [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.crank_authority, is_signer=True, is_writable=False),
    ]
    return TransactionInstruction(
        keys=keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CONSUME_EVENTS_PERMISSIONED,
                args=dict(limit=params.limit),
            )
        ),
    )


def cancel_order(params: CancelOrderParams) -> TransactionInstruction:
    """Generate a transaction instruction to cancel order."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CANCEL_ORDER,
                args=dict(
                    side=params.side,
                    order_id=params.order_id.to_bytes(16, byteorder="little"),
                    open_orders=bytes(params.open_orders),
                    open_orders_slot=params.open_orders_slot,
                ),
            )
        ),
    )


def settle_funds(params: SettleFundsParams) -> TransactionInstruction:
    """Generate a transaction instruction to settle fund."""
    touched_keys = [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.base_wallet, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.quote_wallet, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.vault_signer, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if params.referrer_quote_wallet:
        touched_keys.append(AccountMeta(pubkey=params.referrer_quote_wallet, is_signer=False, is_writable=True))
    return TransactionInstruction(
        keys=touched_keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.SETTLE_FUNDS, args=dict())),
    )


def cancel_order_by_client_id(
    params: CancelOrderByClientIDParams,
) -> TransactionInstruction:
    """Generate a transaction instruction to cancel order by client id."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CANCEL_ORDER_BY_CLIENT_ID,
                args=dict(
                    client_id=params.client_id,
                ),
            )
        ),
    )


def new_order_v3(params: NewOrderV3Params) -> TransactionInstruction:
    """Generate a transaction instruction to place new order."""
    touched_keys = [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.payer, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    if params.fee_discount_pubkey:
        touched_keys.append(
            AccountMeta(pubkey=params.fee_discount_pubkey, is_signer=False, is_writable=False),
        )
    return TransactionInstruction(
        keys=touched_keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.NEW_ORDER_V3,
                args=dict(
                    side=params.side,
                    limit_price=params.limit_price,
                    max_base_quantity=params.max_base_quantity,
                    max_quote_quantity=params.max_quote_quantity,
                    self_trade_behavior=params.self_trade_behavior,
                    order_type=params.order_type,
                    client_id=params.client_id,
                    limit=params.limit,
                ),
            )
        ),
    )


def cancel_order_v2(params: CancelOrderV2Params) -> TransactionInstruction:
    """Generate a transaction instruction to cancel order."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
            AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CANCEL_ORDER_V2,
                args=dict(
                    side=params.side,
                    order_id=params.order_id.to_bytes(16, byteorder="little"),
                ),
            )
        ),
    )


def cancel_order_by_client_id_v2(
    params: CancelOrderByClientIDV2Params,
) -> TransactionInstruction:
    """Generate a transaction instruction to cancel order by client id."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
            AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
            AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CANCEL_ORDER_BY_CLIENT_ID_V2,
                args=dict(
                    client_id=params.client_id,
                ),
            )
        ),
    )


def close_open_orders(params: CloseOpenOrdersParams) -> TransactionInstruction:
    """Generate a transaction instruction to close open orders account."""
    return TransactionInstruction(
        keys=[
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
            AccountMeta(pubkey=params.sol_wallet, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.CLOSE_OPEN_ORDERS, args=dict())),
    )


def init_open_orders(params: InitOpenOrdersParams) -> TransactionInstruction:
    """Generate a transaction instruction to initialize open orders account."""
    touched_keys = [
        AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    if params.market_authority:
        touched_keys.append(
            AccountMeta(pubkey=params.market_authority, is_signer=False, is_writable=False),
        )
    return TransactionInstruction(
        keys=touched_keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(dict(instruction_type=InstructionType.INIT_OPEN_ORDERS, args=dict())),
    )


def prune(params: PruneParams) -> TransactionInstruction:
    """Generate a transaction instruction to prune."""
    keys = [
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.bids, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.asks, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.prune_authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.open_orders_owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=params.event_queue, is_signer=False, is_writable=True),
    ]
    return TransactionInstruction(
        keys=keys,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.PRUNE,
                args=dict(limit=params.limit),
            )
        ),
    )
