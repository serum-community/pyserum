import pytest
from solana.account import Account
from solana.publickey import PublicKey

from src.market import Market

from .utils import confirm_transaction


@pytest.mark.integration
@pytest.fixture(scope="session")
def loaded_market(stubbed_market_pk: PublicKey, stubbed_dex_program_pk: PublicKey) -> Market:
    market = Market.load("http://localhost:8899", str(stubbed_market_pk), None, program_id=stubbed_dex_program_pk)
    return market


@pytest.mark.integration
def test_loaded_market(
    loaded_market: Market,
    stubbed_market_pk: PublicKey,
    stubbed_dex_program_pk: PublicKey,
    stubbed_base_mint: PublicKey,
    stubbed_quote_mint: PublicKey,
):
    assert isinstance(loaded_market, Market)
    assert loaded_market.address() == stubbed_market_pk
    assert loaded_market.program_id() == stubbed_dex_program_pk
    assert loaded_market.base_mint_address() == stubbed_base_mint.public_key()
    assert loaded_market.quote_mint_address() == stubbed_quote_mint.public_key()


@pytest.mark.integration
def test_market_load_bid(loaded_market: Market):
    bids = loaded_market.load_bids()
    cnt = 0
    for bid in bids:
        cnt += 1
    assert cnt == 0


@pytest.mark.integration
def test_market_load_asks(loaded_market: Market):
    asks = loaded_market.load_asks()
    cnt = 0
    for ask in asks:
        cnt += 1
    assert cnt == 0


@pytest.mark.integration
def test_market_load_events(loaded_market: Market):
    event_queue = loaded_market.load_event_queue()
    assert len(event_queue) == 0


@pytest.mark.integration
def test_market_load_requests(loaded_market: Market, stubbed_payer: Account):
    request_queue = loaded_market.load_request_queue()
    # two requests in the request queue in the beginning with one bid and one ask
    assert len(request_queue) == 2
    sig = loaded_market.match_orders(stubbed_payer, 2)
    confirm_transaction(sig)
    request_queue = loaded_market.load_request_queue()
    # 5 event after the order is matched, including 2 fill events
    assert len(request_queue) == 5
