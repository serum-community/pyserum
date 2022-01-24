"""Test instructions."""

from solana.publickey import PublicKey

import pyserum.instructions as inlib
from pyserum.enums import OrderType, Side, SelfTradeBehavior


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
    """Test new orders."""
    params = inlib.NewOrderParams(
        market=PublicKey(0),
        open_orders=PublicKey(1),
        payer=PublicKey(2),
        owner=PublicKey(3),
        request_queue=PublicKey(4),
        base_vault=PublicKey(5),
        quote_vault=PublicKey(6),
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
    """test consume events."""
    params = inlib.ConsumeEventsParams(
        market=PublicKey(0),
        event_queue=PublicKey(1),
        open_orders_accounts=[PublicKey(i + 2) for i in range(8)],
        limit=1,
        program_id=PublicKey(3),
        pc_fee=PublicKey(4),
        coin_fee=PublicKey(5),
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
        side=Side.BUY,
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


def test_new_order_v3():
    """Test new order v3."""
    params = inlib.NewOrderV3Params(
        market=PublicKey(0),
        open_orders=PublicKey(1),
        payer=PublicKey(2),
        owner=PublicKey(3),
        request_queue=PublicKey(4),
        event_queue=PublicKey(5),
        bids=PublicKey(6),
        asks=PublicKey(7),
        base_vault=PublicKey(8),
        quote_vault=PublicKey(9),
        side=Side.BUY,
        limit_price=1,
        max_base_quantity=2,
        max_quote_quantity=3,
        order_type=OrderType.IOC,
        self_trade_behavior=SelfTradeBehavior.DECREMENT_TAKE,
        client_id=4,
        limit=5,
        program_id=PublicKey(10),
        # fee_discount_pubkey=PublicKey(11),
    )
    instruction = inlib.new_order_v3(params)
    assert inlib.decode_new_order_v3(instruction) == params


def test_cancel_order_v2():
    """Test cancel order v2."""
    params = inlib.CancelOrderV2Params(
        market=PublicKey(0),
        bids=PublicKey(1),
        asks=PublicKey(2),
        event_queue=PublicKey(3),
        open_orders=PublicKey(4),
        owner=PublicKey(5),
        side=Side.BUY,
        order_id=1,
        program_id=PublicKey(6),
    )
    instruction = inlib.cancel_order_v2(params)
    assert inlib.decode_cancel_order_v2(instruction) == params


def test_cancel_order_by_client_id_v2():
    """Test cancel order by client id v2."""
    params = inlib.CancelOrderByClientIDV2Params(
        market=PublicKey(0),
        bids=PublicKey(1),
        asks=PublicKey(2),
        event_queue=PublicKey(3),
        open_orders=PublicKey(4),
        owner=PublicKey(5),
        client_id=1,
        program_id=PublicKey(6),
    )
    instruction = inlib.cancel_order_by_client_id_v2(params)
    assert inlib.decode_cancel_order_by_client_id_v2(instruction) == params


def test_close_open_orders():
    """Test close open orders."""
    params = inlib.CloseOpenOrdersParams(
        open_orders=PublicKey(0),
        owner=PublicKey(1),
        sol_wallet=PublicKey(2),
        market=PublicKey(3),
    )
    instruction = inlib.close_open_orders(params)
    assert inlib.decode_close_open_orders(instruction) == params


def test_init_open_orders():
    """Test init open orders."""
    params = inlib.InitOpenOrdersParams(
        open_orders=PublicKey(0),
        owner=PublicKey(1),
        market=PublicKey(2),
        market_authority=None
    )
    instruction = inlib.init_open_orders(params)
    assert inlib.decode_init_open_orders(instruction) == params


def test_init_open_orders_with_authority():
    """Test init open orders with authority."""
    params = inlib.InitOpenOrdersParams(
        open_orders=PublicKey(0),
        owner=PublicKey(1),
        market=PublicKey(2),
        market_authority=PublicKey(3),
    )
    instruction = inlib.init_open_orders(params)
    assert inlib.decode_init_open_orders(instruction) == params


def test_prune():
    """Test prune."""
    params = inlib.PruneParams(
        market=PublicKey(0),
        bids=PublicKey(1),
        asks=PublicKey(2),
        event_queue=PublicKey(3),
        prune_authority=PublicKey(4),
        open_orders=PublicKey(5),
        open_orders_owner=PublicKey(6),
        program_id=PublicKey(7),
        limit=1,
    )
    instruction = inlib.prune(params)
    assert inlib.decode_prune(instruction) == params

