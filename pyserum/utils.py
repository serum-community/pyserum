import base64

from solana.publickey import PublicKey
from solana.rpc.api import Client
from spl.token.constants import WRAPPED_SOL_MINT  # type: ignore # TODO: Remove ignore.

from pyserum._layouts.market import MINT_LAYOUT
from pyserum.instructions import DEFAULT_DEX_PROGRAM_ID

PROGRAM_LAYOUT_VERSIONS = {
    "4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn": 1,
    "BJ3jrUzddfuSrZHXSCxMUUQsjKEyLmuuyZebkcaFp2fg": 1,
    "EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o": 2,
    str(DEFAULT_DEX_PROGRAM_ID): 3,
}


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


def get_layout_version(program_id: PublicKey):
    if str(program_id) in PROGRAM_LAYOUT_VERSIONS:
        return PROGRAM_LAYOUT_VERSIONS[str(program_id)]
    return None
