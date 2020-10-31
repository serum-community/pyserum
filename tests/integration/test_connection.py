from pyserum.connection import get_live_markets, get_token_mints
from pyserum.market.types import MarketInfo, TokenInfo


def test_get_live_markets():
    """Test get_live_markets."""
    assert all(isinstance(market_info, MarketInfo) for market_info in get_live_markets())


def test_get_token_mints():
    """Test get_token_mints."""
    assert all(isinstance(token_info, TokenInfo) for token_info in get_token_mints())
