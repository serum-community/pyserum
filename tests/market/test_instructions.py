"""Test instructions."""

from solana.publickey import PublicKey

import pyserum.market.instructions as inlib
from pyserum.market.enums import OrderType, Side


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


def test_cancel_order():
    """Test cancel order."""
    params = inlib.CancelOrderParams(
        market=PublicKey(0),
        request_queue=PublicKey(1),
        owner=PublicKey(2),
        open_orders=PublicKey(3),
        side=Side.Buy,
        order_id=1,
        open_orders_slot=1,
    )
    instruction = inlib.cancel_order(params)
    assert inlib.decode_cancel_order(instruction) == params


def test_cancel_order_by_client_id():
    """Test cancel order by client id."""
    params = inlib.CancelOrderByClientIDParams(
        market=PublicKey(0), request_queue=PublicKey(1), owner=PublicKey(2), open_orders=PublicKey(3), client_id=1
    )
    instruction = inlib.cancel_order_by_client_id(params)
    assert inlib.decode_cancel_order_by_client_id(instruction) == params


def test_settle_funds():
    """Test settle funds."""
    params = inlib.SettleFundsParams(
        market=PublicKey(0),
        owner=PublicKey(1),
        open_orders=PublicKey(2),
        base_vault=PublicKey(3),
        quote_vault=PublicKey(4),
        base_wallet=PublicKey(5),
        quote_wallet=PublicKey(6),
        vault_signer=PublicKey(7),
    )
    instruction = inlib.settle_funds(params)
    assert inlib.decode_settle_funds(instruction) == params
