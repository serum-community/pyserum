"""Serum Dex Instructions."""
from typing import Dict, List, NamedTuple, Optional

from construct import Container
from solders.sysvar import RENT
from solana.transaction import AccountMeta
from solders.instruction import Instruction
from solana.utils.validate import validate_instruction_keys, validate_instruction_type
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID

from ._layouts.instructions import INSTRUCTIONS_LAYOUT, InstructionType
from .enums import OrderType, SelfTradeBehavior, Side

# V3
DEFAULT_DEX_PROGRAM_ID = Pubkey.from_string(
    "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"
)


class InitializeMarketParams(NamedTuple):
    """Initalize market params."""

    market: Pubkey
    """"""
    request_queue: Pubkey
    """"""
    event_queue: Pubkey
    """"""
    bids: Pubkey
    """"""
    asks: Pubkey
    """"""
    base_vault: Pubkey
    """"""
    quote_vault: Pubkey
    """"""
    base_mint: Pubkey
    """"""
    quote_mint: Pubkey
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
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID


class NewOrderParams(NamedTuple):
    """New order params."""

    market: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    payer: Pubkey
    """"""
    owner: Pubkey
    """"""
    request_queue: Pubkey
    """"""
    base_vault: Pubkey
    """"""
    quote_vault: Pubkey
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
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class MatchOrdersParams(NamedTuple):
    """Match order params."""

    market: Pubkey
    """"""
    request_queue: Pubkey
    """"""
    event_queue: Pubkey
    """"""
    bids: Pubkey
    """"""
    asks: Pubkey
    """"""
    base_vault: Pubkey
    """"""
    quote_vault: Pubkey
    """"""
    limit: int
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class ConsumeEventsParams(NamedTuple):
    """Consume events params."""

    market: Pubkey
    """"""
    event_queue: Pubkey
    """"""
    open_orders_accounts: List[Pubkey]
    """"""
    limit: int
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class CancelOrderParams(NamedTuple):
    """Cancel order params."""

    market: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    request_queue: Pubkey
    """"""
    side: Side
    """"""
    order_id: int
    """"""
    open_orders_slot: int
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class CancelOrderByClientIDParams(NamedTuple):
    """Cancel order by client ID params."""

    market: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    request_queue: Pubkey
    """"""
    client_id: int
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class SettleFundsParams(NamedTuple):
    """Settle fund params."""

    market: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    base_vault: Pubkey
    """"""
    quote_vault: Pubkey
    """"""
    base_wallet: Pubkey
    """"""
    quote_wallet: Pubkey
    """"""
    vault_signer: Pubkey
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID


class NewOrderV3Params(NamedTuple):
    """New order params."""

    market: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    payer: Pubkey
    """"""
    owner: Pubkey
    """"""
    request_queue: Pubkey
    """"""
    event_queue: Pubkey
    """"""
    bids: Pubkey
    """"""
    asks: Pubkey
    """"""
    base_vault: Pubkey
    """"""
    quote_vault: Pubkey
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
    limit: Optional[int]
    """"""
    client_id: int = 0
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""
    fee_discount_pubkey: Optional[Pubkey] = None


class CancelOrderV2Params(NamedTuple):
    """Cancel order params."""

    market: Pubkey
    """"""
    bids: Pubkey
    """"""
    asks: Pubkey
    """"""
    event_queue: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    side: Side
    """"""
    order_id: int
    """"""
    open_orders_slot: int
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class CancelOrderByClientIDV2Params(NamedTuple):
    """Cancel order by client ID params."""

    market: Pubkey
    """"""
    bids: Pubkey
    """"""
    asks: Pubkey
    """"""
    event_queue: Pubkey
    """"""
    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    client_id: int
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class CloseOpenOrdersParams(NamedTuple):
    """Cancel order by client ID params."""

    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    sol_wallet: Pubkey
    """"""
    market: Pubkey
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


class InitOpenOrdersParams(NamedTuple):
    """Cancel order by client ID params."""

    open_orders: Pubkey
    """"""
    owner: Pubkey
    """"""
    market: Pubkey
    """"""
    market_authority: Optional[Pubkey] = None
    """"""
    program_id: Pubkey = DEFAULT_DEX_PROGRAM_ID
    """"""


