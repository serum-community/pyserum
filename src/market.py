"""Market module to interact with Serum DEX."""
import base64
from typing import Any

from construct import Bytes, Int8ul, Int64ul, Padding  # type: ignore
from construct import Struct as cStruct  # type: ignore
from solana.publickey import PublicKey
from solana.rpc.api import Client

from .layouts.account_flags import ACCOUNT_FLAGS_LAYOUT

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

MINT_LAYOUT = cStruct(Padding(36), "decimals" / Int8ul, Padding(3))


class Market:
    """Represents a Serum Market."""

    _decode: Any
    _baseSplTokenDecimals: int
    _quoteSolTokenDecimals: int
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


class Slab:
    """Slab data structure."""

    _header: Any
    _nodes: Any

    def __init__(self, header, nodes):
        self._header = header
        self._nodes = nodes

    def get(self, key: int):
        """Return slab node with the given key."""
        raise NotImplementedError("get is not implemented yet")

    def __iter__(self):
        pass


class OrderBook:
    """Represents an order book."""

    market: Market
    is_bids: bool
    slab: Slab

    def __init__(self, market: Market, account_flags: Any, slab: Slab):
        self.market = market
        self.is_bids = account_flags
        self.slab = slab

    @staticmethod
    def decode(market: Market, buffer):
        """Decode the given buffer into an order book."""
        raise NotImplementedError("decode is not implemented yet")

    def get_l2(self, depth: int):
        """Get the Level 2 market information."""
        raise NotImplementedError("get_l2 is not implemented yet")

    def __iter__(self):
        pass
