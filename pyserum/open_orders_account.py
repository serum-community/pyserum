from __future__ import annotations

import base64
from typing import List, NamedTuple, TypeVar, Type, Tuple

from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Recent
from solana.rpc.types import Commitment, MemcmpOpts, RPCResponse
from solana.system_program import CreateAccountParams, create_account
from solana.transaction import TransactionInstruction

from ._layouts.open_orders import OPEN_ORDERS_LAYOUT
from .instructions import DEFAULT_DEX_PROGRAM_ID
from .utils import load_bytes_data


class ProgramAccount(NamedTuple):
    public_key: PublicKey
    data: bytes
    is_executablable: bool
    lamports: int
    owner: PublicKey


_T = TypeVar("_T", bound="_OpenOrdersAccountCore")


class _OpenOrdersAccountCore:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        address: PublicKey,
        market: PublicKey,
        owner: PublicKey,
        base_token_free: int,
        base_token_total: int,
        quote_token_free: int,
        quote_token_total: int,
        free_slot_bits: int,
        is_bid_bits: int,
        orders: List[int],
        client_ids: List[int],
    ):
        self.address = address
        self.market = market
        self.owner = owner
        self.base_token_free = base_token_free
        self.base_token_total = base_token_total
        self.quote_token_free = quote_token_free
        self.quote_token_total = quote_token_total
        self.free_slot_bits = free_slot_bits
        self.is_bid_bits = is_bid_bits
        self.orders = orders
        self.client_ids = client_ids

    @classmethod
    def from_bytes(cls: Type[_T], address: PublicKey, buffer: bytes) -> _T:
        open_order_decoded = OPEN_ORDERS_LAYOUT.parse(buffer)
        if not open_order_decoded.account_flags.open_orders or not open_order_decoded.account_flags.initialized:
            raise Exception("Not an open order account or not initialized.")

        return cls(
            address=address,
            market=PublicKey(open_order_decoded.market),
            owner=PublicKey(open_order_decoded.owner),
            base_token_free=open_order_decoded.base_token_free,
            base_token_total=open_order_decoded.base_token_total,
            quote_token_free=open_order_decoded.quote_token_free,
            quote_token_total=open_order_decoded.quote_token_total,
            free_slot_bits=int.from_bytes(open_order_decoded.free_slot_bits, "little"),
            is_bid_bits=int.from_bytes(open_order_decoded.is_bid_bits, "little"),
            orders=[int.from_bytes(order, "little") for order in open_order_decoded.orders],
            client_ids=open_order_decoded.client_ids,
        )

    @classmethod
    def _process_get_program_accounts_resp(cls: Type[_T], resp: RPCResponse) -> List[_T]:
        accounts = []
        for account in resp["result"]:
            account_details = account["account"]
            accounts.append(
                ProgramAccount(
                    public_key=PublicKey(account["pubkey"]),
                    data=base64.decodebytes(account_details["data"][0].encode("ascii")),
                    is_executablable=bool(account_details["executable"]),
                    owner=PublicKey(account_details["owner"]),
                    lamports=int(account_details["lamports"]),
                )
            )

        return [cls.from_bytes(account.public_key, account.data) for account in accounts]

    @staticmethod
    def _build_get_program_accounts_args(
        market: PublicKey, program_id: PublicKey, owner: PublicKey, commitment: Commitment
    ) -> Tuple[PublicKey, Commitment, str, None, int, List[MemcmpOpts]]:
        filters = [
            MemcmpOpts(
                offset=5 + 8,  # 5 bytes of padding, 8 bytes of account flag
                bytes=str(market),
            ),
            MemcmpOpts(
                offset=5 + 8 + 32,  # 5 bytes of padding, 8 bytes of account flag, 32 bytes of market public key
                bytes=str(owner),
            ),
        ]
        data_slice = None
        return (
            program_id,
            commitment,
            "base64",
            data_slice,
            OPEN_ORDERS_LAYOUT.sizeof(),
            filters,
        )


class OpenOrdersAccount(_OpenOrdersAccountCore):
    @classmethod
    def find_for_market_and_owner(  # pylint: disable=too-many-arguments
        cls, conn: Client, market: PublicKey, owner: PublicKey, program_id: PublicKey, commitment: Commitment = Recent
    ) -> List[OpenOrdersAccount]:
        args = cls._build_get_program_accounts_args(
            market=market, program_id=program_id, owner=owner, commitment=commitment
        )
        resp = conn.get_program_accounts(*args)
        return cls._process_get_program_accounts_resp(resp)

    @classmethod
    def load(cls, conn: Client, address: str) -> OpenOrdersAccount:
        addr_pub_key = PublicKey(address)
        bytes_data = load_bytes_data(addr_pub_key, conn)
        return cls.from_bytes(addr_pub_key, bytes_data)


def make_create_account_instruction(
    owner_address: PublicKey,
    new_account_address: PublicKey,
    lamports: int,
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID,
) -> TransactionInstruction:
    return create_account(
        CreateAccountParams(
            from_pubkey=owner_address,
            new_account_pubkey=new_account_address,
            lamports=lamports,
            space=OPEN_ORDERS_LAYOUT.sizeof(),
            program_id=program_id,
        )
    )