def __parse_and_validate_instruction(
    instruction: Instruction, instruction_type: InstructionType
) -> Container:
    instruction_type_to_length_map: Dict[InstructionType, int] = {
        InstructionType.INITIALIZE_MARKET: 9,
        InstructionType.NEW_ORDER: 9,
        InstructionType.MATCH_ORDER: 7,
        InstructionType.CONSUME_EVENTS: 2,
        InstructionType.CANCEL_ORDER: 4,
        InstructionType.CANCEL_ORDER_BY_CLIENT_ID: 4,
        InstructionType.SETTLE_FUNDS: 9,
        InstructionType.NEW_ORDER_V3: 12,
        InstructionType.CANCEL_ORDER_V2: 6,
        InstructionType.CANCEL_ORDER_BY_CLIENT_ID_V2: 6,
        InstructionType.CLOSE_OPEN_ORDERS: 4,
        InstructionType.INIT_OPEN_ORDERS: 3,
    }
    validate_instruction_keys(
        instruction, instruction_type_to_length_map[instruction_type]
    )
    data = INSTRUCTIONS_LAYOUT.parse(instruction.data)
    validate_instruction_type(data, instruction_type)
    return data


def decode_initialize_market(
    instruction: Instruction,
) -> InitializeMarketParams:
    """Decode an instialize market instruction and retrieve the instruction params."""
    data = __parse_and_validate_instruction(
        instruction, InstructionType.INITIALIZE_MARKET
    )
    return InitializeMarketParams(
        market=instruction.accounts[0].pubkey,
        request_queue=instruction.accounts[1].pubkey,
        event_queue=instruction.accounts[2].pubkey,
        bids=instruction.accounts[3].pubkey,
        asks=instruction.accounts[4].pubkey,
        base_vault=instruction.accounts[5].pubkey,
        quote_vault=instruction.accounts[6].pubkey,
        base_mint=instruction.accounts[7].pubkey,
        quote_mint=instruction.accounts[8].pubkey,
        base_lot_size=data.args.base_lot_size,
        quote_lot_size=data.args.quote_lot_size,
        fee_rate_bps=data.args.fee_rate_bps,
        vault_signer_nonce=data.args.vault_signer_nonce,
        quote_dust_threshold=data.args.quote_dust_threshold,
        program_id=instruction.program_id,
    )


def decode_new_order(instruction: Instruction) -> NewOrderParams:
    data = __parse_and_validate_instruction(instruction, InstructionType.NEW_ORDER)
    return NewOrderParams(
        market=instruction.accounts[0].pubkey,
        open_orders=instruction.accounts[1].pubkey,
        request_queue=instruction.accounts[2].pubkey,
        payer=instruction.accounts[3].pubkey,
        owner=instruction.accounts[4].pubkey,
        base_vault=instruction.accounts[5].pubkey,
        quote_vault=instruction.accounts[6].pubkey,
        side=data.args.side,
        limit_price=data.args.limit_price,
        max_quantity=data.args.max_quantity,
        order_type=data.args.order_type,
        client_id=data.args.client_id,
    )


def decode_match_orders(instruction: Instruction) -> MatchOrdersParams:
    """Decode a match orders instruction and retrieve the instruction params."""
    data = __parse_and_validate_instruction(instruction, InstructionType.MATCH_ORDER)
    return MatchOrdersParams(
        market=instruction.accounts[0].pubkey,
        request_queue=instruction.accounts[1].pubkey,
        event_queue=instruction.accounts[2].pubkey,
        bids=instruction.accounts[3].pubkey,
        asks=instruction.accounts[4].pubkey,
        base_vault=instruction.accounts[5].pubkey,
        quote_vault=instruction.accounts[6].pubkey,
        limit=data.args.limit,
    )


def decode_consume_events(instruction: Instruction) -> ConsumeEventsParams:
    """Decode a consume events instruction and retrieve the instruction params."""
    data = __parse_and_validate_instruction(instruction, InstructionType.CONSUME_EVENTS)
    return ConsumeEventsParams(
        open_orders_accounts=[a_m.pubkey for a_m in instruction.accounts[:-4]],
        market=instruction.accounts[-4].pubkey,
        event_queue=instruction.accounts[-3].pubkey,
        # NOTE - ignoring pc_fee and coin_fee as unused
        limit=data.args.limit,
    )


def decode_cancel_order(instruction: Instruction) -> CancelOrderParams:
    data = __parse_and_validate_instruction(instruction, InstructionType.CANCEL_ORDER)
    return CancelOrderParams(
        market=instruction.accounts[0].pubkey,
        open_orders=instruction.accounts[1].pubkey,
        request_queue=instruction.accounts[2].pubkey,
        owner=instruction.accounts[3].pubkey,
        side=Side(data.args.side),
        order_id=int.from_bytes(data.args.order_id, "little"),
        open_orders_slot=data.args.open_orders_slot,
    )


