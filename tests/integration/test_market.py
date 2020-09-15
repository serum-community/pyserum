# pylint: disable=redefined-outer-name
import pytest
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client

from src.enums import OrderType, Side
from src.market import Market, PlaceOrderParams

from .utils import confirm_transaction


@pytest.mark.integration
@pytest.fixture(scope="session")
def bootstrapped_market(stubbed_market_pk: PublicKey, stubbed_dex_program_pk: PublicKey) -> Market:
    return Market.load("http://localhost:8899", str(stubbed_market_pk), None, program_id=stubbed_dex_program_pk)


@pytest.mark.integration
def test_bootstrapped_market(
    bootstrapped_market: Market,
    stubbed_market_pk: PublicKey,
    stubbed_dex_program_pk: PublicKey,
    stubbed_base_mint: PublicKey,
    stubbed_quote_mint: PublicKey,
):
    assert isinstance(bootstrapped_market, Market)
    assert bootstrapped_market.address() == stubbed_market_pk
    assert bootstrapped_market.program_id() == stubbed_dex_program_pk
    assert bootstrapped_market.base_mint_address() == stubbed_base_mint.public_key()
    assert bootstrapped_market.quote_mint_address() == stubbed_quote_mint.public_key()


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
def test_match_order(bootstrapped_market: Market, stubbed_payer: Account, http_client: Client):
    sig = bootstrapped_market.match_orders(stubbed_payer, 2)
    confirm_transaction(http_client, sig)

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
def test_new_order(
    bootstrapped_market: Market, stubbed_payer: Account, http_client: Client, stubbed_quote_wallet: Account
):
    initial_request_len = len(bootstrapped_market.load_request_queue())
    order_params = PlaceOrderParams(
        payer=stubbed_quote_wallet.public_key(),
        owner=stubbed_payer,
        side=Side.Buy,
        order_type=OrderType.Limit,
        limit_price=1234,
        max_quantity=4321,
    )
    sig = bootstrapped_market.place_order(order_params)
    confirm_transaction(http_client, sig)

    request_queue = bootstrapped_market.load_request_queue()
    # 0 request after matching.
    assert len(request_queue) == initial_request_len + 1

    # There should be no bid order.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    # There should be no ask order.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0
