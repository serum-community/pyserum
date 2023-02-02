# pylint: disable=redefined-outer-name

import pytest
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

from pyserum.enums import OrderType, Side
from pyserum.market import Market


@pytest.mark.integration
@pytest.fixture(scope="module")
def bootstrapped_market(http_client: Client, stubbed_market_pk: Pubkey, stubbed_dex_program_pk: Pubkey) -> Market:
    return Market.load(http_client, stubbed_market_pk, stubbed_dex_program_pk, force_use_request_queue=True)


@pytest.mark.integration
def test_bootstrapped_market(
    bootstrapped_market: Market,
    stubbed_market_pk: Pubkey,
    stubbed_dex_program_pk: Pubkey,
    stubbed_base_mint: Keypair,
    stubbed_quote_mint: Keypair,
):
    assert isinstance(bootstrapped_market, Market)
    assert bootstrapped_market.state.public_key() == stubbed_market_pk
    assert bootstrapped_market.state.program_id() == stubbed_dex_program_pk
    assert bootstrapped_market.state.base_mint() == stubbed_base_mint.pubkey()
    assert bootstrapped_market.state.quote_mint() == stubbed_quote_mint.pubkey()


@pytest.mark.integration
def test_market_load_bid(bootstrapped_market: Market):
    # TODO: test for non-zero order case.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0


@pytest.mark.integration
def test_market_load_asks(bootstrapped_market: Market):
    # TODO: test for non-zero order case.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0


@pytest.mark.integration
def test_market_load_events(bootstrapped_market: Market):
    event_queue = bootstrapped_market.load_event_queue()
    assert len(event_queue) == 0


@pytest.mark.integration
def test_market_load_requests(bootstrapped_market: Market):
    request_queue = bootstrapped_market.load_request_queue()
    # 2 requests in the request queue in the beginning with one bid and one ask
    assert len(request_queue) == 2


@pytest.mark.integration
def test_match_order(bootstrapped_market: Market, stubbed_payer: Keypair):
    bootstrapped_market.match_orders(stubbed_payer, 2, TxOpts(skip_confirmation=False))

    request_queue = bootstrapped_market.load_request_queue()
    # 0 request after matching.
    assert len(request_queue) == 0

    event_queue = bootstrapped_market.load_event_queue()
    # 5 event after the order is matched, including 2 fill events.
    assert len(event_queue) == 5

    # There should be no bid order.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    # There should be no ask order.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0


@pytest.mark.integration
def test_settle_fund(
    bootstrapped_market: Market,
    stubbed_payer: Keypair,
    stubbed_quote_wallet: Keypair,
    stubbed_base_wallet: Keypair,
):
    open_order_accounts = bootstrapped_market.find_open_orders_accounts_for_owner(stubbed_payer.pubkey())

    with pytest.raises(ValueError):
        # Should not allow base_wallet to be base_vault
        bootstrapped_market.settle_funds(
            stubbed_payer,
            open_order_accounts[0],
            bootstrapped_market.state.base_vault(),
            stubbed_quote_wallet.pubkey(),
        )

    with pytest.raises(ValueError):
        # Should not allow quote_wallet to be wallet_vault
        bootstrapped_market.settle_funds(
            stubbed_payer,
            open_order_accounts[0],
            stubbed_base_wallet.pubkey(),
            bootstrapped_market.state.quote_vault(),
        )

    for open_order_account in open_order_accounts:
        assert "error" not in bootstrapped_market.settle_funds(
            stubbed_payer,
            open_order_account,
            stubbed_base_wallet.pubkey(),
            stubbed_quote_wallet.pubkey(),
            opts=TxOpts(skip_confirmation=False),
        )

    # TODO: Check account states after settling funds


@pytest.mark.integration
def test_order_placement_cancellation_cycle(
    bootstrapped_market: Market,
    stubbed_payer: Keypair,
    stubbed_quote_wallet: Keypair,
    stubbed_base_wallet: Keypair,
):
    initial_request_len = len(bootstrapped_market.load_request_queue())
    bootstrapped_market.place_order(
        payer=stubbed_quote_wallet.pubkey(),
        owner=stubbed_payer,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        limit_price=1000,
        max_quantity=3000,
        opts=TxOpts(skip_confirmation=False),
    )

    request_queue = bootstrapped_market.load_request_queue()
    # 0 request after matching.
    assert len(request_queue) == initial_request_len + 1

    # There should be no bid order.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    # There should be no ask order.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0

    bootstrapped_market.place_order(
        payer=stubbed_base_wallet.pubkey(),
        owner=stubbed_payer,
        side=Side.SELL,
        order_type=OrderType.LIMIT,
        limit_price=1500,
        max_quantity=3000,
        opts=TxOpts(skip_confirmation=False),
    )

    # The two order shouldn't get executed since there is a price difference of 1
    bootstrapped_market.match_orders(
        stubbed_payer,
        2,
        opts=TxOpts(skip_confirmation=False),
    )

    # There should be 1 bid order that we sent earlier.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 1

    # There should be 1 ask order that we sent earlier.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 1

    for bid in bids:
        bootstrapped_market.cancel_order(stubbed_payer, bid, opts=TxOpts(skip_confirmation=False))

    bootstrapped_market.match_orders(stubbed_payer, 1, opts=TxOpts(skip_confirmation=False))

    # All bid order should have been cancelled.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    for ask in asks:
        bootstrapped_market.cancel_order(stubbed_payer, ask, opts=TxOpts(skip_confirmation=False))

    bootstrapped_market.match_orders(stubbed_payer, 1, opts=TxOpts(skip_confirmation=False))

    # All ask order should have been cancelled.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0
