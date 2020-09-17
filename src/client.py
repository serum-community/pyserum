from solana.rpc.api import Client


def market_client(endpoint: str) -> Client:
    """RPC client to interact with the Serum Dex."""
    return Client(endpoint)
