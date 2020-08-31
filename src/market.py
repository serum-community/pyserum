"""Market module to interact with Serum DEX."""
import base64
from struct import Struct
from typing import Any, NamedTuple

from construct import Padding  # type: ignore
from construct import Struct as cStruct  # type: ignore
from solana.publickey import PublicKey
from solana.rpc.api import Client

from .slab import SLAB_LAYOUT

DEFAULT_DEX_PROGRAM_ID = PublicKey(
    "4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn",
)

_MARKET_FORMAT = ""
_MARKET_FORMAT += "<"  # little endian
_MARKET_FORMAT += "5s"  # 5 bytes padding
_MARKET_FORMAT += "8s"  # 8 bytes of accountFlag, treat it as string
_MARKET_FORMAT += "32s"  # 32 bytes of ownAddress
_MARKET_FORMAT += "Q"  # 8 bytes of vaultSignerNonce
_MARKET_FORMAT += "32s"  # 32 bytes of baseMint
_MARKET_FORMAT += "32s"  # 32 bytes of quoteMint
_MARKET_FORMAT += "32s"  # 32 bytes of baseVault
_MARKET_FORMAT += "Q"  # 8 bytes of baseDepositsTotal
_MARKET_FORMAT += "Q"  # 8 bytes of baseFeesAccrued
_MARKET_FORMAT += "32s"  # 32 bytes quoteVault
_MARKET_FORMAT += "Q"  # 8 bytes of quoteDepositsTotal
_MARKET_FORMAT += "Q"  # 8 bytes of quoteFeesAccrued
_MARKET_FORMAT += "Q"  # 8 bytes of quoteDustThreshold
_MARKET_FORMAT += "32s"  # 32 bytes requestQueue
_MARKET_FORMAT += "32s"  # 32 bytes eventQueue
_MARKET_FORMAT += "32s"  # 32 bytes bids
_MARKET_FORMAT += "32s"  # 32 bytes asks
_MARKET_FORMAT += "Q"  # 8 bytes of baseLotSize
_MARKET_FORMAT += "Q"  # 8 bytes of quoteLotSize
_MARKET_FORMAT += "Q"  # 8 bytes of feeRateBps
_MARKET_FORMAT += "7s"  # 7 bytes padding

_MINT_LAYOUT = ""
_MINT_LAYOUT += "36s"
_MINT_LAYOUT += "b"
_MINT_LAYOUT += "3s"


ORDER_BOOK_LAYOUT = cStruct(Padding(5), "account_flag" / Padding(4), "slab_layout" / SLAB_LAYOUT)


class MarketState(NamedTuple):
    """Market State to stored the parsed market data."""

    name: str
    account_flags: int
    ownAddress: str
    vault_signer_nonce: int
    base_mint: str
    quote_mint: str
    base_vault: str
    base_deposits_total: int
    base_fees_accrued: int
    quote_vault: str
    quote_deposits_total: int
    quote_fees_accrused: int
    quote_dust_threshold: int

    request_queue: int
    event_queue: int

    bids: str
    asks: str

    base_lot_size: int
    quote_lot_size: int

    fee_rate_bps: int

    padding: str

    def get_initialized_flag(self):
        """Return initialized account flag."""
        # Not sure about this implementation, not sure why,
        # it returns '\x03\x00\x00\x00\x00\x00\x00\x00', which means the 58th
        # and 57th bits are set, however I was expecting 64th and 63th.
        res = int.from_bytes(self.account_flags, "little") & 1
        return res

    def get_market_flag(self):
        """Return isMarket account flag."""
        res = (int.from_bytes(self.account_flags, "little") >> 1) & 1
        return res


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
        decoded: MarketState,
        base_mint_decimals: int,
        quote_mint_decimals: int,
        options: Any,  # pylint: disable=unused-argument
        program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID,
    ):
        # TODO: add options
        if not decoded.get_initialized_flag or not decoded.get_market_flag:
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
        res = Struct(_MARKET_FORMAT).unpack(base64.decodebytes(base64_res.encode("ascii")))
        market_state = MarketState._make(res)

        # TODO: add ownAddress check!
        if not market_state.get_initialized_flag() or not market_state.get_market_flag():
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
        _, mint_decimals, _ = Struct(_MINT_LAYOUT).unpack(base64.decodebytes(data.encode("ascii")))
        return mint_decimals

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