from __future__ import annotations

from typing import List

from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Recent
from solana.rpc.types import Commitment

from .async_utils import load_bytes_data
from .open_orders_account import _OpenOrdersAccountCore


class AsyncOpenOrdersAccount(_OpenOrdersAccountCore):
    @classmethod
    async def find_for_market_and_owner(  # pylint: disable=too-many-arguments
        cls,
        conn: AsyncClient,
        market: PublicKey,
        owner: PublicKey,
        program_id: PublicKey,
        commitment: Commitment = Recent,
    ) -> List[AsyncOpenOrdersAccount]:
        args = cls._build_get_program_accounts_args(
            market=market, program_id=program_id, owner=owner, commitment=commitment
        )
        resp = await conn.get_program_accounts(*args)
        return cls._process_get_program_accounts_resp(program_id, resp)

    @classmethod
    async def load(cls, conn: AsyncClient, address: str, program_id: PublicKey) -> AsyncOpenOrdersAccount:
        addr_pub_key = PublicKey(address)
        bytes_data = await load_bytes_data(addr_pub_key, conn)
        return cls.from_bytes(addr_pub_key, program_id, bytes_data)
