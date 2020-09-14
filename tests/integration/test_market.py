import pytest
from solana.publickey import PublicKey

from src.market import Market


@pytest.mark.integration
@pytest.fixture(scope="session")
def loaded_market(stubbed_market_pk: PublicKey, stubbed_dex_program_pk: PublicKey):
    market = Market.load("http://localhost:8899", str(stubbed_market_pk), None, program_id=stubbed_dex_program_pk)
    assert isinstance(market, Market)
    return market


@pytest.mark.integration
def test_market_load_bid(loaded_market: Market):
    bids = loaded_market.load_bids()
    cnt = 0
    for bid in bids:
        cnt += 1
    assert cnt == 1
