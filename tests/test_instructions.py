"""Test instructions."""

from solders.pubkey import Pubkey

import pyserum.instructions as inlib
from pyserum.enums import OrderType, Side


def test_initialize_market():
    """Test initialize market."""
    params = inlib.InitializeMarketParams(
        market=Pubkey.from_string("11111111111111111111111111111112"),
        request_queue=Pubkey.from_string("11111111111111111111111111111113"),
        event_queue=Pubkey.from_string("11111111111111111111111111111114"),
        bids=Pubkey.from_string("11111111111111111111111111111115"),
        asks=Pubkey.from_string("11111111111111111111111111111116"),
        base_vault=Pubkey.from_string("11111111111111111111111111111117"),
        quote_vault=Pubkey.from_string("11111111111111111111111111111118"),
        base_mint=Pubkey.from_string("11111111111111111111111111111119"),
        quote_mint=Pubkey.from_string("1111111111111111111111111111111A"),
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
        market=Pubkey.from_string("11111111111111111111111111111112"),
        open_orders=Pubkey.from_string("11111111111111111111111111111113"),
        payer=Pubkey.from_string("11111111111111111111111111111114"),
        owner=Pubkey.from_string("11111111111111111111111111111115"),
        request_queue=Pubkey.from_string("11111111111111111111111111111116"),
        base_vault=Pubkey.from_string("11111111111111111111111111111117"),
        quote_vault=Pubkey.from_string("11111111111111111111111111111118"),
        side=Side.BUY,
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
        market=Pubkey.from_string("11111111111111111111111111111112"),
        request_queue=Pubkey.from_string("11111111111111111111111111111113"),
        event_queue=Pubkey.from_string("11111111111111111111111111111114"),
        bids=Pubkey.from_string("11111111111111111111111111111115"),
        asks=Pubkey.from_string("11111111111111111111111111111116"),
        base_vault=Pubkey.from_string("11111111111111111111111111111117"),
        quote_vault=Pubkey.from_string("11111111111111111111111111111118"),
        limit=1,
    )
    instruction = inlib.match_orders(params)
    assert inlib.decode_match_orders(instruction) == params


def test_consume_events():
    params = inlib.ConsumeEventsParams(
        market=Pubkey.from_string("11111111111111111111111111111112"),
        event_queue=Pubkey.from_string("11111111111111111111111111111113"),
        open_orders_accounts=[Pubkey.from_string("1111111111111111111111111111111{:X}".format(i+2)) for i in range(8)],
        limit=1,
    )
    instruction = inlib.consume_events(params)
    assert inlib.decode_consume_events(instruction) == params


def test_cancel_order():
    """Test cancel order."""
    params = inlib.CancelOrderParams(
        market=Pubkey.from_string("11111111111111111111111111111112"),
        request_queue=Pubkey.from_string("11111111111111111111111111111113"),
        owner=Pubkey.from_string("11111111111111111111111111111114"),
        open_orders=Pubkey.from_string("11111111111111111111111111111115"),
        side=Side.BUY,
        order_id=1,
        open_orders_slot=1,
    )
    instruction = inlib.cancel_order(params)
    assert inlib.decode_cancel_order(instruction) == params


def test_cancel_order_by_client_id():
    """Test cancel order by client id."""
    params = inlib.CancelOrderByClientIDParams(
        market=Pubkey.from_string("11111111111111111111111111111112"),
        request_queue=Pubkey.from_string("11111111111111111111111111111113"),
        owner=Pubkey.from_string("11111111111111111111111111111114"),
        open_orders=Pubkey.from_string("11111111111111111111111111111115"),
        client_id=1
    )
    instruction = inlib.cancel_order_by_client_id(params)
    assert inlib.decode_cancel_order_by_client_id(instruction) == params


def test_settle_funds():
    """Test settle funds."""
    params = inlib.SettleFundsParams(
        market=Pubkey.from_string("11111111111111111111111111111112"),
        owner=Pubkey.from_string("11111111111111111111111111111113"),
        open_orders=Pubkey.from_string("11111111111111111111111111111114"),
        base_vault=Pubkey.from_string("11111111111111111111111111111115"),
        quote_vault=Pubkey.from_string("11111111111111111111111111111116"),
        base_wallet=Pubkey.from_string("11111111111111111111111111111117"),
        quote_wallet=Pubkey.from_string("11111111111111111111111111111118"),
        vault_signer=Pubkey.from_string("11111111111111111111111111111119"),
    )
    instruction = inlib.settle_funds(params)
    assert inlib.decode_settle_funds(instruction) == params


def test_close_open_orders():
    """Test settle funds."""
    params = inlib.CloseOpenOrdersParams(
        open_orders=Pubkey.from_string("11111111111111111111111111111112"),
        owner=Pubkey.from_string("11111111111111111111111111111113"),
        sol_wallet=Pubkey.from_string("11111111111111111111111111111114"),
        market=Pubkey.from_string("11111111111111111111111111111115"),
    )
    instruction = inlib.close_open_orders(params)
    assert inlib.decode_close_open_orders(instruction) == params


def test_init_open_orders():
    """Test settle funds."""
    params = inlib.InitOpenOrdersParams(
        open_orders=Pubkey.from_string("11111111111111111111111111111112"),
        owner=Pubkey.from_string("11111111111111111111111111111113"),
        market=Pubkey.from_string("11111111111111111111111111111114"),
        market_authority=None
    )
    instruction = inlib.init_open_orders(params)
    assert inlib.decode_init_open_orders(instruction) == params


def test_init_open_orders_with_authority():
    """Test settle funds."""
    params = inlib.InitOpenOrdersParams(
        open_orders=Pubkey.from_string("11111111111111111111111111111112"),
        owner=Pubkey.from_string("11111111111111111111111111111113"),
        market=Pubkey.from_string("11111111111111111111111111111114"),
        market_authority=Pubkey.from_string("11111111111111111111111111111115"),
    )
    instruction = inlib.init_open_orders(params)
    assert inlib.decode_init_open_orders(instruction) == params
