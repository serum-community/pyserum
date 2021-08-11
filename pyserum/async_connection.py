from typing import List
import httpx
from solana.rpc.async_api import AsyncClient as async_conn  # pylint: disable=unused-import # noqa:F401

from .market.types import MarketInfo, TokenInfo
from .connection import LIVE_MARKETS_URL, TOKEN_MINTS_URL, parse_live_markets, parse_token_mints


async def get_live_markets(httpx_client: httpx.AsyncClient) -> List[MarketInfo]:
    resp = await httpx_client.get(LIVE_MARKETS_URL)
    return parse_live_markets(resp.json())


async def get_token_mints(httpx_client: httpx.AsyncClient) -> List[TokenInfo]:
    resp = await httpx_client.get(TOKEN_MINTS_URL)
    return parse_token_mints(resp.json())
