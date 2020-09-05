from typing import List

from solana.publickey import PublicKey
from solana.rpc.api import Client

from ._layouts.open_orders import OPEN_ORDERS_LAYOUT


class OpenOrder:
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
    def from_bytes(address: PublicKey, data_bytes: bytes):
        open_order_decoded = OPEN_ORDERS_LAYOUT.parse(data_bytes)
        return OpenOrder(
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

    def find_for_market_and_owner(self, connection: Client, market: PublicKey, owner: PublicKey):
        pass
