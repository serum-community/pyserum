from typing import List

from solana.rpc.api import Client as conn  # pylint: disable=unused-import # noqa:F401
from solana.rpc.providers.http import requests

from .market.types import MarketInfo, TokenInfo


def get_live_markets() -> List[MarketInfo]:
    url = "https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json"
    return [
        MarketInfo(name=m["name"], address=m["address"], program_id=m["programId"])
        for m in requests.get(url).json()
        if not m["deprecated"]
    ]


def get_token_mints() -> List[TokenInfo]:
    url = "https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/token-mints.json"
    return [TokenInfo(**t) for t in requests.get(url).json()]
