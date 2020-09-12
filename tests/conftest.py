import os
import time

import pytest
from solana.publickey import PublicKey
from solana.rpc.api import Client

from src.payer import Payer


@pytest.fixture(scope="session")
def dex_program_id() -> PublicKey:
    """Dex program Id for the docker instance."""
    return PublicKey("HrH1LR2ba4GrGi6LRRdUUAHThcv9hMh3vsYfMSrvQGfA")


@pytest.mark.integration
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), ".", "docker-compose.yml")


@pytest.mark.integration
@pytest.fixture(scope="session")
def http_client(docker_services) -> Client:
    """Solana http client."""
    client = Client()
    docker_services.wait_until_responsive(timeout=15, pause=1, check=client.is_connected)
    time.sleep(3)  # XXX: Hack for container to sync from genesis to deployment snapshot.
    print(client.get_recent_blockhash())
    return client


@pytest.fixture(scope="session")
def stubbed_payer(http_client, dex_program_id) -> Payer:  # pylint: disable=redefined-outer-name
    """Stubbed payer."""
    return Payer(http_client, 9999, dex_program_id)
