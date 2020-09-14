from __future__ import annotations

import base64
from typing import Any, Dict, List

from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.system_program import CreateAccountParams, create_account

from ._layouts.open_orders import OPEN_ORDERS_LAYOUT
from .instructions import DEFAULT_DEX_PROGRAM_ID
from .utils import load_bytes_data


def make_create_account_transaction(
    owner_address: PublicKey,
    new_account_address: PublicKey,
    lamports: int,
    program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID,
):
    return create_account(
        CreateAccountParams(
            from_pubkey=owner_address,
            new_account_pubkey=new_account_address,
            lamports=lamports,
            space=OPEN_ORDERS_LAYOUT.sizeof(),
            program_id=program_id,
        )
    )


def get_filtered_program_accounts(
    address: str, program_id: str, filters: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    resp = Client(address).get_program_accounts(
        program_id, encoding="base64", filter_opts=filters, data_size=OPEN_ORDERS_LAYOUT.sizeof()
    )
    accounts = []
    for account in resp["result"]:
        account_details = account["account"]
        accounts.append(
            {
                "public_key": PublicKey(account["pubkey"]),
                "account_info": {
                    "data": base64.decodebytes(account_details["data"].encode("ascii")),
                    "executable": account_details["executable"],
                    "owner": PublicKey(account_details["owner"]),
                    "lamports": account_details["owner"],
                },
            }
        )
    return accounts


class OpenOrderAccount:
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
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

    @staticmethod
    def from_bytes(address: PublicKey, data_bytes: bytes) -> OpenOrderAccount:
        open_order_decoded = OPEN_ORDERS_LAYOUT.parse(data_bytes)
        return OpenOrderAccount(
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

    @staticmethod
    def find_for_market_and_owner(connection: Client, market: PublicKey, owner: PublicKey):
        pass

    @staticmethod
    def load(endpoint: str, address: str) -> OpenOrderAccount:
        addr_pub_key = PublicKey(address)
        bytes_data = load_bytes_data(addr_pub_key, endpoint)
        return OpenOrderAccount.from_bytes(addr_pub_key, bytes_data)
