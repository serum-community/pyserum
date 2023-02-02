import asyncio
from typing import Dict

import pytest
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient

from pyserum.async_connection import async_conn
from pyserum.connection import conn


@pytest.mark.integration
@pytest.fixture(scope="session")
def __bs_params() -> Dict[str, str]:
    params = {}
    with open("tests/crank.log") as crank_log:
        for line in crank_log.readlines():
            if ":" not in line:
                continue
            key, val = line.strip().replace(",", "").split(": ")
            assert key, "key must not be None"
            assert val, "val must not be None"
            params[key] = val
    return params


def __bootstrap_account(pubkey: str, secretkey: str) -> Keypair:
    secret = [int(b) for b in secretkey[1:-1].split(" ")]
    secret_bytes = bytes(secret)
    keypair = Keypair.from_bytes(secret_bytes)
    assert str(keypair.pubkey()) == pubkey, "account must map to provided public key"
    return keypair


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_dex_program_pk(__bs_params) -> Pubkey:
    """Bootstrapped dex program id."""
    return Pubkey.from_string(__bs_params["dex_program_id"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_payer(__bs_params) -> Keypair:
    """Bootstrapped payer account."""
    return __bootstrap_account(__bs_params["payer"], __bs_params["payer_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_mint(__bs_params) -> Keypair:
    """Bootstrapped base mint account."""
    return __bootstrap_account(__bs_params["coin_mint"], __bs_params["coin_mint_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_mint(__bs_params) -> Keypair:
    """Bootstrapped quote mint account."""
    return __bootstrap_account(__bs_params["pc_mint"], __bs_params["pc_mint_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_wallet(__bs_params) -> Keypair:
    """Bootstrapped base mint account."""
    return __bootstrap_account(__bs_params["coin_wallet"], __bs_params["coin_wallet_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_wallet(__bs_params) -> Keypair:
    """Bootstrapped quote mint account."""
    return __bootstrap_account(__bs_params["pc_wallet"], __bs_params["pc_wallet_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_market_pk(__bs_params) -> Pubkey:
    """Public key of the boostrapped market."""
    return Pubkey.from_string(__bs_params["market"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_req_q_pk(__bs_params) -> Pubkey:
    """Public key of the bootstrapped request queue."""
    return Pubkey.from_string(__bs_params["req_q"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_event_q_pk(__bs_params) -> Pubkey:
    """Public key of the bootstrapped request queue."""
    return Pubkey.from_string(__bs_params["event_q"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bids_pk(__bs_params) -> Pubkey:
    """Public key of the bootstrapped bids book."""
    return Pubkey.from_string(__bs_params["bids"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_asks_pk(__bs_params) -> Pubkey:
    """Public key of the bootstrapped asks book."""
    return Pubkey.from_string(__bs_params["asks"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_vault_pk(__bs_params) -> Pubkey:
    """Public key of the base vault account."""
    return Pubkey.from_string(__bs_params["coin_vault"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_vault_pk(__bs_params) -> Pubkey:
    """Public key of the quote vault account."""
    return Pubkey.from_string(__bs_params["pc_vault"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_vault_signer_pk(__bs_params) -> Pubkey:
    """Public key of the bootstrapped vault signer."""
    return Pubkey.from_string(__bs_params["vault_signer_key"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bid_account_pk(__bs_params) -> Pubkey:
    """Public key of the initial bid order account."""
    return Pubkey.from_string(__bs_params["bid_account"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_ask_account_pk(__bs_params) -> Pubkey:
    """Public key of the initial ask order account."""
    return Pubkey.from_string(__bs_params["ask_account"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def http_client() -> Client:
    """Solana http client."""
    cc = conn("http://localhost:8899")  # pylint: disable=invalid-name
    if not cc.is_connected():
        raise Exception("Could not connect to local node. Please run `make int-tests` to run integration tests.")
    return cc


@pytest.fixture(scope="session")
def event_loop():
    """Event loop for pytest-asyncio."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.async_integration
@pytest.fixture(scope="session")
def async_http_client(event_loop) -> AsyncClient:  # pylint: disable=redefined-outer-name
    """Solana async http client."""
    cc = async_conn("http://localhost:8899")  # pylint: disable=invalid-name
    if not event_loop.run_until_complete(cc.is_connected()):
        raise Exception(
            "Could not connect to local node. Please run `make async-int-tests` to run async integration tests."
        )
    yield cc
    event_loop.run_until_complete(cc.close())
