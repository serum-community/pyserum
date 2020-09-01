"""Market module to interact with Serum DEX."""
import base64
from typing import Any, List, Tuple

from construct import Bytes, Int8ul, Int64ul, Padding  # type: ignore
from construct import Struct as cStruct  # type: ignore
from solana.publickey import PublicKey
from solana.rpc.api import Client

from .layouts.account_flags import ACCOUNT_FLAGS_LAYOUT
from .layouts.slab import Slab

DEFAULT_DEX_PROGRAM_ID = PublicKey(
    "4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn",
)

MARKET_FORMAT = cStruct(
    Padding(5),
    "account_flags" / ACCOUNT_FLAGS_LAYOUT,
    "own_address" / Bytes(32),
    "vault_signer_nonce" / Int64ul,
    "base_mint" / Bytes(32),
    "quote_mint" / Bytes(32),
    "base_vault" / Bytes(32),
    "base_deposits_total" / Int64ul,
    "base_fees_accrued" / Int64ul,
    "quote_vault" / Bytes(32),
    "quote_deposits_total" / Int64ul,
    "quote_fees_accrued" / Int64ul,
    "quote_dust_threshold" / Int64ul,
    "request_queue" / Bytes(32),
    "event_queue" / Bytes(32),
    "bids" / Bytes(32),
    "asks" / Bytes(32),
    "base_lot_size" / Int64ul,
    "quote_lot_size" / Int64ul,
    "fee_rate_bps" / Int64ul,
    Padding(7),
)

# TODO: probably need to change the amount of padding since they recently changed it.
# See here: https://github.com/project-serum/serum-js/commit/87c25716c0f2f1092cf27467dd8bb06aabb83fdb
MINT_LAYOUT = cStruct(Padding(36), "decimals" / Int8ul, Padding(3))


class Market:
    """Represents a Serum Market."""

    _decode: Any
    _baseSplTokenDecimals: int
    _quoteSplTokenDecimals: int
    _skipPreflight: bool
    _confirmations: int
    _porgram_id: PublicKey

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        decoded: Any,
        base_mint_decimals: int,
        quote_mint_decimals: int,
        options: Any,  # pylint: disable=unused-argument
        program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID,
    ):
        # TODO: add options
        if not decoded.account_flags.initialized or not decoded.account_flags.market:
            raise Exception("Invalid market state")
        self._decode = decoded
        self._base_spl_token_decimals = base_mint_decimals
        self._quote_spl_token_decimals = quote_mint_decimals
        self._skip_preflight = False
        self._confirmations = 10
        self._program_id = program_id

    @staticmethod
    # pylint: disable=unused-argument
    def load(endpoint: str, market_address: str, options: Any, program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID):
        """Factory method to create a Market."""
        http_client = Client(endpoint)
        base64_res = http_client.get_account_info(market_address)["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(base64_res.encode("ascii"))
        market_state = MARKET_FORMAT.parse(bytes_data)

        # TODO: add ownAddress check!
        if not market_state.account_flags.initialized or not market_state.account_flags.market:
            raise Exception("Invalid market")

        base_mint_decimals = Market.get_mint_decimals(endpoint, PublicKey(market_state.base_mint))
        quote_mint_decimals = Market.get_mint_decimals(endpoint, PublicKey(market_state.quote_mint))

        return Market(market_state, base_mint_decimals, quote_mint_decimals, options)

    def address(self):
        """Return market address."""
        raise NotImplementedError("address is not implemented yet")

    def base_mint_address(self) -> PublicKey:
        """Returns base mint address."""
        raise NotImplementedError("base_mint_address is not implemented yet")

    def quote_mint_address(self) -> PublicKey:
        """Returns quote mint address."""
        raise NotImplementedError("quote_mint_address is not implemented yet")

    def _base_spl_token_multiplier(self):
        return 10 ** self._base_spl_token_decimals

    def _quote_spl_token_multiplier(self):
        return 10 ** self._quote_spl_token_decimals

    def price_lots_to_number(self, price: int):
        return (price * self._decode.quote_lot_size * self._base_spl_token_multiplier) / (
            self._decode.base_lot_size * self._quote_spl_token_multiplier()
        )

    def price_number_to_lots(self, price: int):
        raise NotImplementedError("price_number_to_lots is not implemented")

    def base_size_lots_to_number(self, size: int):
        return size * self._decode.base_lot_size / self._base_spl_token_multiplier()

    @staticmethod
    def get_mint_decimals(endpoint: str, mint_pub_key: PublicKey) -> int:
        """Get the mint decimals from given public key."""
        data = Client(endpoint).get_account_info(mint_pub_key)["result"]["value"]["data"][0]
        bytes_data = base64.decodebytes(data.encode("ascii"))
        return MINT_LAYOUT.parse(bytes_data).decimals

    def load_bids(self, endpoint: str):
        """Load the bid order book"""
        raise NotImplementedError("load_bids is not implemented yet")

    def load_asks(self, endpoint: str):
        """Load the Ask order book."""
        raise NotImplementedError("load_asks is not implemented yet")


# The key is constructed as the (price << 64) + (seq_no if ask_order else !seq_no)
def get_price_from_key(key: int):
    return key >> 64


class OrderBook:
    """Represents an order book."""

    market: Market
    is_bids: bool
    slab: Slab

    def __init__(self, market: Market, account_flags: Any, slab: Slab):
        if not account_flags.initialized or not account_flags.bids ^ account_flags.asks:
            raise Exception("Invalid order book, either not initialized or neither of bids or asks")
        self.market = market
        self.is_bids = account_flags
        self.slab = slab

    @staticmethod
    def decode(market: Market, buffer: bytes):
        """Decode the given buffer into an order book."""
        # This is a bit hacky at the moment. The first 5 bytes are padding, the
        # total length is 8 bytes which is 5 + 8 = 13 bytes.
        account_flags = ACCOUNT_FLAGS_LAYOUT.parse(buffer[5:13])
        slab = Slab.decode(buffer[13:])
        return OrderBook(market, account_flags, slab)

    def get_l2(self, depth: int) -> List[Tuple[int, int, int, int]]:
        """Get the Level 2 market information."""
        descending = self.is_bids
        levels: List[List[int]] = []
        for node in self.slab.items(descending):
            price = get_price_from_key(int.from_bytes(node.key, "little"))
            if len(levels) > 0 and levels[len(levels) - 1][0] == price:
                levels[len(levels) - 1][1] += node.quantiy
            elif len(levels) == depth:
                break
            else:
                levels.append([price, node.quantity])
        return [
            (
                self.market.price_lots_to_number(price),
                self.market.base_size_lots_to_number(size_lots),
                price_lots,
                size_lots,
            )
            for price_lots, size_lots in levels
        ]

    def __iter__(self):
        pass

    def orders(self):
        for node in self.slab.items():
            key = int.from_bytes(node.key)
            price = get_price_from_key(key)
            open_orders_address = base64.b64encode(node.owner)
            yield {
                "order_id": key,
                "client_id": node.client_order_id,
                "open_orders_address": open_orders_address,
                "fee_tier": node.fee_tier,
                "price": self.market.price_lots_to_number(price),
                "price_lots": price,
                "size": self.market.base_size_lots_to_number(node.quantity),
                "size_lots": node.quantity,
                "side": "buy" if self.is_bids else "sell",
            }