def decode_settle_funds(instruction: Instruction) -> SettleFundsParams:
    # data = __parse_and_validate_instruction(instruction, InstructionType.SettleFunds)
    return SettleFundsParams(
        market=instruction.accounts[0].pubkey,
        open_orders=instruction.accounts[1].pubkey,
        owner=instruction.accounts[2].pubkey,
        base_vault=instruction.accounts[3].pubkey,
        quote_vault=instruction.accounts[4].pubkey,
        base_wallet=instruction.accounts[5].pubkey,
        quote_wallet=instruction.accounts[6].pubkey,
        vault_signer=instruction.accounts[7].pubkey,
    )


def decode_cancel_order_by_client_id(
    instruction: Instruction,
) -> CancelOrderByClientIDParams:
    data = __parse_and_validate_instruction(
        instruction, InstructionType.CANCEL_ORDER_BY_CLIENT_ID
    )
    return CancelOrderByClientIDParams(
        market=instruction.accounts[0].pubkey,
        open_orders=instruction.accounts[1].pubkey,
        request_queue=instruction.accounts[2].pubkey,
        owner=instruction.accounts[3].pubkey,
        client_id=data.args.client_id,
    )


def decode_new_order_v3(instruction: Instruction) -> NewOrderV3Params:
    data = __parse_and_validate_instruction(instruction, InstructionType.NEW_ORDER_V3)
    return NewOrderV3Params(
        market=instruction.accounts[0].pubkey,
        open_orders=instruction.accounts[1].pubkey,
        request_queue=instruction.accounts[2].pubkey,
        event_queue=instruction.accounts[3].pubkey,
        bids=instruction.accounts[4].pubkey,
        asks=instruction.accounts[5].pubkey,
        payer=instruction.accounts[6].pubkey,
        owner=instruction.accounts[7].pubkey,
        base_vault=instruction.accounts[8].pubkey,
        quote_vault=instruction.accounts[9].pubkey,
        side=data.args.side,
        limit_price=data.args.limit_price,
        max_base_quantity=data.args.max_base_quantity,
        max_quote_quantity=data.args.max_quote_quantity,
        self_trade_behavior=SelfTradeBehavior(data.args.self_trade_behavior),
        order_type=OrderType(data.args.order_type),
        client_id=data.args.client_id,
        limit=data.args.limit,
    )


def decode_cancel_order_v2(instruction: Instruction) -> CancelOrderV2Params:
    data = __parse_and_validate_instruction(
        instruction, InstructionType.CANCEL_ORDER_V2
    )
    return CancelOrderV2Params(
        market=instruction.accounts[0].pubkey,
        bids=instruction.accounts[1].pubkey,
        asks=instruction.accounts[2].pubkey,
        open_orders=instruction.accounts[3].pubkey,
        owner=instruction.accounts[4].pubkey,
        event_queue=instruction.accounts[5].pubkey,
        side=Side(data.args.side),
        order_id=int.from_bytes(data.args.order_id, "little"),
        open_orders_slot=data.args.open_orders_slot,
    )


def decode_cancel_order_by_client_id_v2(
    instruction: Instruction,
) -> CancelOrderByClientIDV2Params:
    data = __parse_and_validate_instruction(
        instruction, InstructionType.CANCEL_ORDER_BY_CLIENT_ID_V2
    )
    return CancelOrderByClientIDV2Params(
        market=instruction.accounts[0].pubkey,
        bids=instruction.accounts[1].pubkey,
        asks=instruction.accounts[2].pubkey,
        open_orders=instruction.accounts[3].pubkey,
        owner=instruction.accounts[4].pubkey,
        event_queue=instruction.accounts[5].pubkey,
        client_id=data.args.client_id,
    )


def decode_close_open_orders(
    instruction: Instruction,
) -> CloseOpenOrdersParams:
    return CloseOpenOrdersParams(
        open_orders=instruction.accounts[0].pubkey,
        owner=instruction.accounts[1].pubkey,
        sol_wallet=instruction.accounts[2].pubkey,
        market=instruction.accounts[3].pubkey,
    )


