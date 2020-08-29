from typing import NamedTuple, Any
from struct import Struct
from solana.publickey import PublicKey
from solana.account import Account
from solana.rpc.api import Client
import base64


DEFAULT_DEX_PROGRAM_ID = PublicKey(
  '4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn',
)

_MARKET_FORMAT = ""
_MARKET_FORMAT += "<"    # little endian
_MARKET_FORMAT += "5s"   # 5 bytes padding
_MARKET_FORMAT += "8s"   # 8 bytes of accountFlag, treat it as string
_MARKET_FORMAT += "32s"  # 32 bytes of ownAddress
_MARKET_FORMAT += "Q"    # 8 bytes of vaultSignerNonce
_MARKET_FORMAT += "32s"  # 32 bytes of baseMint
_MARKET_FORMAT += "32s"  # 32 bytes of quoteMint
_MARKET_FORMAT += "32s"  # 32 bytes of baseVault
_MARKET_FORMAT += "Q"    # 8 bytes of baseDepositsTotal
_MARKET_FORMAT += "Q"    # 8 bytes of baseFeesAccrued
_MARKET_FORMAT += "32s"  # 32 bytes quoteVault
_MARKET_FORMAT += "Q"    # 8 bytes of quoteDepositsTotal
_MARKET_FORMAT += "Q"    # 8 bytes of quoteFeesAccrued
_MARKET_FORMAT += "Q"    # 8 bytes of quoteDustThreshold
_MARKET_FORMAT += "32s"  # 32 bytes requestQueue
_MARKET_FORMAT += "32s"  # 32 bytes eventQueue
_MARKET_FORMAT += "32s"  # 32 bytes bids
_MARKET_FORMAT += "32s"  # 32 bytes asks
_MARKET_FORMAT += "Q"    # 8 bytes of baseLotSize
_MARKET_FORMAT += "Q"    # 8 bytes of quoteLotSize
_MARKET_FORMAT += "Q"    # 8 bytes of feeRateBps
_MARKET_FORMAT += "7s"   # 7 bytes padding

# Represents the decoded market state
class MarketState(NamedTuple):
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

    base_lot_size:int
    quote_lot_size: int

    fee_rate_bps: int

    padding: str


    def get_initialized_flag(self):
        # Not sure about this implementation, doesn't produce correct result,
        # it returns '\x03\x00\x00\x00\x00\x00\x00\x00', which means the 58th
        # and 57th bits are set, however I was expecting 64th and 63th.
        return int.from_bytes(self.account_flags, "big") & (1 << 31)



class Market:
    _decode: Any
    _baseSplTokenDecimals: int
    _quoteSolTokenDecimals: int
    _skipPreflight: bool
    _confirmations: int
    _porgram_id: PublicKey

    def __init__(
        self, decoded: Any, base_mint_decimals: int, quote_mint_decimals: int, 
        options: Any, program_id: PublicKey = DEFAULT_DEX_PROGRAM_ID):
        # TODO: add options
        if (not decoded.accountFlags.initialized or not decoded.accountFlags.market):
            raise Exception('Invalid market state')
        self._decode = decoded
        self._base_spl_token_decimals = base_mint_decimals
        self._quote_spl_token_decimals = quote_mint_decimals
        self._skip_preflight = False
        self._confirmations = 10
        self._program_id = program_id

    @staticmethod
    def load(endpoint:str, market_address: str, options: Any, program_id:PublicKey = DEFAULT_DEX_PROGRAM_ID):
        http_client = Client(endpoint)
        base64_res = http_client.get_account_info(
            market_address)["result"]["value"]["data"][0]
        res = Struct(_MARKET_FORMAT).unpack(base64.decodebytes(base64_res.encode("ascii")))
        market_state = MarketState._make(res)
        print(market_state)
        print(market_state.get_initialized_flag())

    def address(self):
        pass

    def base_mint_address(self)->PublicKey:
        pass

    def quoteMintAddress(self)-> PublicKey:
        pass

    def get_mint_decimals(endpoint:str, mint_pub_key) -> int:
        pass


if __name__ == "__main__":
    Market.load(
        "https://api.mainnet-beta.solana.com", "6ibUz1BqSD3f8XP4wEGwoRH4YbYRZ1KDZBeXmrp3KosD", None)
