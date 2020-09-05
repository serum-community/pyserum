"""Test instructions."""

from solana.publickey import PublicKey

import src.instructions as inlib
from enums import OrderType, Side


def test_initialize_market():
    """Test initialize market."""
    params = inlib.InitializeMarketParams(
        market=PublicKey(0),
        request_queue=PublicKey(1),
        event_queue=PublicKey(2),
        bids=PublicKey(3),
        asks=PublicKey(4),
        base_vault=PublicKey(5),
        quote_vault=PublicKey(6),
        base_mint=PublicKey(7),
        quote_mint=PublicKey(8),
        base_lot_size=1,
        quote_lot_size=2,
        fee_rate_bps=3,
        vault_signer_nonce=4,
        quote_dust_threshold=5,
    )
    instruction = inlib.initialize_market(params)
    assert inlib.decode_initialize_market(instruction) == params


def test_new_orders():
    """Test match orders."""
    params = inlib.NewOrderParams(
        market=PublicKey(0),
        open_orders=PublicKey(1),
        payer=PublicKey(2),
        owner=PublicKey(3),
        request_queue=PublicKey(4),
        base_vault=PublicKey(5),
        quote_vault=PublicKey(6),
        side=Side.Buy,
        limit_price=1,
        max_quantity=1,
        order_type=OrderType.IOC,
        client_id=1,
    )
    instruction = inlib.new_order(params)
    assert inlib.decode_new_order(instruction) == params


def test_match_orders():
    """Test match orders."""
    params = inlib.MatchOrdersParams(
        market=PublicKey(0),
        request_queue=PublicKey(1),
        event_queue=PublicKey(2),
        bids=PublicKey(3),
        asks=PublicKey(4),
        base_vault=PublicKey(5),
        quote_vault=PublicKey(6),
        limit=1,
    )
    instruction = inlib.match_orders(params)
    assert inlib.decode_match_orders(instruction) == params


def test_consume_events():
    params = inlib.ConsumeEventsParams(
        market=PublicKey(0),
        event_queue=PublicKey(1),
        open_orders_accounts=[PublicKey(i + 2) for i in range(8)],
        limit=1,
    )
    instruction = inlib.consume_events(params)
    assert inlib.decode_consume_events(instruction) == params
