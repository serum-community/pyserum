from pyserum.connection import get_live_markets
from pyserum.market.types import MarketInfo


def test_get_live_markets():
    assert all(isinstance(market_info, MarketInfo) for market_info in get_live_markets())
