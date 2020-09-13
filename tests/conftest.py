from typing import Dict

import pytest
from solana.account import Account
from solana.publickey import PublicKey

__dex_fixtures = {}


@pytest.mark.integration
@pytest.fixture(scope="session")
def serum_dex() -> Dict[str, PublicKey]:
    if not __dex_fixtures:
        with open("tests/crank.log") as crank_log:
            for line in crank_log.readlines():
                if ":" not in line:
                    continue
                key, val = line.strip().replace(",", "").split(": ")
                assert val is not None
                __dex_fixtures[key] = PublicKey(val)
    return __dex_fixtures


@pytest.fixture(scope="session")
def wallet() -> Account:
    """Account fixture with token balances."""
    __secret = [
        80,
        153,
        206,
        2,
        83,
        121,
        34,
        148,
        53,
        118,
        38,
        177,
        28,
        133,
        4,
        35,
        155,
        181,
        188,
        184,
        134,
        8,
        118,
        116,
        56,
        126,
        76,
        49,
        126,
        79,
        137,
        220,
    ]
    return Account(__secret)
