from __future__ import annotations

import math

from construct import Container, Struct
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient

from pyserum import async_utils, utils

from .._layouts.market import MARKET_STAT_LAYOUT_V1, MARKET_STAT_LAYOUT_V2
from .types import AccountFlags


class MarketState:  # pylint: disable=too-many-public-methods
    PROGRAM_LAYOUT_VERSIONS = {
        "4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn": 1,
        "BJ3jrUzddfuSrZHXSCxMUUQsjKEyLmuuyZebkcaFp2fg": 1,
        "EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o": 2,
        "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": 3,
    }

    def __init__(
        self, parsed_market: Container, program_id: PublicKey, base_mint_decimals: int, quote_mint_decimals: int
    ) -> None:
        self._decoded = parsed_market
        self._program_id = program_id
        self._base_mint_decimals = base_mint_decimals
        self._quote_mint_decimals = quote_mint_decimals

    @classmethod
    def get_layout_version(cls, program_id: PublicKey):
        return cls.PROGRAM_LAYOUT_VERSIONS.get(str(program_id), 3)

    @classmethod
    def LAYOUT(cls, program_id: PublicKey = None) -> Struct:  # pylint: disable=invalid-name
        """Construct layout of the market state."""
        version = MarketState.get_layout_version(program_id) if program_id else 1
        if version == 1:
            return MARKET_STAT_LAYOUT_V1
        return MARKET_STAT_LAYOUT_V2

    @staticmethod
    def _make_parsed_market(bytes_data: bytes, program_id: PublicKey) -> Container:
        parsed_market = MarketState.LAYOUT(program_id).parse(bytes_data)
        # TODO: add ownAddress check!

        if not parsed_market.account_flags.initialized or not parsed_market.account_flags.market:
            raise Exception("Invalid market")
        return parsed_market

    @classmethod
    def load(cls, conn: Client, market_address: PublicKey, program_id: PublicKey) -> MarketState:
        bytes_data = utils.load_bytes_data(market_address, conn)
        parsed_market = cls._make_parsed_market(bytes_data, program_id)

        base_mint_decimals = utils.get_mint_decimals(conn, PublicKey(parsed_market.base_mint))
        quote_mint_decimals = utils.get_mint_decimals(conn, PublicKey(parsed_market.quote_mint))
        return cls(parsed_market, program_id, base_mint_decimals, quote_mint_decimals)

    @classmethod
    async def async_load(cls, conn: AsyncClient, market_address: PublicKey, program_id: PublicKey) -> MarketState:
        bytes_data = await async_utils.load_bytes_data(market_address, conn)
        parsed_market = cls._make_parsed_market(bytes_data, program_id)
        base_mint_decimals = await async_utils.get_mint_decimals(conn, PublicKey(parsed_market.base_mint))
        quote_mint_decimals = await async_utils.get_mint_decimals(conn, PublicKey(parsed_market.quote_mint))
        return cls(parsed_market, program_id, base_mint_decimals, quote_mint_decimals)

    @classmethod
    def from_bytes(
        cls, program_id: PublicKey, base_mint_decimals: int, quote_mint_decimals: int, buffer: bytes
    ) -> MarketState:
        parsed_market = MarketState.LAYOUT(program_id).parse(buffer)
        # TODO: add ownAddress check!

        if not parsed_market.account_flags.initialized or not parsed_market.account_flags.market:
            raise Exception("Invalid market")

        return cls(parsed_market, program_id, base_mint_decimals, quote_mint_decimals)

    def consume_events_authority(self) -> PublicKey:
        return PublicKey(self._decoded.consume_events_authority)

    def authority(self) -> PublicKey:
        return PublicKey(self._decoded.authority)

    def prune_authority(self) -> PublicKey:
        return PublicKey(self._decoded.prune_authority)

    def program_id(self) -> PublicKey:
        return self._program_id

    def public_key(self) -> PublicKey:
        return PublicKey(self._decoded.own_address)

    def account_flags(self) -> AccountFlags:
        return AccountFlags(**self._decoded.account_flags)

    def asks(self) -> PublicKey:
        return PublicKey(self._decoded.asks)

    def bids(self) -> PublicKey:
        return PublicKey(self._decoded.bids)

    def fee_rate_bps(self) -> int:
        return self._decoded.fee_rate_bps

    def event_queue(self) -> PublicKey:
        return PublicKey(self._decoded.event_queue)

    def request_queue(self) -> PublicKey:
        return PublicKey(self._decoded.request_queue)

    def vault_signer_nonce(self) -> int:
        return self._decoded.vault_signer_nonce

    def base_mint(self) -> PublicKey:
        return PublicKey(self._decoded.base_mint)

    def quote_mint(self) -> PublicKey:
        return PublicKey(self._decoded.quote_mint)

    def base_vault(self) -> PublicKey:
        return PublicKey(self._decoded.base_vault)

    def quote_vault(self) -> PublicKey:
        return PublicKey(self._decoded.quote_vault)

    def base_deposits_total(self) -> int:
        return self._decoded.base_deposits_total

    def quote_deposits_total(self) -> int:
        return self._decoded.quote_deposits_total

    def base_fees_accrued(self) -> int:
        return self._decoded.base_fees_accrued

    def quote_fees_accrued(self) -> int:
        return self._decoded.quote_fees_accrued

    def quote_dust_threshold(self) -> int:
        return self._decoded.quote_dust_threshold

    def base_spl_token_decimals(self) -> int:
        return self._base_mint_decimals

    def quote_spl_token_decimals(self) -> int:
        return self._quote_mint_decimals

    def base_spl_token_multiplier(self) -> int:
        return 10**self._base_mint_decimals

    def quote_spl_token_multiplier(self) -> int:
        return 10**self._quote_mint_decimals

    def base_spl_size_to_number(self, size: int) -> float:
        return size / self.base_spl_token_multiplier()

    def quote_spl_size_to_number(self, size: int) -> float:
        return size / self.quote_spl_token_multiplier()

    def base_lot_size(self) -> int:
        return self._decoded.base_lot_size

    def quote_lot_size(self) -> int:
        return self._decoded.quote_lot_size

    def price_lots_to_number(self, price: int) -> float:
        return float(price * self.quote_lot_size() * self.base_spl_token_multiplier()) / (
            self.base_lot_size() * self.quote_spl_token_multiplier()
        )

    def price_number_to_lots(self, price: float) -> int:
        return int(
            round(
                (price * self.quote_spl_token_multiplier() * self.base_lot_size())
                / (self.base_spl_token_multiplier() * self.quote_lot_size())
            )
        )

    def base_size_lots_to_number(self, size: int) -> float:
        return float(size * self.base_lot_size()) / self.base_spl_token_multiplier()

    def base_size_number_to_lots(self, size: float) -> int:
        return int(math.floor(size * self.base_spl_token_multiplier()) / self.base_lot_size())

    def quote_size_lots_to_number(self, size: int) -> float:
        return float(size * self.quote_lot_size()) / self.quote_spl_token_multiplier()

    def quote_size_number_to_lots(self, size: float) -> int:
        return int(math.floor(size * self.quote_spl_token_multiplier()) / self.quote_lot_size())
