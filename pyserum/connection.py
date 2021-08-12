from typing import List, Dict, Any

import requests

from solana.rpc.api import Client as conn  # pylint: disable=unused-import # noqa:F401
from solana.publickey import PublicKey
from .market.types import MarketInfo, TokenInfo

LIVE_MARKETS_URL = "https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/markets.json"
TOKEN_MINTS_URL = "https://raw.githubusercontent.com/project-serum/serum-ts/master/packages/serum/src/token-mints.json"


def parse_live_markets(data: List[Dict[str, Any]]) -> List[MarketInfo]:
    return [
        MarketInfo(name=m["name"], address=m["address"], program_id=m["programId"]) for m in data if not m["deprecated"]
    ]


def parse_token_mints(data: List[Dict[str, str]]) -> List[TokenInfo]:
    return [TokenInfo(name=t["name"], address=PublicKey(t["address"])) for t in data]


def get_live_markets() -> List[MarketInfo]:
    return parse_live_markets(requests.get(LIVE_MARKETS_URL).json())


def get_token_mints() -> List[TokenInfo]:
    return parse_token_mints(requests.get(TOKEN_MINTS_URL).json())
