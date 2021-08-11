from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from spl.token.constants import WRAPPED_SOL_MINT

from pyserum.utils import parse_bytes_data, parse_mint_decimals


async def load_bytes_data(addr: PublicKey, conn: AsyncClient) -> bytes:
    res = await conn.get_account_info(addr)
    return parse_bytes_data(res)


async def get_mint_decimals(conn: AsyncClient, mint_pub_key: PublicKey) -> int:
    """Get the mint decimals for a token mint"""
    if mint_pub_key == WRAPPED_SOL_MINT:
        return 9

    bytes_data = await load_bytes_data(mint_pub_key, conn)
    return parse_mint_decimals(bytes_data)
