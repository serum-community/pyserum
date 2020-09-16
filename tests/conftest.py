import os
from typing import Dict

import pytest
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client

__cached_params = {}


@pytest.mark.integration
@pytest.fixture(scope="session")
def __bs_params() -> Dict[str, str]:
    if not __cached_params:
        with open("tests/crank.log") as crank_log:
            for line in crank_log.readlines():
                if ":" not in line:
                    continue
                key, val = line.strip().replace(",", "").split(": ")
                assert key, "key must not be None"
                assert val, "val must not be None"
                __cached_params[key] = val
    return __cached_params


def __bootstrap_account(pubkey: str, secret: str) -> Account:
    secret = [int(b) for b in secret[1:-1].split(" ")]
    account = Account(secret)
    assert str(account.public_key()) == pubkey, "account must map to provided public key"
    return account


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_dex_program_pk(__bs_params) -> PublicKey:
    """Bootstrapped dex program id."""
    return PublicKey(__bs_params["dex_program_id"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_payer(__bs_params) -> Account:
    """Bootstrapped payer account."""
    return __bootstrap_account(__bs_params["payer"], __bs_params["payer_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_mint(__bs_params) -> Account:
    """Bootstrapped base mint account."""
    return __bootstrap_account(__bs_params["coin_mint"], __bs_params["coin_mint_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_mint(__bs_params) -> Account:
    """Bootstrapped quote mint account."""
    return __bootstrap_account(__bs_params["pc_mint"], __bs_params["pc_mint_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_wallet(__bs_params) -> Account:
    """Bootstrapped base mint account."""
    return __bootstrap_account(__bs_params["coin_wallet"], __bs_params["coin_wallet_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_wallet(__bs_params) -> Account:
    """Bootstrapped quote mint account."""
    return __bootstrap_account(__bs_params["pc_wallet"], __bs_params["pc_wallet_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_market_pk(__bs_params) -> PublicKey:
    """Public key of the boostrapped market."""
    return PublicKey(__bs_params["market"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_req_q_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped request queue."""
    return PublicKey(__bs_params["req_q"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_event_q_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped request queue."""
    return PublicKey(__bs_params["event_q"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bids_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped bids book."""
    return PublicKey(__bs_params["bids"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_asks_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped asks book."""
    return PublicKey(__bs_params["asks"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_vault_pk(__bs_params) -> PublicKey:
    """Public key of the base vault account."""
    return PublicKey(__bs_params["coin_vault"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_vault_pk(__bs_params) -> PublicKey:
    """Public key of the quote vault account."""
    return PublicKey(__bs_params["pc_vault"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_vault_signer_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped vault signer."""
    return PublicKey(__bs_params["vault_signer_key"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bid_account_pk(__bs_params) -> PublicKey:
    """Public key of the initial bid order account."""
    return PublicKey(__bs_params["bid_account"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_ask_account_pk(__bs_params) -> PublicKey:
    """Public key of the initial ask order account."""
    return PublicKey(__bs_params["ask_account"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), ".", "docker-compose.yml")


@pytest.mark.integration
@pytest.fixture(scope="session")
def http_client() -> Client:
    """Solana http client."""
    client = Client()
    if not client.is_connected():
        raise Exception("Could not connect to local node. Please run `make int-tests` to run integration tests.")
    return client
