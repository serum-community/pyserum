from solana.rpc.api import Client


def conn(endpoint: str) -> Client:
    """RPC client connection to interact with the Serum Dex."""
    return Client(endpoint)
