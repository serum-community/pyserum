import pytest

from solana.publickey import PublicKey

__dex_fixtures = {}


@pytest.mark.integration
@pytest.fixture(scope="session")
def serum_dex():
    if not __dex_fixtures:
        with open("tests/crank.log") as crank_log:
            for line in crank_log.readlines():
                if ":" not in line:
                    continue
                key, val = line.strip().replace(",", "").split(": ")
                assert val is not None
                __dex_fixtures[key] = PublicKey(val)
    return __dex_fixtures
