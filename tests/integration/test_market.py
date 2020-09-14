from solana.publickey import PublicKey

from src.market import Market


def test_market_load(stubbed_market_pk: PublicKey, stubbed_dex_program_pk: PublicKey):
    market = Market.load("http://localhost:8899", str(stubbed_market_pk), program_id=stubbed_dex_program_pk)
    assert isinstance(market, Market)
