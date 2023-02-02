from __future__ import annotations

from typing import List

from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solana.rpc.types import Commitment

from .async_utils import load_bytes_data
from .open_orders_account import _OpenOrdersAccountCore


class AsyncOpenOrdersAccount(_OpenOrdersAccountCore):
    @classmethod
    async def find_for_market_and_owner(  # pylint: disable=too-many-arguments
        cls,
        conn: AsyncClient,
        market: Pubkey,
        owner: Pubkey,
        program_id: Pubkey,
        commitment: Commitment = Processed,
    ) -> List[AsyncOpenOrdersAccount]:
        args = cls._build_get_program_accounts_args(
            market=market, program_id=program_id, owner=owner, commitment=commitment
        )
        resp = await conn.get_program_accounts(*args)
        return cls._process_get_program_accounts_resp(resp)

    @classmethod
    async def load(cls, conn: AsyncClient, address: str) -> AsyncOpenOrdersAccount:
        addr_pub_key = Pubkey.from_string(address)
        bytes_data = await load_bytes_data(addr_pub_key, conn)
        return cls.from_bytes(addr_pub_key, bytes_data)
