import base64

from solana.publickey import PublicKey
from solana.rpc.api import Client
from spl.token.constants import WRAPPED_SOL_MINT

from pyserum._layouts.market import MINT_LAYOUT


def load_bytes_data(addr: PublicKey, conn: Client):
    res = conn.get_account_info(addr)
    if ("result" not in res) or ("value" not in res["result"]) or ("data" not in res["result"]["value"]):
        raise Exception("Cannot load byte data.")
    data = res["result"]["value"]["data"][0]
    return base64.decodebytes(data.encode("ascii"))


def get_mint_decimals(conn: Client, mint_pub_key: PublicKey) -> int:
    """Get the mint decimals for a token mint"""
    if mint_pub_key == WRAPPED_SOL_MINT:
        return 9

    bytes_data = load_bytes_data(mint_pub_key, conn)
    return MINT_LAYOUT.parse(bytes_data).decimals
