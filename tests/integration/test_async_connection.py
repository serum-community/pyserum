# pylint: disable=R0801
import pytest
import httpx

from pyserum.async_connection import get_live_markets, get_token_mints
from pyserum.market.types import MarketInfo, TokenInfo


@pytest.mark.async_integration
@pytest.mark.asyncio
async def test_get_live_markets():
    """Test get_live_markets."""
    async with httpx.AsyncClient() as client:
        resp = await get_live_markets(client)
    assert all(isinstance(market_info, MarketInfo) for market_info in resp)


@pytest.mark.async_integration
@pytest.mark.asyncio
async def test_get_token_mints():
    """Test get_token_mints."""
    async with httpx.AsyncClient() as client:
        resp = await get_token_mints(client)
    assert all(isinstance(token_info, TokenInfo) for token_info in resp)