def decode_init_open_orders(
    instruction: Instruction,
) -> InitOpenOrdersParams:
    market_authority = (
        instruction.accounts[-1].pubkey if len(instruction.accounts) == 5 else None
    )
    return InitOpenOrdersParams(
        open_orders=instruction.accounts[0].pubkey,
        owner=instruction.accounts[1].pubkey,
        market=instruction.accounts[2].pubkey,
        market_authority=market_authority,
    )


def initialize_market(params: InitializeMarketParams) -> Instruction:
    """Generate a transaction instruction to initialize a Serum market."""
    return Instruction(
        accounts=[
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


def new_order(params: NewOrderParams) -> Instruction:
    """Generate a transaction instruction to place new order."""
    return Instruction(
        accounts=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.request_queue, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.payer, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
            AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.NEW_ORDER,
                args=dict(
                    side=params.side,
                    limit_price=params.limit_price,
                    max_quantity=params.max_quantity,
                    order_type=params.order_type,
                    client_id=params.client_id,
                ),
            )
        ),
    )


def match_orders(params: MatchOrdersParams) -> Instruction:
    """Generate a transaction instruction to match order."""
    return Instruction(
        accounts=[
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
                instruction_type=InstructionType.MATCH_ORDER,
                args=dict(limit=params.limit),
            )
        ),
    )


def consume_events(params: ConsumeEventsParams) -> Instruction:
    """Generate a transaction instruction to consume market events."""
    accounts = [
        AccountMeta(pubkey=pubkey, is_signer=False, is_writable=True)
        # NOTE - last two accounts are required for backwards compatibility but are ignored
        for pubkey in params.open_orders_accounts
        + (2 * [params.market, params.event_queue])
    ]
    return Instruction(
        accounts=accounts,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(
                instruction_type=InstructionType.CONSUME_EVENTS,
                args=dict(limit=params.limit),
            )
        ),
    )


def cancel_order(params: CancelOrderParams) -> Instruction:
    """Generate a transaction instruction to cancel order."""
    return Instruction(
        accounts=[
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


def settle_funds(params: SettleFundsParams) -> Instruction:
    """Generate a transaction instruction to settle fund."""
    return Instruction(
        accounts=[
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
            AccountMeta(pubkey=params.base_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.quote_vault, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.base_wallet, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.quote_wallet, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.vault_signer, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(instruction_type=InstructionType.SETTLE_FUNDS, args=dict())
        ),
    )


def cancel_order_by_client_id(
    params: CancelOrderByClientIDParams,
) -> Instruction:
    """Generate a transaction instruction to cancel order by client id."""
    return Instruction(
        accounts=[
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


def new_order_v3(params: NewOrderV3Params) -> Instruction:
    """Generate a transaction instruction to place new order."""
    touched_accounts = [
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
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if params.fee_discount_pubkey:
        touched_accounts.append(
            AccountMeta(
                pubkey=params.fee_discount_pubkey, is_signer=False, is_writable=False
            ),
        )
    return Instruction(
        accounts=touched_accounts,
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
                    limit=65535,
                ),
            )
        ),
    )


def cancel_order_v2(params: CancelOrderV2Params) -> Instruction:
    """Generate a transaction instruction to cancel order."""
    return Instruction(
        accounts=[
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
) -> Instruction:
    """Generate a transaction instruction to cancel order by client id."""
    return Instruction(
        accounts=[
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


def close_open_orders(params: CloseOpenOrdersParams) -> Instruction:
    """Generate a transaction instruction to close open orders account."""
    return Instruction(
        accounts=[
            AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
            AccountMeta(pubkey=params.sol_wallet, is_signer=False, is_writable=True),
            AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
        ],
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(instruction_type=InstructionType.CLOSE_OPEN_ORDERS, args=dict())
        ),
    )


def init_open_orders(params: InitOpenOrdersParams) -> Instruction:
    """Generate a transaction instruction to initialize open orders account."""
    touched_accounts = [
        AccountMeta(pubkey=params.open_orders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=params.owner, is_signer=True, is_writable=False),
        AccountMeta(pubkey=params.market, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if params.market_authority:
        touched_accounts.append(
            AccountMeta(
                pubkey=params.market_authority, is_signer=False, is_writable=False
            ),
        )
    return Instruction(
        accounts=touched_accounts,
        program_id=params.program_id,
        data=INSTRUCTIONS_LAYOUT.build(
            dict(instruction_type=InstructionType.INIT_OPEN_ORDERS, args=dict())
        ),
    )
