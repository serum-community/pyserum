import time

from solana.rpc.api import Client
from solana.rpc.types import RPCResponse


def confirm_transaction(tx_sig: str) -> RPCResponse:
    """Confirm a transaction."""
    client = Client("http://localhost:8899")
    TIMEOUT = 30  # 30 seconds  pylint: disable=invalid-name
    elapsed_time = 0
    while elapsed_time < TIMEOUT:
        sleep_time = 3
        if not elapsed_time:
            sleep_time = 7
            time.sleep(sleep_time)
        else:
            time.sleep(sleep_time)
        resp = client.get_confirmed_transaction(tx_sig)
        if resp.get("result"):
            break
        elapsed_time += sleep_time

    if not resp.get("result"):
        raise RuntimeError("could not confirm transaction: ", tx_sig)
    return resp
